"""Crea la carcasa exterior de pecho y hombros Robot Toreto 95 cm."""

import traceback

import adsk.core
import adsk.fusion


COMPONENT_NAME = "04_PECHO_HOMBROS"
FEATURE_NAME = "PECHO_HOMBROS_EXTERIOR_TORETO_95CM"
ALIGNMENT_FEATURE_NAME = "MONTAJE_GLOBAL_95CM"
BODY_PREFIX = "PECHO95_"
VERSION = "3.0.0"
# Centro en Z de la ROG Ally X (coordenadas del modulo, cm): Z 566-687 global.
ALLY_ZC = 8.65

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
    if min(width, height, depth) <= 0:
        raise ValueError(
            "Panel con dimensión no positiva: "
            f"{width:.3f} x {height:.3f} x {depth:.3f} cm"
        )
    # Fusion rechaza una caja si el radio supera la mitad de una dimensión.
    # Esto ocurría en la línea cian, cuya altura es muy pequeña.
    radius = min(radius, width * 0.49, height * 0.49, depth * 0.49)
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


def _show_body(body):
    for property_name in ("isLightBulbOn", "isVisible"):
        try:
            setattr(body, property_name, True)
        except Exception:
            pass


def _body_report(component):
    bodies = [
        component.bRepBodies.item(index)
        for index in range(component.bRepBodies.count)
        if component.bRepBodies.item(index).name.startswith(BODY_PREFIX)
    ]
    minimum = None
    maximum = None
    for body in bodies:
        try:
            minimum = body.boundingBox.minPoint.z * 10 if minimum is None else min(minimum, body.boundingBox.minPoint.z * 10)
            maximum = body.boundingBox.maxPoint.z * 10 if maximum is None else max(maximum, body.boundingBox.maxPoint.z * 10)
        except Exception:
            pass
    if minimum is None:
        return f"cuerpos {len(bodies)}; Z no disponible"
    return f"cuerpos {len(bodies)}; Z {minimum:.1f}–{maximum:.1f} mm"


def _replace_old(component):
    if not _has_bodies(component):
        return False
    for index in range(component.features.moveFeatures.count - 1, -1, -1):
        move = component.features.moveFeatures.item(index)
        if move.name == ALIGNMENT_FEATURE_NAME and not move.deleteMe():
            raise RuntimeError("No se pudo retirar la alineación anterior del pecho.")
    feature = None
    for index in range(component.features.baseFeatures.count):
        candidate = component.features.baseFeatures.item(index)
        if candidate.name == FEATURE_NAME:
            feature = candidate
            break
    if not feature or not feature.deleteMe() or _has_bodies(component):
        raise RuntimeError("No se pudo retirar el pecho anterior.")
    return True


def _outer_solid(manager, body_width, depth, height, r, d, z, skirt=0.0):
    """Silueta exterior maciza del pecho (frontal y lateral redondeadas).

    `skirt` la alarga hacia abajo sin cambiar los radios de las esquinas.
    """
    shell = _rounded_panel(
        manager,
        0,
        0,
        z(11.4) - skirt / 2,
        body_width,
        height + skirt,
        depth,
        min(body_width, height) * .12,
    )
    side_shell = _rounded_side(
        manager,
        0,
        d(.15),
        z(11.4) - skirt / 2,
        depth,
        height + skirt,
        body_width + r(.5),
        min(depth, height) * .17,
    )
    if not manager.booleanOperation(
        shell, side_shell, adsk.fusion.BooleanTypes.IntersectionBooleanType
    ):
        raise RuntimeError("No se pudo redondear la silueta lateral del pecho.")
    return shell


def _build(
    manager,
    body_width,
    shoulder_span,
    depth,
    height,
    screen_width,
    screen_height,
    screen_depth,
    clearance,
):
    """Construye el pecho siguiendo las vistas frontal, lateral y trasera."""
    # La lámina frontal mide unos 252 mm para la carcasa blanca. Los 340 mm
    # corresponden al conjunto de hombros, no al rectángulo del pecho.
    rs = shoulder_span / 34.0
    ds = depth / 21.6
    hs = height / 22.8
    r = lambda value: value * rs
    d = lambda value: value * ds
    z = lambda value: value * hs
    specs = []

    # Cuerpo rectangular redondeado; sustituye el antiguo pecho elíptico.
    # 2.9.0: falda del lienzo, la carcasa baja 20 mm (hasta Z 520) sobre el
    # bloque superior de la cintura (170 x 136 mm), con 3 mm de holgura.
    skirt = z(2.4)
    shell = _outer_solid(manager, body_width, depth, height, r, d, z, skirt)
    waist_opening = _box(
        manager, 0, 0, z(1.5) - skirt / 2, r(17.6), r(14.2), z(3.0) + skirt + .2
    )
    if not manager.booleanOperation(
        shell, waist_opening, adsk.fusion.BooleanTypes.DifferenceBooleanType
    ):
        raise RuntimeError("No se pudo abrir la falda sobre la cintura.")
    inner = _rounded_panel(
        manager,
        0,
        0,
        z(11.4),
        body_width - r(1.7),
        height - z(1.7),
        depth - d(1.8),
        min(body_width, height) * .095,
    )
    side_inner = _rounded_side(
        manager,
        0,
        d(.15),
        z(11.4),
        depth - d(1.8),
        height - z(1.7),
        body_width - r(1.2),
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

    # 3.0.0: la ROG Xbox Ally X va a la vista (DECISIONES.md, 1 oct 2026).
    # Ventana de su silueta (290 x 121) + 2 mm, esquinas R12, atravesando la
    # pared frontal. Sustituye al hueco del movil de 160 x 90.
    window = _rounded_panel(
        manager, 0, -10.5, ALLY_ZC, 29.4, 12.5, 3.0, 1.2
    )
    if not manager.booleanOperation(
        shell, window, adsk.fusion.BooleanTypes.DifferenceBooleanType
    ):
        raise RuntimeError("No se pudo abrir la ventana de la Ally.")

    # Rejillas de aire: la Ally toma aire por los costados y lo echa por
    # arriba. Entrada: 5 ranuras en cada costado, frente a sus extremos.
    # Salida: 8 ranuras en el techo a cada lado del asiento del cuello.
    vents = []
    for side in (-1.0, 1.0):
        for index in range(5):
            vents.append(_box(
                manager, side * body_width / 2, -7.7, ALLY_ZC - 3.6 + index * 1.8,
                2.0, 4.0, .4,
            ))
        for index in range(8):
            vents.append(_box(
                manager, side * 10.5, -6.5 + index * 1.3, height / 2 + z(11.4),
                5.0, .4, 2.0,
            ))
    for vent in vents:
        if not manager.booleanOperation(
            shell, vent, adsk.fusion.BooleanTypes.DifferenceBooleanType
        ):
            raise RuntimeError("No se pudo abrir una rejilla del pecho.")

    # 2.7.0: rebaje en U del cuello como en el lienzo frontal (135 mm de
    # ancho, fondo en Z 700). Antes era una ranura de 112 x 33 mm que
    # atravesaba el pecho de delante a atrás y dejaba ver el interior hueco.
    # Se abre por delante y acaba 30 mm antes de la pared trasera (en la vista
    # trasera de la lámina el borde superior es recto). Un asiento negro de
    # 6 mm forma el suelo y las paredes del rebaje y cierra la carcasa.
    notch_width = r(13.5)
    lining = r(.6)
    floor_z = z(19.2)
    notch_top = z(22.8) + 4.0
    notch_front = -depth / 2 - 1.0
    notch_back = depth / 2 - d(2.95)
    envelope_back = notch_back + lining
    envelope_bottom = floor_z - lining

    def notch_envelope():
        return _rounded_panel(
            manager,
            0,
            (notch_front + envelope_back) / 2,
            (envelope_bottom + notch_top) / 2,
            notch_width,
            notch_top - envelope_bottom,
            envelope_back - notch_front,
            r(3.1),
        )

    if not manager.booleanOperation(
        shell, notch_envelope(), adsk.fusion.BooleanTypes.DifferenceBooleanType
    ):
        raise RuntimeError("No se pudo abrir el rebaje del cuello.")
    _append(specs, shell, "01_CARCASA_RECTANGULAR_REDONDEADA", WHITE)

    lower = _rounded_panel(
        manager, 0, d(.45), z(1.1), r(14.5), z(2.2), d(9.8), z(.68)
    )
    _append(specs, lower, "02_INSERTO_INFERIOR_NEGRO", BLACK)

    seat = notch_envelope()
    if not manager.booleanOperation(
        seat,
        _outer_solid(manager, body_width, depth, height, r, d, z),
        adsk.fusion.BooleanTypes.IntersectionBooleanType,
    ):
        raise RuntimeError("No se pudo recortar el asiento del cuello.")
    notch = _rounded_panel(
        manager,
        0,
        (notch_front + notch_back) / 2,
        (floor_z + notch_top) / 2,
        notch_width - 2 * lining,
        notch_top - floor_z,
        notch_back - notch_front,
        r(2.5),
    )
    # 2.8.0: como en el render 3D, una tapa negra rellena el rebaje hasta
    # 8 mm bajo el borde (Z 722); solo se vacía lo que queda por encima.
    cover_top = z(22.8) - .8
    if not manager.booleanOperation(
        notch,
        _box(
            manager,
            0,
            (notch_front + notch_back) / 2,
            (cover_top + notch_top) / 2,
            notch_width,
            notch_back - notch_front + 1.0,
            notch_top - cover_top,
        ),
        adsk.fusion.BooleanTypes.IntersectionBooleanType,
    ):
        raise RuntimeError("No se pudo limitar el vaciado sobre la tapa.")
    if not manager.booleanOperation(
        seat, notch, adsk.fusion.BooleanTypes.DifferenceBooleanType
    ):
        raise RuntimeError("No se pudo vaciar el asiento del cuello.")
    _append(specs, seat, "03_TAPA_CUELLO_NEGRA", BLACK)

    # Disco negro sobre la tapa (Z 722-730), 97 mm como la base del cuello.
    disc = _ellipse(manager, cover_top, z(22.8), r(4.85), r(4.85 * .77))
    _append(specs, disc, "03_DISCO_CUELLO_NEGRO", BLACK)

    # 3.0.0: la ROG Xbox Ally X (290 x 121 x 27,5 / 50,9 mm, ficha oficial)
    # como pieza del pecho, con la cara 4 mm por dentro del frente y los
    # mandos asomando. Medidas de los mandos aproximadas: medir en la real.
    face = -10.6
    ally = _box(manager, 0, face + 1.375, ALLY_ZC, 29.0, 2.75, 12.1)
    for side in (-1.0, 1.0):
        grip = _box(manager, side * 11.5, face + 2.545, ALLY_ZC, 6.0, 5.09, 12.1)
        _union(manager, ally, grip, "empunadura de la Ally")
    _append(specs, ally, "04_ROG_ALLY_X", DARK)
    screen = _box(manager, 0, face - .03, ALLY_ZC, 15.5, .06, 8.7)
    _append(specs, screen, "05_ALLY_PANTALLA_7", BLACK)
    for name, x, dz in (("JOYSTICK_IZQ", -11.8, 2.5), ("CRUCETA", -11.8, -2.8),
                        ("ABXY", 11.8, 2.5), ("JOYSTICK_DER", 11.8, -2.8)):
        radius = 1.1 if "JOYSTICK" in name else 1.0
        knob = _cylinder(
            manager, _point(x, face, ALLY_ZC + dz), _point(x, face - 1.0, ALLY_ZC + dz), radius
        )
        _append(specs, knob, "05_ALLY_" + name, BLACK)

    # La onda cian del lienzo, ahora como imagen en la pantalla de la Ally.
    screen_glow = _rounded_panel(
        manager, 0, face - .1, ALLY_ZC, 11.0, z(.28), .08, r(.12)
    )
    _append(specs, screen_glow, "06_LINEA_PANTALLA_CIAN", CYAN)
    waveform = (0.7, 1.25, 2.0, 3.2, 1.8, 1.1, 2.4, 3.8, 2.3, 1.35, 2.7, 1.65, 0.8)
    spacing = .95
    for index, bar_height in enumerate(waveform):
        bar = _rounded_panel(
            manager,
            (index - (len(waveform) - 1) / 2.0) * spacing,
            face - .11,
            ALLY_ZC,
            r(.28),
            z(bar_height),
            .07,
            r(.08),
        )
        _append(specs, bar, f"06_ONDA_CIAN_{index + 1:02d}", CYAN)

    # Sólo el conector negro pertenece al pecho; la carcasa blanca es del brazo.
    # 2.6.0: pieza de hombro como en la lámina frontal, del costado del pecho
    # al interior del brazo (antes empezaba en X 166 y dejaba un hueco de
    # 40 mm entre pecho y brazo): disco R47, disco R39, cuello R29, disco R39
    # y el eje R36,5 que entra en el brazo. Coaxial con el eje del hombro
    # (en la lámina se dibuja inclinado con el brazo). El brazo no baja de
    # X ~159: los discos acaban en 157 y solo el eje entra en él.
    # 3.0.0: el pecho ocupa ahora el hueco de los discos (llega a X 163,5);
    # queda un aro negro fino hasta el brazo (X 168,6) y el eje que entra en
    # el brazo. Los brazos no se mueven.
    shoulder_parts = (
        (body_width / 2 / rs - .05, 16.86, 3.9),  # aro negro (entra .5 mm)
        (16.86, 19.65, 3.65),                      # eje dentro del brazo
    )
    for side, label in ((-1.0, "IZQ"), (1.0, "DER")):
        socket = None
        for start, end, radius in shoulder_parts:
            part = _cylinder(
                manager,
                _point(side * r(start), 0, z(18.1)),
                _point(side * r(end), 0, z(18.1)),
                r(radius),
            )
            if socket is None:
                socket = part
            elif not manager.booleanOperation(
                socket, part, adsk.fusion.BooleanTypes.UnionBooleanType
            ):
                raise RuntimeError("No se pudo unir la pieza de hombro " + label)
        _append(specs, socket, f"07_CONECTOR_HOMBRO_{label}", BLACK)

    back_y = depth / 2 + d(.08)
    back_panel = _rounded_panel(
        manager,
        0,
        back_y + d(.14),
        z(11.5),
        body_width - r(1.2),
        z(14.3),
        d(.26),
        z(1.0),
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
        # La ocurrencia puede haber quedado apagada al ejecutar Componentes.
        # Reactivarla aquí evita que el pecho exista pero no sea visible.
        try:
            occurrence.isLightBulbOn = True
        except Exception:
            pass
        try:
            component.isLightBulbOn = True
        except Exception:
            pass
        if _version(component) == VERSION and _has_bodies(component):
            for index in range(component.bRepBodies.count):
                body = component.bRepBodies.item(index)
                if body.name.startswith(BODY_PREFIX):
                    _show_body(body)
            ui.messageBox("El pecho exterior ya existe y se ha hecho visible.\n\n" + _body_report(component))
            return
        replaced = _replace_old(component)
        # Valores de la envolvente exterior definida en continuidad.
        shoulder_span = _set_master_value(
            design,
            "ancho_pecho",
            "340 mm",
            "Separación exterior de referencia del conjunto de hombros",
        )
        body_width = _set_master_value(
            design,
            "ancho_carcasa_pecho",
            "327 mm",
            "Anchura del pecho: 3.0.0, Ally X a la vista (el lienzo da 252)",
        )
        depth = _set_master_value(
            design, "fondo_pecho", "220 mm", "Profundidad máxima de la carcasa de pecho"
        )
        height = _set_master_value(
            design, "alto_pecho", "190 mm", "Altura exterior de la carcasa de pecho"
        )
        _GEOMETRY_Z = sum(
            _ensure_value(design, name, expression, comment)
            for name, expression, comment in (
                ("alto_base", "200 mm", "Altura base"),
                ("alto_tronco", "190 mm", "Altura tronco"),
                ("alto_cintura", "150 mm", "Altura cintura"),
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
            body_width,
            shoulder_span,
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
                _show_body(body)
                persisted.append(body)
        finally:
            feature.finishEdit()
        component.attributes.add("RobotToreto", "pecho_95cm_version", VERSION)
        design.rootComponent.attributes.add("RobotToreto", "ultimo_modulo", "04_PECHO_HOMBROS")
        try:
            occurrence.isLightBulbOn = True
        except Exception:
            pass
        app.activeViewport.fit()
        ui.messageBox(
            ("Pecho y hombros actualizados." if replaced else "Pecho y hombros creados.")
            + f"\n\nCuerpos exteriores: {len(persisted)}\n"
            f"Ancho {body_width * 10:.0f} mm con la ROG Ally X a la vista,\n"
            "rejillas de aire y aro fino del hombro.\n"
            "Z inferior global previsto: 520 mm (falda sobre la cintura).\n"
            + _body_report(component)
            + "\nSin mecánica ni esqueleto.",
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
