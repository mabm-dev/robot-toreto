"""Crea la base exterior nativa del Robot Toreto de 95 cm."""

import math
import traceback

import adsk.core
import adsk.fusion


COMPONENT_NAME = "01_BASE"
BODY_PREFIX = "BASE95_"
# 2.0.0 (29-09-2026): planta redonda, disco + cuerpo con arcos + pilares,
# ruedas mecanum con aspecto del render, eje y soporte visibles.
# 2.0.1 (29-09-2026): chasis recortado al disco, placas R 57, pasadores en
# los rodillos y carcasa de motor redonda.
VERSION = "2.0.1"

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
        side = -1.0 if math.cos(angle) < 0 else 1.0
        cx = side * center_radius
        cy = (-1.0 if math.sin(angle) < 0 else 1.0) * 14.8
        cutter = _cylinder(
            manager,
            _point(
                cx - 5.0,
                cy,
                z,
            ),
            _point(
                cx + 5.0,
                cy,
                z,
            ),
            radius,
        )
        _difference(manager, body, cutter, "paso de rueda paralelo a X")
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


def _intersect(manager, target, tool, label):
    if not manager.booleanOperation(
        target, tool, adsk.fusion.BooleanTypes.IntersectionBooleanType
    ):
        raise RuntimeError(f"Falló la intersección: {label}")
    return target


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


def _build_specs(manager, radial_scale, height_scale):
    """Base 2.0.0: lámina de 4 vistas (medidas) y render 3D (forma).

    Planta REDONDA de 450 mm (la lámina mide lo mismo de frente y de lado;
    antes era una elipse de 450 x 356). Disco blanco de Z 160 a 200 con un
    aro negro en la tapa, cuerpo negro con arcos sobre las ruedas, chasis
    negro delante y detrás, pilares blancos entre las ruedas, ruedas
    mecanum con aspecto del render, eje y soporte de motor visibles.
    """
    specs = []

    # Medidas en mm (diametro_base 450, alto_base 200).
    def rr(mm):
        return mm / 10.0 * radial_scale / 1.125

    def rz(mm):
        return mm / 10.0 * height_scale * 22.5 / 20.0

    radius = 225.0

    # --- Ruedas: centros de la lámina (vía 390, batalla 296). -------------
    wheel_x, wheel_y = 195.0, 148.0
    # 66 mm de ancho (lienzo ~70): placas en ±29-33, rodillos hasta ±26.
    roller_count = 10
    roller_radius = 12.0         # rodillos de 24 mm
    roller_core = 40.0           # entre centros de las puntas: 64 mm en total
    roller_ring = 60.5
    slope = 1.0                  # 45 grados, mecanum
    wheel_z = max(
        abs(roller_ring * math.sin(2 * math.pi * i / roller_count))
        + roller_core / 2 * abs(slope * math.cos(2 * math.pi * i / roller_count))
        / math.sqrt(1 + slope ** 2)
        + roller_radius
        for i in range(roller_count)
    )
    arch_radius = wheel_z + 8.0
    wheel_positions = (
        (-1.0, -1.0, "DELANTERA_IZQ"),
        (1.0, -1.0, "DELANTERA_DER"),
        (1.0, 1.0, "TRASERA_DER"),
        (-1.0, 1.0, "TRASERA_IZQ"),
    )

    def arch(side_x, side_y):
        cx, cy = side_x * wheel_x, side_y * wheel_y
        return _cylinder(
            manager,
            _point(rr(cx - side_x * 45), rr(cy), rz(wheel_z)),
            _point(rr(cx + side_x * 60), rr(cy), rz(wheel_z)),
            rr(arch_radius),
        )

    # --- Pilares blancos entre las ruedas (vista lateral de la lámina). ---
    def side_pillar(side):
        pillar = _rounded_side_panel(
            manager, rr(side * 187.5), 0, rz(117.5), rr(112), rz(165),
            rr(75), rr(25),
        )
        # Solo hasta el disco (Z 160) y con la cara exterior curva.
        _intersect(
            manager, pillar,
            _box(manager, rr(side * 187.5), 0, rz(97.5), rr(80), rr(120), rz(125)),
            "pilar hasta el disco",
        )
        _intersect(
            manager, pillar,
            _cylinder(manager, _point(0, 0, rz(30)), _point(0, 0, rz(165)), rr(radius)),
            "pilar enrasado",
        )
        return pillar

    # --- Chasis negro (Z 31-100) y cuerpo con arcos (Z 100-160). ---------
    chassis = _rounded_xy(
        manager, 0, 0, rz(65.5), rr(246), rr(410), rz(69), rr(20)
    )
    # 2.0.1: recortado al círculo del cuerpo negro; sus esquinas asomaban
    # fuera del disco (a 231 mm del centro).
    _intersect(
        manager, chassis,
        _cylinder(manager, _point(0, 0, rz(30)), _point(0, 0, rz(101)), rr(218)),
        "chasis bajo el disco",
    )
    _append(specs, chassis, "01_CHASIS_NEGRO", BLACK)

    body = _cylinder(manager, _point(0, 0, rz(100)), _point(0, 0, rz(160)), rr(218))
    for side_y in (-1.0, 1.0):
        # Frente y trasera planos, enrasados con el chasis.
        _difference(
            manager, body,
            _box(manager, 0, rr(side_y * 230), rz(130), rr(246), rr(50), rz(62)),
            "frente plano",
        )
    for side_x, side_y, _label in wheel_positions:
        _difference(manager, body, arch(side_x, side_y), "arco de rueda")
    for side in (-1.0, 1.0):
        _difference(manager, body, side_pillar(side), "hueco del pilar")
    _append(specs, body, "02_CUERPO_NEGRO_ARCOS", BLACK)

    # --- Disco blanco de Z 160 a 200 con chaflán y aro negro. ------------
    disc = _cylinder(manager, _point(0, 0, rz(160)), _point(0, 0, rz(192)), rr(radius))
    _union(
        manager, disc,
        manager.createCylinderOrCone(
            _point(0, 0, rz(192)), rr(radius), _point(0, 0, rz(200)), rr(217)
        ),
        "chaflán del disco",
    )

    def top_ring(z1, z2):
        ring = _cylinder(manager, _point(0, 0, z1), _point(0, 0, z2), rr(212))
        _difference(
            manager, ring,
            _cylinder(manager, _point(0, 0, z1 - .1), _point(0, 0, z2 + .1), rr(200)),
            "aro de la tapa",
        )
        return ring

    _difference(manager, disc, top_ring(rz(197), rz(200.1)), "ranura del aro")
    _append(specs, disc, "03_DISCO_SUPERIOR_BLANCO", WHITE)
    _append(specs, top_ring(rz(197), rz(200.5)), "04_ARO_NEGRO_TAPA", BLACK)

    for index, side in enumerate((-1.0, 1.0), start=1):
        _append(specs, side_pillar(side), f"08_PILAR_LATERAL_{index:02d}", WHITE)

    # --- Frente: ventanas de sensores (misma forma, sobre el chasis). -----
    front = -205.0
    fascia = _rounded_panel(
        manager, 0, rr(front - 6.3), rz(120), rr(184.5), rz(35.6), rr(14.6), rr(12.9)
    )
    _append(specs, fascia, "09_MARCO_SENSOR_FRONTAL", BLACK)
    insert = _rounded_panel(
        manager, 0, rr(front - 15.0), rz(120), rr(153), rz(18.7), rr(5.1), rr(7.0)
    )
    _append(specs, insert, "10_INSERTO_SENSOR_FRONTAL", DARK)
    lower_fascia = _rounded_panel(
        manager, 0, rr(front - 6.5), rz(66.7), rr(166.5), rz(21.3), rr(12.9), rr(8.1)
    )
    _append(specs, lower_fascia, "11_MARCO_INFERIOR", BLACK)
    for index, (x, lens_radius, color) in enumerate(
        [(-65.25, 9.0, DARK), (0.0, 6.2, CYAN), (65.25, 9.0, DARK)], start=1
    ):
        lens = _cylinder(
            manager,
            _point(rr(x), rr(front - 17.0), rz(120)),
            _point(rr(x), rr(front - 20.5), rz(120)),
            rr(lens_radius),
        )
        _append(specs, lens, f"12_SENSOR_FRONTAL_{index:02d}", color)

    # --- Ruedas mecanum con aspecto del render. --------------------------
    for number, (side_x, side_y, label) in enumerate(wheel_positions, start=1):
        cx, cy = side_x * wheel_x, side_y * wheel_y

        def along(a, b, r, _cx=cx, _cy=cy, _s=side_x):
            return _cylinder(
                manager,
                _point(rr(_cx + _s * a), rr(_cy), rz(wheel_z)),
                _point(rr(_cx + _s * b), rr(_cy), rz(wheel_z)),
                rr(r),
            )

        _append(specs, along(-29, 29, 44), f"20_RUEDA_{number}_{label}", BLACK)
        # 2.0.1: placas de R 57 que tapan las puntas de los rodillos.
        _append(specs, along(-33, -29, 57), f"24_PLACA_INTERIOR_{number}", DARK)
        _append(specs, along(29, 33, 57), f"24_PLACA_EXTERIOR_{number}", DARK)
        _append(specs, along(33, 36, 30), f"21_BUJE_{number}", BLACK)
        _append(specs, along(36, 37, 5.4), f"22_LUZ_BUJE_{number}", CYAN)

        # Eje visible entre el chasis y la rueda, y soporte del motor.
        _append(
            specs,
            _cylinder(
                manager,
                _point(rr(side_x * 150), rr(cy), rz(wheel_z)),
                _point(rr(cx - side_x * 33), rr(cy), rz(wheel_z)),
                rr(18),
            ),
            f"25_EJE_{number}",
            BLACK,
        )
        # 2.0.1: carcasa de motor redonda (Ø 44) en vez del bloque cuadrado.
        _append(
            specs,
            _cylinder(
                manager,
                _point(rr(side_x * 123), rr(cy), rz(wheel_z)),
                _point(rr(side_x * 150), rr(cy), rz(wheel_z)),
                rr(22),
            ),
            f"26_SOPORTE_MOTOR_{number}",
            DARK,
        )

        handedness = 1.0 if number in (1, 3) else -1.0
        for index in range(roller_count):
            angle = 2.0 * math.pi * index / roller_count
            # Tangente en el plano YZ de la rueda (eje de la rueda = X).
            center = _point(
                rr(cx),
                rr(cy + roller_ring * math.cos(angle)),
                rz(wheel_z + roller_ring * math.sin(angle)),
            )
            direction = _vector(
                handedness,
                -slope * math.sin(angle),
                slope * math.cos(angle),
            )
            roller = _capsule(
                manager, center, direction, rr(roller_core), rr(roller_radius)
            )
            # 2.0.1: pasador del rodillo, 4 mm fuera de cada punta (render).
            pin = direction.copy()
            pin.normalize()
            pin.scaleBy(rr(roller_core / 2 + roller_radius + 4))
            p1 = center.copy()
            p1.translateBy(_vector(-pin.x, -pin.y, -pin.z))
            p2 = center.copy()
            p2.translateBy(pin)
            _union(manager, roller, _cylinder(manager, p1, p2, rr(3)), "pasador")
            _append(specs, roller, f"23_RODILLO_{number}_{index + 1:02d}", ROLLER)

    # --- LIDAR: delante del tronco, con el pedestal abrazándolo. ----------
    # El zócalo del tronco (1.6.0) mide 254 x 229 mm en Z 200.
    pod_y = -150.0
    pod_base = _cylinder(
        manager, _point(0, rr(pod_y), rz(198.7)), _point(0, rr(pod_y), rz(206.7)), rr(46.7)
    )
    _difference(
        manager, pod_base,
        _ellipse(manager, rz(195), rz(210), rr(127), rr(114.3)),
        "pedestal contra el tronco",
    )
    _append(specs, pod_base, "30_BASE_TORRETA_BLANCA", WHITE)
    pod = _cylinder(
        manager, _point(0, rr(pod_y), rz(204)), _point(0, rr(pod_y), rz(228.9)), rr(34.3)
    )
    _append(specs, pod, "31_TORRETA_NEGRA", BLACK)
    lens = _cylinder(
        manager,
        _point(0, rr(pod_y - 33.75), rz(216.4)),
        _point(0, rr(pod_y - 37.7), rz(216.4)),
        rr(4.7),
    )
    _append(specs, lens, "32_LENTE_TORRETA", CYAN)

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


        diameter = _parameter_value(design, "diametro_base", 45.0)
        height = _parameter_value(design, "alto_base", 20.0)
        radial_scale = diameter / 40.0
        height_scale = height / 22.5

        manager = adsk.fusion.TemporaryBRepManager.get()
        specs = _build_specs(manager, radial_scale, height_scale)
        replaced = _replace_previous_generation(component)

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
