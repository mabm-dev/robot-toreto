"""Crea la base exterior nativa del Robot Toreto de 95 cm."""

import math
import traceback

import adsk.core
import adsk.fusion


COMPONENT_NAME = "01_BASE"
BODY_PREFIX = "BASE95_"
VERSION = "1.5.0"

WHITE = (238, 239, 237)
BLACK = (18, 21, 24)
DARK = (43, 48, 53)
ROLLER = (76, 82, 88)
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


def _has_generated_bodies(component):
    for index in range(component.bRepBodies.count):
        if component.bRepBodies.item(index).name.startswith(BODY_PREFIX):
            return True
    return False


def _generated_version(component):
    attribute = component.attributes.itemByName(
        "RobotToreto", "base_95cm_version"
    )
    return attribute.value if attribute else None


def _replace_previous_generation(component):
    if not _has_generated_bodies(component):
        return False

    feature = None
    for index in range(component.features.baseFeatures.count):
        candidate = component.features.baseFeatures.item(index)
        if candidate.name == "BASE_EXTERIOR_TORETO_95CM":
            feature = candidate
            break

    if not feature:
        raise RuntimeError(
            "Hay cuerpos BASE95_ sin su función generadora. "
            "No se modificaron para proteger posibles cambios manuales."
        )

    if not feature.deleteMe():
        raise RuntimeError("Fusion no pudo retirar la revisión anterior.")
    if _has_generated_bodies(component):
        raise RuntimeError("Quedaron cuerpos de la revisión anterior.")
    return True


def _point(x, y, z):
    return adsk.core.Point3D.create(x, y, z)


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


def _ellipse_y(manager, x, y1, y2, z, major, minor):
    return manager.createEllipticalCylinderOrCone(
        _point(x, y1, z),
        major,
        minor,
        _point(x, y2, z),
        major,
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


def _difference(manager, target, tool, label):
    if not manager.booleanOperation(
        target, tool, adsk.fusion.BooleanTypes.DifferenceBooleanType
    ):
        raise RuntimeError(f"Falló el vaciado: {label}")
    return target


def _union(manager, target, tool, label):
    if not manager.booleanOperation(
        target, tool, adsk.fusion.BooleanTypes.UnionBooleanType
    ):
        raise RuntimeError(f"Falló la unión: {label}")
    return target


def _elliptical_ring(
    manager, z1, z2, outer_major, outer_minor, inner_major, inner_minor
):
    outer = _ellipse(manager, z1, z2, outer_major, outer_minor)
    inner = _ellipse(
        manager, z1 - 0.1, z2 + 0.1, inner_major, inner_minor
    )
    return _difference(manager, outer, inner, "anillo elíptico")


def _cut_wheel_wells(manager, body, wheel_angles, center_radius, z, radius):
    for angle in wheel_angles:
        axis_x = math.cos(angle)
        axis_y = math.sin(angle)
        cutter = _cylinder(
            manager,
            _point(
                axis_x * (center_radius - 5.0),
                axis_y * (center_radius - 5.0),
                z,
            ),
            _point(
                axis_x * (center_radius + 5.0),
                axis_y * (center_radius + 5.0),
                z,
            ),
            radius,
        )
        _difference(manager, body, cutter, "paso de rueda radial")
    return body


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
            corner_x = x + side_x * (width / 2.0 - radius)
            corner_z = z + side_z * (height / 2.0 - radius)
            corner = _cylinder(
                manager,
                _point(corner_x, y - depth / 2.0, corner_z),
                _point(corner_x, y + depth / 2.0, corner_z),
                radius,
            )
            _union(manager, body, corner, "esquina panel redondeado")
    return body


def _rounded_side_panel(manager, x, y, z, width_y, height, depth_x, radius):
    """Panel vertical orientado al lateral: ancho en Y y espesor en X."""
    body = _box(
        manager,
        x,
        y,
        z,
        depth_x,
        width_y - 2.0 * radius,
        height,
    )
    _union(
        manager,
        body,
        _box(
            manager,
            x,
            y,
            z,
            depth_x,
            width_y,
            height - 2.0 * radius,
        ),
        "centro separador lateral",
    )
    for side_y in (-1.0, 1.0):
        for side_z in (-1.0, 1.0):
            corner_y = y + side_y * (width_y / 2.0 - radius)
            corner_z = z + side_z * (height / 2.0 - radius)
            corner = _cylinder(
                manager,
                _point(x - depth_x / 2.0, corner_y, corner_z),
                _point(x + depth_x / 2.0, corner_y, corner_z),
                radius,
            )
            _union(manager, body, corner, "esquina separador lateral")
    return body


def _capsule(manager, center, direction, length, radius):
    direction = direction.copy()
    if not direction.normalize():
        raise RuntimeError("Dirección de rodillo no válida.")
    half = direction.copy()
    half.scaleBy(length / 2.0)

    p1 = center.copy()
    p1.translateBy(_vector(-half.x, -half.y, -half.z))
    p2 = center.copy()
    p2.translateBy(half)

    body = _cylinder(manager, p1, p2, radius)
    _union(manager, body, manager.createSphere(p1, radius), "punta rodillo 1")
    _union(manager, body, manager.createSphere(p2, radius), "punta rodillo 2")
    return body


def _append(specs, body, name, color):
    if not body:
        raise RuntimeError(f"No se pudo construir: {name}")
    specs.append((body, BODY_PREFIX + name, color))


def _make_appearance(app, design, name, rgb):
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
        for library_index in range(app.materialLibraries.count):
            candidate_library = app.materialLibraries.item(library_index)
            generic = candidate_library.appearances.itemById("Prism-129")
            if generic:
                break

    if not generic:
        return None

    appearance = design.appearances.addByCopy(generic, name)
    color_property = appearance.appearanceProperties.itemById("opaque_albedo")
    if color_property:
        color_property.value = adsk.core.Color.create(
            rgb[0], rgb[1], rgb[2], 255
        )
    return appearance


def _build_specs(manager, radial_scale, height_scale):
    rs = radial_scale
    hs = height_scale
    specs = []

    def rz(value):
        return value * hs

    def rr(value):
        return value * rs

    wheel_angles = tuple(
        math.radians(value) for value in (-135.0, -45.0, 45.0, 135.0)
    )
    wheel_center_radius = rr(18.25)
    wheel_z = rz(5.0)
    well_radius = rr(5.05)

    lower_skirt = _elliptical_ring(
        manager,
        rz(1.0),
        rz(10.8),
        rr(20.0),
        rr(15.8),
        rr(19.15),
        rr(14.95),
    )
    _cut_wheel_wells(
        manager,
        lower_skirt,
        wheel_angles,
        wheel_center_radius,
        wheel_z,
        well_radius,
    )
    _append(specs, lower_skirt, "01_FALDON_NEGRO", BLACK)

    sensor_band = _elliptical_ring(
        manager,
        rz(3.0),
        rz(13.2),
        rr(19.15),
        rr(14.95),
        rr(18.55),
        rr(14.35),
    )
    _cut_wheel_wells(
        manager,
        sensor_band,
        wheel_angles,
        wheel_center_radius,
        wheel_z,
        well_radius,
    )
    _append(specs, sensor_band, "02_BANDA_NEGRA", BLACK)

    upper_shell = _elliptical_ring(
        manager,
        rz(12.2),
        rz(17.3),
        rr(20.0),
        rr(16.25),
        rr(19.15),
        rr(15.40),
    )
    _cut_wheel_wells(
        manager,
        upper_shell,
        wheel_angles,
        wheel_center_radius,
        wheel_z,
        well_radius,
    )
    _append(specs, upper_shell, "03_CARCASA_SUPERIOR_BLANCA", WHITE)

    trim = _elliptical_ring(
        manager,
        rz(16.7),
        rz(17.4),
        rr(19.75),
        rr(16.0),
        rr(17.55),
        rr(13.8),
    )
    _append(specs, trim, "04_ANILLO_NEGRO", BLACK)

    deck = _ellipse(
        manager,
        rz(17.35),
        rz(20.9),
        rr(19.55),
        rr(15.8),
        rr(17.55),
    )
    _append(specs, deck, "05_CUBIERTA_TRONCOCONICA", WHITE)

    deck_trim = _elliptical_ring(
        manager,
        rz(20.25),
        rz(21.05),
        rr(17.15),
        rr(13.75),
        rr(13.1),
        rr(9.9),
    )
    _append(specs, deck_trim, "06_JUNTA_SUPERIOR_NEGRA", BLACK)

    top_lid = _ellipse(
        manager, rz(20.9), rz(22.5), rr(16.2), rr(12.9)
    )
    _append(specs, top_lid, "07_TAPA_SUPERIOR_BLANCA", WHITE)

    for side_index, side in enumerate((-1.0, 1.0), start=1):
        side_cover = _rounded_side_panel(
            manager,
            side * rr(19.45),
            0,
            rz(7.9),
            rr(9.4),
            rz(8.2),
            rr(1.05),
            rr(2.05),
        )
        _append(
            specs,
            side_cover,
            f"08_SEPARACION_LATERAL_{side_index:02d}",
            WHITE,
        )

    fascia = _rounded_panel(
        manager,
        0,
        -rr(15.65),
        rz(9.0),
        rr(16.4),
        rz(4.0),
        rr(1.3),
        rr(1.15),
    )
    _append(specs, fascia, "09_MARCO_SENSOR_FRONTAL", BLACK)

    sensor_insert = _rounded_panel(
        manager,
        0,
        -rr(16.42),
        rz(9.0),
        rr(13.6),
        rz(2.1),
        rr(0.45),
        rr(0.62),
    )
    _append(specs, sensor_insert, "10_INSERTO_SENSOR_FRONTAL", DARK)

    lower_fascia = _rounded_panel(
        manager,
        0,
        -rr(15.5),
        rz(4.1),
        rr(14.8),
        rz(2.4),
        rr(1.15),
        rr(0.72),
    )
    _append(specs, lower_fascia, "11_MARCO_INFERIOR", BLACK)

    for sensor_index, (x, radius, color) in enumerate(
        [(-5.8, 0.8, DARK), (0.0, 0.55, CYAN), (5.8, 0.8, DARK)],
        start=1,
    ):
        lens = _cylinder(
            manager,
            _point(rr(x), -rr(17.3), rz(9.0)),
            _point(rr(x), -rr(17.75), rz(9.0)),
            rr(radius),
        )
        _append(specs, lens, f"12_SENSOR_FRONTAL_{sensor_index:02d}", color)

    wheel_labels = (
        "DELANTERA_IZQ",
        "DELANTERA_DER",
        "TRASERA_DER",
        "TRASERA_IZQ",
    )

    for wheel_number, (wheel_angle, label) in enumerate(
        zip(wheel_angles, wheel_labels), start=1
    ):
        axis_x = math.cos(wheel_angle)
        axis_y = math.sin(wheel_angle)
        tangent_x = -axis_y
        tangent_y = axis_x
        cx = axis_x * wheel_center_radius
        cy = axis_y * wheel_center_radius
        half_width = rr(2.2)
        tire = _cylinder(
            manager,
            _point(
                cx - axis_x * half_width,
                cy - axis_y * half_width,
                wheel_z,
            ),
            _point(
                cx + axis_x * half_width,
                cy + axis_y * half_width,
                wheel_z,
            ),
            rr(4.35),
        )
        _append(specs, tire, f"20_RUEDA_{wheel_number}_{label}", BLACK)

        hub = _cylinder(
            manager,
            _point(
                cx + axis_x * rr(1.75),
                cy + axis_y * rr(1.75),
                wheel_z,
            ),
            _point(
                cx + axis_x * rr(2.55),
                cy + axis_y * rr(2.55),
                wheel_z,
            ),
            rr(1.95),
        )
        _append(specs, hub, f"21_BUJE_{wheel_number}", DARK)

        cap = _cylinder(
            manager,
            _point(
                cx + axis_x * rr(2.5),
                cy + axis_y * rr(2.5),
                wheel_z,
            ),
            _point(
                cx + axis_x * rr(2.78),
                cy + axis_y * rr(2.78),
                wheel_z,
            ),
            rr(0.48),
        )
        _append(specs, cap, f"22_LUZ_BUJE_{wheel_number}", CYAN)

        roller_count = 10
        roller_ring = rr(3.88)
        for roller_index in range(roller_count):
            roller_angle = 2.0 * math.pi * roller_index / roller_count
            ring_offset = roller_ring * math.cos(roller_angle)
            center = _point(
                cx + tangent_x * ring_offset,
                cy + tangent_y * ring_offset,
                wheel_z + roller_ring * math.sin(roller_angle),
            )
            handedness = 1.0 if wheel_number in (1, 3) else -1.0
            direction = _vector(
                tangent_x * (-0.72 * math.sin(roller_angle))
                + axis_x * handedness,
                tangent_y * (-0.72 * math.sin(roller_angle))
                + axis_y * handedness,
                0.72 * math.cos(roller_angle),
            )
            roller = _capsule(
                manager,
                center,
                direction,
                rr(2.35),
                rr(0.84),
            )
            _append(
                specs,
                roller,
                f"23_RODILLO_{wheel_number}_{roller_index + 1:02d}",
                ROLLER,
            )

    pod_x = rr(8.8)
    pod_y = -rr(8.7)
    pod_base = _cylinder(
        manager,
        _point(pod_x, pod_y, rz(22.35)),
        _point(pod_x, pod_y, rz(23.25)),
        rr(4.15),
    )
    _append(specs, pod_base, "30_BASE_TORRETA_BLANCA", WHITE)

    pod = _cylinder(
        manager,
        _point(pod_x, pod_y, rz(22.95)),
        _point(pod_x, pod_y, rz(25.75)),
        rr(3.05),
    )
    _append(specs, pod, "31_TORRETA_NEGRA", BLACK)

    pod_lens = _cylinder(
        manager,
        _point(pod_x, pod_y - rr(3.0), rz(24.35)),
        _point(pod_x, pod_y - rr(3.35), rz(24.35)),
        rr(0.42),
    )
    _append(specs, pod_lens, "32_LENTE_TORRETA", CYAN)

    return specs


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

        occurrence = _find_occurrence(design.rootComponent, COMPONENT_NAME)
        if not occurrence:
            raise RuntimeError(
                "Falta 01_BASE. Ejecuta primero Toreto_Componentes_95cm."
            )

        component = occurrence.component
        current_version = _generated_version(component)
        if current_version == VERSION and _has_generated_bodies(component):
            ui.messageBox(
                "La base exterior revisada ya existe en 01_BASE.\n"
                "No se ha duplicado ningún cuerpo.",
                "Robot Toreto 95 cm",
            )
            return

        replaced = _replace_previous_generation(component)

        diameter = _parameter_value(design, "diametro_base", 40.0)
        height = _parameter_value(design, "alto_base", 22.5)
        radial_scale = diameter / 40.0
        height_scale = height / 22.5

        manager = adsk.fusion.TemporaryBRepManager.get()
        specs = _build_specs(manager, radial_scale, height_scale)

        appearances = {
            WHITE: _make_appearance(app, design, "TORETO Blanco satinado", WHITE),
            BLACK: _make_appearance(app, design, "TORETO Negro profundo", BLACK),
            DARK: _make_appearance(app, design, "TORETO Grafito", DARK),
            ROLLER: _make_appearance(
                app, design, "TORETO Rodillo mecanum", ROLLER
            ),
            CYAN: _make_appearance(app, design, "TORETO Cian", CYAN),
        }

        base_feature = component.features.baseFeatures.add()
        if not base_feature:
            raise RuntimeError("Fusion no pudo crear la función base.")
        base_feature.name = "BASE_EXTERIOR_TORETO_95CM"

        persisted = []
        base_feature.startEdit()
        try:
            for temp_body, name, color in specs:
                body = component.bRepBodies.add(temp_body, base_feature)
                if not body:
                    raise RuntimeError(f"Fusion no pudo añadir {name}.")
                body.name = name
                appearance = appearances.get(color)
                if appearance:
                    body.appearance = appearance
                body.isLightBulbOn = True
                persisted.append(body)
        finally:
            base_feature.finishEdit()

        component.attributes.add("RobotToreto", "base_95cm_version", VERSION)
        design.rootComponent.attributes.add(
            "RobotToreto", "ultimo_modulo", "01_BASE"
        )
        app.activeViewport.fit()

        ui.messageBox(
            (
                "Base exterior actualizada correctamente.\n\n"
                if replaced
                else "Base exterior creada correctamente.\n\n"
            )
            +
            f"Cuerpos exteriores: {len(persisted)}\n"
            f"Diámetro maestro: {diameter * 10:.0f} mm\n"
            f"Altura maestra: {height * 10:.0f} mm\n\n"
            "No se han creado motores, ejes, chasis ni electrónica.",
            "Robot Toreto 95 cm",
        )

    except Exception:
        ui.messageBox(
            "No se pudo crear la base exterior:\n\n" + traceback.format_exc(),
            "Robot Toreto 95 cm - Error",
        )


def stop(context):
    pass
