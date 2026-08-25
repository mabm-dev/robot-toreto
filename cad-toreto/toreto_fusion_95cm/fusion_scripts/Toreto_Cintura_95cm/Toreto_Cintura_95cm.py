"""Crea la carcasa exterior de la cintura Robot Toreto 95 cm."""

import traceback

import adsk.core
import adsk.fusion


COMPONENT_NAME = "03_CINTURA"
FEATURE_NAME = "CINTURA_EXTERIOR_TORETO_95CM"
BODY_PREFIX = "CINTURA95_"
VERSION = "1.2.0"

_GEOMETRY_Z = 0.0

BLACK = (18, 21, 24)
DARK = (43, 48, 53)
CYAN = (0, 174, 235)


def _find_occurrence(root, name):
    for index in range(root.occurrences.count):
        occurrence = root.occurrences.item(index)
        if occurrence.component.name == name:
            return occurrence
    return None


def _value(design, name, fallback):
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


def _ring(manager, z1, z2, outer, inner):
    body = _ellipse(manager, z1, z2, *outer)
    tool = _ellipse(manager, z1 - 0.1, z2 + 0.1, *inner)
    if not manager.booleanOperation(
        body, tool, adsk.fusion.BooleanTypes.DifferenceBooleanType
    ):
        raise RuntimeError("No se pudo ahuecar la carcasa de cintura.")
    return body


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


def _cylinder(manager, p1, p2, radius):
    return manager.createCylinderOrCone(p1, radius, p2, radius)


def _union(manager, target, tool, label):
    if not manager.booleanOperation(
        target, tool, adsk.fusion.BooleanTypes.UnionBooleanType
    ):
        raise RuntimeError(f"Falló la unión: {label}")


def _rounded_panel(manager, x, y, z, width, height, depth, radius):
    body = _box(manager, x, y, z, width - 2 * radius, depth, height)
    _union(
        manager,
        body,
        _box(manager, x, y, z, width, depth, height - 2 * radius),
        "centro del panel",
    )
    for sx in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            cx = x + sx * (width / 2 - radius)
            cz = z + sz * (height / 2 - radius)
            _union(
                manager,
                body,
                _cylinder(
                    manager,
                    _point(cx, y - depth / 2, cz),
                    _point(cx, y + depth / 2, cz),
                    radius,
                ),
                "esquina del panel",
            )
    return body


def _rounded_xy(manager, x, y, z, width, depth, height, radius):
    """Prisma vertical con planta rectangular y cuatro esquinas redondas."""
    radius = min(radius, width * 0.48, depth * 0.48)
    body = _box(manager, x, y, z, width - 2 * radius, depth, height)
    _union(
        manager,
        body,
        _box(manager, x, y, z, width, depth - 2 * radius, height),
        "centro de cintura redondeada",
    )
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            cx = x + sx * (width / 2 - radius)
            cy = y + sy * (depth / 2 - radius)
            _union(
                manager,
                body,
                _cylinder(
                    manager,
                    _point(cx, cy, z - height / 2),
                    _point(cx, cy, z + height / 2),
                    radius,
                ),
                "esquina de cintura",
            )
    return body


def _append(specs, body, name, color):
    if not body:
        raise RuntimeError(f"No se pudo construir {name}.")
    specs.append((body, BODY_PREFIX + name, color))


def _appearance(app, design, name, rgb):
    existing = design.appearances.itemByName(name)
    if existing:
        return existing
    generic = None
    library = app.materialLibraries.itemById(
        "BA5EE55E-9982-449B-9D66-9F036540E140"
    )
    if library:
        generic = library.appearances.itemById("Prism-129")
    if not generic:
        for index in range(app.materialLibraries.count):
            generic = app.materialLibraries.item(index).appearances.itemById(
                "Prism-129"
            )
            if generic:
                break
    if not generic:
        return None
    appearance = design.appearances.addByCopy(generic, name)
    prop = appearance.appearanceProperties.itemById("opaque_albedo")
    if prop:
        prop.value = adsk.core.Color.create(rgb[0], rgb[1], rgb[2], 255)
    return appearance


def _has_bodies(component):
    for index in range(component.bRepBodies.count):
        if component.bRepBodies.item(index).name.startswith(BODY_PREFIX):
            return True
    return False


def _version(component):
    attribute = component.attributes.itemByName(
        "RobotToreto", "cintura_95cm_version"
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
    if not feature or not feature.deleteMe() or _has_bodies(component):
        raise RuntimeError("No se pudo retirar la cintura exterior anterior.")
    return True


def _build(manager, rs, hs):
    r = lambda value: value * rs
    z = lambda value: value * hs
    specs = []

    # Bloque compacto de esquinas redondeadas. En las referencias la cintura
    # no es un cono: es una cápsula rectangular negra más estrecha que el
    # pecho y que el pedestal inferior.
    core = _rounded_xy(
        manager, 0, 0, z(5.0), r(20.2), r(14.6), z(9.4), r(2.35)
    )
    _append(specs, core, "01_BLOQUE_NEGRO_REDONDEADO", BLACK)

    lower = _rounded_xy(
        manager, 0, 0, z(0.55), r(20.8), r(15.2), z(1.1), r(2.55)
    )
    _append(specs, lower, "02_COLLAR_INFERIOR_GRAFITO", DARK)

    upper = _rounded_xy(
        manager, 0, 0, z(9.45), r(19.8), r(14.25), z(1.1), r(2.25)
    )
    _append(specs, upper, "03_COLLAR_SUPERIOR_NEGRO", BLACK)

    # El frontal queda negro y limpio. La tapa técnica visible en las vistas
    # de cuatro caras pertenece a la espalda.
    back_y = r(7.38)
    panel = _rounded_panel(
        manager, 0, back_y, z(5.4), r(8.4), z(4.6), r(0.45), r(0.72)
    )
    _append(specs, panel, "04_TAPA_TRASERA_GRAFITO", DARK)

    seam = _box(manager, 0, back_y + r(0.42), z(5.4), r(0.14), r(0.16), z(3.8))
    _append(specs, seam, "05_JUNTA_TAPA_TRASERA", BLACK)

    for index, x in enumerate((-2.6, 2.6), start=1):
        fastener = _cylinder(
            manager,
            _point(r(x), back_y + r(0.40), z(2.9)),
            _point(r(x), back_y + r(0.62), z(2.9)),
            r(0.22),
        )
        _append(specs, fastener, f"06_FIJACION_TRASERA_{index:02d}", BLACK)
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
                "Falta 03_CINTURA. Ejecuta primero Toreto_Componentes_95cm."
            )
        component = occurrence.component
        if _version(component) == VERSION and _has_bodies(component):
            ui.messageBox("La cintura exterior ya existe; no se duplicó.")
            return

        replaced = _replace_old(component)
        diameter = _value(design, "diametro_base", 40.0)
        waist_h = _value(design, "alto_cintura", 10.0)
        _GEOMETRY_Z = (
            _value(design, "alto_base", 22.5)
            + _value(design, "alto_tronco", 18.5)
        )
        rs = diameter / 40.0
        hs = waist_h / 10.0
        manager = adsk.fusion.TemporaryBRepManager.get()
        specs = _build(manager, rs, hs)
        appearances = {
            BLACK: _appearance(app, design, "TORETO Negro profundo", BLACK),
            DARK: _appearance(app, design, "TORETO Grafito", DARK),
            CYAN: _appearance(app, design, "TORETO Cian", CYAN),
        }

        feature = component.features.baseFeatures.add()
        if not feature:
            raise RuntimeError("Fusion no pudo crear la función base de cintura.")
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

        component.attributes.add("RobotToreto", "cintura_95cm_version", VERSION)
        design.rootComponent.attributes.add("RobotToreto", "ultimo_modulo", "03_CINTURA")
        app.activeViewport.fit()
        ui.messageBox(
            ("Cintura exterior actualizada." if replaced else "Cintura exterior creada.")
            + f"\n\nCuerpos exteriores: {len(persisted)}\nAltura: {waist_h * 10:.0f} mm\n\n"
            "Sin estructura, motores ni electrónica.",
            "Robot Toreto 95 cm",
        )
    except Exception:
        ui.messageBox(
            "No se pudo crear la cintura exterior:\n\n" + traceback.format_exc(),
            "Robot Toreto 95 cm - Error",
        )
    finally:
        _GEOMETRY_Z = 0.0


def stop(context):
    pass
