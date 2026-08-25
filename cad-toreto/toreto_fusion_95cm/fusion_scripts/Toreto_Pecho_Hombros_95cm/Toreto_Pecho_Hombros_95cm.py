"""Crea la carcasa exterior de pecho y hombros Robot Toreto 95 cm."""

import traceback

import adsk.core
import adsk.fusion


COMPONENT_NAME = "04_PECHO_HOMBROS"
FEATURE_NAME = "PECHO_HOMBROS_EXTERIOR_TORETO_95CM"
BODY_PREFIX = "PECHO95_"
VERSION = "2.1.0"

_GEOMETRY_Z = 0.0

WHITE = (238, 239, 237)
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


def _ensure_value(design, name, expression, comment):
    parameter = design.userParameters.itemByName(name)
    if not parameter:
        parameter = design.userParameters.add(
            name,
            adsk.core.ValueInput.createByString(expression),
            "mm",
            comment,
        )
    return parameter.value


def _set_master_value(design, name, expression, comment):
    parameter = design.userParameters.itemByName(name)
    if parameter:
        parameter.expression = expression
        parameter.comment = comment
    else:
        parameter = design.userParameters.add(
            name,
            adsk.core.ValueInput.createByString(expression),
            "mm",
            comment,
        )
    return parameter.value


def _point(x, y, z):
    return adsk.core.Point3D.create(x, y, z + _GEOMETRY_Z)


def _vector(x, y, z):
    return adsk.core.Vector3D.create(x, y, z)


def _ellipse(manager, z1, z2, major1, minor1, major2=None):
    if major2 is None:
        major2 = major1
    return manager.createEllipticalCylinderOrCone(
        _point(0, 0, z1), major1, minor1,
        _point(0, 0, z2), major2, _vector(1, 0, 0)
    )


def _ring(manager, z1, z2, outer, inner):
    body = _ellipse(manager, z1, z2, *outer)
    tool = _ellipse(manager, z1 - 0.1, z2 + 0.1, *inner)
    if not manager.booleanOperation(
        body, tool, adsk.fusion.BooleanTypes.DifferenceBooleanType
    ):
        raise RuntimeError("No se pudo ahuecar la carcasa del pecho.")
    return body


def _box(manager, x, y, z, sx, sy, sz):
    bounds = adsk.core.OrientedBoundingBox3D.create(
        _point(x, y, z), _vector(1, 0, 0), _vector(0, 1, 0), sx, sy, sz
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
    _union(manager, body, _box(manager, x, y, z, width, depth, height - 2 * radius), "centro panel")
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
                "esquina panel",
            )
    return body


def _rounded_side(manager, x, y, z, depth, height, width, radius):
    """Envolvente redondeada en la vista lateral, extruida sobre X."""
    radius = min(radius, depth * .48, height * .48)
    body = _box(manager, x, y, z, width, depth - 2 * radius, height)
    _union(
        manager,
        body,
        _box(manager, x, y, z, width, depth, height - 2 * radius),
        "centro lateral del pecho",
    )
    for sy in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            cy = y + sy * (depth / 2 - radius)
            cz = z + sz * (height / 2 - radius)
            _union(
                manager,
                body,
                _cylinder(
                    manager,
                    _point(x - width / 2, cy, cz),
                    _point(x + width / 2, cy, cz),
                    radius,
                ),
                "esquina lateral del pecho",
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
    library = app.materialLibraries.itemById("BA5EE55E-9982-449B-9D66-9F036540E140")
    if library:
        generic = library.appearances.itemById("Prism-129")
    if not generic:
        for index in range(app.materialLibraries.count):
            generic = app.materialLibraries.item(index).appearances.itemById("Prism-129")
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
    attr = component.attributes.itemByName("RobotToreto", "pecho_95cm_version")
    return attr.value if attr else None


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
        raise RuntimeError("No se pudo retirar el pecho anterior.")
    return True


def _build(manager, width, depth, height, screen_width, screen_height, screen_depth, clearance):
    """Construye el pecho siguiendo las vistas frontal, lateral y trasera."""
    rs = width / 34.0
    ds = depth / 21.6
    hs = height / 22.8
    r = lambda value: value * rs
    d = lambda value: value * ds
    z = lambda value: value * hs
    specs = []

    # Cuerpo rectangular redondeado; sustituye el antiguo pecho elíptico.
    shell = _rounded_panel(
        manager, 0, 0, z(11.4), width, height, depth, min(width, height) * .12
    )
    side_shell = _rounded_side(
        manager, 0, d(.15), z(11.4), depth, height, width + r(.5), min(depth, height) * .17
    )
    if not manager.booleanOperation(
        shell, side_shell, adsk.fusion.BooleanTypes.IntersectionBooleanType
    ):
        raise RuntimeError("No se pudo redondear la silueta lateral del pecho.")
    inner = _rounded_panel(
        manager,
        0,
        0,
        z(11.4),
        width - r(1.7),
        height - z(1.7),
        depth - d(1.8),
        min(width, height) * .095,
    )
    side_inner = _rounded_side(
        manager,
        0,
        d(.15),
        z(11.4),
        depth - d(1.8),
        height - z(1.7),
        width - r(1.2),
        min(depth, height) * .13,
    )
    if not manager.booleanOperation(
        inner, side_inner, adsk.fusion.BooleanTypes.IntersectionBooleanType
    ):
        raise RuntimeError("No se pudo formar la cavidad lateral del pecho.")
    if not manager.booleanOperation(
        shell, inner, adsk.fusion.BooleanTypes.DifferenceBooleanType
    ):
        raise RuntimeError("No se pudo ahuecar la carcasa rectangular del pecho.")

    cavity_width = screen_width + 2.0 * clearance
    cavity_height = screen_height + 2.0 * clearance
    cavity = _rounded_panel(
        manager,
        0,
        -depth / 2 + d(.55),
        z(11.4),
        cavity_width,
        cavity_height,
        d(2.8),
        min(cavity_width, cavity_height) * .10,
    )
    if not manager.booleanOperation(
        shell, cavity, adsk.fusion.BooleanTypes.DifferenceBooleanType
    ):
        raise RuntimeError("No se pudo abrir el hueco de la pantalla.")

    neck_cut = _ellipse(manager, z(19.0), z(23.2), r(6.4), d(4.3), r(6.1))
    if not manager.booleanOperation(
        shell, neck_cut, adsk.fusion.BooleanTypes.DifferenceBooleanType
    ):
        raise RuntimeError("No se pudo abrir el paso superior del cuello.")
    _append(specs, shell, "01_CARCASA_RECTANGULAR_REDONDEADA", WHITE)

    lower = _rounded_panel(
        manager, 0, d(.45), z(1.1), r(14.5), z(2.2), d(9.8), z(.68)
    )
    _append(specs, lower, "02_INSERTO_INFERIOR_NEGRO", BLACK)

    neck_insert = _ring(
        manager, z(20.2), z(23.0), (r(7.25), d(5.05)), (r(5.85), d(3.75))
    )
    _append(specs, neck_insert, "03_INSERTO_CUELLO_NEGRO", BLACK)

    front_y = -depth / 2 - d(.08)
    bezel = _rounded_panel(
        manager,
        0,
        front_y,
        z(11.4),
        cavity_width + r(.8),
        cavity_height + z(.8),
        d(.52),
        min(cavity_width, cavity_height) * .10,
    )
    _append(specs, bezel, "04_MARCO_PANTALLA_NEGRO", BLACK)

    screen = _rounded_panel(
        manager,
        0,
        front_y - d(.32),
        z(11.4),
        screen_width,
        screen_height,
        d(.36),
        min(screen_width, screen_height) * .07,
    )
    _append(specs, screen, "05_PANTALLA_GRAFITO", DARK)

    screen_glow = _rounded_panel(
        manager,
        0,
        front_y - d(.54),
        z(11.4),
        min(screen_width * .72, r(12.0)),
        z(.28),
        d(.08),
        r(.12),
    )
    _append(specs, screen_glow, "06_LINEA_PANTALLA_CIAN", CYAN)

    # Sólo el conector negro pertenece al pecho; la carcasa blanca es del brazo.
    for side, label in ((-1.0, "IZQ"), (1.0, "DER")):
        cx = side * r(17.15)
        socket = _cylinder(
            manager,
            _point(cx - side * r(.55), 0, z(16.4)),
            _point(cx + side * r(2.5), 0, z(16.4)),
            r(3.65),
        )
        _append(specs, socket, f"07_CONECTOR_HOMBRO_{label}", BLACK)

    back_y = depth / 2 + d(.08)
    back_panel = _rounded_panel(
        manager, 0, back_y + d(.14), z(11.5), r(26.3), z(14.3), d(.26), z(1.0)
    )
    _append(specs, back_panel, "08_TAPA_TRASERA_BLANCA", WHITE)
    for index, x in enumerate((-4.8, 4.8), start=1):
        latch = _cylinder(
            manager,
            _point(r(x), back_y + d(.42), z(4.2)),
            _point(r(x), back_y + d(.66), z(4.2)),
            r(.27),
        )
        _append(specs, latch, f"09_FIJACION_TRASERA_{index:02d}", DARK)

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
            raise RuntimeError("Falta 04_PECHO_HOMBROS. Ejecuta Componentes primero.")
        component = occurrence.component
        if _version(component) == VERSION and _has_bodies(component):
            ui.messageBox("El pecho exterior ya existe; no se duplicó.")
            return
        replaced = _replace_old(component)
        # Valores de la envolvente exterior definida en continuidad.
        width = _set_master_value(
            design, "ancho_pecho", "340 mm", "Anchura máxima de la carcasa de pecho"
        )
        depth = _set_master_value(
            design, "fondo_pecho", "216 mm", "Profundidad máxima de la carcasa de pecho"
        )
        height = _set_master_value(
            design, "alto_pecho", "228 mm", "Altura exterior de la carcasa de pecho"
        )
        _GEOMETRY_Z = sum(
            _ensure_value(design, name, expression, comment)
            for name, expression, comment in (
                ("alto_base", "225 mm", "Altura base"),
                ("alto_tronco", "185 mm", "Altura tronco"),
                ("alto_cintura", "100 mm", "Altura cintura"),
            )
        )
        screen_width = _ensure_value(
            design,
            "pantalla_ancho",
            "160 mm",
            "Anchura del dispositivo Android en horizontal",
        )
        screen_height = _ensure_value(
            design,
            "pantalla_alto",
            "90 mm",
            "Altura del dispositivo Android en horizontal",
        )
        screen_depth = _ensure_value(
            design,
            "pantalla_fondo",
            "12 mm",
            "Profundidad del dispositivo con carcasa",
        )
        clearance = _ensure_value(
            design,
            "pantalla_holgura",
            "3 mm",
            "Holgura total por lado del hueco de pantalla",
        )
        manager = adsk.fusion.TemporaryBRepManager.get()
        specs = _build(
            manager,
            width,
            depth,
            height,
            screen_width,
            screen_height,
            screen_depth,
            clearance,
        )
        appearances = {
            WHITE: _appearance(app, design, "TORETO Blanco satinado", WHITE),
            BLACK: _appearance(app, design, "TORETO Negro profundo", BLACK),
            DARK: _appearance(app, design, "TORETO Grafito", DARK),
            CYAN: _appearance(app, design, "TORETO Cian", CYAN),
        }
        feature = component.features.baseFeatures.add()
        if not feature:
            raise RuntimeError("Fusion no pudo crear la función base del pecho.")
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
        component.attributes.add("RobotToreto", "pecho_95cm_version", VERSION)
        design.rootComponent.attributes.add("RobotToreto", "ultimo_modulo", "04_PECHO_HOMBROS")
        app.activeViewport.fit()
        ui.messageBox(
            ("Pecho y hombros actualizados." if replaced else "Pecho y hombros creados.")
            + f"\n\nCuerpos exteriores: {len(persisted)}\n"
            f"Hueco dispositivo: {screen_width * 10:.0f} x {screen_height * 10:.0f} mm\n"
            f"Holgura: {clearance * 10:.0f} mm por lado\n\n"
            "Pantalla y carcasas de hombro incluidas.\nSin mecánica ni esqueleto.",
            "Robot Toreto 95 cm",
        )
    except Exception:
        ui.messageBox(
            "No se pudo crear el pecho:\n\n" + traceback.format_exc(),
            "Robot Toreto 95 cm - Error",
        )
    finally:
        _GEOMETRY_Z = 0.0


def stop(context):
    pass
