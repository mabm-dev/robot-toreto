param(
    [string]$OpenScad = "C:\Program Files\OpenSCAD\openscad.com"
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Scad = Join-Path $PSScriptRoot "chest_shoulders_exterior_95cm.scad"
$Exports = Join-Path $Root "exports\chest_shoulders"
$Renders = Join-Path $Root "renders"

if (-not (Test-Path -LiteralPath $OpenScad)) {
    throw "OpenSCAD no encontrado: $OpenScad"
}

New-Item -ItemType Directory -Force -Path $Exports,$Renders | Out-Null

$Parts = @(
    "chest_front_left",
    "chest_front_right",
    "chest_back_left",
    "chest_back_right",
    "chest_top_left",
    "chest_top_right",
    "display_bezel",
    "display_panel",
    "waveform_inlay",
    "neck_deck_insert",
    "neck_deck_accent",
    "shoulder_ring_shell",
    "shoulder_socket_disc",
    "shoulder_center_cap",
    "lower_corner_insert",
    "lower_front_slot"
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
    @{ Name="chest_shoulders_iso.png"; Camera="620,-760,390,0,0,0"; Projection="p" },
    @{ Name="chest_shoulders_front.png"; Camera="0,-850,20,0,0,0"; Projection="o" }
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

Write-Host "Hombros y pecho exteriores de Toreto exportados correctamente."

