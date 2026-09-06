param(
    [string]$ReceiptPath = ""
)

$ErrorActionPreference = "Stop"

function Assert-Command {
    param([Parameter(Mandatory = $true)][string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command not found: $Name"
    }
}

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$ArgumentList = @(),
        [string]$WorkingDirectory = ""
    )

    $oldLocation = Get-Location
    try {
        if ($WorkingDirectory) {
            Set-Location $WorkingDirectory
        }
        & $FilePath @ArgumentList
        if ($LASTEXITCODE -ne 0) {
            throw "Command failed with exit code $LASTEXITCODE: $FilePath $($ArgumentList -join ' ')"
        }
    }
    finally {
        Set-Location $oldLocation
    }
}

function Get-CheckedOutput {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$ArgumentList = @()
    )

    $output = & $FilePath @ArgumentList
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE: $FilePath $($ArgumentList -join ' ')"
    }
    return ($output | Out-String).Trim()
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

Assert-Command git
Assert-Command py
Assert-Command deno
Assert-Command supabase
Assert-Command docker
Assert-Command psql

$sourceCommit = Get-CheckedOutput git @("rev-parse", "HEAD")
$sourceTree = Get-CheckedOutput git @("rev-parse", "HEAD^{tree}")
if (-not $sourceCommit -or $sourceCommit.Length -lt 40 -or -not $sourceTree -or $sourceTree.Length -lt 40) {
    throw "Could not determine exact source commit/tree"
}

$workingTreeState = Get-CheckedOutput git @("status", "--porcelain")
if ($workingTreeState) {
    throw "Working tree is not clean. Qualification receipts must bind exact committed bytes only."
}

$pythonVersions = @("3.11", "3.12")
foreach ($version in $pythonVersions) {
    $observed = Get-CheckedOutput py @("-$version", "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if ($observed -ne $version) {
        throw "Python $version required; observed $observed"
    }
}

$denoFirstLine = (Get-CheckedOutput deno @("--version") -split "`r?`n")[0]
if ($denoFirstLine -ne "deno 2.9.6") {
    throw "Deno 2.9.6 required; observed '$denoFirstLine'"
}

$supabaseVersion = Get-CheckedOutput supabase @("--version")
if ($supabaseVersion -ne "2.116.0") {
    throw "Supabase CLI 2.116.0 required; observed '$supabaseVersion'"
}

Invoke-Checked docker @("info")

Write-Host "==> Radar local qualification"
Write-Host "source_commit=$sourceCommit"
Write-Host "source_tree=$sourceTree"
Write-Host "mode=LOCAL_NO_PAID_SERVICES"

foreach ($version in $pythonVersions) {
    Write-Host "==> Python $version"
    $venv = Join-Path $env:TEMP "radar-qualify-$version-$($sourceCommit.Substring(0,12))"
    if (Test-Path $venv) {
        Remove-Item -Recurse -Force $venv
    }

    Invoke-Checked py @("-$version", "-m", "venv", $venv)
    $venvPython = Join-Path $venv "Scripts\python.exe"
    Invoke-Checked $venvPython @("-m", "pip", "install", "pip==26.2.1")
    Invoke-Checked $venvPython @("-m", "pip", "install", "-e", ".[test]")
    Invoke-Checked $venvPython @("-m", "compileall", "-q", "src")
    Invoke-Checked $venvPython @("-m", "pytest", "-q")
    Invoke-Checked $venvPython @("scripts/radar_source_hashes.py")
}

Write-Host "==> Edge / Deno"
$edgeDir = Join-Path $repoRoot "supabase/functions/github-bus-ingest"
Invoke-Checked deno @("ci") $edgeDir
Invoke-Checked deno @("check", "index.ts") $edgeDir

Write-Host "==> SQL / local Supabase"
$null = & supabase status 2>$null
if ($LASTEXITCODE -eq 0) {
    throw "Local Supabase stack is already running; refusing destructive qualification"
}

$supabaseProjectId = "chat-communication-bus"
$supabaseDbResource = "supabase_db_$supabaseProjectId"

$null = & docker container inspect $supabaseDbResource 2>$null
if ($LASTEXITCODE -eq 0) {
    throw "Local Supabase database container already exists; refusing destructive qualification"
}

$null = & docker volume inspect $supabaseDbResource 2>$null
if ($LASTEXITCODE -eq 0) {
    throw "Local Supabase database volume already exists; refusing destructive qualification"
}

$supabaseProjectLabel = "com.supabase.cli.project=$supabaseProjectId"
$existingProjectContainers = Get-CheckedOutput docker @("ps", "-a", "--filter", "label=$supabaseProjectLabel", "--format", "{{.ID}}")
$existingProjectVolumes = Get-CheckedOutput docker @("volume", "ls", "--filter", "label=$supabaseProjectLabel", "--format", "{{.Name}}")
$existingProjectNetworks = Get-CheckedOutput docker @("network", "ls", "--filter", "label=$supabaseProjectLabel", "--format", "{{.ID}}")
if ($existingProjectContainers -or $existingProjectVolumes -or $existingProjectNetworks) {
    throw "Local Supabase project Docker resources already exist; refusing destructive qualification"
}

$sqlCleanupRequired = $true
$sqlFailure = $null
$cleanupFailure = $null
try {
    Invoke-Checked supabase @("start")
    Invoke-Checked supabase @("db", "reset")

    $pguri = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"
    $tests = Get-ChildItem (Join-Path $repoRoot "supabase/tests") -Filter "radar_*.sql" | Sort-Object Name
    if (-not $tests) {
        throw "No Radar SQL assertion files found"
    }

    foreach ($test in $tests) {
        Write-Host "==> $($test.FullName)"
        Invoke-Checked psql @($pguri, "-v", "ON_ERROR_STOP=1", "-f", $test.FullName)
    }
}
catch {
    $sqlFailure = $_
}
finally {
    if ($sqlCleanupRequired) {
        try {
            Invoke-Checked supabase @("stop", "--no-backup")
        }
        catch {
            $cleanupFailure = $_
        }
    }
}

if ($sqlFailure -and $cleanupFailure) {
    throw "SQL qualification failed: $($sqlFailure.Exception.Message); Local Supabase cleanup failed: $($cleanupFailure.Exception.Message)"
}
if ($cleanupFailure) {
    throw "Local Supabase cleanup failed: $($cleanupFailure.Exception.Message)"
}
if ($sqlFailure) {
    throw $sqlFailure
}

$finalSourceCommit = Get-CheckedOutput git @("rev-parse", "HEAD")
if ($finalSourceCommit -ne $sourceCommit) {
    throw "Source commit changed during qualification"
}

$finalSourceTree = Get-CheckedOutput git @("rev-parse", "HEAD^{tree}")
if ($finalSourceTree -ne $sourceTree) {
    throw "Source tree changed during qualification"
}

$finalWorkingTreeState = Get-CheckedOutput git @("status", "--porcelain")
if ($finalWorkingTreeState) {
    throw "Working tree changed during qualification"
}

$receipt = [ordered]@{
    schema_version = 1
    status = "PASS"
    qualification_mode = "LOCAL_NO_PAID_SERVICES"
    source_commit = $sourceCommit
    source_tree = $sourceTree
    working_tree = "CLEAN"
    python = @("3.11", "3.12")
    pip = "26.2.1"
    deno = "2.9.6"
    supabase_cli = "2.116.0"
    completed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
}

$json = $receipt | ConvertTo-Json -Depth 4
if ($ReceiptPath) {
    if ([System.IO.Path]::IsPathRooted($ReceiptPath)) {
        $receiptFullPath = [System.IO.Path]::GetFullPath($ReceiptPath)
    }
    else {
        $receiptFullPath = [System.IO.Path]::GetFullPath((Join-Path $repoRoot $ReceiptPath))
    }

    $repoFullPath = [System.IO.Path]::GetFullPath($repoRoot)
    $repoPrefix = $repoFullPath
    if (-not $repoPrefix.EndsWith([System.IO.Path]::DirectorySeparatorChar.ToString())) {
        $repoPrefix += [System.IO.Path]::DirectorySeparatorChar
    }
    if (
        $receiptFullPath.Equals($repoFullPath, [System.StringComparison]::OrdinalIgnoreCase) -or
        $receiptFullPath.StartsWith($repoPrefix, [System.StringComparison]::OrdinalIgnoreCase)
    ) {
        throw "Receipt path must be outside source checkout"
    }

    $receiptDir = Split-Path -Parent $receiptFullPath
    if ($receiptDir -and -not (Test-Path $receiptDir)) {
        New-Item -ItemType Directory -Force -Path $receiptDir | Out-Null
    }
    Set-Content -Path $receiptFullPath -Value $json -Encoding UTF8
    Write-Host "receipt=$receiptFullPath"
}

Write-Output $json
