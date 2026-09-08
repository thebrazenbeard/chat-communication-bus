[CmdletBinding()]
param(
    [string]$Repo = 'thebrazenbeard/chat-communication-bus',
    [string]$RepoUrl = 'https://github.com/thebrazenbeard/chat-communication-bus',
    [string]$RunnerDir = "$env:USERPROFILE\vera-blender-runner",
    [string]$RunnerName = "$env:COMPUTERNAME-vera-blender",
    [switch]$SkipStartupShortcut
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Ensure-GitHubCli {
    $gh = Get-Command gh -ErrorAction SilentlyContinue
    if ($gh) { return $gh.Source }

    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if (-not $winget) {
        throw 'GitHub CLI is not installed and winget is unavailable. Install GitHub CLI from https://cli.github.com/ and rerun this installer.'
    }

    Write-Host 'Installing GitHub CLI with winget...'
    & winget install --id GitHub.cli --exact --accept-source-agreements --accept-package-agreements
    if ($LASTEXITCODE -ne 0) { throw "GitHub CLI installation failed with exit code $LASTEXITCODE." }

    $candidates = @(
        "$env:ProgramFiles\GitHub CLI\gh.exe",
        "$env:LOCALAPPDATA\Programs\GitHub CLI\gh.exe"
    )
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) { return $candidate }
    }
    $gh = Get-Command gh -ErrorAction SilentlyContinue
    if ($gh) { return $gh.Source }
    throw 'GitHub CLI was installed but gh.exe could not be found. Open a new PowerShell window and rerun the installer.'
}

function Ensure-GitHubAuth {
    param([Parameter(Mandatory=$true)][string]$GhExe)
    & $GhExe auth status --hostname github.com 2>$null
    if ($LASTEXITCODE -eq 0) { return }

    Write-Host 'GitHub authentication is required once so the installer can request a short-lived runner registration token.'
    Write-Host 'A browser/device login will open. The relay never stores the temporary runner token itself.'
    & $GhExe auth login --hostname github.com --git-protocol https --web
    if ($LASTEXITCODE -ne 0) { throw "GitHub CLI authentication failed with exit code $LASTEXITCODE." }
}

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

function Get-RunnerRegistrationToken {
    param([Parameter(Mandatory=$true)][string]$GhExe)
    Write-Host 'Requesting a short-lived repository runner registration token from GitHub...'
    $response = Invoke-GhJson -GhExe $GhExe -Arguments @('api','--method','POST',"repos/$Repo/actions/runners/registration-token") -FailureMessage 'Could not obtain a GitHub self-hosted runner registration token.'
    $token = [string]$response.token
    if ([string]::IsNullOrWhiteSpace($token)) {
        throw 'GitHub returned no runner registration token. Confirm the signed-in GitHub account has admin access to the private repository.'
    }
    return $token
}

function Test-BlenderSocket {
    Write-Host 'Checking local Blender MCP socket...'
    $probe = [System.Net.Sockets.TcpClient]::new()
    try {
        $async = $probe.BeginConnect('127.0.0.1', 9876, $null, $null)
        if (-not $async.AsyncWaitHandle.WaitOne(2500)) { throw 'timeout' }
        $probe.EndConnect($async)
        Write-Host 'Blender MCP port 9876 is reachable.'
    }
    catch {
        Write-Warning 'Blender MCP port 9876 is not reachable right now. Installation can continue; Blender jobs will fail cleanly until Blender and the MCP addon are running.'
    }
    finally {
        $probe.Dispose()
    }
}

function Get-OfficialRunnerAsset {
    Write-Host 'Resolving the latest official GitHub Actions runner release...'
    $release = Invoke-RestMethod -Uri 'https://api.github.com/repos/actions/runner/releases/latest' -Headers @{ 'User-Agent' = 'vera-blender-relay-installer' }
    $asset = @($release.assets | Where-Object { $_.name -match '^actions-runner-win-x64-.*\.zip$' }) | Select-Object -First 1
    if ($null -eq $asset) { throw 'Could not locate the official Windows x64 GitHub Actions runner archive.' }
    return $asset
}

if (Test-Path -LiteralPath (Join-Path $RunnerDir '.runner')) {
    throw "A GitHub Actions runner is already configured at '$RunnerDir'. The installer will not overwrite existing runner identity state."
}

Test-BlenderSocket
$ghExe = Ensure-GitHubCli
Ensure-GitHubAuth -GhExe $ghExe

Write-Host 'Verifying access to the private relay repository...'
$repoInfo = Invoke-GhJson -GhExe $ghExe -Arguments @('repo','view',$Repo,'--json','nameWithOwner,visibility') -FailureMessage "Cannot access private repository '$Repo' with the current GitHub login."
if ([string]$repoInfo.nameWithOwner -ne $Repo) {
    throw "GitHub resolved an unexpected repository '$($repoInfo.nameWithOwner)' instead of '$Repo'."
}
if ([string]$repoInfo.visibility -ne 'PRIVATE') {
    throw "Relay repository '$Repo' is not private. Refusing to attach a self-hosted runner."
}
Write-Host "Verified private repository: $($repoInfo.nameWithOwner)"

$registrationToken = Get-RunnerRegistrationToken -GhExe $ghExe
$asset = Get-OfficialRunnerAsset

New-Item -ItemType Directory -Force -Path $RunnerDir | Out-Null
$zipPath = Join-Path $env:TEMP $asset.name
Write-Host "Downloading official runner $($asset.name)..."
Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $zipPath -UseBasicParsing

if ($asset.PSObject.Properties.Name -contains 'digest' -and -not [string]::IsNullOrWhiteSpace([string]$asset.digest)) {
    $digest = [string]$asset.digest
    if ($digest -match '^sha256:([0-9a-fA-F]{64})$') {
        $expected = $Matches[1].ToLowerInvariant()
        $actual = (Get-FileHash -LiteralPath $zipPath -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actual -ne $expected) { throw "Official runner archive SHA-256 mismatch. Expected $expected, got $actual." }
        Write-Host 'Verified official runner archive SHA-256.'
    }
}

Write-Host 'Extracting runner...'
Expand-Archive -LiteralPath $zipPath -DestinationPath $RunnerDir -Force
Remove-Item -LiteralPath $zipPath -Force -ErrorAction SilentlyContinue

$config = Join-Path $RunnerDir 'config.cmd'
if (-not (Test-Path -LiteralPath $config)) { throw 'Runner archive did not contain config.cmd.' }

Push-Location $RunnerDir
try {
    Write-Host 'Registering repository-scoped runner with dedicated vera-blender label...'
    & $config --unattended --url $RepoUrl --token $registrationToken --name $RunnerName --labels 'vera-blender' --work '_work' --replace
    if ($LASTEXITCODE -ne 0) { throw "GitHub runner registration failed with exit code $LASTEXITCODE." }
}
finally {
    Pop-Location
    $registrationToken = $null
}

$starter = Join-Path $RunnerDir 'Start-VeraBlenderRunner.ps1'
@'
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$runnerDir = Split-Path -Parent $MyInvocation.MyCommand.Path
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
Write-Host 'The short-lived runner registration token was requested automatically, used by config.cmd, and discarded.'
Write-Host 'Leave Blender running with MCP for Blender started on 127.0.0.1:9876 when you want relay jobs to execute.'
