param(
    [string]$OpenScad = "C:\Program Files\OpenSCAD\openscad.com"
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Scad = Join-Path $PSScriptRoot "arms_exterior_95cm.scad"
$Exports = Join-Path $Root "exports\arms"
$Renders = Join-Path $Root "renders"

if (-not (Test-Path -LiteralPath $OpenScad)) {
    throw "OpenSCAD no encontrado: $OpenScad"
}

New-Item -ItemType Directory -Force -Path $Exports,$Renders | Out-Null

$Parts = @(
    "upper_arm_shell_left",
    "upper_arm_shell_right",
    "upper_arm_seam",
    "elbow_cover",
    "elbow_side_cap",
    "forearm_shell_left",
    "forearm_shell_right",
    "forearm_seam",
    "wrist_cuff",
    "shoulder_anchor",
    "shoulder_outer_hood",
    "hand_palm_left",
    "hand_palm_right",
    "finger_proximal_main",
    "finger_middle_main",
    "finger_distal_main",
    "thumb_proximal",
    "thumb_middle",
    "thumb_distal"
)

foreach ($Name in $Parts) {
    $Output = Join-Path $Exports "$Name.stl"
    $Define = 'part="' + $Name + '"'
    $CliArgs = @('-o',$Output,'-D',$Define,$Scad)
    & $OpenScad @CliArgs
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $Output)) {
        throw "Fallo al exportar $Name"
    }
    Write-Host "STL: $Name"
}

$Views = @(
    @{ Name="arms_exterior_iso.png"; Camera="700,-920,180,0,0,-245"; Projection="p"; Part="assembly" },
    @{ Name="arms_exterior_front.png"; Camera="0,-900,-220,0,0,-245"; Projection="o"; Part="assembly" },
    @{ Name="hand_articulation_detail.png"; Camera="180,-260,70,0,0,-45"; Projection="p"; Part="hand_detail" },
    @{ Name="hand_articulation_front.png"; Camera="0,-420,20,0,0,-42"; Projection="p"; Part="hand_detail" },
    @{ Name="shoulder_anchor_detail.png"; Camera="260,-330,170,0,0,-45"; Projection="p"; Part="shoulder_connection_preview" }
)

foreach ($View in $Views) {
    $Output = Join-Path $Renders $View.Name
    $ViewArgs = @(
        '-o',$Output,
        '--imgsize=1400,1100',
        '--colorscheme=Tomorrow Night',
        "--projection=$($View.Projection)",
        "--camera=$($View.Camera)",
        '--viewall',
        '--autocenter',
        '-D',('part="' + $View.Part + '"'),
        $Scad
    )
    & $OpenScad @ViewArgs

    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $Output)) {
        throw "Fallo al renderizar $($View.Name)"
    }
    Write-Host "Render: $($View.Name)"
}

Write-Host "Brazos exteriores de Toreto exportados correctamente."
