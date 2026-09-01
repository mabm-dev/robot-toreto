"""Crea las carcasas exteriores de los dos brazos Robot Toreto 95 cm."""

import adsk.core
import adsk.fusion
import math
import traceback


COMPONENTS = ("07_BRAZO_IZQUIERDO", "08_BRAZO_DERECHO")
FEATURE_NAME = "BRAZOS_EXTERIORES_TORETO_95CM"
ALIGNMENT_FEATURE_NAME = "MONTAJE_GLOBAL_95CM"
BODY_PREFIX = "BRAZO95_"
VERSION = "3.0.0"

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
    for index in range(component.features.moveFeatures.count - 1, -1, -1):
        move = component.features.moveFeatures.item(index)
        if move.name == ALIGNMENT_FEATURE_NAME and not move.deleteMe():
            raise RuntimeError("No se pudo retirar la alineación anterior del brazo.")
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
    """Prisma orientado entre dos puntos, incluso fuera del plano frontal."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 0.001:
        raise RuntimeError("Segmento de brazo demasiado corto.")
    ax = (dx / length, dy / length, dz / length)
    axis = _vector(*ax)
    # Proyecta el eje Y sobre el plano normal al segmento. Esto conserva la
    # profundidad frontal de brazos/dedos y también permite que el pulgar
    # salga de verdad del plano de la palma sin crear ejes paralelos.
    dot = ax[1]
    depth_direction = (-dot * ax[0], 1.0 - dot * ax[1], -dot * ax[2])
    depth_length = math.sqrt(sum(value * value for value in depth_direction))
    if depth_length < 0.001:
        dot = ax[0]
        depth_direction = (1.0 - dot * ax[0], -dot * ax[1], -dot * ax[2])
        depth_length = math.sqrt(sum(value * value for value in depth_direction))
    depth_axis = _vector(*(value / depth_length for value in depth_direction))
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


def _elliptical_segment(manager, p1, p2, width1, depth1, width2=None):
    """Carcasa eliptica y troncoconica orientada entre dos puntos.

    Fusion conserva la relacion entre los dos radios durante el cono. Esto
    produce una piel continua y organica, sin la lectura de caja + tapas de
    las versiones anteriores.
    """
    if width2 is None:
        width2 = width1
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 0.001:
        raise RuntimeError("Segmento eliptico demasiado corto.")
    axis = (dx / length, dy / length, dz / length)
    # Proyecta X en el plano normal al eje del segmento. En los brazos esta
    # direccion define la anchura que debe coincidir con el lienzo frontal.
    dot = axis[0]
    major = (1.0 - dot * axis[0], -dot * axis[1], -dot * axis[2])
    major_length = math.sqrt(sum(value * value for value in major))
    if major_length < 0.001:
        dot = axis[1]
        major = (-dot * axis[0], 1.0 - dot * axis[1], -dot * axis[2])
        major_length = math.sqrt(sum(value * value for value in major))
    major_axis = _vector(*(value / major_length for value in major))
    return manager.createEllipticalCylinderOrCone(
        _point(*p1),
        width1 / 2.0,
        depth1 / 2.0,
        _point(*p2),
        width2 / 2.0,
        major_axis,
    )


def _build_v2(manager, side, upper_length, fore_length):
    """Brazo neutral frontal, dimensionado y encadenado desde el hombro."""
    specs = []

    # El eje del hombro queda detras de una cubierta blanca estrecha. La cara
    # circular se ve en el lateral, tal como ocurre en los cuatro lienzos.
    _append(
        specs,
        _cylinder(manager, _point(-4.25, 0, -1.0), _point(4.25, 0, -1.0), 3.65),
        "01_NUCLEO_HOMBRO_EJE_X",
        BLACK,
    )
    shoulder_p1 = _global_point(side, (0.45, 0, -1.0))
    shoulder_p2 = _global_point(side, (0.95, 0, -8.2))
    _append(
        specs,
        _elliptical_segment(manager, shoulder_p1, shoulder_p2, 8.4, 7.4, 7.5),
        "02_CARCASA_HOMBRO_BLANCA",
        WHITE,
    )
    _append(
        specs,
        _cylinder(
            manager,
            _point(side * 3.75, 0, -1.0),
            _point(side * 4.55, 0, -1.0),
            3.05,
        ),
        "03_TAPA_CIRCULAR_HOMBRO",
        DARK,
    )
    _append(
        specs,
        _cylinder(
            manager,
            _point(side * 4.48, 0, -1.0),
            _point(side * 4.72, 0, -1.0),
            1.42,
        ),
        "04_DISCO_CENTRAL_HOMBRO",
        BLACK,
    )

    # Brazo superior afilado: ya no es una capsula rectangular. La cota del
    # codo se calcula siempre desde largo_brazo, sin coordenadas heredadas.
    upper_p1 = _global_point(side, (0.70, 0, -2.0))
    upper_p2 = _global_point(side, (1.30, 0, -upper_length))
    _append(
        specs,
        _elliptical_segment(manager, upper_p1, upper_p2, 7.4, 6.8, 5.8),
        "05_CARCASA_BRAZO_SUPERIOR",
        WHITE,
    )
    _append(
        specs,
        _cylinder(
            manager,
            _point(upper_p2[0] - 3.05, 0, upper_p2[2]),
            _point(upper_p2[0] + 3.05, 0, upper_p2[2]),
            1.72,
        ),
        "06_CODO_EJE_X",
        BLACK,
    )

    # Antebrazo ligeramente abierto hacia fuera en la pose frontal. El
    # lateral de referencia usa otra pose articulada; la geometria es la
    # misma y no se falsea para intentar satisfacer dos poses simultaneas.
    fore_p1 = _global_point(side, (1.25, 0, upper_p2[2] - 1.1))
    fore_p2 = _global_point(side, (2.15, 0, fore_p1[2] - fore_length))
    _append(
        specs,
        _elliptical_segment(manager, fore_p1, fore_p2, 5.8, 5.4, 6.5),
        "07_CARCASA_ANTEBRAZO",
        WHITE,
    )

    # A partir de aqui todas las cotas dependen del extremo real del
    # antebrazo. Este encadenado corrige el desfase que aparecio al pasar a
    # 170 + 150 mm manteniendo las coordenadas antiguas de la mano.
    wrist_top = fore_p2
    wrist_bottom = (fore_p2[0], fore_p2[1], fore_p2[2] - 1.65)
    _append(
        specs,
        _elliptical_segment(manager, wrist_top, wrist_bottom, 5.15, 4.85),
        "08_ANILLO_ROTACION_MUNECA",
        BLACK,
    )

    palm_x = abs(wrist_bottom[0])
    palm_top = (side * palm_x, -0.10, wrist_bottom[2] - 0.15)
    palm_bottom = (side * (palm_x + 0.35), -0.35, palm_top[2] - 7.25)
    palm = _elliptical_segment(manager, palm_top, palm_bottom, 5.3, 4.7, 7.25)
    # Eminencia tenar integrada: forma parte de la palma y recibe el pulgar;
    # no es una placa o un bloque cuadrado independiente.
    thumb_root_x = palm_x - 2.35
    thumb_root_z = palm_top[2] - 3.65
    thumb_bulge = manager.createSphere(
        _point(side * thumb_root_x, -0.55, thumb_root_z), 1.62
    )
    _union(manager, palm, thumb_bulge, "eminencia tenar integrada")
    _append(specs, palm, "09_PALMA_ANATOMICA_CONTINUA", DARK)

    # Cuatro raices embebidas dentro de la mitad distal de la palma. Los
    # dedos no nacen de una arista exterior ni de una placa dorsal.
    finger_offsets = (-2.30, -0.77, 0.77, 2.30)
    finger_lengths = (
        (2.18, 1.95, 1.62),
        (2.48, 2.15, 1.78),
        (2.38, 2.05, 1.70),
        (2.02, 1.78, 1.48),
    )
    root_z = palm_bottom[2] + 2.10
    for index, (offset, lengths) in enumerate(zip(finger_offsets, finger_lengths), 1):
        u0 = palm_x + 0.35 + offset
        l1, l2, l3 = lengths
        p0 = (u0, -2.05, root_z)
        p1 = (u0 - offset * 0.08, -2.35, p0[2] - l1)
        p2 = (u0 - offset * 0.18, -2.58, p1[2] - l2)
        p3 = (u0 - offset * 0.30, -2.70, p2[2] - l3)
        g0, g1, g2, g3 = (_global_point(side, p) for p in (p0, p1, p2, p3))
        _append(specs, _joint_y(manager, side, p0, 1.45, 0.66), f"10_DEDO_{index}_SERVO_BASE", BLACK)
        _append(specs, _elliptical_segment(manager, g0, g1, 1.35, 1.22, 1.20), f"11_DEDO_{index}_FALANGE_1", DARK)
        _append(specs, _joint_y(manager, side, p1, 1.34, 0.59), f"12_DEDO_{index}_BISAGRA_1", BLACK)
        _append(specs, _elliptical_segment(manager, g1, g2, 1.22, 1.12, 1.08), f"13_DEDO_{index}_FALANGE_2", DARK)
        _append(specs, _joint_y(manager, side, p2, 1.24, 0.53), f"14_DEDO_{index}_BISAGRA_2", BLACK)
        _append(specs, _elliptical_segment(manager, g2, g3, 1.10, 1.00, 0.92), f"15_DEDO_{index}_FALANGE_3", DARK)
        tip = (p3[0] - offset * 0.025, p3[1] - 0.05, p3[2] - 0.82)
        _append(specs, _elliptical_segment(manager, g3, _global_point(side, tip), 0.92, 0.86, 0.72), f"16_DEDO_{index}_PUNTA_BLANCA", WHITE)

    # Pulgar de dos falanges, anclado en el centro lateral de la palma y
    # adelantado en Y para ser realmente oponible.
    t0 = (thumb_root_x, -1.65, thumb_root_z)
    t1 = (thumb_root_x - 1.65, -3.25, thumb_root_z - 1.20)
    t2 = (thumb_root_x - 2.65, -4.15, thumb_root_z - 2.85)
    gt0, gt1, gt2 = (_global_point(side, p) for p in (t0, t1, t2))
    _append(specs, _joint_y(manager, side, t0, 1.70, 0.82), "17_PULGAR_SERVO_LATERAL", BLACK)
    _append(specs, _elliptical_segment(manager, gt0, gt1, 1.55, 1.38, 1.30), "18_PULGAR_FALANGE_1", DARK)
    _append(specs, _joint_y(manager, side, t1, 1.48, 0.70), "19_PULGAR_BISAGRA", BLACK)
    _append(specs, _elliptical_segment(manager, gt1, gt2, 1.32, 1.20, 1.05), "20_PULGAR_FALANGE_2", DARK)
    thumb_tip = (t2[0] - 0.55, t2[1] - 0.25, t2[2] - 0.50)
    _append(specs, _elliptical_segment(manager, gt2, _global_point(side, thumb_tip), 1.06, 0.96, 0.80), "21_PULGAR_PUNTA_BLANCA", WHITE)
    return specs


def run(context):
    global _GEOMETRY_OFFSET
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
        base_h = _value(design, "alto_base", 20.0)
        trunk_h = _value(design, "alto_tronco", 19.0)
        waist_h = _value(design, "alto_cintura", 15.0)
        chest_h = _value(design, "alto_pecho", 19.0)
        chest_w = _value(design, "ancho_pecho", 34.0)
        upper_length = _value(design, "largo_brazo", 17.0)
        fore_length = _value(design, "largo_antebrazo", 15.0)
        z_chest = base_h + trunk_h + waist_h
        shoulder_z = z_chest + chest_h * 0.88
        shoulder_x = chest_w / 2.0 + 0.15
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
                for temp_body, name, color in _build_v2(
                    manager, side, upper_length, fore_length
                ):
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
            f"Longitudes maestras aplicadas: brazo {upper_length * 10:.0f} mm + "
            f"antebrazo {fore_length * 10:.0f} mm.\n"
            "Cuatro dedos anatómicos de longitudes distintas y pulgar opuesto.\n"
            "Sin motores, articulaciones internas ni esqueleto.",
            "Robot Toreto 95 cm",
        )
    except Exception:
        ui.messageBox(
            "No se pudieron crear los brazos:\n\n" + traceback.format_exc(),
            "Robot Toreto 95 cm - Error",
        )
    finally:
        _GEOMETRY_OFFSET = (0.0, 0.0, 0.0)


def stop(context):
    pass
