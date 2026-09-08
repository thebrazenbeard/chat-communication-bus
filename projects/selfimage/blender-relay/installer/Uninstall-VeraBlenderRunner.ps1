[CmdletBinding()]
param(
    [string]$RemovalToken,
    [string]$RunnerDir = "$env:USERPROFILE\vera-blender-runner",
    [switch]$KeepFiles
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

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
    if ([string]::IsNullOrWhiteSpace($RemovalToken)) {
        $RemovalToken = Read-Host 'Paste a fresh GitHub self-hosted runner removal token (or press Enter to leave GitHub registration intact)'
    }
    if (-not [string]::IsNullOrWhiteSpace($RemovalToken)) {
        Push-Location $RunnerDir
        try {
            & $config remove --unattended --token $RemovalToken
            if ($LASTEXITCODE -ne 0) { throw "GitHub runner removal failed with exit code $LASTEXITCODE." }
        } finally {
            Pop-Location
        }
    } else {
        Write-Warning 'Local startup was disabled, but GitHub runner registration was not removed because no removal token was supplied.'
    }
}

if (-not $KeepFiles -and (Test-Path -LiteralPath $RunnerDir)) {
    if (Test-Path -LiteralPath (Join-Path $RunnerDir '.runner')) {
        Write-Warning "Runner files were kept because registration state still exists at '$RunnerDir'."
    } else {
        Remove-Item -LiteralPath $RunnerDir -Recurse -Force
        Write-Host "Removed runner directory '$RunnerDir'."
    }
}

Write-Host 'Local Vera Blender relay startup is disabled.'
