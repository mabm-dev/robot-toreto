param(
    [string]$OpenScad = "C:\Program Files\OpenSCAD\openscad.com"
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Scad = Join-Path $PSScriptRoot "trunk_exterior_95cm.scad"
$Exports = Join-Path $Root "exports\trunk"
$Renders = Join-Path $Root "renders"

if (-not (Test-Path -LiteralPath $OpenScad)) {
    throw "OpenSCAD no encontrado: $OpenScad"
}

New-Item -ItemType Directory -Force -Path $Exports,$Renders | Out-Null

$Parts = @(
    "lower_skirt_front",
    "lower_skirt_back",
    "skirt_top_lip_half",
    "tower_shell",
    "tower_collar",
    "tower_front_relief",
    "tower_detail_tab",
    "trunk_sensor_bezel",
    "trunk_sensor_insert",
    "service_panel_frame",
    "service_port_ring",
    "service_marker"
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
    @{ Name="trunk_exterior_iso.png"; Camera="480,-650,330,0,0,100"; Projection="p" },
    @{ Name="trunk_exterior_front.png"; Camera="0,-700,115,0,0,100"; Projection="o" }
)

foreach ($View in $Views) {
    $Output = Join-Path $Renders $View.Name
    & $OpenScad `
        -o $Output `
        "--imgsize=1400,1100" `
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

Write-Host "Tronco exterior de Toreto exportado correctamente."

