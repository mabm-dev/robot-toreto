param(
    [string]$OpenScad = "C:\Program Files\OpenSCAD\openscad.com"
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Scad = Join-Path $PSScriptRoot "base_exterior_95cm.scad"
$Exports = Join-Path $Root "exports\base"
$Renders = Join-Path $Root "renders"

if (-not (Test-Path -LiteralPath $OpenScad)) {
    throw "OpenSCAD no encontrado: $OpenScad"
}

New-Item -ItemType Directory -Force -Path $Exports,$Renders | Out-Null

$Parts = @(
    "core_fascia_quadrant",
    "outer_side_panel",
    "top_deck_quadrant",
    "trim_ring_quadrant",
    "wheel_arch_shell",
    "sensor_panel_bezel",
    "sensor_panel_insert",
    "top_sensor_plinth",
    "top_sensor_cover"
)

foreach ($Name in $Parts) {
    $Output = Join-Path $Exports "$Name.stl"
    $Define = 'part="' + $Name + '"'
    & $OpenScad -o $Output -D $Define $Scad
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $Output)) {
        throw "Fallo al exportar $Name"
    }
    Write-Host "STL: $Name"
}

$Views = @(
    @{ Name="base_exterior_iso.png"; Camera="680,-820,430,0,0,115"; Projection="p" },
    @{ Name="base_exterior_front.png"; Camera="0,-900,145,0,0,110"; Projection="o" },
    @{ Name="base_exterior_top.png"; Camera="0,0,1000,0,0,100"; Projection="o" }
)

foreach ($View in $Views) {
    $Output = Join-Path $Renders $View.Name
    & $OpenScad `
        -o $Output `
        "--imgsize=1400,1050" `
        "--colorscheme=Tomorrow Night" `
        "--projection=$($View.Projection)" `
        "--camera=$($View.Camera)" `
        --viewall `
        --autocenter `
        -D 'part="assembly"' `
        $Scad

    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $Output)) {
        throw "Fallo al renderizar $($View.Name)"
    }
    Write-Host "Render: $($View.Name)"
}

Write-Host "Base exterior de Toreto exportada correctamente."
