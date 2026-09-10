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

$RequiredWindowsAccount = 'vera-blender-runner'
$RunnerVersion = '2.337.0'
$RunnerAssetName = 'actions-runner-win-x64-2.337.0.zip'
$RunnerAssetUrl = 'https://github.com/actions/runner/releases/download/v2.337.0/actions-runner-win-x64-2.337.0.zip'
$RunnerAssetBytes = 103528051
$RunnerAssetSha256 = '1150692afa94e71f872017e254ea55b6eece1eece3fe7e3a6d4c93d0a1b85cfc'

function Assert-DedicatedLowPrivilegeAccount {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $account = ($identity.Name -split '\\')[-1]
    if ($account -ne $RequiredWindowsAccount) {
        throw "Refusing runner installation under '$($identity.Name)'. Run this installer while signed in as dedicated Windows account '$RequiredWindowsAccount'."
    }
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    if ($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw "Dedicated runner account '$RequiredWindowsAccount' must not be a local administrator."
    }
}

function Require-GitHubCli {
    $gh = Get-Command gh -ErrorAction SilentlyContinue
    if (-not $gh) {
        throw 'GitHub CLI is required but is not installed. This governed installer will not install or upgrade gh implicitly.'
    }
    return $gh.Source
}

function Require-EphemeralAdminToken {
    if ([string]::IsNullOrWhiteSpace($env:GITHUB_RUNNER_ADMIN_TOKEN)) {
        throw 'Set GITHUB_RUNNER_ADMIN_TOKEN only for this installer process to a credential authorized to create a repository runner registration token. Persistent gh login is not accepted.'
    }
    return $env:GITHUB_RUNNER_ADMIN_TOKEN
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
        throw 'GitHub returned no runner registration token.'
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

if (Test-Path -LiteralPath (Join-Path $RunnerDir '.runner')) {
    throw "A GitHub Actions runner is already configured at '$RunnerDir'. The installer will not overwrite existing runner identity state."
}

Assert-DedicatedLowPrivilegeAccount
Test-BlenderSocket
$ghExe = Require-GitHubCli
$adminToken = Require-EphemeralAdminToken
$priorGhToken = $env:GH_TOKEN
$registrationToken = $null

try {
    # gh reads GH_TOKEN directly; do not create a persistent gh auth entry.
    $env:GH_TOKEN = $adminToken

    Write-Host 'Verifying access to the private relay repository with the process-scoped token...'
    $repoInfo = Invoke-GhJson -GhExe $ghExe -Arguments @('repo','view',$Repo,'--json','nameWithOwner,visibility') -FailureMessage "Cannot access private repository '$Repo' with the process-scoped token."
    if ([string]$repoInfo.nameWithOwner -ne $Repo) {
        throw "GitHub resolved an unexpected repository '$($repoInfo.nameWithOwner)' instead of '$Repo'."
    }
    if ([string]$repoInfo.visibility -ne 'PRIVATE') {
        throw "Relay repository '$Repo' is not private. Refusing to attach a self-hosted runner."
    }
    Write-Host "Verified private repository: $($repoInfo.nameWithOwner)"

    $registrationToken = Get-RunnerRegistrationToken -GhExe $ghExe
}
finally {
    $env:GH_TOKEN = $priorGhToken
    $env:GITHUB_RUNNER_ADMIN_TOKEN = $null
    $adminToken = $null
}

New-Item -ItemType Directory -Force -Path $RunnerDir | Out-Null
$zipPath = Join-Path $env:TEMP $RunnerAssetName
Write-Host "Downloading pinned official GitHub Actions runner v$RunnerVersion..."
Invoke-WebRequest -Uri $RunnerAssetUrl -OutFile $zipPath -UseBasicParsing

$item = Get-Item -LiteralPath $zipPath
if ($item.Length -ne $RunnerAssetBytes) {
    Remove-Item -LiteralPath $zipPath -Force -ErrorAction SilentlyContinue
    throw "Pinned runner archive byte-count mismatch. Expected $RunnerAssetBytes, got $($item.Length)."
}
$actual = (Get-FileHash -LiteralPath $zipPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $RunnerAssetSha256) {
    Remove-Item -LiteralPath $zipPath -Force -ErrorAction SilentlyContinue
    throw "Pinned runner archive SHA-256 mismatch. Expected $RunnerAssetSha256, got $actual."
}
Write-Host 'Verified pinned runner archive byte count and SHA-256.'

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
    Write-Host "Installed per-user startup shortcut for dedicated runner account: $shortcutPath"
}

Write-Host 'Starting the runner now...'
& powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File $starter

Write-Host ''
Write-Host 'Vera Blender runner installation completed.'
Write-Host "Runner version: $RunnerVersion"
Write-Host "Runner archive SHA-256: $RunnerAssetSha256"
Write-Host "Runner directory: $RunnerDir"
Write-Host "Runner name: $RunnerName"
Write-Host "Windows account: $RequiredWindowsAccount (non-admin required)"
Write-Host 'Required labels: self-hosted, Windows, X64, vera-blender'
Write-Host 'The process-scoped admin token and short-lived runner registration token were discarded.'
Write-Host 'Leave Blender running with MCP for Blender started on 127.0.0.1:9876 when you want relay jobs to execute.'
