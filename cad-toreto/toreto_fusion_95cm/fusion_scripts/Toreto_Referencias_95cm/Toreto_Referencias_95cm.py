"""Inserta cuatro lienzos ortogonales calibrados del Robot Toreto 95 cm."""

import os
import traceback

import adsk.core
import adsk.fusion


PROJECT_DIR = (
    r"C:\Users\tarif\Desktop\Robot-Toreto\cad-toreto"
    r"\toreto_fusion_95cm"
)
CANVAS_DIR = os.path.join(PROJECT_DIR, "reference", "lienzos_95cm")
MESH_PATH = os.path.join(
    PROJECT_DIR, "reference", "toreto_fusion_95cm_assembly.stl"
)

REFERENCE_COMPONENT = "00_REFERENCIAS"
LEGACY_CANVAS_NAME = "REF_VISUAL_APROBADA_95CM"
MESH_NAME = "REF_VOLUMENES_SCAD_95CM"

# Los cuatro PNG comparten exactamente el mismo encuadre y escala.
# La transformación sitúa el contacto de las ruedas en Z=0 y la parte más
# alta de la cabeza en Z=950 mm. La regla cian permite comprobarlo a mano.
IMAGE_WIDTH_PX = 2000.0
IMAGE_HEIGHT_PX = 2000.0
ROBOT_TOP_PX = 50.0
ROBOT_BOTTOM_PX = 1950.0
ROBOT_HEIGHT_CM = 95.0

CANVAS_SPECS = (
    (
        "PATRON_01_FRONTAL_95CM",
        "toreto_95cm_frontal.png",
        "XZ",
        False,
        True,
    ),
    (
        "PATRON_02_POSTERIOR_95CM",
        "toreto_95cm_posterior.png",
        "XZ",
        True,
        False,
    ),
    (
        "PATRON_03_LATERAL_IZQUIERDO_95CM",
        "toreto_95cm_lateral_izquierdo.png",
        "YZ",
        False,
        False,
    ),
    (
        "PATRON_04_LATERAL_DERECHO_95CM",
        "toreto_95cm_lateral_derecho.png",
        "YZ",
        False,
        False,
    ),
)


def _find_occurrence(root, component_name):
    for index in range(root.occurrences.count):
        occurrence = root.occurrences.item(index)
        if occurrence.component.name == component_name:
            return occurrence
    return None


def _find_canvas(component, name):
    for index in range(component.canvases.count):
        canvas = component.canvases.item(index)
        if canvas.name == name:
            return canvas
    return None


def _find_mesh(component, name):
    for index in range(component.meshBodies.count):
        body = component.meshBodies.item(index)
        if body.name == name:
            return body
    return None


def _canvas_transform(plane_code, mirror):
    """Calcula la transformación 2D del lienzo para el plano indicado.

    OJO: la convención de ejes nativos (U,V) de cada plano de origen de
    Fusion no es la misma para XZ que para YZ, y no se puede deducir por
    simetría de nombre -- hay que comprobarlo dentro de Fusion. Solo el
    caso XZ sin espejo (frontal) está verificado visualmente (ver
    docs/CUADERNO.md, 26 ago 2026): en xZConstructionPlane, U nativo
    corresponde a la Z del mundo y V nativo a la X del mundo.

    El caso YZ (los dos laterales) usa aquí una PRIMERA HIPÓTESIS sin
    verificar todavía: que el plano YZ no necesita el mismo intercambio
    (U nativo = Y, V nativo = Z, sin invertir). Si al ejecutar el add-in
    los laterales siguen sin encajar, ese es el primer sitio a corregir --
    probablemente haya que intercambiar u_axis/v_axis como se hizo para XZ.

    `mirror` invierte el ancho de la imagen (para vistas tomadas mirando en
    sentido contrario al frontal, como la posterior -- ver la izquierda y la
    derecha del robot invertidas al mirarlo de espaldas).
    """
    cm_per_pixel = ROBOT_HEIGHT_CM / (ROBOT_BOTTOM_PX - ROBOT_TOP_PX)
    image_width_cm = IMAGE_WIDTH_PX * cm_per_pixel
    image_height_cm = IMAGE_HEIGHT_PX * cm_per_pixel

    # Con una transformación explícita, Fusion sitúa el origen del lienzo en
    # su esquina inferior izquierda. El margen de imagen situado bajo las
    # ruedas debe quedar por debajo de Z=0.
    vertical_offset_cm = -(
        IMAGE_HEIGHT_PX - ROBOT_BOTTOM_PX
    ) * cm_per_pixel

    width_sign = -1.0 if mirror else 1.0
    half_width_signed = width_sign * image_width_cm / 2.0
    width_vector_signed = width_sign * image_width_cm

    # canvas_u_vector / canvas_v_vector son, en ese orden, el 2º y 3er
    # argumento de setWithCoordinateSystem -- cómo se mueve el punto del
    # plano cuando el lienzo avanza a lo largo de su propio ancho (U) o
    # alto (V) de imagen. El orden importa: invertirlo NO es lo mismo que
    # intercambiar U y V dentro de cada vector.
    if plane_code == "XZ":
        # Verificado en Fusion para frontal (mirror=False): avanzar en
        # ancho de imagen mueve la coordenada V del plano; avanzar en alto
        # de imagen mueve la coordenada U del plano.
        origin = adsk.core.Point2D.create(vertical_offset_cm, -half_width_signed)
        canvas_u_vector = adsk.core.Vector2D.create(0.0, width_vector_signed)
        canvas_v_vector = adsk.core.Vector2D.create(image_height_cm, 0.0)
    elif plane_code == "YZ":
        # SIN VERIFICAR (ver docstring) -- primera hipótesis: sin el
        # intercambio que sí hizo falta en XZ (ancho de imagen mueve U,
        # alto de imagen mueve V).
        origin = adsk.core.Point2D.create(-half_width_signed, vertical_offset_cm)
        canvas_u_vector = adsk.core.Vector2D.create(width_vector_signed, 0.0)
        canvas_v_vector = adsk.core.Vector2D.create(0.0, image_height_cm)
    else:
        raise ValueError("Plano de lienzo no reconocido: " + plane_code)

    matrix = adsk.core.Matrix2D.create()
    if not matrix.setWithCoordinateSystem(origin, canvas_u_vector, canvas_v_vector):
        raise RuntimeError("No se pudo calcular la transformación del lienzo.")
    return matrix


def _plane_for(component, plane_code):
    if plane_code == "XZ":
        return component.xZConstructionPlane
    if plane_code == "YZ":
        return component.yZConstructionPlane
    raise ValueError("Plano de lienzo no reconocido: " + plane_code)


def _create_or_update_canvas(component, name, image_path, plane_code, mirror, visible):
    canvas = _find_canvas(component, name)
    if canvas:
        canvas.imageFilename = image_path
        canvas.transform = _canvas_transform(plane_code, mirror)
        canvas.opacity = 55
        canvas.isDisplayedThrough = True
        canvas.isSelectable = False
        canvas.isRenderable = False
        canvas.isLightBulbOn = visible
        return False

    canvas_input = component.canvases.createInput(
        image_path, _plane_for(component, plane_code)
    )
    if not canvas_input:
        raise RuntimeError("Fusion no pudo preparar el lienzo " + name + ".")
    canvas_input.transform = _canvas_transform(plane_code, mirror)
    canvas_input.opacity = 55
    canvas_input.isDisplayedThrough = True
    canvas_input.isSelectable = False
    canvas_input.isRenderable = False

    canvas = component.canvases.add(canvas_input)
    if not canvas:
        raise RuntimeError("Fusion no pudo crear el lienzo " + name + ".")
    canvas.name = name
    canvas.isLightBulbOn = visible
    return True


def _prepare_canvases(component):
    legacy = _find_canvas(component, LEGACY_CANVAS_NAME)
    if legacy:
        legacy.isLightBulbOn = False

    created = 0
    updated = 0
    for name, filename, plane_code, mirror, visible in CANVAS_SPECS:
        image_path = os.path.join(CANVAS_DIR, filename)
        if not os.path.isfile(image_path):
            raise FileNotFoundError("Falta el lienzo:\n" + image_path)
        if _create_or_update_canvas(
            component, name, image_path, plane_code, mirror, visible
        ):
            created += 1
        else:
            updated += 1
    return created, updated


def _import_mesh(component):
    existing = _find_mesh(component, MESH_NAME)
    if existing:
        existing.isLightBulbOn = True
        existing.isSelectable = False
        return False

    base_feature = component.features.baseFeatures.add()
    if not base_feature:
        raise RuntimeError("No se pudo crear la función base para la malla.")
    base_feature.name = "BASE_REF_VOLUMENES_SCAD"

    base_feature.startEdit()
    try:
        bodies = component.meshBodies.add(
            MESH_PATH,
            adsk.fusion.MeshUnits.MillimeterMeshUnit,
            base_feature,
        )
    finally:
        base_feature.finishEdit()

    if not bodies or bodies.count == 0:
        raise RuntimeError("Fusion no pudo importar la malla STL de referencia.")

    body = bodies.item(0)
    body.name = MESH_NAME
    body.isLightBulbOn = True
    body.isSelectable = False
    return True


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

        root = design.rootComponent
        occurrence = _find_occurrence(root, REFERENCE_COMPONENT)
        if not occurrence:
            raise RuntimeError(
                "Falta el componente 00_REFERENCIAS. Ejecuta primero "
                "Toreto_Componentes_95cm."
            )

        component = occurrence.component
        canvases_created, canvases_updated = _prepare_canvases(component)

        mesh_status = "pendiente (el STL todavía no está disponible)"
        if os.path.isfile(MESH_PATH):
            mesh_created = _import_mesh(component)
            mesh_status = "importada" if mesh_created else "ya existente"

        root.attributes.add("RobotToreto", "referencias_95cm", "2.2.0")
        app.activeViewport.fit()

        ui.messageBox(
            "Cuatro patrones ortogonales preparados.\n\n"
            f"Lienzos creados: {canvases_created}\n"
            f"Lienzos actualizados: {canvases_updated}\n"
            f"Malla dimensional: {mesh_status}\n\n"
            "El FRONTAL está verificado: encaja en altura (Z=0-950mm) y en "
            "ancho (X).\n"
            "POSTERIOR y los dos LATERALES son la v2.2.0, sin comprobar "
            "todavía -- revisa cada uno contra la malla o el modelo antes "
            "de fiarte de ellos. Si alguno no encaja, dilo con detalle "
            "(¿gira 90°? ¿aparece en espejo? ¿tamaño distinto?) para poder "
            "corregir la fórmula concreta.\n\n"
            "Se muestra el FRONTAL por defecto. En 00_REFERENCIAS > "
            "Lienzos, apaga uno y enciende el patrón que quieras seguir.\n"
            "Los lienzos son guías; no son piezas imprimibles.",
            "Robot Toreto 95 cm",
        )

    except Exception:
        ui.messageBox(
            "No se pudieron preparar las referencias:\n\n"
            + traceback.format_exc(),
            "Robot Toreto 95 cm - Error",
        )


def stop(context):
    pass
