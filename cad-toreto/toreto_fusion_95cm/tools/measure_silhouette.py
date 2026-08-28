"""Extrae la tabla maestra de la silueta del robot desde los lienzos calibrados.

Por qué existe: a 29 ago 2026 hay TRES geometrías del mismo robot que no
coinciden -- los add-ins de Fusion, los módulos OpenSCAD de
`toreto_exterior_95cm`, y la lámina de referencia. `docs/DECISIONES.md`
("Fuente maestra de cotas") dice que manda **la lámina**, así que esta
herramienta la mide y produce la tabla contra la que hay que corregir las
otras dos.

Ejemplo del desacuerdo que motivó esto: la carcasa del pecho mide ~252 mm de
ancho en la lámina; el add-in de Fusion lo tiene bien (`ancho_carcasa_pecho
= 252 mm`, distinto de `ancho_pecho = 340 mm`, que es la separación de
HOMBROS), pero OpenSCAD se comió esa distinción y modela el pecho como un
loft de 288->340 mm. Es decir, ~40-90 mm de más en la parte que más importa
para decidir qué cabe dentro.

Qué mide, a partir de los PNG ya calibrados a 0,5 mm/px (Z=0 en el suelo,
Z=950 en la coronilla):

  - Lienzo FRONTAL  -> ancho en X, separando el torso de los brazos.
  - Lienzo LATERAL  -> fondo en Y (proyección: incluye el brazo, que en
                       vista lateral se solapa con el torso; se avisa).

Limitaciones conocidas, para no leer los números con más fe de la que
merecen:

  1. El panel oscuro de la pantalla del pecho tiene casi el mismo tono que
     el fondo del lienzo. Se reconstruye fusionando tramos separados por
     menos de `MERGE_GAP_PX`; si algún día cambia el arte de la lámina, ese
     valor hay que revisarlo.
  2. A la altura de los hombros el brazo toca el torso y no hay hueco de
     fondo que los separe: ahí la columna "torso" incluye hombro y se marca
     con `~`.
  3. En vista lateral no se puede separar brazo de torso de ninguna forma
     fiable: son el mismo bulto proyectado. El fondo del torso limpio solo
     es de fiar por debajo de la cintura y por encima del cuello.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

LIENZOS_DIR = Path(__file__).resolve().parents[1] / "reference" / "lienzos_95cm"
CALIBRATION_JSON = LIENZOS_DIR / "calibracion_95cm.json"

BG_TOLERANCE = 12
MIN_RUN_PX = 6
MERGE_GAP_PX = 90      # reconstruye la carcasa a través del panel oscuro
EDGE_MARGIN_PX = 200   # excluye la regla cian (izq) y las líneas guía (der)
CENTER_SLACK_PX = 40   # cuánto puede desviarse del eje el tramo del torso


def _is_background(pixel, bg) -> bool:
    return all(abs(pixel[i] - bg[i]) <= BG_TOLERANCE for i in range(3))


def _runs(px, width: int, y: int, bg) -> list[tuple[int, int]]:
    """Tramos horizontales de cuerpo en la fila `y`."""
    out: list[tuple[int, int]] = []
    start = None
    for x in range(EDGE_MARGIN_PX, width - EDGE_MARGIN_PX):
        if not _is_background(px[x, y], bg):
            if start is None:
                start = x
        else:
            if start is not None and x - start >= MIN_RUN_PX:
                out.append((start, x - 1))
            start = None
    if start is not None:
        out.append((start, width - EDGE_MARGIN_PX - 1))
    return out


def _merge(runs: list[tuple[int, int]], gap: int) -> list[list[int]]:
    if not runs:
        return []
    merged = [list(runs[0])]
    for a, b in runs[1:]:
        if a - merged[-1][1] <= gap:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    return merged


def _measure_row(px, width: int, y: int, bg, center: int):
    """Devuelve (ancho_torso_mm, ancho_total_mm, n_grupos) para una fila.

    `ancho_total` abarca de la extremidad más a la izquierda a la más a la
    derecha (brazos incluidos); `ancho_torso` es solo el grupo central.
    """
    groups = _merge(_runs(px, width, y, bg), MERGE_GAP_PX)
    if not groups:
        return None, None, 0
    total = (groups[-1][1] - groups[0][0])
    central = [
        g for g in groups
        if g[0] - CENTER_SLACK_PX <= center <= g[1] + CENTER_SLACK_PX
    ]
    torso = max(central, key=lambda g: g[1] - g[0]) if central else None
    torso_w = (torso[1] - torso[0]) if torso else None
    return torso_w, total, len(groups)


def main() -> None:
    calibration = json.loads(CALIBRATION_JSON.read_text(encoding="utf-8"))
    mm_per_px = calibration["mm_per_pixel"]
    z0_px = calibration["robot_bottom_px"]
    views = calibration["views"]

    frontal = Image.open(LIENZOS_DIR / views["frontal"]).convert("RGB")
    lateral = Image.open(LIENZOS_DIR / views["lateral_derecho"]).convert("RGB")
    fpx, lpx = frontal.load(), lateral.load()
    fw, _ = frontal.size
    lw, _ = lateral.size
    bg = frontal.getpixel((5, 5))
    fcenter, lcenter = fw // 2, lw // 2

    print("TABLA MAESTRA DE SILUETA -- medida sobre los lienzos calibrados")
    print(f"({mm_per_px} mm/px, Z=0 en el suelo, Z=950 en la coronilla)\n")
    print("  Z(mm)   ANCHO torso   ANCHO total   FONDO (lateral)   grupos")
    print("  " + "-" * 62)

    for z in range(940, -1, -20):
        y = int(round(z0_px - z / mm_per_px))
        ftorso, ftotal, fgroups = _measure_row(fpx, fw, y, bg, fcenter)
        _, ltotal, _ = _measure_row(lpx, lw, y, bg, lcenter)

        def fmt(v):
            return f"{v * mm_per_px:8.1f}" if v is not None else "     n/a"

        # Un solo grupo en frontal = brazos pegados al torso, no separables.
        mark = "~" if fgroups == 1 else " "
        print(f"  {z:5}   {fmt(ftorso)}{mark}     {fmt(ftotal)}      "
              f"{fmt(ltotal)}          {fgroups}")

    print()
    print("  ~ = brazos pegados al torso en esa fila; el ancho de torso los incluye.")
    print("  FONDO incluye siempre el brazo (en vista lateral se solapa con el torso).")
    print()
    print("Comparar con: OpenSCAD en toreto_exterior_95cm/src/*.scad y los")
    print("parametros maestros de los add-ins en fusion_scripts/. Ver")
    print("docs/DECISIONES.md, 'Fuente maestra de cotas'.")


if __name__ == "__main__":
    main()
