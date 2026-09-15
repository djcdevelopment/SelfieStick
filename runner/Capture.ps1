param(
    [Parameter(Mandatory=$true)][string]$GameRoot,
    [Parameter(Mandatory=$true)][string]$WorldDb,
    [Parameter(Mandatory=$true)][string]$WorldFwl,
    [Parameter(Mandatory=$true)][string]$CharacterFile,
    [string]$Out = (Join-Path $PSScriptRoot 'results')
)
$ErrorActionPreference = 'Stop'
python (Join-Path $PSScriptRoot 'capture.py') --spec (Join-Path $PSScriptRoot 'capture.json') --game-root $GameRoot --world-db $WorldDb --world-fwl $WorldFwl --character-file $CharacterFile --out $Out
exit $LASTEXITCODE
