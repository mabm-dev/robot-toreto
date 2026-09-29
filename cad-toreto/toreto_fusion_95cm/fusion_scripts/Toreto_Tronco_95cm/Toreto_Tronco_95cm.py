"""Crea la carcasa exterior del tronco Robot Toreto 95 cm."""

import math
import traceback

import adsk.core
import adsk.fusion


COMPONENT_NAME = "02_TRONCO"
FEATURE_NAME = "TRONCO_EXTERIOR_TORETO_95CM"
BODY_PREFIX = "TRONCO95_"
# 1.3.1 (29-09-2026): misma geometria. Solo cambia la version para que el
# complemento se regenere: el montaje tenia el tronco hecho con alto_tronco =
# 185 mm (acababa en Z 385 y dejaba 5 mm de hueco bajo la cintura) y la
# comprobacion de version impedia rehacerlo con el valor actual (190).
# 1.4.0 (29-09-2026): borde en silla y sin collar negro (cintura 2.0.0).
# 1.4.1 (29-09-2026): silla de radio 40 y relleno que cierra el interior.
# 1.5.0 (29-09-2026): cintura fija y encajada (sin holgura, con espiga) y
# tronco casi recto como en el lienzo.
# 1.6.0 (29-09-2026): collar superior de planta cuadrada que envuelve el
# bloque de la cintura (antes asomaba por las esquinas) y fondo 0,9.
# 1.6.1 (29-09-2026): panel frontal sobre el LIDAR.
VERSION = "1.6.1"

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


def _rounded_xy(manager, x, y, z, width, depth, height, radius):
    """Prisma vertical con planta rectangular y cuatro esquinas redondas."""
    radius = min(radius, width * 0.48, depth * 0.48)
    body = _box(manager, x, y, z, width - 2 * radius, depth, height)
    _union(
        manager,
        body,
        _box(manager, x, y, z, width, depth - 2 * radius, height),
        "centro de planta redondeada",
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
                "esquina de planta redondeada",
            )
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

    # Medidas absolutas en mm (diametro_base 450, alto_tronco 190).
    def rmm(mm):
        return mm / 10.0 * rs / 1.125

    def zmm(mm):
        return mm / 10.0 * hs * 18.5 / 19.0

    # z = 0 es Z 200. Semiejes en mm. 1.6.0: el fondo es 0,9 del ancho
    # (vista lateral de la lámina); antes 0,8.
    k = .9

    def ring(z1, z2, outer1, outer2, wall):
        return _ring(
            manager,
            zmm(z1),
            zmm(z2),
            (rmm(outer1), rmm(outer1 * k), rmm(outer2)),
            (rmm(outer1 - wall), rmm((outer1 - wall) * k), rmm(outer2 - wall)),
        )

    # 1.4.0: borde en silla del lienzo y del render.
    # 1.5.0: el bloque inferior de la cintura va FIJO y encajado en la silla,
    # sin holgura: la silla es su mismo perfil (182 mm, radio 36, fondo en
    # Z 354), abierta por delante y por detrás.
    def saddle():
        return _rounded_panel(
            manager, 0, 0, zmm(204), rmm(182), zmm(100), rmm(400), rmm(36)
        )

    specs = []

    # Núcleo hasta Z 320, bajo el bloque de la cintura (que baja a Z 330).
    core = _ellipse(manager, zmm(6), zmm(120), rmm(100), rmm(85))
    _append(specs, core, "01_NUCLEO_NEGRO", BLACK)

    # 1.5.0: tronco casi recto como en el lienzo (247 mm en Z 215, 226 en
    # Z 340). Antes 282-297 mm abajo.
    base_ring = ring(0, 26.7, 127, 125, 8)
    _append(specs, base_ring, "02_ZOCALO_INFERIOR_REDONDEADO", WHITE)

    base_seam = _ring(
        manager,
        zmm(18),
        zmm(24),
        (rmm(126.5), rmm(126.5 * k)),
        (rmm(120), rmm(120 * k)),
    )
    _append(specs, base_seam, "03_JUNTA_NEGRA_BASE", BLACK)

    # 1.6.0: el cono acaba en Z 335; encima va el collar.
    shell_z1, shell_z2 = 20.5, 135
    shell_out1, shell_out2, shell_wall = 123, 114, 7
    shell = ring(shell_z1, shell_z2, shell_out1, shell_out2, shell_wall)
    _append(specs, shell, "04_CARCASA_BLANCA_CONICA_SUAVE", WHITE)

    # 1.6.1: panel frontal del lienzo sobre la torreta del LIDAR: 82 mm de
    # ancho, esquinas R9, hasta Z 310 (desde Z 228, sobre el zócalo). Es una
    # piel de 1,5 mm que sigue la curva del cono, no una placa plana.
    def outer_cone(extra):
        return _ellipse(
            manager, zmm(shell_z1), zmm(shell_z2), rmm(shell_out1 + extra),
            rmm((shell_out1 + extra) * k), rmm(shell_out2 + extra),
        )

    panel = outer_cone(1.5)
    _difference(manager, panel, outer_cone(0), "piel del panel")
    if not manager.booleanOperation(
        panel,
        _rounded_panel(manager, 0, rmm(-105), zmm(69), rmm(82), zmm(82), rmm(60), rmm(9)),
        adsk.fusion.BooleanTypes.IntersectionBooleanType,
    ):
        raise RuntimeError("No se pudo recortar el panel frontal.")
    _append(specs, panel, "09_PANEL_FRONTAL_BLANCO", WHITE)

    # Bloque inferior de la cintura en planta (182 x 146, radio 50). El
    # collar lo envuelve sin holgura y la tapa interior le deja paso.
    def waist_block(z1, z2):
        return _rounded_xy(
            manager, 0, 0, zmm((z1 + z2) / 2), rmm(182), rmm(146),
            zmm(z2 - z1), rmm(50),
        )

    # 1.6.0: collar superior como en el render: planta cuadrada de esquinas
    # redondeadas (212 x 190, radio 85: cabe en el cono de Z 335, que mide
    # 228 x 205) de Z 335 a 390, que abraza el bloque negro por todos los
    # lados con paredes de 11 mm o más. La silla en U se recorta en él
    # (fondo en Z 354).
    collar = _rounded_xy(
        manager, 0, 0, zmm(162.5), rmm(212), rmm(190), zmm(55), rmm(85)
    )
    _difference(manager, collar, waist_block(133, 192), "hueco del collar")
    _difference(manager, collar, saddle(), "silla del collar")
    _append(specs, collar, "05_COLLAR_SUPERIOR_BLANCO", WHITE)

    # Tapa interior (Z 325-335) que cierra el cono hueco bajo el collar.
    # Sigue el vaciado de _ring, que se alarga 1 mm por cada lado.
    def inner_major(zlocal):
        z1, z2 = shell_z1 - 1, shell_z2 + 1
        inner1, inner2 = shell_out1 - shell_wall, shell_out2 - shell_wall
        return inner1 + (inner2 - inner1) * (zlocal - z1) / (z2 - z1)

    cap = _ellipse(
        manager, zmm(125), zmm(135),
        rmm(inner_major(125)), rmm(inner_major(125) * k), rmm(inner_major(135)),
    )
    _difference(manager, cap, waist_block(130, 140), "paso del bloque")
    _append(specs, cap, "08_TAPA_INTERIOR_BLANCA", WHITE)

    # Dos fijaciones discretas en la cara posterior, apoyadas en la carcasa.
    fz = 28.8
    fa = shell_out1 + (shell_out2 - shell_out1) * (fz - shell_z1) / (shell_z2 - shell_z1)
    for index, x in enumerate((-49.5, 49.5), start=1):
        surface_y = fa * k * (1 - (x / fa) ** 2) ** .5
        fastener = _cylinder(
            manager,
            _point(rmm(x), rmm(surface_y - .5), zmm(fz)),
            _point(rmm(x), rmm(surface_y + 2.6), zmm(fz)),
            rmm(2.9),
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

        trunk_height = _parameter_value(design, "alto_tronco", 19.0)
        _GEOMETRY_Z = _parameter_value(design, "alto_base", 20.0)
        diameter = _parameter_value(design, "diametro_base", 45.0)
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
