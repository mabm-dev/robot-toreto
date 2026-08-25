param(
    [string]$OpenScad = "C:\Program Files\OpenSCAD\openscad.com"
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Scad = Join-Path $PSScriptRoot "head_neck_exterior_95cm.scad"
$Exports = Join-Path $Root "exports\head_neck"
$Renders = Join-Path $Root "renders"

if (-not (Test-Path -LiteralPath $OpenScad)) {
    throw "OpenSCAD no encontrado: $OpenScad"
}

New-Item -ItemType Directory -Force -Path $Exports,$Renders | Out-Null

$Parts = @(
    "head_front_left",
    "head_front_right",
    "head_back_left",
    "head_back_right",
    "face_bezel_left",
    "face_bezel_right",
    "face_panel_left",
    "face_panel_right",
    "face_glass_left",
    "face_glass_right",
    "eye_ring",
    "eye_pupil",
    "face_camera_dot",
    "side_pod_shell",
    "side_pod_insert",
    "neck_lower_ring",
    "neck_column_shell",
    "neck_upper_ring",
    "neck_bridge_cover"
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
    @{ Name="head_neck_iso.png"; Camera="570,-720,380,0,0,145"; Projection="p" },
    @{ Name="head_neck_front.png"; Camera="0,-800,160,0,0,150"; Projection="o" }
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

Write-Host "Cabeza y cuello exteriores de Toreto exportados correctamente."

