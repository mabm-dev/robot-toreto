"""Crea la carcasa exterior del tronco Robot Toreto 95 cm."""

import math
import traceback

import adsk.core
import adsk.fusion


COMPONENT_NAME = "02_TRONCO"
FEATURE_NAME = "TRONCO_EXTERIOR_TORETO_95CM"
BODY_PREFIX = "TRONCO95_"
VERSION = "1.3.0"

_GEOMETRY_Z = 0.0

WHITE = (238, 239, 237)
BLACK = (18, 21, 24)
DARK = (43, 48, 53)
CYAN = (0, 174, 235)


def _find_occurrence(root, component_name):
    for index in range(root.occurrences.count):
        occurrence = root.occurrences.item(index)
        if occurrence.component.name == component_name:
            return occurrence
    return None


def _parameter_value(design, name, fallback):
    parameter = design.userParameters.itemByName(name)
    return parameter.value if parameter else fallback


def _point(x, y, z):
    return adsk.core.Point3D.create(x, y, z + _GEOMETRY_Z)


def _vector(x, y, z):
    return adsk.core.Vector3D.create(x, y, z)


def _ellipse(manager, z1, z2, major1, minor1, major2=None):
    if major2 is None:
        major2 = major1
    return manager.createEllipticalCylinderOrCone(
        _point(0, 0, z1),
        major1,
        minor1,
        _point(0, 0, z2),
        major2,
        _vector(1, 0, 0),
    )


def _cylinder(manager, p1, p2, radius):
    return manager.createCylinderOrCone(p1, radius, p2, radius)


def _box(manager, x, y, z, size_x, size_y, size_z):
    bounds = adsk.core.OrientedBoundingBox3D.create(
        _point(x, y, z),
        _vector(1, 0, 0),
        _vector(0, 1, 0),
        size_x,
        size_y,
        size_z,
    )
    return manager.createBox(bounds)


def _union(manager, target, tool, label):
    if not manager.booleanOperation(
        target, tool, adsk.fusion.BooleanTypes.UnionBooleanType
    ):
        raise RuntimeError(f"Falló la unión: {label}")
    return target


def _difference(manager, target, tool, label):
    if not manager.booleanOperation(
        target, tool, adsk.fusion.BooleanTypes.DifferenceBooleanType
    ):
        raise RuntimeError(f"Falló el vaciado: {label}")
    return target


def _ring(manager, z1, z2, outer, inner):
    body = _ellipse(manager, z1, z2, *outer)
    tool = _ellipse(manager, z1 - 0.1, z2 + 0.1, *inner)
    return _difference(manager, body, tool, "carcasa cónica")


def _rounded_panel(manager, x, y, z, width, height, depth, radius):
    body = _box(manager, x, y, z, width - 2.0 * radius, depth, height)
    _union(
        manager,
        body,
        _box(manager, x, y, z, width, depth, height - 2.0 * radius),
        "centro panel redondeado",
    )
    for side_x in (-1.0, 1.0):
        for side_z in (-1.0, 1.0):
            corner = _cylinder(
                manager,
                _point(
                    x + side_x * (width / 2.0 - radius),
                    y - depth / 2.0,
                    z + side_z * (height / 2.0 - radius),
                ),
                _point(
                    x + side_x * (width / 2.0 - radius),
                    y + depth / 2.0,
                    z + side_z * (height / 2.0 - radius),
                ),
                radius,
            )
            _union(manager, body, corner, "esquina panel")
    return body


def _append(specs, body, name, color):
    if not body:
        raise RuntimeError(f"No se pudo construir: {name}")
    specs.append((body, BODY_PREFIX + name, color))


def _appearance(app, design, name, rgb):
    existing = design.appearances.itemByName(name)
    if existing:
        return existing
    library = app.materialLibraries.itemById(
        "BA5EE55E-9982-449B-9D66-9F036540E140"
    )
    generic = library.appearances.itemById("Prism-129") if library else None
    if not generic:
        for index in range(app.materialLibraries.count):
            candidate = app.materialLibraries.item(index)
            generic = candidate.appearances.itemById("Prism-129")
            if generic:
                break
    if not generic:
        return None
    result = design.appearances.addByCopy(generic, name)
    prop = result.appearanceProperties.itemById("opaque_albedo")
    if prop:
        prop.value = adsk.core.Color.create(rgb[0], rgb[1], rgb[2], 255)
    return result


def _has_bodies(component):
    for index in range(component.bRepBodies.count):
        if component.bRepBodies.item(index).name.startswith(BODY_PREFIX):
            return True
    return False


def _version(component):
    attribute = component.attributes.itemByName(
        "RobotToreto", "tronco_95cm_version"
    )
    return attribute.value if attribute else None


def _replace_old(component):
    if not _has_bodies(component):
        return False
    feature = None
    for index in range(component.features.baseFeatures.count):
        candidate = component.features.baseFeatures.item(index)
        if candidate.name == FEATURE_NAME:
            feature = candidate
            break
    if not feature:
        raise RuntimeError(
            "Hay cuerpos TRONCO95_ sin su función generadora; no se modifican."
        )
    if not feature.deleteMe() or _has_bodies(component):
        raise RuntimeError("No se pudo retirar el tronco anterior.")
    return True


def _build(manager, rs, hs):
    def r(value):
        return value * rs

    def z(value):
        return value * hs

    specs = []

    core = _ellipse(manager, z(0.6), z(18.5), r(10.0), r(7.9))
    _append(specs, core, "01_NUCLEO_NEGRO", BLACK)

    # Zócalo inferior: una ligera panza que se asienta sobre la base, como
    # en la referencia, en vez de un cilindro de paredes verticales.
    base_ring = _ring(
        manager,
        z(0.0),
        z(2.6),
        (r(13.2), r(10.6), r(12.35)),
        (r(11.9), r(9.35), r(11.15)),
    )
    _append(specs, base_ring, "02_ZOCALO_INFERIOR_REDONDEADO", WHITE)

    # Línea negra de separación entre la carcasa y la base.
    base_seam = _ring(
        manager,
        z(1.75),
        z(2.35),
        (r(12.95), r(10.35), r(12.65)),
        (r(12.25), r(9.65), r(11.95)),
    )
    _append(specs, base_seam, "03_JUNTA_NEGRA_BASE", BLACK)

    # Carcasa principal de transición suave: ancha abajo y más estrecha
    # arriba, pero sin el escalón visual de la versión anterior.
    shell = _ring(
        manager,
        z(2.0),
        z(17.0),
        (r(12.55), r(10.05), r(9.95)),
        (r(11.90), r(9.40), r(9.20)),
    )
    _append(specs, shell, "04_CARCASA_BLANCA_CONICA_SUAVE", WHITE)

    # Hombro superior redondeado que recibe el núcleo negro de la cintura.
    upper_shoulder = _ring(
        manager,
        z(16.2),
        z(18.5),
        (r(10.25), r(7.95), r(9.55)),
        (r(9.55), r(7.20), r(8.80)),
    )
    _append(specs, upper_shoulder, "05_HOMBRO_SUPERIOR_SUAVE", WHITE)

    top_collar = _ring(
        manager,
        z(16.8),
        z(18.5),
        (r(9.55), r(7.35)),
        (r(7.75), r(5.85)),
    )
    _append(specs, top_collar, "06_COLLAR_SUPERIOR_NEGRO", BLACK)

    # Las vistas definitivas muestran el pedestal frontal completamente
    # limpio. Sólo quedan dos fijaciones discretas en la cara posterior.
    back_y = r(9.82)
    for index, x in enumerate((-4.4, 4.4), start=1):
        fastener = _cylinder(
            manager,
            _point(r(x), back_y, z(2.8)),
            _point(r(x), back_y + r(0.28), z(2.8)),
            r(0.26),
        )
        _append(specs, fastener, f"07_FIJACION_TRASERA_{index:02d}", BLACK)

    return specs


def run(context):
    global _GEOMETRY_Z
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Abre 00_Toreto_Ensamblaje_95cm antes de ejecutar.")
            return

        occurrence = _find_occurrence(design.rootComponent, COMPONENT_NAME)
        if not occurrence:
            raise RuntimeError(
                "Falta 02_TRONCO. Ejecuta primero Toreto_Componentes_95cm."
            )
        component = occurrence.component
        if _version(component) == VERSION and _has_bodies(component):
            ui.messageBox("El tronco exterior ya existe; no se duplicó.")
            return
        replaced = _replace_old(component)

        trunk_height = _parameter_value(design, "alto_tronco", 18.5)
        _GEOMETRY_Z = _parameter_value(design, "alto_base", 22.5)
        diameter = _parameter_value(design, "diametro_base", 40.0)
        rs = diameter / 40.0
        hs = trunk_height / 18.5

        manager = adsk.fusion.TemporaryBRepManager.get()
        specs = _build(manager, rs, hs)
        appearances = {
            WHITE: _appearance(app, design, "TORETO Blanco satinado", WHITE),
            BLACK: _appearance(app, design, "TORETO Negro profundo", BLACK),
            DARK: _appearance(app, design, "TORETO Grafito", DARK),
            CYAN: _appearance(app, design, "TORETO Cian", CYAN),
        }

        feature = component.features.baseFeatures.add()
        if not feature:
            raise RuntimeError("Fusion no pudo crear la función base del tronco.")
        feature.name = FEATURE_NAME

        persisted = []
        feature.startEdit()
        try:
            for temp_body, name, color in specs:
                body = component.bRepBodies.add(temp_body, feature)
                if not body:
                    raise RuntimeError(f"Fusion no pudo añadir {name}.")
                body.name = name
                if appearances.get(color):
                    body.appearance = appearances[color]
                body.isLightBulbOn = True
                persisted.append(body)
        finally:
            feature.finishEdit()

        component.attributes.add("RobotToreto", "tronco_95cm_version", VERSION)
        design.rootComponent.attributes.add(
            "RobotToreto", "ultimo_modulo", "02_TRONCO"
        )
        app.activeViewport.fit()
        status = "actualizado" if replaced else "creado"
        ui.messageBox(
            f"Tronco exterior {status}.\n\n"
            f"Cuerpos exteriores: {len(persisted)}\n"
            f"Altura: {trunk_height * 10:.0f} mm\n\n"
            f"Cota global inferior: Z={_GEOMETRY_Z * 10:.0f} mm\n"
            "Sin estructura, batería, electrónica ni anclajes mecánicos.",
            "Robot Toreto 95 cm",
        )
    except Exception:
        ui.messageBox(
            "No se pudo crear el tronco exterior:\n\n" + traceback.format_exc(),
            "Robot Toreto 95 cm - Error",
        )
    finally:
        _GEOMETRY_Z = 0.0


def stop(context):
    pass
