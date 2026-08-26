"""Recorta las cuatro vistas Toreto y genera lienzos calibrados a 950 mm.

Reescrito el 26 de agosto de 2026 para corregir el fallo original: la
version anterior escalaba la ALTURA DE LA CAJA DE RECORTE manual, no la
altura real de la silueta dentro de ella. Como las cuatro cajas no tenian
el mismo margen sobrante, salian CUATRO ESCALAS DISTINTAS (0.518 frontal/
lateral derecho, 0.526 posterior/lateral izquierdo) en vez de una sola.

Esta version:
  1. Parte de la copia local de la lamina (no de %TEMP%, que es efimero).
  2. Usa cajas de silueta auditadas sobre las cuatro vistas, conservando
     manos y ruedas completas y excluyendo los margenes desiguales.
  3. Escala cada vista de forma INDEPENDIENTE a 1900 intervalos verticales
     (950 mm a 0.5 mm/px), con 1901 filas para incluir ambos extremos.
  4. Valida el resultado: si la silueta de salida no cae exactamente entre
     Y=50 y Y=1950 (con tolerancia de redondeo de 1 px), el script falla en
     vez de escribir un lienzo mal calibrado.
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Copia local verificada por hash (ver docs/CUADERNO.md, 26 ago 2026) -- ya
# no depende de %TEMP%, que Windows puede vaciar en cualquier momento.
SOURCE = Path(__file__).resolve().parents[1] / "reference" / "lamina_maestra_4vistas.jpg"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "reference" / "lienzos_95cm"

SOURCE_SIZE = (2400, 1792)

# Los cuatro cuadrantes son mitades exactas de la lamina -- limite
# estructural fiable, no una caja ajustada a mano pieza por pieza.
QUADRANTS = {
    "frontal": (0, 0, 1200, 896),
    "lateral_derecho": (1200, 0, 2400, 896),
    "posterior": (0, 896, 1200, 1792),
    "lateral_izquierdo": (1200, 896, 2400, 1792),
}

# Cajas finales auditadas sobre la lamina fuente. Derecha e inferior son
# exclusivas (convencion PIL). A diferencia de los cuadrantes, cada caja
# empieza en la coronilla y termina en la ultima fila del suelo. Tambien
# conserva las manos completas; la deteccion automatica anterior perdia la
# mano adelantada del lateral izquierdo al quedar fuera de su nucleo.
AUDITED_SILHOUETTE_BOXES = {
    "frontal": (330, 89, 870, 863),
    "lateral_derecho": (1580, 89, 2020, 863),
    "posterior": (340, 946, 870, 1727),
    "lateral_izquierdo": (1360, 946, 2010, 1727),
}

# Eje longitudinal del robot en la lamina original. No se usa el centro de
# la caja de silueta porque una mano adelantada desplaza mucho esa caja en
# los laterales. Fusion debe superponer este eje con el origen del montaje.
SOURCE_ROBOT_AXIS_X = {
    "frontal": 600,
    "posterior": 600,
    "lateral_derecho": 1800,
    "lateral_izquierdo": 1800,
}

# El rotulo SIDE invade el margen superior del recorte lateral izquierdo.
# Se elimina por filas copiando el fondo contiguo; no intersecta el robot.
ERASE_AREAS = {
    "lateral_izquierdo": ((1360, 946, 1580, 990),),
}

CANVAS_WIDTH_PX = 2000
CANVAS_HEIGHT_PX = 2000
ROBOT_TOP_PX = 50
ROBOT_BOTTOM_PX = 1950
ROBOT_HEIGHT_PX = ROBOT_BOTTOM_PX - ROBOT_TOP_PX  # 1900 intervalos
ROBOT_RASTER_HEIGHT_PX = ROBOT_HEIGHT_PX + 1  # incluye ambos extremos
ROBOT_HEIGHT_MM = 950
MM_PER_PX = ROBOT_HEIGHT_MM / ROBOT_HEIGHT_PX  # 0.5 exacto, una vez corregido

BG_TOLERANCE = 20
INSET = 10          # se aleja de las lineas divisorias entre cuadrantes
TITLE_SKIP = 5        # margen minimo, casi nulo: el propio MIN_RUN ya basta
                      # para descartar el rotulo (ancho maximo medido 27px,
                      # ver docs/CUADERNO.md). Un valor alto aqui llego a
                      # cortar la cabeza real en posterior/lateral_izquierdo,
                      # cuya silueta empieza mucho antes que en las otras dos
                      # vistas -- ese fue el bug de esta misma reescritura.
MIN_RUN = 30          # ancho minimo de un tramo para contar como robot, no
                      # como una linea de leyenda o una letra suelta (el
                      # rotulo de texto no supera los 27px en esta lamina)
PAD_FOR_EXTREMITIES = 150  # margen extra al recortar, para no cortar dedos
                             # u otros extremos finos que el filtro MIN_RUN
                             # descarta al localizar el nucleo de la silueta

# El rotulo (FRONT / RIGHT SIDE / BACK / LEFT SIDE) siempre vive en la
# esquina superior izquierda de su cuadrante -- es la maquetacion fija de
# esta lamina concreta, no un parametro que dependa del contenido. Excluirlo
# por posicion es mas fiable que intentar distinguirlo del robot por ancho
# de trazo: un margen de busqueda amplio (PAD_FOR_EXTREMITIES, para no
# perder dedos extendidos) puede alcanzar el rotulo igualmente si no se
# excluye la zona explicitamente -- eso paso en la primera version de esta
# reescritura, con "FRONT" colandose por la izquierda.
TITLE_BOX_W = 340
TITLE_BOX_H = 110


def _is_background(pixel, bg):
    return all(abs(pixel[i] - bg[i]) < BG_TOLERANCE for i in range(3))


def _in_title_zone(x, y, box):
    left, top, _, _ = box
    return x < left + TITLE_BOX_W and y < top + TITLE_BOX_H


def _detect_core_bbox(img: Image.Image, box: tuple[int, int, int, int], bg) -> tuple[int, int, int, int]:
    """Pasada robusta: solo cuenta tramos anchos (MIN_RUN), ignora el
    rotulo de texto (excluido por posicion, ver _in_title_zone) y las
    lineas divisorias (excluidas por INSET). Sirve para localizar el robot
    con seguridad, no para el recorte final -- un dedo fino no pasa este
    filtro de ancho."""
    left, top, right, bottom = box
    l2, r2 = left + INSET, right - INSET
    t2, b2 = top + TITLE_SKIP, bottom - INSET
    px = img.load()
    minx, maxx, miny, maxy = 10**9, -1, 10**9, -1
    for y in range(t2, b2):
        run_start = None
        best = (0, 0, 0)
        for x in range(l2, r2 + 1):
            is_bg = x >= r2 or _in_title_zone(x, y, box) or _is_background(px[x, y], bg)
            if not is_bg:
                if run_start is None:
                    run_start = x
            else:
                if run_start is not None:
                    length = x - run_start
                    if length > best[0]:
                        best = (length, run_start, x)
                    run_start = None
        if best[0] >= MIN_RUN:
            _, x0, x1 = best
            minx, maxx = min(minx, x0), max(maxx, x1)
            miny, maxy = min(miny, y), max(maxy, y)
    if maxx < 0:
        raise RuntimeError(f"No se encontro silueta en el cuadrante {box}")
    return minx, maxx, miny, maxy


def _detect_full_bbox(img: Image.Image, box: tuple[int, int, int, int], core, bg) -> tuple[int, int, int, int]:
    """Segunda pasada: dentro de una region acotada alrededor del nucleo ya
    localizado, cuenta CUALQUIER pixel no-fondo (sin filtro de ancho), para
    no perder dedos, antenas u otros extremos finos.

    El margen es distinto por eje a proposito: una mano extendida se sale
    mucho en horizontal (PAD_FOR_EXTREMITIES), pero casi nada en vertical
    mas alla de lo que ya capturo el nucleo -- darle el mismo margen grande
    en Y volvia a alcanzar el rotulo de texto cuando la cabeza empezaba
    cerca del techo del cuadrante (el bug que motivo este comentario)."""
    left, top, right, bottom = box
    cminx, cmaxx, cminy, cmaxy = core
    l2 = max(left + INSET, cminx - PAD_FOR_EXTREMITIES)
    r2 = min(right - INSET, cmaxx + PAD_FOR_EXTREMITIES)
    t2 = max(top + TITLE_SKIP, cminy - PAD_FOR_EXTREMITIES)
    b2 = min(bottom - INSET, cmaxy + PAD_FOR_EXTREMITIES)
    px = img.load()
    minx, maxx, miny, maxy = 10**9, -1, 10**9, -1
    for y in range(t2, b2 + 1):
        for x in range(l2, r2 + 1):
            if _in_title_zone(x, y, box):
                continue
            if not _is_background(px[x, y], bg):
                minx, maxx = min(minx, x), max(maxx, x)
                miny, maxy = min(miny, y), max(maxy, y)
    return minx, maxx, miny, maxy


def _font(size: int):
    for candidate in (
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
    ):
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def _make_canvas(source: Image.Image, name: str, bg) -> tuple[Image.Image, dict]:
    left, top, right, bottom = AUDITED_SILHOUETTE_BOXES[name]
    silhouette_h = bottom - top
    silhouette_w = right - left
    crop = source.crop((left, top, right, bottom))

    crop_draw = ImageDraw.Draw(crop)
    for erase_left, erase_top, erase_right, erase_bottom in ERASE_AREAS.get(
        name, ()
    ):
        x0 = erase_left - left
        x1 = erase_right - left
        for source_y in range(erase_top, erase_bottom):
            y = source_y - top
            sample_x = min(crop.width - 1, x1 + 5)
            crop_draw.line(
                (x0, y, x1, y), fill=crop.getpixel((sample_x, y))
            )

    scale = ROBOT_RASTER_HEIGHT_PX / silhouette_h
    resized_w = round(silhouette_w * scale)
    crop = crop.resize(
        (resized_w, ROBOT_RASTER_HEIGHT_PX), Image.Resampling.LANCZOS
    )

    if resized_w > CANVAS_WIDTH_PX - 40:
        raise RuntimeError(
            f"La vista no cabe en el lienzo ({resized_w}px > {CANVAS_WIDTH_PX - 40}px "
            "disponibles) -- ampliar CANVAS_WIDTH_PX."
        )

    canvas = Image.new("RGB", (CANVAS_WIDTH_PX, CANVAS_HEIGHT_PX), bg)
    x = (CANVAS_WIDTH_PX - resized_w) // 2
    canvas.paste(crop, (x, ROBOT_TOP_PX))

    draw = ImageDraw.Draw(canvas)
    cyan = (0, 174, 235)
    guide_x = 28
    draw.line((guide_x, ROBOT_TOP_PX, guide_x, ROBOT_BOTTOM_PX), fill=cyan, width=4)
    draw.line((guide_x - 14, ROBOT_TOP_PX, guide_x + 14, ROBOT_TOP_PX), fill=cyan, width=4)
    draw.line((guide_x - 14, ROBOT_BOTTOM_PX, guide_x + 14, ROBOT_BOTTOM_PX), fill=cyan, width=4)
    draw.text((50, ROBOT_TOP_PX + 8), "950 mm", font=_font(28), fill=cyan)

    meta = {
        "source_bbox_px": [left, top, right, bottom],
        "source_silhouette_px": [silhouette_w, silhouette_h],
        "scale_applied": round(scale, 6),
        "canvas_offset_x": x,
        "fusion_anchor_x_px": round(
            x + (SOURCE_ROBOT_AXIS_X[name] - left) * scale, 2
        ),
        "content_box_px": [
            x,
            ROBOT_TOP_PX,
            x + resized_w - 1,
            ROBOT_BOTTOM_PX,
        ],
    }
    return canvas, meta


def _validate(canvas: Image.Image, bg, name: str) -> None:
    """Falla en vez de escribir un lienzo mal calibrado: vuelve a medir la
    silueta ya pegada en el lienzo final y exige que quede exactamente
    entre Y=50 y Y=1950 (tolerancia 1 px por redondeo de escala)."""
    px = canvas.load()
    ys = [
        y
        for y in range(0, CANVAS_HEIGHT_PX)
        for x in (CANVAS_WIDTH_PX // 2,)  # columna central, ya centrado al pegar
        if not _is_background(px[x, y], bg)
    ]
    # La columna central puede no tocar la silueta en according de brazo;
    # usar una franja ancha en vez de una sola columna.
    ys = [
        y
        for y in range(0, CANVAS_HEIGHT_PX)
        if any(
            not _is_background(px[x, y], bg)
            for x in range(CANVAS_WIDTH_PX // 2 - 200, CANVAS_WIDTH_PX // 2 + 200)
        )
    ]
    if not ys:
        raise RuntimeError(f"[{name}] Validacion fallida: no se encuentra silueta en el lienzo final.")
    top, bottom = min(ys), max(ys)

    # Defensa especifica contra el bug que motivo esta reescritura: pegar el
    # recorte siempre en la fila 50 hace que el check de mas abajo (top==50)
    # se cumpla aunque el propio recorte ya viniera con la coronilla
    # cortada -- por si sola es una tautologia, no detecta nada. Una cabeza
    # redondeada real empieza estrecha (la punta de la coronilla) y se
    # ensancha hacia abajo; si la fila superior ya es ancha, es que se
    # recorto la parte de arriba en origen, no al pegar en el lienzo.
    # Excluye la franja de la regla cian de calibracion (x~14..190, linea +
    # texto "950 mm") -- si no, cualquier fila entre Y=50 y Y=1950 mide
    # "ancho" hasta la regla aunque el robot en si sea estrecho ahi. Ese fue
    # el segundo falso positivo de esta misma comprobacion.
    RULER_ZONE_RIGHT = 200

    def _row_width(y):
        xs = [
            x
            for x in range(RULER_ZONE_RIGHT, CANVAS_WIDTH_PX)
            if not _is_background(px[x, y], bg)
        ]
        return (max(xs) - min(xs)) if xs else 0

    w_top = _row_width(top)
    w_below = _row_width(min(top + 20, CANVAS_HEIGHT_PX - 1))
    if w_top > 120 and w_top > 0.6 * w_below:
        raise RuntimeError(
            f"[{name}] Validacion fallida: la fila superior (Y={top}) ya mide "
            f"{w_top}px de ancho (20 filas mas abajo: {w_below}px) -- no parece "
            "la punta de una coronilla redondeada, sino un corte a media cabeza "
            "en el recorte de origen."
        )

    # Tolerancia de 3px: ruido de antialiasing del redimensionado Lanczos
    # (suaviza el borde hacia el fondo, no un error de escala). El fallo
    # original que motivo esta reescritura era de ~70px equivalentes -- muy
    # por encima de este margen, así que sigue detectandose sin problema.
    TOLERANCE = 3
    if abs(top - ROBOT_TOP_PX) > TOLERANCE or abs(bottom - ROBOT_BOTTOM_PX) > TOLERANCE:
        raise RuntimeError(
            f"[{name}] Validacion fallida: silueta en Y=[{top},{bottom}], "
            f"se esperaba [{ROBOT_TOP_PX},{ROBOT_BOTTOM_PX}] (+-{TOLERANCE}px). "
            "No se escribe el lienzo -- revisar deteccion de fondo/silueta."
        )


def main() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(
            f"No se encuentra la lamina maestra: {SOURCE}\n"
            "Debe ser la copia local verificada, no el archivo de %TEMP%."
        )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    source = Image.open(SOURCE).convert("RGB")
    if source.size != SOURCE_SIZE:
        raise ValueError(f"Tamano inesperado: {source.size}; se esperaba {SOURCE_SIZE}")

    bg = source.getpixel((5, 5))

    outputs = {}
    views_meta = {}
    for name in QUADRANTS:
        canvas, meta = _make_canvas(source, name, bg)
        _validate(canvas, bg, name)
        path = OUTPUT_DIR / f"toreto_95cm_{name}.png"
        canvas.save(path, format="PNG", optimize=True)
        outputs[name] = path.name
        views_meta[name] = meta
        print(f"OK {name}: silueta origen {meta['source_silhouette_px']} px, "
              f"escala aplicada {meta['scale_applied']:.4f} -> validado Z=0..950mm")

    metadata = {
        "source": str(SOURCE.relative_to(Path(__file__).resolve().parents[1])),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "canvas_px": [CANVAS_WIDTH_PX, CANVAS_HEIGHT_PX],
        "robot_top_px": ROBOT_TOP_PX,
        "robot_bottom_px": ROBOT_BOTTOM_PX,
        "robot_height_px": ROBOT_HEIGHT_PX,
        "robot_raster_height_px": ROBOT_RASTER_HEIGHT_PX,
        "robot_height_mm": ROBOT_HEIGHT_MM,
        "mm_per_pixel": MM_PER_PX,
        "fusion_calibration": "Seleccionar los dos extremos cian e introducir 950 mm",
        "views": outputs,
        "per_view_detection": views_meta,
        "note": (
            "Cada vista se calibro de forma independiente con su caja de "
            "silueta auditada (no contra el cuadrante con margenes). Ver "
            "docs/CUADERNO.md, 26 ago 2026, para el porque."
        ),
    }
    (OUTPUT_DIR / "calibracion_95cm.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("\nTodas las vistas validadas y escritas.")


if __name__ == "__main__":
    main()
