"""Alinea los cuerpos del Robot Toreto 95 cm horneando sus cotas globales."""

import adsk.core
import adsk.fusion
import traceback


VERSION = "1.1.0"
FEATURE_NAME = "MONTAJE_GLOBAL_95CM"


def _value(design, name, fallback):
    parameter = design.userParameters.itemByName(name)
    return parameter.value if parameter else fallback


def _find_occurrence(root, name):
    for index in range(root.occurrences.count):
        occurrence = root.occurrences.item(index)
        if occurrence.component.name == name or occurrence.name == name:
            return occurrence
    return None


def _identity_occurrence(occurrence, design):
    transform = adsk.core.Matrix3D.create()
    try:
        occurrence.isGroundToParent = False
    except Exception:
        pass
    try:
        occurrence.transform2 = transform
    except Exception:
        occurrence.transform = transform
    try:
        if design.snapshots.hasPendingTransforms:
            design.snapshots.add()
    except Exception:
        pass


def _minimum_z(component):
    minimum = None
    for index in range(component.bRepBodies.count):
        body = component.bRepBodies.item(index)
        if not body.isSolid:
            continue
        value = body.boundingBox.minPoint.z
        minimum = value if minimum is None else min(minimum, value)
    return minimum


def _remove_previous_moves(component):
    """Retira correcciones antiguas antes de medir las cotas actuales."""
    removed = 0
    features = component.features.moveFeatures
    for index in range(features.count - 1, -1, -1):
        feature = features.item(index)
        if feature.name == FEATURE_NAME and feature.deleteMe():
            removed += 1
    return removed


def _move_bodies(component, dz):
    entities = adsk.core.ObjectCollection.create()
    for index in range(component.bRepBodies.count):
        body = component.bRepBodies.item(index)
        if body.isSolid:
            entities.add(body)
    if entities.count == 0:
        return 0
    transform = adsk.core.Matrix3D.create()
    transform.translation = adsk.core.Vector3D.create(0, 0, dz)
    move_features = component.features.moveFeatures
    try:
        move_input = move_features.createInput2(entities)
        if not move_input or not move_input.defineAsFreeMove(transform):
            raise RuntimeError("Fusion rechazó el movimiento libre.")
    except Exception:
        move_input = move_features.createInput(entities, transform)
    feature = move_features.add(move_input)
    if feature:
        feature.name = FEATURE_NAME
    return entities.count


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Abre 00_Toreto_Ensamblaje_95cm antes de ejecutar.")
            return
        root = design.rootComponent
        base_h = _value(design, "alto_base", 22.5)
        trunk_h = _value(design, "alto_tronco", 18.5)
        waist_h = _value(design, "alto_cintura", 10.0)
        chest_h = _value(design, "alto_pecho", 22.8)
        neck_h = _value(design, "alto_cuello", 5.5)
        z_trunk = base_h
        z_waist = z_trunk + trunk_h
        z_chest = z_waist + waist_h
        z_neck = z_chest + chest_h
        z_head = z_neck + neck_h
        targets = (
            ("01_BASE", 0.0),
            ("02_TRONCO", z_trunk),
            ("03_CINTURA", z_waist),
            ("04_PECHO_HOMBROS", z_chest),
            ("05_CUELLO", z_neck),
            ("06_CABEZA", z_head),
        )
        moved_modules = []
        already_aligned = []
        missing = []
        removed_moves = 0
        for name, target_z in targets:
            occurrence = _find_occurrence(root, name)
            if not occurrence:
                missing.append(name)
                continue
            _identity_occurrence(occurrence, design)
            component = occurrence.component
            removed_moves += _remove_previous_moves(component)
            minimum_z = _minimum_z(component)
            if minimum_z is None:
                missing.append(name + " (sin cuerpos)")
                continue
            # El módulo está alineado si su cota mínima ya está más cerca del
            # destino que del origen local. La base siempre permanece en cero.
            if target_z == 0.0 or abs(minimum_z - target_z) < 0.15:
                already_aligned.append(name)
                continue
            if abs(minimum_z) > 0.15 and abs(minimum_z - target_z) < abs(minimum_z):
                already_aligned.append(name)
                continue
            body_count = _move_bodies(component, target_z - minimum_z)
            component.attributes.add("RobotToreto", "montaje_global_95cm", VERSION)
            moved_modules.append(f"{name}: {body_count} cuerpos a Z={target_z * 10:.0f} mm")
        # Los brazos v1.5+ ya contienen X/Z globales y sólo necesitan identidad.
        for name in ("07_BRAZO_IZQUIERDO", "08_BRAZO_DERECHO"):
            occurrence = _find_occurrence(root, name)
            if occurrence:
                _identity_occurrence(occurrence, design)
        app.activeViewport.fit()
        lines = ["Montaje global verificado.", ""]
        if removed_moves:
            lines.append(f"Correcciones antiguas retiradas: {removed_moves}")
        if moved_modules:
            lines.append("Módulos desplazados:")
            lines.extend(moved_modules)
        if already_aligned:
            lines.append("\nYa alineados: " + ", ".join(already_aligned))
        if missing:
            lines.append("\nPendientes: " + ", ".join(missing))
        lines.append("\nLos generadores nuevos ya crean cada módulo directamente en su Z global.")
        ui.messageBox("\n".join(lines), "Robot Toreto 95 cm")
    except Exception:
        ui.messageBox(
            "No se pudo alinear el montaje:\n\n" + traceback.format_exc(),
            "Robot Toreto 95 cm - Error",
        )


def stop(context):
    pass
