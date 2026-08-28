"""Crea la estructura paramétrica del ensamblaje Robot Toreto 95 cm."""

import adsk.core
import adsk.fusion
import traceback


VERSION = "1.2.0"
COMPONENT_NAMES = [
    "00_REFERENCIAS",
    "01_BASE",
    "02_TRONCO",
    "03_CINTURA",
    "04_PECHO_HOMBROS",
    "05_CUELLO",
    "06_CABEZA",
    "07_BRAZO_IZQUIERDO",
    "08_BRAZO_DERECHO",
]


PLANE_DEFINITIONS = [
    ("Z_200_BASE_SUPERIOR", "alto_base"),
    ("Z_390_TRONCO_SUPERIOR", "alto_base+alto_tronco"),
    ("Z_540_CINTURA_SUPERIOR", "alto_base+alto_tronco+alto_cintura"),
    (
        "Z_730_PECHO_SUPERIOR",
        "alto_base+alto_tronco+alto_cintura+alto_pecho",
    ),
    (
        "Z_790_CUELLO_SUPERIOR",
        "alto_base+alto_tronco+alto_cintura+alto_pecho+alto_cuello",
    ),
    ("Z_950_ALTURA_TOTAL", "altura_total"),
]


def _parameter(user_parameters, name):
    parameter = user_parameters.itemByName(name)
    if not parameter:
        raise RuntimeError(f"Falta el parámetro de usuario: {name}")
    return parameter


def _find_occurrence(root, name):
    for index in range(root.occurrences.count):
        occurrence = root.occurrences.item(index)
        if occurrence.component.name == name or occurrence.name == name:
            return occurrence
    return None


def _reset_empty_occurrence_transforms(occurrences, design):
    """Deja en identidad únicamente componentes nuevos o todavía vacíos.

    Una ocurrencia que ya contiene cuerpos puede incluir una corrección de
    montaje legítima. Reiniciarla desde este organizador era la causa de que
    piezas ya montadas reapareciesen en Z=0 al volver a ejecutar Componentes.
    """
    identity = adsk.core.Matrix3D.create()
    for occurrence in occurrences.values():
        if occurrence.component.bRepBodies.count:
            continue
        try:
            occurrence.isGroundToParent = False
        except Exception:
            pass
        try:
            occurrence.transform2 = identity.copy()
        except Exception:
            occurrence.transform = identity.copy()
    try:
        if design.snapshots.hasPendingTransforms:
            design.snapshots.add()
    except Exception:
        pass


def _create_or_update_component(root, name):
    occurrence = _find_occurrence(root, name)
    created = occurrence is None
    if created:
        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        if not occurrence:
            raise RuntimeError(f"Fusion no pudo crear el componente: {name}")

    occurrence.component.name = name
    return created


def _find_plane(planes, name):
    for index in range(planes.count):
        plane = planes.item(index)
        if plane.name == name:
            return plane
    return None


def _create_or_update_plane(root, name, expression):
    planes = root.constructionPlanes
    existing = _find_plane(planes, name)
    if existing:
        try:
            definition = adsk.fusion.OffsetConstructionPlaneDefinition.cast(
                existing.definition
            )
            if definition:
                definition.offset.expression = expression
        except Exception:
            pass
        existing.isLightBulbOn = True
        return False

    plane_input = planes.createInput()
    if not plane_input.setByOffset(
        root.xYConstructionPlane,
        adsk.core.ValueInput.createByString(expression),
    ):
        raise RuntimeError(f"No se pudo definir el plano: {name}")

    plane = planes.add(plane_input)
    if not plane:
        raise RuntimeError(f"No se pudo crear el plano: {name}")
    plane.name = name
    plane.isLightBulbOn = True
    return True


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface

    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox(
                "Abre el diseño híbrido 00_Toreto_Ensamblaje_95cm antes de ejecutar.",
                "Robot Toreto 95 cm",
            )
            return

        root = design.rootComponent
        user_parameters = design.userParameters

        for parameter_name in (
            "altura_total",
            "alto_base",
            "alto_tronco",
            "alto_cintura",
            "alto_pecho",
            "alto_cuello",
        ):
            _parameter(user_parameters, parameter_name)

        created_components = 0
        updated_components = 0
        occurrences = {}
        for name in COMPONENT_NAMES:
            created = _create_or_update_component(root, name)
            occurrences[name] = _find_occurrence(root, name)
            if created:
                created_components += 1
            else:
                updated_components += 1

        # Este script organiza, pero no recoloca ni modifica geometría ya
        # creada. Las cotas físicas pertenecen a cada generador y al alineador.
        _reset_empty_occurrence_transforms(occurrences, design)

        created_planes = 0
        for name, expression in PLANE_DEFINITIONS:
            if _create_or_update_plane(root, name, expression):
                created_planes += 1

        root.attributes.add("RobotToreto", "estructura_95cm", VERSION)

        ui.messageBox(
            "Estructura del ensamblaje creada correctamente.\n\n"
            f"Componentes creados: {created_components}\n"
            f"Componentes actualizados: {updated_components}\n"
            f"Planos de referencia nuevos: {created_planes}\n\n"
            "No se ha trasladado, borrado ni duplicado geometría existente.\n"
            "Solo las ocurrencias vacías quedan en identidad.\n\n"
            "Ejecuta los generadores y, al final, "
            "Toreto_Alinear_Montaje_95cm.",
            "Robot Toreto 95 cm",
        )

    except Exception:
        ui.messageBox(
            "No se pudo crear la estructura:\n\n" + traceback.format_exc(),
            "Robot Toreto 95 cm - Error",
        )


def stop(context):
    pass
