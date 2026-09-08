[CmdletBinding()]
param(
    [string]$Repo = 'thebrazenbeard/chat-communication-bus',
    [string]$RunnerDir = "$env:USERPROFILE\vera-blender-runner",
    [switch]$KeepFiles
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-GhJson {
    param(
        [Parameter(Mandatory=$true)][string]$GhExe,
        [Parameter(Mandatory=$true)][string[]]$Arguments,
        [Parameter(Mandatory=$true)][string]$FailureMessage
    )
    $raw = (& $GhExe @Arguments 2>&1 | Out-String).Trim()
    $exit = $LASTEXITCODE
    if ($exit -ne 0) {
        throw "$FailureMessage`nGitHub CLI output: $raw"
    }
    try {
        return ($raw | ConvertFrom-Json)
    }
    catch {
        throw "$FailureMessage`nGitHub CLI returned non-JSON output: $raw"
    }
}

$startup = [Environment]::GetFolderPath('Startup')
$shortcutPath = Join-Path $startup 'Vera Blender GitHub Runner.lnk'
if (Test-Path -LiteralPath $shortcutPath) {
    Remove-Item -LiteralPath $shortcutPath -Force
    Write-Host 'Removed the Vera Blender runner startup shortcut.'
}

$running = @(Get-CimInstance Win32_Process -Filter "Name='Runner.Listener.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.ExecutablePath -and $_.ExecutablePath.StartsWith($RunnerDir, [System.StringComparison]::OrdinalIgnoreCase) })
foreach ($proc in $running) {
    Write-Host "Stopping runner process $($proc.ProcessId)..."
    Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
}

$config = Join-Path $RunnerDir 'config.cmd'
if (Test-Path -LiteralPath (Join-Path $RunnerDir '.runner')) {
    $gh = Get-Command gh -ErrorAction SilentlyContinue
    if (-not $gh) {
        Write-Warning 'GitHub CLI is unavailable; local startup is disabled but the GitHub runner registration cannot be removed automatically.'
    }
    else {
        & $gh.Source auth status --hostname github.com 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host 'GitHub login is required once to request the short-lived runner removal token.'
            & $gh.Source auth login --hostname github.com --git-protocol https --web
            if ($LASTEXITCODE -ne 0) { throw 'GitHub authentication failed; local startup is disabled but GitHub runner registration remains.' }
        }

        $response = Invoke-GhJson -GhExe $gh.Source -Arguments @('api','--method','POST',"repos/$Repo/actions/runners/remove-token") -FailureMessage 'Could not obtain a short-lived GitHub runner removal token.'
        $removalToken = [string]$response.token
        if ([string]::IsNullOrWhiteSpace($removalToken)) {
            throw 'GitHub returned no runner removal token.'
        }
        Push-Location $RunnerDir
        try {
            & $config remove --unattended --token $removalToken
            if ($LASTEXITCODE -ne 0) { throw "GitHub runner removal failed with exit code $LASTEXITCODE." }
        }
        finally {
            Pop-Location
            $removalToken = $null
        }
    }
}

if (-not $KeepFiles -and (Test-Path -LiteralPath $RunnerDir)) {
    if (Test-Path -LiteralPath (Join-Path $RunnerDir '.runner')) {
        Write-Warning "Runner files were kept because GitHub registration state still exists at '$RunnerDir'."
    }
    else {
        Remove-Item -LiteralPath $RunnerDir -Recurse -Force
        Write-Host "Removed runner directory '$RunnerDir'."
    }
}

Write-Host 'Local Vera Blender relay startup is disabled.'
