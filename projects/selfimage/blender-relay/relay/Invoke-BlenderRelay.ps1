[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$RequestFile,
    [Parameter(Mandatory=$true)][string]$ArtifactDir,
    [Parameter(Mandatory=$true)][string]$ResultFile
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RelayVersion = '1.1.1'
$HostName = '127.0.0.1'
$Port = 9876
$AllowedOperations = @(
    'ping',
    'addon_info',
    'scene_info',
    'object_info',
    'world_state',
    'viewport_capture',
    'mesh_audit',
    'scene_audit_v1',
    'import_exact_cc0',
    'save_blend_copy',
    'export_scene_glb'
)

$ExactCc0 = @{
    Url = 'https://raw.githubusercontent.com/GilHyeonSoo/HealthAPP/09b0e4af53d3e9436be5e37d9aefa3c5e882b272/assets/models/blender-human-female.glb'
    Bytes = 1644424
    Sha256 = '835d2bf3b55f7e7249bc8fbaa98f40d51e88c7fde55653884d67e6bdd658c8e0'
    GitBlobSha1 = 'df189d7ff267ab47fd6069232395401391399868'
}

$RelayRoot = Split-Path -Parent $PSScriptRoot
$ApprovedSceneAudit = Join-Path $RelayRoot 'approved-scripts\selfimage_blender_scene_audit_v1.py'

function Write-JsonFile {
    param([Parameter(Mandatory=$true)]$Object, [Parameter(Mandatory=$true)][string]$Path)
    $parent = Split-Path -Parent $Path
    if ($parent) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
    $Object | ConvertTo-Json -Depth 40 | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Get-GitBlobSha1 {
    param([Parameter(Mandatory=$true)][string]$Path)
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    $header = [System.Text.Encoding]::ASCII.GetBytes("blob $($bytes.Length)`0")
    $all = New-Object byte[] ($header.Length + $bytes.Length)
    [Array]::Copy($header, 0, $all, 0, $header.Length)
    [Array]::Copy($bytes, 0, $all, $header.Length, $bytes.Length)
    $sha1 = [System.Security.Cryptography.SHA1]::Create()
    try {
        return (($sha1.ComputeHash($all) | ForEach-Object { $_.ToString('x2') }) -join '')
    } finally {
        $sha1.Dispose()
    }
}

function Send-BlenderCommand {
    param(
        [Parameter(Mandatory=$true)][string]$Type,
        [hashtable]$Params = @{},
        [int]$TimeoutMs = 15000
    )

    $client = [System.Net.Sockets.TcpClient]::new()
    $client.ReceiveTimeout = $TimeoutMs
    $client.SendTimeout = $TimeoutMs
    try {
        $async = $client.BeginConnect($HostName, $Port, $null, $null)
        if (-not $async.AsyncWaitHandle.WaitOne([Math]::Min($TimeoutMs, 5000))) {
            throw "Timed out connecting to Blender MCP at ${HostName}:$Port."
        }
        $client.EndConnect($async)
        $stream = $client.GetStream()
        $payload = @{ type = $Type; params = $Params } | ConvertTo-Json -Compress -Depth 50
        $outBytes = [System.Text.Encoding]::UTF8.GetBytes($payload)
        $stream.Write($outBytes, 0, $outBytes.Length)
        $stream.Flush()

        $memory = [System.IO.MemoryStream]::new()
        $buffer = New-Object byte[] 8192
        while ($true) {
            try {
                $count = $stream.Read($buffer, 0, $buffer.Length)
            } catch [System.IO.IOException] {
                break
            }
            if ($count -le 0) { break }
            $memory.Write($buffer, 0, $count)
            $text = [System.Text.Encoding]::UTF8.GetString($memory.ToArray())
            try {
                # Windows PowerShell 5.1 has no ConvertFrom-Json -Depth parameter.
                return ($text | ConvertFrom-Json)
            } catch {
                # Keep reading until a complete JSON response is available.
            }
        }
        throw "Blender did not return a complete JSON response for '$Type'."
    } finally {
        $client.Dispose()
    }
}

function Invoke-FixedBlenderPython {
    param([Parameter(Mandatory=$true)][string]$Code)
    return Send-BlenderCommand -Type 'execute_code' -Params @{ code = $Code } -TimeoutMs 60000
}

function Assert-SafeRequestId {
    param([Parameter(Mandatory=$true)][string]$RequestId)
    if ($RequestId -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$') {
        throw 'Invalid request_id.'
    }
}

function Get-ArgValue {
    param($ArgsObject, [string]$Name, $Default = $null)
    if ($null -ne $ArgsObject -and $ArgsObject.PSObject.Properties.Name -contains $Name) {
        return $ArgsObject.$Name
    }
    return $Default
}

New-Item -ItemType Directory -Force -Path $ArtifactDir | Out-Null
# Windows PowerShell 5.1 has no ConvertFrom-Json -Depth parameter.
$request = Get-Content -LiteralPath $RequestFile -Raw | ConvertFrom-Json

if ($request.version -ne 1) { throw 'Unsupported request version.' }
if (-not $request.request_id) { throw 'request_id is required.' }
Assert-SafeRequestId -RequestId ([string]$request.request_id)
if (-not $request.operation) { throw 'operation is required.' }
$operation = [string]$request.operation
if ($AllowedOperations -notcontains $operation) { throw "Operation '$operation' is not allowlisted." }
$args = $request.args
if ($null -eq $args) { $args = [pscustomobject]@{} }

$started = [DateTimeOffset]::UtcNow
$artifactPaths = @()
$blenderResponse = $null

try {
    switch ($operation) {
        'ping' {
            $blenderResponse = Send-BlenderCommand -Type 'ping'
        }
        'addon_info' {
            $blenderResponse = Send-BlenderCommand -Type 'get_addon_info'
        }
        'scene_info' {
            $blenderResponse = Send-BlenderCommand -Type 'get_scene_info'
        }
        'object_info' {
            $name = [string](Get-ArgValue $args 'name' '')
            if ([string]::IsNullOrWhiteSpace($name) -or $name.Length -gt 200) { throw 'object_info requires a bounded args.name.' }
            $blenderResponse = Send-BlenderCommand -Type 'get_object_info' -Params @{ name = $name }
        }
        'world_state' {
            $blenderResponse = Send-BlenderCommand -Type 'get_world_state_snapshot'
        }
        'viewport_capture' {
            $maxSize = [int](Get-ArgValue $args 'max_size' 1200)
            $maxSize = [Math]::Max(256, [Math]::Min(2000, $maxSize))
            $path = Join-Path $ArtifactDir ("viewport-{0}.png" -f $request.request_id)
            $blenderResponse = Send-BlenderCommand -Type 'get_viewport_screenshot' -Params @{ max_size = $maxSize; filepath = $path; format = 'png' } -TimeoutMs 60000
            if (Test-Path -LiteralPath $path) { $artifactPaths += $path }
        }
        'mesh_audit' {
            $code = @'
import bpy, json
payload = {
    "scene": bpy.context.scene.name,
    "active_object": bpy.context.view_layer.objects.active.name if bpy.context.view_layer.objects.active else None,
    "objects": []
}
for obj in bpy.context.scene.objects:
    row = {
        "name": obj.name,
        "type": obj.type,
        "location": [float(v) for v in obj.location],
        "rotation_euler": [float(v) for v in obj.rotation_euler],
        "scale": [float(v) for v in obj.scale],
        "dimensions": [float(v) for v in obj.dimensions],
        "modifiers": [m.type for m in obj.modifiers],
        "materials": [slot.material.name for slot in obj.material_slots if slot.material]
    }
    if obj.type == "MESH":
        mesh = obj.data
        row.update({
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "polygons": len(mesh.polygons),
            "loops": len(mesh.loops),
            "uv_layers": [uv.name for uv in mesh.uv_layers],
            "color_attributes": [a.name for a in getattr(mesh, "color_attributes", [])]
        })
    payload["objects"].append(row)
print(json.dumps(payload, sort_keys=True))
'@
            $blenderResponse = Invoke-FixedBlenderPython -Code $code
        }
        'scene_audit_v1' {
            if (-not (Test-Path -LiteralPath $ApprovedSceneAudit)) {
                throw 'Approved Self Image scene audit script is missing from the checked-out relay source.'
            }
            $code = Get-Content -LiteralPath $ApprovedSceneAudit -Raw
            $blenderResponse = Invoke-FixedBlenderPython -Code $code
        }
        'import_exact_cc0' {
            $scene = Send-BlenderCommand -Type 'get_scene_info'
            if ($scene.status -ne 'success') { throw 'Could not inspect scene before import.' }
            $names = @($scene.result.objects | ForEach-Object { $_.name })
            $allowedStarter = @('Cube','Light','Camera')
            $unexpected = @($names | Where-Object { $allowedStarter -notcontains $_ })
            if ($unexpected.Count -gt 0 -or [int]$scene.result.object_count -gt 3) {
                throw 'import_exact_cc0 refuses a non-default/non-empty scene.'
            }

            $assetPath = Join-Path $ArtifactDir 'blender-human-female.glb'
            Invoke-WebRequest -Uri $ExactCc0.Url -OutFile $assetPath -UseBasicParsing
            $item = Get-Item -LiteralPath $assetPath
            if ($item.Length -ne $ExactCc0.Bytes) { throw "CC0 source byte count mismatch: $($item.Length)." }
            $sha256 = (Get-FileHash -LiteralPath $assetPath -Algorithm SHA256).Hash.ToLowerInvariant()
            if ($sha256 -ne $ExactCc0.Sha256) { throw "CC0 source SHA-256 mismatch: $sha256." }
            $gitBlob = Get-GitBlobSha1 -Path $assetPath
            if ($gitBlob -ne $ExactCc0.GitBlobSha1) { throw "CC0 source Git blob SHA-1 mismatch: $gitBlob." }

            $jsonPath = ($assetPath | ConvertTo-Json -Compress)
            $code = @"
import bpy, json
path = $jsonPath
for name in ("Cube", "Light", "Camera"):
    obj = bpy.data.objects.get(name)
    if obj is not None:
        bpy.data.objects.remove(obj, do_unlink=True)
bpy.ops.import_scene.gltf(filepath=path)
print(json.dumps({"imported": [o.name for o in bpy.context.scene.objects]}, sort_keys=True))
"@
            $blenderResponse = Invoke-FixedBlenderPython -Code $code
            $artifactPaths += $assetPath
        }
        'save_blend_copy' {
            $path = Join-Path $ArtifactDir ("scene-{0}.blend" -f $request.request_id)
            $jsonPath = ($path | ConvertTo-Json -Compress)
            $code = @"
import bpy, json
path = $jsonPath
bpy.ops.wm.save_as_mainfile(filepath=path, copy=True)
print(json.dumps({"saved_copy": path}, sort_keys=True))
"@
            $blenderResponse = Invoke-FixedBlenderPython -Code $code
            if (Test-Path -LiteralPath $path) { $artifactPaths += $path }
        }
        'export_scene_glb' {
            $path = Join-Path $ArtifactDir ("scene-{0}.glb" -f $request.request_id)
            $jsonPath = ($path | ConvertTo-Json -Compress)
            $code = @"
import bpy, json
path = $jsonPath
bpy.ops.export_scene.gltf(filepath=path, export_format='GLB')
print(json.dumps({"exported_glb": path}, sort_keys=True))
"@
            $blenderResponse = Invoke-FixedBlenderPython -Code $code
            if (Test-Path -LiteralPath $path) { $artifactPaths += $path }
        }
    }

    if ($null -eq $blenderResponse -or $blenderResponse.status -ne 'success') {
        $msg = if ($null -eq $blenderResponse) { 'No Blender response.' } else { $blenderResponse | ConvertTo-Json -Depth 20 -Compress }
        throw "Blender operation failed: $msg"
    }

    $artifactReceipts = @()
    foreach ($artifact in $artifactPaths) {
        if (Test-Path -LiteralPath $artifact) {
            $file = Get-Item -LiteralPath $artifact
            $artifactReceipts += [ordered]@{
                name = $file.Name
                bytes = $file.Length
                sha256 = (Get-FileHash -LiteralPath $artifact -Algorithm SHA256).Hash.ToLowerInvariant()
            }
        }
    }

    $result = [ordered]@{
        version = 1
        relay_version = $RelayVersion
        request_id = [string]$request.request_id
        operation = $operation
        status = 'success'
        started_at = $started.ToString('o')
        completed_at = [DateTimeOffset]::UtcNow.ToString('o')
        blender = $blenderResponse
        artifacts = $artifactReceipts
    }
    Write-JsonFile -Object $result -Path $ResultFile
    exit 0
}
catch {
    $result = [ordered]@{
        version = 1
        relay_version = $RelayVersion
        request_id = [string]$request.request_id
        operation = $operation
        status = 'failed'
        started_at = $started.ToString('o')
        completed_at = [DateTimeOffset]::UtcNow.ToString('o')
        error = $_.Exception.Message
        artifacts = @()
    }
    Write-JsonFile -Object $result -Path $ResultFile
    Write-Error $_.Exception.Message
    exit 1
}