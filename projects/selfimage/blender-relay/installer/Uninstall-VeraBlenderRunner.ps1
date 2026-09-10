[CmdletBinding()]
param(
    [string]$Repo = 'thebrazenbeard/chat-communication-bus',
    [string]$RunnerDir = "$env:USERPROFILE\vera-blender-runner",
    [switch]$KeepFiles
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RequiredWindowsAccount = 'vera-blender-runner'

function Assert-DedicatedLowPrivilegeAccount {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $account = ($identity.Name -split '\\')[-1]
    if ($account -ne $RequiredWindowsAccount) {
        throw "Refusing runner uninstallation under '$($identity.Name)'. Run this uninstaller while signed in as dedicated Windows account '$RequiredWindowsAccount'."
    }
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    if ($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw "Dedicated runner account '$RequiredWindowsAccount' must not be a local administrator."
    }
}

function Require-GitHubCli {
    $gh = Get-Command gh -ErrorAction SilentlyContinue
    if (-not $gh) {
        throw 'GitHub CLI is required to remove the repository runner registration. This governed uninstaller will not install or authenticate gh implicitly.'
    }
    return $gh.Source
}

function Require-EphemeralAdminToken {
    if ([string]::IsNullOrWhiteSpace($env:GITHUB_RUNNER_ADMIN_TOKEN)) {
        throw 'Set GITHUB_RUNNER_ADMIN_TOKEN only for this uninstaller process to a credential authorized to request a repository runner removal token. Persistent gh login is not accepted.'
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

Assert-DedicatedLowPrivilegeAccount

$configured = Test-Path -LiteralPath (Join-Path $RunnerDir '.runner')
$ghExe = $null
$adminToken = $null
$priorGhToken = $env:GH_TOKEN
$removalToken = $null

if ($configured) {
    $ghExe = Require-GitHubCli
    $adminToken = Require-EphemeralAdminToken

    try {
        $env:GH_TOKEN = $adminToken

        Write-Host 'Verifying private relay repository with the process-scoped token...'
        $repoInfo = Invoke-GhJson -GhExe $ghExe -Arguments @('repo','view',$Repo,'--json','nameWithOwner,visibility') -FailureMessage "Cannot access repository '$Repo' with the process-scoped token."
        if ([string]$repoInfo.nameWithOwner -ne $Repo) {
            throw "GitHub resolved an unexpected repository '$($repoInfo.nameWithOwner)' instead of '$Repo'."
        }
        if ([string]$repoInfo.visibility -ne 'PRIVATE') {
            throw "Relay repository '$Repo' is not private. Refusing governed runner removal through this path."
        }

        Write-Host 'Requesting a short-lived repository runner removal token from GitHub...'
        $response = Invoke-GhJson -GhExe $ghExe -Arguments @('api','--method','POST',"repos/$Repo/actions/runners/remove-token") -FailureMessage 'Could not obtain a short-lived GitHub runner removal token.'
        $removalToken = [string]$response.token
        if ([string]::IsNullOrWhiteSpace($removalToken)) {
            throw 'GitHub returned no runner removal token.'
        }
    }
    finally {
        $env:GH_TOKEN = $priorGhToken
        $env:GITHUB_RUNNER_ADMIN_TOKEN = $null
        $adminToken = $null
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
if ($configured) {
    if (-not (Test-Path -LiteralPath $config)) {
        throw "Runner identity exists but config.cmd is missing from '$RunnerDir'. Files are preserved for manual recovery."
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
Write-Host 'No persistent GitHub authentication was created or consumed by this uninstaller.'
