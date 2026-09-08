[CmdletBinding()]
param(
    [string]$RegistrationToken,
    [string]$RepoUrl = 'https://github.com/thebrazenbeard/chat-communication-bus',
    [string]$RunnerDir = "$env:USERPROFILE\vera-blender-runner",
    [string]$RunnerName = "$env:COMPUTERNAME-vera-blender",
    [switch]$SkipStartupShortcut
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($RegistrationToken)) {
    $RegistrationToken = Read-Host 'Paste the short-lived GitHub self-hosted runner registration token'
}
if ([string]::IsNullOrWhiteSpace($RegistrationToken)) { throw 'A runner registration token is required.' }

Write-Host 'Checking local Blender MCP socket...'
try {
    $probe = [System.Net.Sockets.TcpClient]::new()
    $probe.Connect('127.0.0.1', 9876)
    $probe.Dispose()
    Write-Host 'Blender MCP port 9876 is reachable.'
} catch {
    Write-Warning 'Blender MCP port 9876 is not reachable right now. Runner installation can continue; Blender jobs will fail cleanly until Blender and the addon are running.'
}

if (Test-Path -LiteralPath (Join-Path $RunnerDir '.runner')) {
    throw "A GitHub Actions runner is already configured at '$RunnerDir'. Uninstall/reconfigure it deliberately rather than overwriting registration state."
}

New-Item -ItemType Directory -Force -Path $RunnerDir | Out-Null

Write-Host 'Resolving the latest official GitHub Actions runner release...'
$release = Invoke-RestMethod -Uri 'https://api.github.com/repos/actions/runner/releases/latest' -Headers @{ 'User-Agent' = 'vera-blender-relay-installer' }
$asset = @($release.assets | Where-Object { $_.name -match '^actions-runner-win-x64-.*\.zip$' }) | Select-Object -First 1
if ($null -eq $asset) { throw 'Could not locate the official Windows x64 GitHub Actions runner archive.' }

$zipPath = Join-Path $env:TEMP $asset.name
Write-Host "Downloading official runner $($asset.name)..."
Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $zipPath -UseBasicParsing

Write-Host 'Extracting runner...'
Expand-Archive -LiteralPath $zipPath -DestinationPath $RunnerDir -Force
Remove-Item -LiteralPath $zipPath -Force -ErrorAction SilentlyContinue

$config = Join-Path $RunnerDir 'config.cmd'
if (-not (Test-Path -LiteralPath $config)) { throw 'Runner archive did not contain config.cmd.' }

Push-Location $RunnerDir
try {
    Write-Host 'Registering repository-scoped runner with dedicated vera-blender label...'
    & $config --unattended --url $RepoUrl --token $RegistrationToken --name $RunnerName --labels 'vera-blender' --work '_work' --replace
    if ($LASTEXITCODE -ne 0) { throw "GitHub runner registration failed with exit code $LASTEXITCODE." }
} finally {
    Pop-Location
}

$starter = Join-Path $RunnerDir 'Start-VeraBlenderRunner.ps1'
@'
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$runnerDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$listener = Join-Path $runnerDir 'bin\Runner.Listener.exe'
$existing = @(Get-CimInstance Win32_Process -Filter "Name='Runner.Listener.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.ExecutablePath -and $_.ExecutablePath.StartsWith($runnerDir, [System.StringComparison]::OrdinalIgnoreCase) })
if ($existing.Count -gt 0) { exit 0 }
Start-Process -FilePath (Join-Path $runnerDir 'run.cmd') -WorkingDirectory $runnerDir -WindowStyle Hidden
'@ | Set-Content -LiteralPath $starter -Encoding UTF8

if (-not $SkipStartupShortcut) {
    $startup = [Environment]::GetFolderPath('Startup')
    $shortcutPath = Join-Path $startup 'Vera Blender GitHub Runner.lnk'
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = 'powershell.exe'
    $shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$starter`""
    $shortcut.WorkingDirectory = $RunnerDir
    $shortcut.WindowStyle = 7
    $shortcut.Description = 'Starts the repository-scoped Vera Blender GitHub Actions runner at user logon.'
    $shortcut.Save()
    Write-Host "Installed per-user startup shortcut: $shortcutPath"
}

Write-Host 'Starting the runner now...'
& powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File $starter

Write-Host ''
Write-Host 'Vera Blender runner installation completed.'
Write-Host "Runner directory: $RunnerDir"
Write-Host "Runner name: $RunnerName"
Write-Host 'Required labels: self-hosted, Windows, X64, vera-blender'
Write-Host 'The registration token was used only by config.cmd and is not written by this installer.'
Write-Host 'Next gate: GitHub must show the runner Online, then a relay ping request can prove end-to-end execution.'
