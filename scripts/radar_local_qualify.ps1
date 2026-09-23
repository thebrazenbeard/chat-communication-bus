param(
    [string]$ReceiptPath = (Join-Path $env:TEMP "radar-local-qualification.json")
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Required command not found: py"
}

$engine = Join-Path $PSScriptRoot "radar_qualify.py"
& py -3.11 $engine --receipt-path $ReceiptPath
$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    exit $exitCode
}
exit 0
