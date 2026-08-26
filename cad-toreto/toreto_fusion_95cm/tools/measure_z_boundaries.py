"""Genera recortes con regla de píxeles sobre el lienzo frontal calibrado,
para medir a ojo (pero contra una escala exacta) dónde caen los cortes
verticales entre módulos (base/tronco/cintura/pecho/cuello/cabeza).

Por qué existe: `prepare_fusion_canvases.py` calibra el lienzo (0,5 mm/px,
Z=0 en Y=1950, Z=950 en Y=50) pero no dice DÓNDE dentro de esos 950 mm
empieza cada módulo -- eso es el "siguiente paso exacto" que fija
`docs/ROADMAP.md` (milestone v0.3) tras cerrar la calibración el 26 ago 2026.

Este script NO detecta los cortes automáticamente. Al menos dos costuras
(cintura->tronco y pecho->cintura) son curvas de estilo, no líneas rectas --
decidir dónde "corta" una curva es una decisión de diseño, no una medida
objetiva. Lo que hace el script es producir la regla milimetrada superpuesta
para que esa decisión se tome mirando la imagen real a escala conocida, no a
ojo sobre una captura sin referencia.

Salida: recortes PNG en reference/lienzos_95cm/_measure/ -- 3 tiras de
cuerpo completo (visión general) + 4 zooms sobre las zonas de costura
(cabeza/cuello/pecho, pecho/cintura/tronco, la transición curva
cintura->tronco, y tronco/base). Ver docs/CUADERNO.md, 26 ago 2026, para la
lectura resultante de estas reglas y por qué la tabla no se fija todavía
(depende de fase 2 -- ver docs/DECISIONES.md).
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

LIENZOS_DIR = Path(__file__).resolve().parents[1] / "reference" / "lienzos_95cm"
SOURCE = LIENZOS_DIR / "toreto_95cm_frontal.png"
CALIBRATION_JSON = LIENZOS_DIR / "calibracion_95cm.json"
OUTPUT_DIR = LIENZOS_DIR / "_measure"

# Zonas de costura a inspeccionar de cerca: nombre -> (y0, y1, x0, x1, escala).
# Los rangos Y cubren cada transición de módulo con margen a ambos lados;
# los rangos X excluyen la regla cian de la izquierda y las líneas de guía
# de la derecha (ver INSET/RULER_ZONE_RIGHT en prepare_fusion_canvases.py).
ZOOM_REGIONS: dict[str, tuple[int, int, int, int, float]] = {
    "zoom_head_neck_chest": (320, 540, 550, 1450, 1.5),
    "zoom_chest_waist_trunk": (800, 1120, 550, 1450, 1.5),
    "zoom_waist_trunk_transition": (1050, 1420, 600, 1400, 1.4),
    "zoom_trunk_base": (1400, 1700, 550, 1450, 1.5),
}

# Tiras de cuerpo completo para orientarse antes de entrar en cada zoom.
FULL_BODY_STRIPS = 3
FULL_BODY_CROP = (550, 40, 1500, 1960)


def _font(size: int):
    for candidate in (
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ):
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def _draw_ruler(
    img: Image.Image,
    y0: int,
    y_bottom_px: int,
    mm_per_px: float,
    display_scale: float = 1.0,
    minor_step: int = 5,
    major_step: int = 25,
) -> Image.Image:
    """Dibuja marcas cada `minor_step` px y una línea+etiqueta "yNNN ZNNN"
    cada `major_step` px. Z se calcula desde `y_bottom_px` (Z=0), no desde
    el origen del recorte -- así la etiqueta es la cota real del robot,
    no una coordenada local del PNG."""
    draw = ImageDraw.Draw(img)
    font = _font(16)
    w, h = img.size
    if display_scale <= 0:
        raise ValueError("display_scale debe ser mayor que cero")
    original_height = h / display_scale
    first = y0 - (y0 % minor_step)
    for y_orig in range(first, int(y0 + original_height) + 1):
        y_local = round((y_orig - y0) * display_scale)
        if y_local < 0 or y_local >= h:
            continue
        major = y_orig % major_step == 0
        color = (255, 0, 0) if major else (255, 150, 0)
        length = 50 if major else 20
        draw.line([(0, y_local), (length, y_local)], fill=color, width=2 if major else 1)
        draw.line([(w - length, y_local), (w, y_local)], fill=color, width=2 if major else 1)
        if major:
            mm = round((y_bottom_px - y_orig) * mm_per_px)
            draw.text((length + 4, y_local - 9), f"y{y_orig} Z{mm}", fill=(255, 0, 0), font=font)
            draw.line([(0, y_local), (w, y_local)], fill=(255, 0, 0), width=1)
    return img


def main() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(
            f"No se encuentra el lienzo frontal: {SOURCE}\n"
            "Ejecutar antes prepare_fusion_canvases.py."
        )
    calibration = json.loads(CALIBRATION_JSON.read_text(encoding="utf-8"))
    mm_per_px = calibration["mm_per_pixel"]
    y_bottom_px = calibration["robot_bottom_px"]

    img = Image.open(SOURCE).convert("RGB")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Tiras de cuerpo completo.
    crop = img.crop(FULL_BODY_CROP)
    cw, ch = crop.size
    strip_h = ch // FULL_BODY_STRIPS
    for i in range(FULL_BODY_STRIPS):
        top = i * strip_h
        bottom = ch if i == FULL_BODY_STRIPS - 1 else (i + 1) * strip_h
        strip = crop.crop((0, top, cw, bottom)).copy()
        strip = _draw_ruler(strip, FULL_BODY_CROP[1] + top, y_bottom_px, mm_per_px)
        out = OUTPUT_DIR / f"strip_{i}.png"
        strip.save(out)
        print(f"OK {out.name} (Y={FULL_BODY_CROP[1] + top}..{FULL_BODY_CROP[1] + bottom})")

    # Zooms de costura.
    for name, (y0, y1, x0, x1, scale) in ZOOM_REGIONS.items():
        region = img.crop((x0, y0, x1, y1))
        rw, rh = region.size
        big = region.resize((int(rw * scale), int(rh * scale)), Image.Resampling.LANCZOS)
        big = _draw_ruler(
            big.copy(), y0, y_bottom_px, mm_per_px, display_scale=scale
        )
        out = OUTPUT_DIR / f"{name}.png"
        big.save(out)
        print(f"OK {out.name} (Y={y0}..{y1}, Z={round((y_bottom_px - y1) * mm_per_px)}..{round((y_bottom_px - y0) * mm_per_px)} mm)")

    print(
        "\nRecortes escritos en", OUTPUT_DIR,
        "-- la lectura de cada costura y por qué la tabla de cotas no se "
        "fija todavía está en docs/CUADERNO.md (26 ago 2026)."
    )


if __name__ == "__main__":
    main()
