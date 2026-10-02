"""Crea la carcasa exterior de la cintura Robot Toreto 95 cm."""

import traceback

import adsk.core
import adsk.fusion


COMPONENT_NAME = "03_CINTURA"
FEATURE_NAME = "CINTURA_EXTERIOR_TORETO_95CM"
ALIGNMENT_FEATURE_NAME = "MONTAJE_GLOBAL_95CM"
BODY_PREFIX = "CINTURA95_"
VERSION = "2.3.0"

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
    for index in range(component.features.moveFeatures.count - 1, -1, -1):
        move = component.features.moveFeatures.item(index)
        if move.name == ALIGNMENT_FEATURE_NAME and not move.deleteMe():
            raise RuntimeError("No se pudo retirar la alineación anterior de la cintura.")
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
    # 2.0.0: cintura del lienzo frontal en tres piezas, con la forma del
    # render 3D. Medidas en mm del lienzo (diametro_base 450, alto_cintura
    # 150); z = 0 es la junta con el tronco (Z 390). El bloque inferior baja
    # 36 mm dentro de la silla del tronco y el superior sube bajo la falda
    # del pecho: ambos solapes son a propósito.
    r = lambda mm: mm / 10.0 * rs / 1.125
    z = lambda mm: mm / 10.0 * hs / 1.5
    specs = []

    # Bloque superior: 170 x 136 mm, Z 470-540, con un conector redondo en
    # cada costado.
    upper = _rounded_xy(manager, 0, 0, z(115), r(170), r(136), z(70), r(14))
    _append(specs, upper, "01_BLOQUE_SUPERIOR_NEGRO", BLACK)
    for side, label in ((-1.0, "IZQ"), (1.0, "DER")):
        port = _cylinder(
            manager,
            _point(side * r(83), 0, z(108)),
            _point(side * r(91), 0, z(108)),
            r(12.5),
        )
        _union(
            manager,
            port,
            _cylinder(
                manager,
                _point(side * r(91), 0, z(108)),
                _point(side * r(92), 0, z(108)),
                r(8),
            ),
            "conector lateral",
        )
        _append(specs, port, f"02_CONECTOR_LATERAL_{label}", DARK)

    # Junta de giro: cilindro de 128 mm (Z 460-470) con dos nervios.
    joint = _cylinder(manager, _point(0, 0, z(70)), _point(0, 0, z(80)), r(62))
    for z1 in (72.5, 75.5):
        _union(
            manager,
            joint,
            _cylinder(manager, _point(0, 0, z(z1)), _point(0, 0, z(z1 + 2)), r(64)),
            "nervio de la junta",
        )
    _append(specs, joint, "03_JUNTA_ANILLOS_GRAFITO", DARK)

    # Bloque inferior: 182 x 146 mm hasta Z 460. 2.2.0: va fijo y entero
    # por dentro del collar del tronco hasta Z 330 (planta de esquinas de
    # radio 50 como en el render); lo que se ve por delante lo marca el
    # borde en U del collar (fondo en Z 354). Sustituye a la espiga.
    lower = _rounded_xy(manager, 0, 0, z(5), r(182), r(146), z(130), r(50))
    # 2.3.0: CADERA, eje en X a Z 400 (z local 10). Por debajo del eje el
    # bloque se limita a un arco de R70 alrededor de el (visto de lado), para
    # que al girar no toque el collar ni la tapa interior del tronco.
    hip = z(10)
    trim = _cylinder(manager, _point(-r(100), 0, hip), _point(r(100), 0, hip), r(70))
    _union(manager, trim, _box(manager, 0, 0, hip + z(40), r(200), r(200), z(80)),
           "zona del bloque sobre el eje")
    if not manager.booleanOperation(
        lower, trim, adsk.fusion.BooleanTypes.IntersectionBooleanType
    ):
        raise RuntimeError("No se pudo redondear el bloque para la cadera.")
    _append(specs, lower, "04_BLOQUE_INFERIOR_NEGRO", BLACK)
    # Eje hueco de la cadera (R15, paso de cables R8) que gira con la cintura
    # en los discos del tronco.
    axle = _cylinder(manager, _point(-r(118), 0, hip), _point(r(118), 0, hip), r(15))
    if not manager.booleanOperation(
        axle,
        _cylinder(manager, _point(-r(120), 0, hip), _point(r(120), 0, hip), r(8)),
        adsk.fusion.BooleanTypes.DifferenceBooleanType,
    ):
        raise RuntimeError("No se pudo ahuecar el eje de la cadera.")
    _append(specs, axle, "09_EJE_CADERA", DARK)

    # Franja central de 94 mm en los dos bloques y panel cuadrado de 74 x 70.
    for name, face_y, z1, z2 in (
        ("05_FRANJA_INFERIOR_GRAFITO", r(73), -z(30), z(70)),
        ("05_FRANJA_SUPERIOR_GRAFITO", r(68), z(80), z(130)),
    ):
        strip = _box(
            manager, 0, -face_y - r(.5), (z1 + z2) / 2, r(94), r(1), z2 - z1
        )
        _append(specs, strip, name, DARK)
    front_panel = _rounded_panel(
        manager, 0, -r(74), z(21.5), r(74), z(69), r(2), r(8)
    )
    _append(specs, front_panel, "06_PANEL_FRONTAL_GRAFITO", DARK)

    back_panel = _rounded_panel(
        manager, 0, r(74), z(21.5), r(74), z(69), r(2), r(8)
    )
    _append(specs, back_panel, "07_TAPA_TRASERA_GRAFITO", DARK)
    for index, x in enumerate((-25, 25), start=1):
        fastener = _cylinder(
            manager,
            _point(r(x), r(75), z(-8)),
            _point(r(x), r(77), z(-8)),
            r(2.2),
        )
        _append(specs, fastener, f"08_FIJACION_TRASERA_{index:02d}", BLACK)
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
        diameter = _value(design, "diametro_base", 45.0)
        waist_h = _value(design, "alto_cintura", 15.0)
        _GEOMETRY_Z = (
            _value(design, "alto_base", 20.0)
            + _value(design, "alto_tronco", 19.0)
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
