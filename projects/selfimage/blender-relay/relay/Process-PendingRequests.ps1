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

New-Item -ItemType Directory -Force -Path $requestsDir, $resultsDir, $ArtifactRoot | Out-Null

$pending = Get-ChildItem -LiteralPath $requestsDir -Filter '*.json' -File | Sort-Object Name
if ($pending.Count -eq 0) {
    Write-Host 'No relay request files found.'
    exit 0
}

$processed = 0
$failures = 0
foreach ($requestFile in $pending) {
    try {
        $request = Get-Content -LiteralPath $requestFile.FullName -Raw | ConvertFrom-Json -Depth 50
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
        if ($LASTEXITCODE -ne 0) {
            $failures++
            Write-Warning "Relay request $requestId failed; durable failure receipt was written."
        }
        $processed++
    }
    catch {
        $failures++
        $fallbackId = $requestFile.BaseName
        if ($fallbackId -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$') {
            $fallbackId = "invalid-$([Guid]::NewGuid().ToString('N'))"
        }
        $fallback = [ordered]@{
            version = 1
            relay_version = '1.0.0'
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
# Preserve results for failed jobs but let the workflow become red when any operation failed.
if ($failures -gt 0) { exit 2 }
exit 0
