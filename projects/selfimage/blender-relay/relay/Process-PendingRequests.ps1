[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$Workspace,
    [Parameter(Mandatory=$true)][string]$ArtifactRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$base = Join-Path $Workspace 'projects/selfimage/blender-relay'
$requestsDir = Join-Path $base 'requests'
$resultsDir = Join-Path $base 'results'
$relay = Join-Path $base 'relay/Invoke-BlenderRelay.ps1'
$sourceCommit = (& git -C $Workspace rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $sourceCommit -notmatch '^[0-9a-f]{40}$') { throw 'Could not resolve exact relay source commit.' }
$sourceTree = (& git -C $Workspace rev-parse 'HEAD^{tree}').Trim()
if ($LASTEXITCODE -ne 0 -or $sourceTree -notmatch '^[0-9a-f]{40}$') { throw 'Could not resolve exact relay source tree.' }

function Add-SourceIdentityToReceipt {
    param([Parameter(Mandatory=$true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return }
    $receipt = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    $receipt | Add-Member -NotePropertyName source_commit -NotePropertyValue $sourceCommit -Force
    $receipt | Add-Member -NotePropertyName source_tree -NotePropertyValue $sourceTree -Force
    $receipt | ConvertTo-Json -Depth 40 | Set-Content -LiteralPath $Path -Encoding UTF8
}

New-Item -ItemType Directory -Force -Path $requestsDir, $resultsDir, $ArtifactRoot | Out-Null

$pending = Get-ChildItem -LiteralPath $requestsDir -Filter '*.json' -File | Sort-Object Name
if ($pending.Count -eq 0) {
    Write-Host 'No relay request files found.'
    exit 0
}

$processed = 0
$failures = 0
foreach ($requestFile in $pending) {
    $requestId = $null
    $resultPath = $null
    try {
        $request = Get-Content -LiteralPath $requestFile.FullName -Raw | ConvertFrom-Json
        $requestId = [string]$request.request_id
        if ($requestId -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$') {
            throw "Invalid request_id in $($requestFile.Name)."
        }
        if ($requestFile.BaseName -ne $requestId) {
            throw "Request filename must equal request_id: expected '$requestId.json'."
        }
        $resultPath = Join-Path $resultsDir ("$requestId.json")
        if (Test-Path -LiteralPath $resultPath) {
            Write-Host "Skipping already-completed request $requestId."
            continue
        }

        $jobArtifactDir = Join-Path $ArtifactRoot $requestId
        New-Item -ItemType Directory -Force -Path $jobArtifactDir | Out-Null
        Write-Host "Processing Blender relay request $requestId ($($request.operation))."

        & $relay -RequestFile $requestFile.FullName -ArtifactDir $jobArtifactDir -ResultFile $resultPath
        Add-SourceIdentityToReceipt -Path $resultPath
        if ($LASTEXITCODE -ne 0) {
            $failures++
            Write-Warning "Relay request $requestId failed; durable failure receipt was written."
        }
        $processed++
    }
    catch {
        $failures++

        if ($resultPath -and (Test-Path -LiteralPath $resultPath)) {
            Add-SourceIdentityToReceipt -Path $resultPath
            Write-Warning "Relay request $requestId failed after writing its detailed receipt; preserving that receipt."
            Write-Warning $_.Exception.Message
            continue
        }

        $fallbackId = $requestFile.BaseName
        if ($fallbackId -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$') {
            $fallbackId = "invalid-$([Guid]::NewGuid().ToString('N'))"
        }
        $fallback = [ordered]@{
            version = 1
            relay_version = '1.1.2'
            source_commit = $sourceCommit
            source_tree = $sourceTree
            request_id = $fallbackId
            operation = $null
            status = 'failed'
            started_at = [DateTimeOffset]::UtcNow.ToString('o')
            completed_at = [DateTimeOffset]::UtcNow.ToString('o')
            error = $_.Exception.Message
            artifacts = @()
        }
        $fallbackPath = Join-Path $resultsDir ("$fallbackId.json")
        $fallback | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $fallbackPath -Encoding UTF8
        Write-Warning $_.Exception.Message
    }
}

Write-Host "Processed $processed relay request(s); failures: $failures."
if ($failures -gt 0) { exit 2 }
exit 0
