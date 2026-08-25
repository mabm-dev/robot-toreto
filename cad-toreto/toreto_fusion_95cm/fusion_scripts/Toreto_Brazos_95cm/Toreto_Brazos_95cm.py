"""Crea las carcasas exteriores de los dos brazos Robot Toreto 95 cm."""

import adsk.core
import adsk.fusion
import math
import traceback


COMPONENTS = ("07_BRAZO_IZQUIERDO", "08_BRAZO_DERECHO")
FEATURE_NAME = "BRAZOS_EXTERIORES_TORETO_95CM"
BODY_PREFIX = "BRAZO95_"
VERSION = "2.2.0"

# Desplazamiento de emergencia para Fusion: algunas versiones dejan una
# ocurrencia recién creada en (0,0,0) aunque transform2 se haya escrito. El
# módulo calcula la diferencia y hornea la posición en sus cuerpos si ocurre.
_GEOMETRY_OFFSET = (0.0, 0.0, 0.0)

WHITE = (238, 239, 237)
BLACK = (18, 21, 24)
DARK = (58, 63, 68)
CYAN = (0, 174, 235)


def _point(x, y, z):
    return adsk.core.Point3D.create(
        x + _GEOMETRY_OFFSET[0],
        y + _GEOMETRY_OFFSET[1],
        z + _GEOMETRY_OFFSET[2],
    )


def _vector(x, y, z):
    return adsk.core.Vector3D.create(x, y, z)


def _find_occurrence(root, name):
    for index in range(root.occurrences.count):
        occurrence = root.occurrences.item(index)
        if occurrence.component.name == name or occurrence.name == name:
            return occurrence
    return None


def _box(manager, x, y, z, sx, sy, sz):
    bounds = adsk.core.OrientedBoundingBox3D.create(
        _point(x, y, z), _vector(1, 0, 0), _vector(0, 1, 0), sx, sy, sz
    )
    return manager.createBox(bounds)


def _cylinder(manager, p1, p2, radius, radius2=None):
    if radius2 is None:
        radius2 = radius
    return manager.createCylinderOrCone(p1, radius, p2, radius2)


def _union(manager, target, tool, label):
    if not manager.booleanOperation(
        target, tool, adsk.fusion.BooleanTypes.UnionBooleanType
    ):
        raise RuntimeError(f"Falló la unión: {label}")


def _rounded_panel(manager, x, y, z, width, height, depth, radius):
    """Panel redondeado en el plano XZ, con profundidad en Y."""
    radius = min(radius, width * 0.48, height * 0.48)
    body = _box(manager, x, y, z, width - 2 * radius, depth, height)
    _union(
        manager,
        body,
        _box(manager, x, y, z, width, depth, height - 2 * radius),
        "centro panel",
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
                "esquina panel",
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
    attr = component.attributes.itemByName("RobotToreto", "brazos_95cm_version")
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
        raise RuntimeError("No se pudieron retirar los brazos anteriores.")
    return True


def _segment(manager, specs, side, name, p1, p2, radius, color):
    p1 = (side * p1[0], p1[1], p1[2])
    p2 = (side * p2[0], p2[1], p2[2])
    _append(specs, _cylinder(manager, _point(*p1), _point(*p2), radius), name, color)


def _oriented_box(manager, p1, p2, width, depth):
    """Prisma orientado entre dos puntos, con profundidad frontal Y."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 0.001:
        raise RuntimeError("Segmento de brazo demasiado corto.")
    axis = _vector(dx / length, dy / length, dz / length)
    depth_axis = _vector(0, 1, 0)
    center = _point(
        (p1[0] + p2[0]) / 2,
        (p1[1] + p2[1]) / 2,
        (p1[2] + p2[2]) / 2,
    )
    return adsk.core.OrientedBoundingBox3D.create(
        center, axis, depth_axis, length, depth, width
    )


def _capsule(manager, p1, p2, width, depth):
    """Cápsula rectangular con extremos redondeados para brazo y antebrazo."""
    bounds = _oriented_box(manager, p1, p2, width, depth)
    body = manager.createBox(bounds)
    cap_radius = min(width, depth) / 2.0
    for point in (p1, p2):
        _union(
            manager,
            body,
            _cylinder(
                manager,
                _point(point[0], point[1] - depth / 2, point[2]),
                _point(point[0], point[1] + depth / 2, point[2]),
                cap_radius,
            ),
            "extremo redondeado",
        )
    return body


def _global_point(side, point):
    return (side * point[0], point[1], point[2])


def _value(design, name, fallback):
    parameter = design.userParameters.itemByName(name)
    return parameter.value if parameter else fallback


def _set_occurrence_identity(occurrence, design):
    """Deja la ocurrencia en el origen; la cota se hornea en los cuerpos."""
    transform = adsk.core.Matrix3D.create()
    try:
        occurrence.isGroundToParent = False
    except Exception:
        pass
    try:
        occurrence.transform2 = transform
    except Exception:
        try:
            occurrence.transform = transform
        except Exception:
            pass
    try:
        if design.snapshots.hasPendingTransforms:
            design.snapshots.add()
    except Exception:
        pass
    return occurrence.transform2.translation


def _build(manager, side):
    """Construye un brazo local; side=-1 izquierda, +1 derecha."""
    specs = []
    # Hombro: la carcasa y el disco comparten el mismo eje, sin desplazamiento.
    _append(
        specs,
        _rounded_panel(manager, 0, 0, -3.0, 8.8, 14.2, 7.8, 4.2),
        "01_CARCASA_HOMBRO",
        WHITE,
    )
    _append(
        specs,
        _cylinder(
            manager,
            _point(side * 2.0, -4.4, -1.0),
            _point(side * 2.0, 4.4, -1.0),
            2.70,
        ),
        "02_DISCO_HOMBRO_EXTERIOR",
        BLACK,
    )
    _append(
        specs,
        _cylinder(
            manager,
            _point(-side * 3.75, -1.2, -1.0),
            _point(-side * 3.75, 3.2, -1.0),
            2.45,
        ),
        "03_ANILLO_HOMBRO_INTERIOR",
        BLACK,
    )

    # Brazo superior: cápsula inclinada, más ancha en el hombro que en el codo.
    upper_p1 = _global_point(side, (0.7, 0, -8.0))
    upper_p2 = _global_point(side, (2.8, 0, -19.0))
    _append(
        specs,
        _capsule(manager, upper_p1, upper_p2, 6.7, 6.8),
        "04_CARCASA_BRAZO_SUPERIOR",
        WHITE,
    )
    _append(
        specs,
        _cylinder(
            manager,
            _point(upper_p2[0] + side * 0.75, -3.7, upper_p2[2]),
            _point(upper_p2[0] + side * 0.75, 3.7, upper_p2[2]),
            1.70,
        ),
        "05_ARTICULACION_CODO_EXTERIOR",
        BLACK,
    )
    _append(
        specs,
        _cylinder(
            manager,
            _point(upper_p2[0] + side * 0.75, -3.9, upper_p2[2]),
            _point(upper_p2[0] + side * 0.75, -3.35, upper_p2[2]),
            1.05,
        ),
        "06_TAPA_CODO",
        DARK,
    )

    # Antebrazo: otra cápsula inclinada, con la unión negra visible.
    fore_p1 = _global_point(side, (2.8, 0, -20.2))
    fore_p2 = _global_point(side, (5.2, 0, -34.4))
    _append(
        specs,
        _capsule(manager, fore_p1, fore_p2, 5.8, 6.1),
        "07_CARCASA_ANTEBRAZO",
        WHITE,
    )
    _append(
        specs,
        _cylinder(
            manager,
            _point(fore_p2[0], -3.6, fore_p2[2]),
            _point(fore_p2[0], 3.6, fore_p2[2]),
            1.60,
        ),
        "08_ANILLO_MUNECA",
        BLACK,
    )
    _append(
        specs,
        _rounded_panel(
            manager,
            side * 5.2,
            -0.15,
            -36.4,
            6.0,
            4.0,
            6.4,
            1.8,
        ),
        "09_CUFF_MUNECA_BLANCO",
        WHITE,
    )

    # Palma compacta; los dedos comienzan en una fila de nudillos separada.
    _append(
        specs,
        _rounded_panel(manager, side * 5.7, 0, -39.4, 6.8, 6.4, 5.4, 1.55),
        "10_CARCASA_PALMA",
        BLACK,
    )
    _append(
        specs,
        _rounded_panel(manager, side * 5.7, -2.85, -39.4, 5.6, 5.2, 0.7, 1.2),
        "11_NUCLEO_PALMA_GRAFITO",
        DARK,
    )

    # Cuatro dedos realmente independientes, con tres falanges y dos nudillos.
    # La convergencia total equivale visualmente a unos 35 grados hacia dentro.
    inward_tan = math.tan(math.radians(35.0))
    finger_offsets = (-2.35, -0.78, 0.78, 2.35)
    for finger_index, offset in enumerate(finger_offsets, 1):
        u0 = 5.7 + offset
        z0 = -42.55
        du1 = -offset * inward_tan * 2.25 / 9.0
        du2 = -offset * inward_tan * 2.15 / 9.0
        du3 = -offset * inward_tan * 1.85 / 9.0
        # Y negativo es la cara frontal; los dedos se adelantan a la palma
        # para que no queden ocultos en la vista frontal.
        p0 = (u0, -3.75, z0)
        p1 = (u0 + du1, -3.75, z0 - 2.25)
        p2 = (u0 + du1 + du2, -3.75, z0 - 4.40)
        p3 = (u0 + du1 + du2 + du3, -3.75, z0 - 6.25)
        _append(
            specs,
            _cylinder(
                manager,
                _point(side * p0[0], -4.1, p0[2]),
                _point(side * p0[0], -3.4, p0[2]),
                0.72,
            ),
            f"12_DEDO_{finger_index}_NUDILLO_BASE",
            BLACK,
        )
        _segment(manager, specs, side, f"13_DEDO_{finger_index}_FALANGE_1", p0, p1, 0.62, DARK)
        _segment(manager, specs, side, f"14_DEDO_{finger_index}_FALANGE_2", p1, p2, 0.55, DARK)
        _segment(manager, specs, side, f"15_DEDO_{finger_index}_FALANGE_3", p2, p3, 0.48, DARK)
        for joint_index, joint in enumerate((p1, p2), 1):
            _append(
                specs,
                _cylinder(
                    manager,
                    _point(side * joint[0], -4.1, joint[2]),
                    _point(side * joint[0], -3.4, joint[2]),
                    0.67 if joint_index == 1 else 0.59,
                ),
                f"16_DEDO_{finger_index}_ARTICULACION_{joint_index}",
                BLACK,
            )
        _segment(
            manager,
            specs,
            side,
            f"17_DEDO_{finger_index}_PUNTA",
            p3,
            (p3[0] - offset * 0.04, -3.75, p3[2] - 0.75),
            0.43,
            WHITE,
        )

    # Pulgar lateral con base, dos falanges y punta diferenciada.
    thumb0 = (8.85, -3.75, -39.5)
    thumb1 = (10.25, -3.75, -41.5)
    thumb2 = (11.25, -3.75, -43.55)
    _segment(manager, specs, side, "18_PULGAR_FALANGE_1", thumb0, thumb1, 0.72, DARK)
    _segment(manager, specs, side, "19_PULGAR_FALANGE_2", thumb1, thumb2, 0.61, DARK)
    _append(
        specs,
        _cylinder(
            manager, _point(side * thumb1[0], -4.1, thumb1[2]),
            _point(side * thumb1[0], -3.4, thumb1[2]), 0.78,
        ),
        "20_PULGAR_ARTICULACION",
        BLACK,
    )
    _segment(
        manager,
        specs,
        side,
        "21_PULGAR_PUNTA",
        thumb2,
        (thumb2[0] + 0.15, -3.75, thumb2[2] - 0.75),
        0.48,
        WHITE,
    )

    # Dos pequeños indicadores de diseño, no funcionales.
    _append(
        specs,
        _cylinder(
            manager,
            _point(side * 5.7, -3.45, -38.0),
            _point(side * 5.7, -3.05, -38.0),
            0.42,
        ),
        "22_INDICADOR_CIAN",
        CYAN,
    )
    return specs


def _rounded_side_panel(manager, x, y, z, width_y, height_z, depth_x, radius):
    """Carcasa redondeada en YZ; su cara principal se mira desde el lateral."""
    radius = min(radius, width_y * 0.48, height_z * 0.48)
    body = _box(manager, x, y, z, depth_x, width_y - 2 * radius, height_z)
    _union(
        manager,
        body,
        _box(manager, x, y, z, depth_x, width_y, height_z - 2 * radius),
        "centro carcasa lateral",
    )
    for sy in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            cy = y + sy * (width_y / 2 - radius)
            cz = z + sz * (height_z / 2 - radius)
            _union(
                manager,
                body,
                _cylinder(
                    manager,
                    _point(x - depth_x / 2, cy, cz),
                    _point(x + depth_x / 2, cy, cz),
                    radius,
                ),
                "esquina carcasa lateral",
            )
    return body


def _finger_box(manager, side, p1, p2, width, depth):
    g1 = (side * p1[0], p1[1], p1[2])
    g2 = (side * p2[0], p2[1], p2[2])
    return manager.createBox(_oriented_box(manager, g1, g2, width, depth))


def _joint_y(manager, side, point, depth, radius):
    x = side * point[0]
    return _cylinder(
        manager,
        _point(x, point[1] - depth / 2, point[2]),
        _point(x, point[1] + depth / 2, point[2]),
        radius,
    )


def _build_v2(manager, side):
    """Brazo exterior basado en las vistas frontal/lateral definitivas."""
    specs = []

    # Hombro: el eje es X. La gran cara circular se ve de perfil, no de frente.
    _append(
        specs,
        _cylinder(manager, _point(-4.0, 0, -1.0), _point(4.0, 0, -1.0), 3.55),
        "01_NUCLEO_HOMBRO_EJE_X",
        BLACK,
    )
    upper_p1 = _global_point(side, (.65, 0, -1.5))
    upper_p2 = _global_point(side, (1.25, 0, -13.0))
    _append(
        specs,
        _capsule(manager, upper_p1, upper_p2, 5.6, 7.2),
        "02_CARCASA_BRAZO_SUPERIOR",
        WHITE,
    )
    _append(
        specs,
        _cylinder(
            manager,
            _point(side * 3.65, 0, -1.0),
            _point(side * 4.35, 0, -1.0),
            3.0,
        ),
        "03_TAPA_CIRCULAR_HOMBRO",
        DARK,
    )
    _append(
        specs,
        _cylinder(
            manager,
            _point(side * 4.30, 0, -1.0),
            _point(side * 4.55, 0, -1.0),
            1.45,
        ),
        "04_DISCO_CENTRAL_HOMBRO",
        BLACK,
    )

    # El codo termina la misma carcasa continua; no se añade un segundo
    # volumen superpuesto como en las versiones anteriores.
    _append(
        specs,
        _cylinder(
            manager,
            _point(upper_p2[0] - 3.0, 0, upper_p2[2]),
            _point(upper_p2[0] + 3.0, 0, upper_p2[2]),
            1.65,
        ),
        "05_CODO_EJE_X",
        BLACK,
    )
    _append(
        specs,
        _cylinder(
            manager,
            _point(upper_p2[0] + side * 2.65, 0, upper_p2[2]),
            _point(upper_p2[0] + side * 3.15, 0, upper_p2[2]),
            0.78,
        ),
        "06_TAPA_CODO_LATERAL",
        DARK,
    )

    # Antebrazo inclinado hacia el cuerpo: en la vista frontal las muñecas
    # quedan más juntas que los codos, como en las referencias definitivas.
    fore_p1 = _global_point(side, (1.35, 0, -14.4))
    fore_p2 = _global_point(side, (0.80, 0, -25.1))
    _append(
        specs,
        _capsule(manager, fore_p1, fore_p2, 5.2, 6.4),
        "07_CARCASA_ANTEBRAZO",
        WHITE,
    )
    # Anillo de muñeca alrededor del eje longitudinal del antebrazo.
    _append(
        specs,
        _cylinder(
            manager,
            _point(side * 0.80, 0, -25.3),
            _point(side * 0.80, 0, -27.0),
            2.25,
        ),
        "08_ANILLO_ROTACION_MUNECA",
        BLACK,
    )

    # Palma negra compacta con placa blanca posterior de cuatro fijaciones.
    palm_x = 0.80
    _append(
        specs,
        _rounded_panel(manager, side * palm_x, 0, -29.7, 7.6, 6.6, 5.2, 1.45),
        "09_NUCLEO_PALMA_NEGRO",
        BLACK,
    )
    _append(
        specs,
        _rounded_panel(manager, side * palm_x, -2.82, -29.7, 6.8, 5.8, 0.56, 1.25),
        "10_CUBIERTA_FRONTAL_PALMA",
        WHITE,
    )
    _append(
        specs,
        _rounded_panel(manager, side * palm_x, 2.82, -29.7, 6.25, 5.35, 0.58, 1.10),
        "11_PLACA_POSTERIOR_PALMA",
        WHITE,
    )
    for sx in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            _append(
                specs,
                _cylinder(
                    manager,
                    _point(side * (palm_x + sx * 2.25), 3.08, -29.7 + sz * 1.75),
                    _point(side * (palm_x + sx * 2.25), 3.30, -29.7 + sz * 1.75),
                    0.22,
                ),
                f"12_TORNILLO_PALMA_{int(sx)}_{int(sz)}",
                BLACK,
            )

    # Cuatro dedos con tres falanges prismáticas, bisagras negras y punta blanca.
    finger_offsets = (-2.55, -0.85, 0.85, 2.55)
    for index, offset in enumerate(finger_offsets, 1):
        u0 = palm_x + offset
        p0 = (u0, -3.02, -32.55)
        p1 = (u0 - offset * 0.075, -3.02, -34.35)
        p2 = (u0 - offset * 0.16, -3.02, -36.05)
        p3 = (u0 - offset * 0.25, -3.02, -37.55)
        _append(specs, _joint_y(manager, side, p0, 1.55, 0.69), f"13_DEDO_{index}_NUDILLO", BLACK)
        _append(specs, _finger_box(manager, side, p0, p1, 1.38, 1.55), f"14_DEDO_{index}_FALANGE_1", DARK)
        _append(specs, _joint_y(manager, side, p1, 1.46, 0.64), f"15_DEDO_{index}_BISAGRA_1", BLACK)
        _append(specs, _finger_box(manager, side, p1, p2, 1.28, 1.47), f"16_DEDO_{index}_FALANGE_2", DARK)
        _append(specs, _joint_y(manager, side, p2, 1.38, 0.59), f"17_DEDO_{index}_BISAGRA_2", BLACK)
        _append(specs, _finger_box(manager, side, p2, p3, 1.15, 1.38), f"18_DEDO_{index}_FALANGE_3", DARK)
        _segment(
            manager,
            specs,
            side,
            f"19_DEDO_{index}_PUNTA_BLANCA",
            p3,
            (p3[0] - offset * 0.025, p3[1], p3[2] - 0.78),
            0.57,
            WHITE,
        )

    # Pulgar lateral, separado de los cuatro dedos y con dos falanges.
    t0 = (palm_x - 3.35, -2.95, -29.55)
    t1 = (palm_x - 4.95, -2.95, -30.85)
    t2 = (palm_x - 6.20, -2.95, -32.35)
    _append(specs, _joint_y(manager, side, t0, 1.7, 0.88), "20_PULGAR_NUDILLO", BLACK)
    _append(specs, _finger_box(manager, side, t0, t1, 1.55, 1.72), "21_PULGAR_FALANGE_1", DARK)
    _append(specs, _joint_y(manager, side, t1, 1.60, 0.76), "22_PULGAR_BISAGRA", BLACK)
    _append(specs, _finger_box(manager, side, t1, t2, 1.35, 1.62), "23_PULGAR_FALANGE_2", DARK)
    _segment(
        manager,
        specs,
        side,
        "24_PULGAR_PUNTA_BLANCA",
        t2,
        (t2[0] - 0.48, t2[1], t2[2] - 0.48),
        0.61,
        WHITE,
    )
    return specs


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Abre 00_Toreto_Ensamblaje_95cm antes de ejecutar.")
            return
        root = design.rootComponent
        occurrences = []
        for name in COMPONENTS:
            occurrence = _find_occurrence(root, name)
            if not occurrence:
                raise RuntimeError(f"Falta {name}. Ejecuta Toreto_Componentes_95cm primero.")
            occurrences.append(occurrence)
        if all(_version(occurrence.component) == VERSION and _has_bodies(occurrence.component) for occurrence in occurrences):
            ui.messageBox("Los brazos exteriores ya existen; no se duplicaron.")
            return
        # Fusion muestra estas ocurrencias en el origen aunque transform2
        # informe otra cota. Para evitar el fallo, los cuerpos se construyen
        # directamente en coordenadas globales y la ocurrencia queda neutra.
        base_h = _value(design, "alto_base", 22.5)
        trunk_h = _value(design, "alto_tronco", 18.5)
        waist_h = _value(design, "alto_cintura", 10.0)
        chest_h = _value(design, "alto_pecho", 22.8)
        chest_w = _value(design, "ancho_pecho", 34.0)
        z_chest = base_h + trunk_h + waist_h
        shoulder_z = z_chest + chest_h * 0.72
        shoulder_x = chest_w / 2.0 + 2.3
        expected_positions = ((-shoulder_x, 0.0, shoulder_z), (shoulder_x, 0.0, shoulder_z))
        actual_positions = []
        for occurrence in occurrences:
            actual_positions.append(_set_occurrence_identity(occurrence, design))

        manager = adsk.fusion.TemporaryBRepManager.get()
        appearances = {
            WHITE: _appearance(app, design, "TORETO Blanco satinado", WHITE),
            BLACK: _appearance(app, design, "TORETO Negro profundo", BLACK),
            DARK: _appearance(app, design, "TORETO Grafito", DARK),
            CYAN: _appearance(app, design, "TORETO Cian", CYAN),
        }
        total = 0
        replaced = False
        baked_offsets = 0
        for occurrence, side, expected, actual in zip(
            occurrences, (-1, 1), expected_positions, actual_positions
        ):
            component = occurrence.component
            if _version(component) == VERSION and _has_bodies(component):
                continue
            replaced = _replace_old(component) or replaced
            global _GEOMETRY_OFFSET
            tolerance = 0.001
            _GEOMETRY_OFFSET = (
                expected[0],
                expected[1],
                expected[2],
            )
            baked_offsets += 1
            feature = component.features.baseFeatures.add()
            if not feature:
                raise RuntimeError(f"Fusion no pudo crear la función base de {component.name}.")
            feature.name = FEATURE_NAME
            feature.startEdit()
            try:
                for temp_body, name, color in _build_v2(manager, side):
                    body = component.bRepBodies.add(temp_body, feature)
                    if not body:
                        raise RuntimeError(f"Fusion no pudo añadir {name}.")
                    body.name = name
                    if appearances.get(color):
                        body.appearance = appearances[color]
                    body.isLightBulbOn = True
                    total += 1
            finally:
                feature.finishEdit()
            component.attributes.add("RobotToreto", "brazos_95cm_version", VERSION)
        _GEOMETRY_OFFSET = (0.0, 0.0, 0.0)
        root.attributes.add("RobotToreto", "ultimo_modulo", "07_08_BRAZOS")
        app.activeViewport.fit()
        ui.messageBox(
            ("Brazos exteriores actualizados." if replaced else "Brazos exteriores creados.")
            + f"\n\nCuerpos generados: {total}\n"
            f"Posiciones globales integradas en cuerpos: {baked_offsets}\n"
            "Hombros, brazo superior, antebrazo, muñecas y manos segmentadas.\n"
            "Cuatro dedos orientados 35° hacia dentro y pulgar lateral.\n"
            "Sin motores, articulaciones internas ni esqueleto.",
            "Robot Toreto 95 cm",
        )
    except Exception:
        ui.messageBox(
            "No se pudieron crear los brazos:\n\n" + traceback.format_exc(),
            "Robot Toreto 95 cm - Error",
        )


def stop(context):
    pass
