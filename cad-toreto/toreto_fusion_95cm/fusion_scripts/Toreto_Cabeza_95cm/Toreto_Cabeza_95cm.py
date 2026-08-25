"""Crea la carcasa exterior de la cabeza Robot Toreto 95 cm."""

import traceback
import adsk.core
import adsk.fusion

COMPONENT_NAME = "06_CABEZA"
FEATURE_NAME = "CABEZA_EXTERIOR_TORETO_95CM"
BODY_PREFIX = "CABEZA95_"
VERSION = "2.1.0"
_GEOMETRY_Z = 0.0
WHITE = (238, 239, 237)
BLACK = (18, 21, 24)
DARK = (43, 48, 53)
CYAN = (0, 174, 235)


def _occ(root):
    for i in range(root.occurrences.count):
        o = root.occurrences.item(i)
        if o.component.name == COMPONENT_NAME:
            return o
    return None


def _value(design, name, fallback):
    p = design.userParameters.itemByName(name)
    return p.value if p else fallback


def _ensure(design, name, expression, comment):
    p = design.userParameters.itemByName(name)
    if not p:
        p = design.userParameters.add(name, adsk.core.ValueInput.createByString(expression), "mm", comment)
    return p.value


def _p(x, y, z): return adsk.core.Point3D.create(x, y, z + _GEOMETRY_Z)
def _v(x, y, z): return adsk.core.Vector3D.create(x, y, z)


def _ellipse(m, z1, z2, a1, b1, a2=None):
    if a2 is None: a2 = a1
    return m.createEllipticalCylinderOrCone(_p(0, 0, z1), a1, b1, _p(0, 0, z2), a2, _v(1, 0, 0))


def _cylinder(m, p1, p2, radius): return m.createCylinderOrCone(p1, radius, p2, radius)


def _box(m, x, y, z, sx, sy, sz):
    b = adsk.core.OrientedBoundingBox3D.create(_p(x, y, z), _v(1, 0, 0), _v(0, 1, 0), sx, sy, sz)
    return m.createBox(b)


def _union(m, target, tool, label):
    if not m.booleanOperation(target, tool, adsk.fusion.BooleanTypes.UnionBooleanType):
        raise RuntimeError(f"Falló la unión: {label}")


def _rounded(m, x, y, z, width, height, depth, radius):
    body = _box(m, x, y, z, width - 2 * radius, depth, height)
    _union(m, body, _box(m, x, y, z, width, depth, height - 2 * radius), "centro panel")
    for sx in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            cx = x + sx * (width / 2 - radius); cz = z + sz * (height / 2 - radius)
            _union(m, body, _cylinder(m, _p(cx, y - depth / 2, cz), _p(cx, y + depth / 2, cz), radius), "esquina panel")
    return body


def _rounded_side(m, x, y, z, width_y, height, depth_x, radius):
    """Panel redondeado visto de lado, extruido sobre el eje X."""
    radius = min(radius, width_y * .48, height * .48)
    body = _box(m, x, y, z, depth_x, width_y - 2 * radius, height)
    _union(m, body, _box(m, x, y, z, depth_x, width_y, height - 2 * radius), "centro lateral")
    for sy in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            cy = y + sy * (width_y / 2 - radius)
            cz = z + sz * (height / 2 - radius)
            _union(
                m,
                body,
                _cylinder(m, _p(x - depth_x / 2, cy, cz), _p(x + depth_x / 2, cy, cz), radius),
                "esquina lateral",
            )
    return body


def _ring(m, z1, z2, outer, inner):
    body = _ellipse(m, z1, z2, *outer); tool = _ellipse(m, z1 - .1, z2 + .1, *inner)
    if not m.booleanOperation(body, tool, adsk.fusion.BooleanTypes.DifferenceBooleanType):
        raise RuntimeError("No se pudo ahuecar la cabeza.")
    return body


def _append(specs, body, name, color):
    if not body: raise RuntimeError(f"No se pudo construir {name}.")
    specs.append((body, BODY_PREFIX + name, color))


def _appearance(app, design, name, rgb):
    old = design.appearances.itemByName(name)
    if old: return old
    lib = app.materialLibraries.itemById("BA5EE55E-9982-449B-9D66-9F036540E140")
    generic = lib.appearances.itemById("Prism-129") if lib else None
    if not generic:
        for i in range(app.materialLibraries.count):
            generic = app.materialLibraries.item(i).appearances.itemById("Prism-129")
            if generic: break
    if not generic: return None
    appearance = design.appearances.addByCopy(generic, name)
    prop = appearance.appearanceProperties.itemById("opaque_albedo")
    if prop: prop.value = adsk.core.Color.create(*rgb, 255)
    return appearance


def _has(component):
    return any(component.bRepBodies.item(i).name.startswith(BODY_PREFIX) for i in range(component.bRepBodies.count))


def _version(component):
    a = component.attributes.itemByName("RobotToreto", "cabeza_95cm_version")
    return a.value if a else None


def _replace(component):
    if not _has(component): return False
    feature = None
    for i in range(component.features.baseFeatures.count):
        f = component.features.baseFeatures.item(i)
        if f.name == FEATURE_NAME: feature = f; break
    if not feature or not feature.deleteMe() or _has(component):
        raise RuntimeError("No se pudo retirar la cabeza anterior.")
    return True


def run(context):
    global _GEOMETRY_Z
    app = adsk.core.Application.get(); ui = app.userInterface
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design: ui.messageBox("Abre 00_Toreto_Ensamblaje_95cm antes de ejecutar."); return
        occurrence = _occ(design.rootComponent)
        if not occurrence: raise RuntimeError("Falta 06_CABEZA. Ejecuta Componentes primero.")
        component = occurrence.component
        if _version(component) == VERSION and _has(component):
            ui.messageBox("La cabeza exterior ya existe; no se duplicó."); return
        replaced = _replace(component)
        width = _value(design, "ancho_cabeza", 28.5)
        depth = _value(design, "fondo_cabeza", 17.5)
        height = _value(design, "alto_cabeza", 15.7)
        _GEOMETRY_Z = sum(
            _value(design, name, fallback)
            for name, fallback in (
                ("alto_base", 22.5),
                ("alto_tronco", 18.5),
                ("alto_cintura", 10.0),
                ("alto_pecho", 19.0),
                ("alto_cuello", 5.5),
            )
        )
        screen_width = _ensure(design, "cabeza_pantalla_ancho", "192.96 mm", "Anchura del Waveshare LCD 7 en horizontal")
        screen_height = _ensure(design, "cabeza_pantalla_alto", "110.76 mm", "Altura del Waveshare LCD 7 en horizontal")
        screen_depth = _ensure(design, "cabeza_pantalla_fondo", "12 mm", "Profundidad del módulo de pantalla")
        clearance = _ensure(design, "cabeza_pantalla_holgura", "2 mm", "Holgura por lado del hueco de cabeza")
        rs = width / 28.5; ds = depth / 17.5; hs = height / 15.7
        r = lambda x: x * rs; d = lambda x: x * ds; z = lambda x: x * hs
        m = adsk.fusion.TemporaryBRepManager.get(); specs = []
        # Carcasa prismática redondeada: reproduce el contorno rectangular de
        # frente y la profundidad compacta visible en las vistas laterales.
        shell = _rounded(
            m, 0, 0, z(8.05), width, height, depth, min(width, height) * .18
        )
        side_envelope = _rounded_side(
            m, 0, d(.18), z(8.05), depth, height, width + r(.6), min(depth, height) * .22
        )
        if not m.booleanOperation(shell, side_envelope, adsk.fusion.BooleanTypes.IntersectionBooleanType):
            raise RuntimeError("No se pudo redondear la silueta lateral de la cabeza.")
        cavity_w = screen_width + 2 * clearance; cavity_h = screen_height + 2 * clearance
        cutter = _rounded(
            m, 0, -depth / 2 + d(.55), z(8.15), cavity_w, cavity_h, d(2.7), min(cavity_w, cavity_h) * .10
        )
        if not m.booleanOperation(shell, cutter, adsk.fusion.BooleanTypes.DifferenceBooleanType):
            raise RuntimeError("No se pudo abrir el hueco frontal de la cabeza.")
        neck_cut = _ellipse(m, z(-.2), z(2.2), r(6.8), d(4.8))
        if not m.booleanOperation(shell, neck_cut, adsk.fusion.BooleanTypes.DifferenceBooleanType):
            raise RuntimeError("No se pudo abrir el paso inferior del cuello.")
        _append(specs, shell, "01_CARCASA_BLANCA_REDONDEADA", WHITE)
        bezel_y = -depth / 2 - d(.08)
        bezel = _rounded(m, 0, bezel_y, z(8.15), cavity_w + r(1.0), cavity_h + z(1.0), d(.52), min(cavity_w, cavity_h) * .12)
        _append(specs, bezel, "02_MARCO_FRONTAL_NEGRO", BLACK)
        screen = _rounded(m, 0, bezel_y - d(.30), z(8.15), screen_width, screen_height, d(.34), min(screen_width, screen_height) * .08)
        _append(specs, screen, "03_PANTALLA_GRAFITO", DARK)

        # Tapa posterior blanca; el propio borde de Fusion marca una junta
        # fina, sin el marco negro grueso de la versión anterior.
        back_y = depth / 2 + d(.06)
        back_panel = _rounded(m, 0, back_y + d(.12), z(8.2), r(22.1), z(11.1), d(.24), z(1.5))
        _append(specs, back_panel, "04_TAPA_POSTERIOR_BLANCA", WHITE)
        for side, label in ((-1.0, "IZQ"), (1.0, "DER")):
            cx = side * (width / 2 + r(.12))
            camera = _rounded_side(m, cx, 0, z(8.4), d(5.2), z(5.2), r(.55), z(.9))
            _append(specs, camera, f"06_PANEL_LATERAL_{label}", BLACK)
            lens = _cylinder(m, _p(cx, -d(.05), z(8.4)), _p(cx + side * r(.42), -d(.05), z(8.4)), r(1.15))
            _append(specs, lens, f"07_LENTE_LATERAL_{label}", DARK)
        bottom = _ring(m, z(0), z(1.4), (r(7.2), d(5.1)), (r(5.8), d(3.9)))
        _append(specs, bottom, "08_ANILLO_INFERIOR_CUELLO", BLACK)
        appearances = {WHITE: _appearance(app, design, "TORETO Blanco satinado", WHITE), BLACK: _appearance(app, design, "TORETO Negro profundo", BLACK), DARK: _appearance(app, design, "TORETO Grafito", DARK), CYAN: _appearance(app, design, "TORETO Cian", CYAN)}
        feature = component.features.baseFeatures.add()
        if not feature: raise RuntimeError("Fusion no pudo crear la función de cabeza.")
        feature.name = FEATURE_NAME; persisted = []; feature.startEdit()
        try:
            for temp, name, color in specs:
                body = component.bRepBodies.add(temp, feature)
                if not body: raise RuntimeError(f"Fusion no pudo añadir {name}.")
                body.name = name
                if appearances.get(color): body.appearance = appearances[color]
                body.isLightBulbOn = True; persisted.append(body)
        finally: feature.finishEdit()
        component.attributes.add("RobotToreto", "cabeza_95cm_version", VERSION)
        design.rootComponent.attributes.add("RobotToreto", "ultimo_modulo", "06_CABEZA")
        app.activeViewport.fit()
        ui.messageBox(("Cabeza exterior actualizada." if replaced else "Cabeza exterior creada.") + f"\n\nCuerpos exteriores: {len(persisted)}\nPantalla: {screen_width * 10:.2f} x {screen_height * 10:.2f} mm\n\nSin mecánica ni electrónica.", "Robot Toreto 95 cm")
    except Exception:
        ui.messageBox("No se pudo crear la cabeza:\n\n" + traceback.format_exc(), "Robot Toreto 95 cm - Error")
    finally:
        _GEOMETRY_Z = 0.0


def stop(context): pass
