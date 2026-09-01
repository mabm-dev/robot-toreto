"""Crea bocetos con el contorno EXACTO del robot tomado de los lienzos.

Los add-ins de módulo (Base, Tronco, Pecho...) construyen volúmenes
paramétricos aproximados: prismas redondeados y lofts. Este trae la silueta
real de la lámina, al milímetro, como boceto sobre el que modelar.

Cómo se usa: ejecutar, y luego construir sobre los bocetos con las
herramientas de Fusion (revolución para la base, loft entre secciones,
extrusión + intersección para volúmenes prismáticos...).

IMPORTANTE -- un contorno 2D no define un sólido 3D
===================================================
Una base cilíndrica de ⌀450 mm y una caja de 450 × 450 mm tienen la MISMA
silueta en las cuatro vistas. Estos bocetos fijan el contorno; decidir si
algo es redondo, prismático o achaflanado sigue siendo criterio de diseño.
No son geometría final.

Los puntos los genera `tools/extract_profiles.py` y viven en
`reference/lienzos_95cm/perfiles_95cm.json`. Si se regeneran los lienzos,
hay que volver a lanzar esa herramienta antes que este add-in.
"""

import json
import os
import traceback

import adsk.core
import adsk.fusion


PROJECT_DIR = (
    r"C:\Users\tarif\Desktop\Robot-Toreto\cad-toreto"
    r"\toreto_fusion_95cm"
)
PROFILES_JSON = os.path.join(
    PROJECT_DIR, "reference", "lienzos_95cm", "perfiles_95cm.json"
)

REFERENCE_COMPONENT = "00_REFERENCIAS"
SKETCH_PREFIX = "PERFIL_"
MM_TO_CM = 0.1


def _find_occurrence(root, component_name):
    for index in range(root.occurrences.count):
        occurrence = root.occurrences.item(index)
        if occurrence.component.name == component_name:
            return occurrence
    return None


def _find_sketch(component, name):
    for index in range(component.sketches.count):
        sketch = component.sketches.item(index)
        if sketch.name == name:
            return sketch
    return None


def _plane_for(component, plane_code):
    if plane_code == "XZ":
        return component.xZConstructionPlane
    if plane_code == "YZ":
        return component.yZConstructionPlane
    raise ValueError("Plano no reconocido: " + plane_code)


def _world_point(plane_code, horizontal_mm, vertical_mm):
    """Punto en coordenadas de MODELO (cm), no del boceto.

    Se construye en el espacio del modelo a propósito y luego se convierte
    con `modelToSketchSpace`. Cada plano de origen de Fusion tiene su propia
    convención de ejes U/V, y darla por supuesta es justo el error que
    descolocó los lienzos laterales en su día -- dejar que Fusion haga la
    conversión evita repetirlo.
    """
    h = horizontal_mm * MM_TO_CM
    v = vertical_mm * MM_TO_CM
    if plane_code == "XZ":
        return adsk.core.Point3D.create(h, 0.0, v)
    return adsk.core.Point3D.create(0.0, h, v)


def _draw_profile(component, name, plane_code, points_mm):
    existing = _find_sketch(component, name)
    if existing:
        existing.deleteMe()

    sketch = component.sketches.add(_plane_for(component, plane_code))
    sketch.name = name
    sketch.isComputeDeferred = True          # sin esto, cientos de líneas van lentísimas
    try:
        lines = sketch.sketchCurves.sketchLines
        sketch_points = [
            sketch.modelToSketchSpace(_world_point(plane_code, h, v))
            for h, v in points_mm
        ]
        for index in range(len(sketch_points)):
            start = sketch_points[index]
            end = sketch_points[(index + 1) % len(sketch_points)]   # cierra el contorno
            if start.distanceTo(end) > 1e-6:
                lines.addByTwoPoints(start, end)
    finally:
        sketch.isComputeDeferred = False

    sketch.isVisible = False
    return sketch


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface

    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox(
                "Abre 00_Toreto_Ensamblaje_95cm antes de ejecutar.",
                "Robot Toreto 95 cm",
            )
            return

        if not os.path.isfile(PROFILES_JSON):
            raise FileNotFoundError(
                "Faltan los perfiles:\n" + PROFILES_JSON +
                "\n\nEjecuta antes tools/extract_profiles.py."
            )

        with open(PROFILES_JSON, "r", encoding="utf-8") as handle:
            data = json.load(handle)

        root = design.rootComponent
        occurrence = _find_occurrence(root, REFERENCE_COMPONENT)
        if not occurrence:
            raise RuntimeError(
                "Falta el componente 00_REFERENCIAS. Ejecuta primero "
                "Toreto_Componentes_95cm."
            )
        component = occurrence.component

        lines = []
        for view_name, view in data["views"].items():
            sketch_name = SKETCH_PREFIX + view_name.upper()
            sketch = _draw_profile(
                component, sketch_name, view["plane"], view["points_mm"]
            )
            drift = view.get("axis_error_mm", view.get("axis_drift_mm", 0.0))
            mirror = "; espejo horizontal" if view.get("mirror_for_fusion", False) else ""
            warn = "  <-- REVISAR" if abs(drift) > 20 else ""
            lines.append(
                f"{sketch_name}: {view['point_count']} puntos, plano "
                f"{view['plane']}, error de eje {drift:+.1f} mm{mirror}{warn}"
            )

        app.activeViewport.fit()
        ui.messageBox(
            "Perfiles exactos creados desde los lienzos.\n\n"
            + "\n".join(lines)
            + "\n\nSe crean OCULTOS para no estorbar: enciéndelos uno a uno "
            "en el árbol, dentro de 00_REFERENCIAS > Bocetos.\n\n"
            "OJO: un contorno 2D no define un solido 3D. Una base cilindrica "
            "de 450 mm y una caja de 450x450 tienen la misma silueta en las "
            "cuatro vistas. Son guias para modelar encima, no geometria "
            "final.\n\n"
            "'Error de eje' es la diferencia entre la base detectada y el "
            "anclaje calibrado del lienzo. Por encima de 20 mm conviene "
            "comprobar que el PNG y su calibracion corresponden a la misma "
            "lamina.",
            "Robot Toreto 95 cm",
        )

    except Exception:
        ui.messageBox(
            "No se pudieron crear los perfiles:\n\n" + traceback.format_exc(),
            "Robot Toreto 95 cm - Error",
        )


def stop(context):
    pass
