"""Extrae los contornos exactos del robot desde los lienzos calibrados.

Para qué sirve: `measure_silhouette.py` da anchos y fondos por altura -- útil
para corregir parámetros, pero son cajas. Esta herramienta saca la **curva
real** de cada vista, en milímetros, para poder dibujarla como boceto en
Fusion y modelar contra ella en vez de contra un prisma aproximado.

LIMITACIÓN QUE HAY QUE TENER PRESENTE
=====================================
Un contorno 2D no define un sólido 3D. Una base cilíndrica de ⌀450 mm y una
caja de 450 × 450 mm tienen **exactamente la misma silueta** en las cuatro
vistas. Esta herramienta da los perfiles correctos; decidir si algo es
redondo, prismático o achaflanado sigue siendo criterio de diseño.

Por eso la salida son BOCETOS para construir encima (revolución, loft,
extrusión + intersección...), no un sólido terminado.

Además, la lámina es una ilustración de estilo, no una proyección
ortográfica rigurosa: tiene líneas interiores de detalle, sombreado y
rótulos que no son silueta. Aquí solo se toma el **contorno exterior** del
mayor grupo conectado, que es lo único fiable.

Salida: `reference/lienzos_95cm/perfiles_95cm.json`, con los puntos en mm
y el origen en el eje del robot a nivel de suelo (X/Y=0 en el eje, Z=0 en
el suelo, Z=950 en la coronilla). Lo consume el add-in
`Toreto_Perfiles_95cm`.
"""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

LIENZOS_DIR = Path(__file__).resolve().parents[1] / "reference" / "lienzos_95cm"
CALIBRATION_JSON = LIENZOS_DIR / "calibracion_95cm.json"
OUTPUT_JSON = LIENZOS_DIR / "perfiles_95cm.json"

BG_TOLERANCE = 12
EDGE_MARGIN_PX = 200      # descarta la regla cian (izq) y las líneas guía (der)
MIN_CONTOUR_AREA = 5000   # descarta rótulos y trazos sueltos
SIMPLIFY_EPSILON_MM = 0.6  # tolerancia de simplificación del contorno

# Qué vista se dibuja en qué plano de Fusion. La coordenada horizontal de
# cada lienzo es X en las vistas frontales y Y en las laterales.
VIEW_PLANES = {
    "frontal": "XZ",
    "posterior": "XZ",
    "lateral_derecho": "YZ",
    "lateral_izquierdo": "YZ",
}


def _mask(path: Path) -> tuple[np.ndarray, int]:
    """Máscara binaria del cuerpo del robot, sin regla ni líneas guía."""
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"No se pudo abrir el lienzo: {path}")
    bg = img[5, 5].astype(int)
    diff = np.abs(img.astype(int) - bg).max(axis=2)
    mask = (diff > BG_TOLERANCE).astype(np.uint8) * 255
    mask[:, :EDGE_MARGIN_PX] = 0
    mask[:, -EDGE_MARGIN_PX:] = 0
    return mask, img.shape[1]


def _largest_contour(mask: np.ndarray) -> np.ndarray:
    """Contorno exterior del mayor grupo conectado (el robot).

    RETR_EXTERNAL descarta los agujeros interiores: la pantalla del pecho o
    la ventana facial son detalle de dibujo, no silueta.
    """
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = [c for c in contours if cv2.contourArea(c) >= MIN_CONTOUR_AREA]
    if not contours:
        raise RuntimeError("No se encontró ningún contorno de robot en el lienzo.")
    return max(contours, key=cv2.contourArea)


def _axis_px(mask: np.ndarray, z0_px: int, mm_per_px: float) -> float:
    """Posición horizontal del EJE del robot, en píxeles.

    No vale usar el centro de la imagen: `prepare_fusion_canvases.py` centra
    cada vista sobre su propia silueta, y en los laterales el brazo
    extendido desplaza ese centro respecto al eje real. Medido: el lateral
    izquierdo salía 124 mm corrido respecto al derecho.

    La base sí es un buen testigo del eje -- es el mismo cilindro en las
    cuatro vistas y no tiene apéndices que la descentren. Se toma la franja
    Z=20..180 mm y se promedia el centro de su silueta fila a fila.
    """
    y_top = int(round(z0_px - 180 / mm_per_px))
    y_bottom = int(round(z0_px - 20 / mm_per_px))
    centers = []
    for y in range(max(0, y_top), min(mask.shape[0], y_bottom)):
        xs = np.flatnonzero(mask[y])
        if xs.size:
            centers.append((xs[0] + xs[-1]) / 2.0)
    if not centers:
        raise RuntimeError("No se pudo localizar la base para fijar el eje.")
    return float(np.median(centers))


def main() -> None:
    calibration = json.loads(CALIBRATION_JSON.read_text(encoding="utf-8"))
    mm_per_px = calibration["mm_per_pixel"]
    z0_px = calibration["robot_bottom_px"]
    views = calibration["views"]

    epsilon_px = SIMPLIFY_EPSILON_MM / mm_per_px
    out: dict[str, dict] = {}

    for name, filename in views.items():
        mask, width_px = _mask(LIENZOS_DIR / filename)
        contour = _largest_contour(mask)
        simplified = cv2.approxPolyDP(contour, epsilon_px, closed=True)

        axis_px = _axis_px(mask, z0_px, mm_per_px)
        drift_mm = (axis_px - width_px / 2.0) * mm_per_px
        points = [
            [
                round((float(x) - axis_px) * mm_per_px, 2),   # horizontal (X o Y)
                round((z0_px - float(y)) * mm_per_px, 2),     # vertical (Z)
            ]
            for (x, y) in simplified.reshape(-1, 2)
        ]
        zs = [p[1] for p in points]
        hs = [p[0] for p in points]

        out[name] = {
            "plane": VIEW_PLANES.get(name, "XZ"),
            "points_mm": points,
            "point_count": len(points),
            "z_range_mm": [round(min(zs), 1), round(max(zs), 1)],
            "horizontal_range_mm": [round(min(hs), 1), round(max(hs), 1)],
            "axis_drift_mm": round(drift_mm, 1),
        }
        print(
            f"OK {name:18} {len(points):4} puntos, "
            f"Z {min(zs):6.1f}..{max(zs):6.1f} mm, "
            f"horiz {min(hs):7.1f}..{max(hs):6.1f} mm, "
            f"eje corrido {drift_mm:+6.1f} mm respecto al centro de imagen"
        )

    OUTPUT_JSON.write_text(
        json.dumps(
            {
                "mm_per_pixel": mm_per_px,
                "simplify_epsilon_mm": SIMPLIFY_EPSILON_MM,
                "origin": "X/Y=0 en el eje del robot; Z=0 en el suelo",
                "note": (
                    "Contornos exteriores de la lamina calibrada. Un contorno 2D "
                    "no define un solido 3D: usar como boceto de referencia, no "
                    "como geometria final. Ver el docstring de "
                    "tools/extract_profiles.py."
                ),
                "views": out,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nEscrito {OUTPUT_JSON}")
    print("Lo consume el add-in Toreto_Perfiles_95cm para crear los bocetos.")


if __name__ == "__main__":
    main()
