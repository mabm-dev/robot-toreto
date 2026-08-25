param(
    [string]$OpenScad = 'C:\Program Files\OpenSCAD\openscad.com'
)

$ErrorActionPreference = 'Stop'

$sourceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $sourceDir
$sourceFile = Join-Path $sourceDir 'toreto_fusion_95cm.scad'
$outputDir = Join-Path $projectDir 'exports'

if (-not (Test-Path -LiteralPath $OpenScad -PathType Leaf)) {
    throw "No se encontró OpenSCAD en: $OpenScad"
}
if (-not (Test-Path -LiteralPath $sourceFile -PathType Leaf)) {
    throw "No se encontró el modelo: $sourceFile"
}

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

$parts = @(
    'base_quadrant',
    'wheel_arch',
    'trunk_front',
    'trunk_back',
    'waist_shell',
    'chest_front_left',
    'chest_front_right',
    'chest_back_left',
    'chest_back_right',
    'display_bezel',
    'head_front_left',
    'head_front_right',
    'head_back_left',
    'head_back_right',
    'face_bezel',
    'upper_arm_shell',
    'forearm_shell',
    'palm_shell',
    'finger_proximal',
    'finger_middle',
    'finger_distal',
    'thumb_proximal',
    'thumb_distal'
)

foreach ($name in $parts) {
    $outputFile = Join-Path $outputDir ($name + '.stl')
    $definition = 'part="' + $name + '"'
    Write-Host "Exportando $name..."
    & $OpenScad -o $outputFile -D $definition $sourceFile
    if ($null -ne $LASTEXITCODE -and $LASTEXITCODE -ne 0) {
        throw "Falló la exportación de $name (código $LASTEXITCODE)"
    }
    if (-not (Test-Path -LiteralPath $outputFile -PathType Leaf) -or
        (Get-Item -LiteralPath $outputFile).Length -le 84) {
        throw "OpenSCAD no produjo un STL válido para $name"
    }
}

Write-Host "STL exportados en: $outputDir"
