"""Crea la carcasa exterior de la cabeza Robot Toreto 95 cm."""

import traceback
import importlib.util
from pathlib import Path
import adsk.core
import adsk.fusion

_profile_spec = importlib.util.spec_from_file_location("toreto_head_profiles", Path(__file__).with_name("toreto_profile_geometry.py"))
_profiles = importlib.util.module_from_spec(_profile_spec)
_profile_spec.loader.exec_module(_profiles)

COMPONENT_NAME = "06_CABEZA"
FEATURE_NAME = "CABEZA_EXTERIOR_TORETO_95CM"
ALIGNMENT_FEATURE_NAME = "MONTAJE_GLOBAL_95CM"
BODY_PREFIX = "CABEZA95_"
VERSION = "4.2.1"
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


def _set_value(design, name, expression, comment):
    p = design.userParameters.itemByName(name)
    if p:
        p.expression = expression
        p.comment = comment
    else:
        p = design.userParameters.add(name, adsk.core.ValueInput.createByString(expression), "mm", comment)
    return p.value


def _p(x, y, z):
    # Gira la cabeza frontal/posterior sin modificar su altura ni anchura.
    # La pantalla que se veia desde posterior pasa al frontal del ensamblaje.
    return adsk.core.Point3D.create(x, -y, z + _GEOMETRY_Z)
def _v(x, y, z): return adsk.core.Vector3D.create(x, y, z)


def _ellipse(m, z1, z2, a1, b1, a2=None):
    if a2 is None: a2 = a1
    return m.createEllipticalCylinderOrCone(_p(0, 0, z1), a1, b1, _p(0, 0, z2), a2, _v(1, 0, 0))


def _cylinder(m, p1, p2, radius): return m.createCylinderOrCone(p1, radius, p2, radius)


def _ring_y(m, x, y1, y2, z, outer, inner):
    body = _cylinder(m, _p(x, y1, z), _p(x, y2, z), outer)
    low_y = min(y1, y2) - .1
    high_y = max(y1, y2) + .1
    tool = _cylinder(m, _p(x, low_y, z), _p(x, high_y, z), inner)
    if not m.booleanOperation(body, tool, adsk.fusion.BooleanTypes.DifferenceBooleanType):
        raise RuntimeError("No se pudo formar el aro frontal de la cara.")
    return body


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


def _bowed_face(m, y, z, width, height, depth, label):
    """Bowed top/bottom rather than a straight-sided rounded rectangle."""
    sections = []
    for fraction, width_factor in ((0, .30), (.035, .68), (.10, .89), (.25, .98), (.5, 1.0), (.75, .98), (.90, .89), (.965, .68), (1, .30)):
        center = _p(0, y, z + (fraction - .5) * height)
        sections.append((center.z, center.x, center.y, width * width_factor / 2, depth / 2, 4.0))
    return _profiles.loft(m, sections, label)


def _ellipse_side(m, x, y, z, depth_x, radius_z, radius_y):
    """Prisma eliptico sobre X; su contorno se controla en la vista YZ."""
    return m.createEllipticalCylinderOrCone(
        _p(x - depth_x / 2, y, z),
        radius_z,
        radius_y,
        _p(x + depth_x / 2, y, z),
        radius_z,
        _v(0, 0, 1),
    )


def _d_side_envelope(m, width_x, height, curved_y, flat_y):
    """Silueta lateral en D medida en el lienzo derecho.

    El dorso es muy curvo y sobresale; el frontal de pantalla es casi
    vertical. Un rectangulo redondeado simetrico no reproduce ambas cosas.
    """
    center_z = height / 2.0
    curved_sign = 1.0 if curved_y > flat_y else -1.0
    join_y = curved_sign * 3.35
    curved = _ellipse_side(
        m,
        0,
        join_y,
        center_z,
        width_x,
        height / 2.0,
        abs(curved_y - join_y),
    )
    flat_width = abs(flat_y - join_y)
    flat = _rounded_side(
        m,
        0,
        (join_y + flat_y) / 2.0,
        center_z,
        flat_width,
        height - 1.2,
        width_x,
        1.25,
    )
    _union(m, curved, flat, "envolvente lateral asimetrica")
    return curved


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
    for i in range(component.features.moveFeatures.count - 1, -1, -1):
        move = component.features.moveFeatures.item(i)
        if move.name == ALIGNMENT_FEATURE_NAME and not move.deleteMe():
            raise RuntimeError("No se pudo retirar la alineación anterior de la cabeza.")
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
        # Medidas del contorno calibrado: X=-132..+132 mm y
        # Y=-124..+89 mm. Se fijan aqui para no heredar el antiguo ancho de
        # 285 mm que aun puede existir como parametro en documentos previos.
        width = 26.4
        depth = 21.3
        # 4.2.0: cabeza 15 mm mas alta (160 -> 175) para que el iPhone 12 Pro
        # Max con giro tipo libro (156 mm entre sus dos posiciones) no asome
        # por los cantos (DECISIONES.md, 1 oct 2026). Todo se estira en vertical.
        height = _set_value(design, "alto_cabeza", "175 mm", "Altura de la cabeza: 4.2.0, iPhone volteable")
        _GEOMETRY_Z = sum(
            _value(design, name, fallback)
            for name, fallback in (
                ("alto_base", 20.0),
                ("alto_tronco", 19.0),
                ("alto_cintura", 15.0),
                ("alto_pecho", 19.0),
                ("alto_cuello", 6.0),
            )
        )
        rs = width / 26.4; ds = depth / 21.3; hs = height / 16.0
        r = lambda x: x * rs; d = lambda x: x * ds; z = lambda x: x * hs
        m = adsk.fusion.TemporaryBRepManager.get(); specs = []
        # En Fusion el frontal real del ensamblaje es -Y global; aqui +Y local
        # (ver _p). Dorso curvo en -Y local, frente casi plano en +Y local.
        back_y = -12.4
        front_y = 8.9
        # 4.1.0: cada seccion sale de esquinas redondeadas reales en las tres
        # vistas: de frente 264 x 160 con radio 40 (lienzo); de lado en D,
        # frente casi recto con canto de radio 1,5 y dorso de radio 7,5.
        def arc(radius, zz):
            edge = max(0.0, radius - min(zz, 16.0 - zz))
            return radius - (radius * radius - edge * edge) ** .5

        def sections_for(levels, inset):
            result = []
            for zz in levels:
                half_width = 13.2 - arc(4.0, zz) - inset
                rear = back_y + arc(7.5, zz) + inset
                front = front_y - arc(1.5, zz) - inset
                center = _p(0, (rear + front) / 2, z(zz))
                result.append((center.z, center.x, center.y, r(half_width), (front - rear) / 2, 3.6))
            return result

        shell = _profiles.loft(m, sections_for(
            (0.0, .2, .5, 1.0, 1.7, 2.5, 3.5, 4.5, 8.0, 11.5, 12.5, 13.5, 14.3, 15.0, 15.5, 15.8, 16.0),
            0.0), "CABEZA_CUATRO_VISTAS")
        solid = m.copy(shell)
        # 4.2.0: carcasa HUECA, pared de 3 mm, para el iPhone y para que la
        # rejilla trasera saque el aire.
        inner = _profiles.loft(m, sections_for(
            (0.3, .5, 1.0, 1.7, 2.5, 3.5, 4.5, 8.0, 11.5, 12.5, 13.5, 14.3, 15.0, 15.5, 15.7),
            0.3), "CABEZA_INTERIOR")
        hollow = m.copy(inner)
        if not m.booleanOperation(shell, inner, adsk.fusion.BooleanTypes.DifferenceBooleanType):
            raise RuntimeError("No se pudo vaciar la cabeza.")
        neck_cut = _ellipse(m, z(-.2), z(2.2), r(6.8), d(4.8))
        if not m.booleanOperation(shell, neck_cut, adsk.fusion.BooleanTypes.DifferenceBooleanType):
            raise RuntimeError("No se pudo abrir el paso inferior del cuello.")

        # Visor: marco negro y, dentro, acrilico tintado. Los dos son la PIEL
        # de 3 mm de la cara en su contorno (siguen su curva: el frente se va
        # hacia atras por los lados), no laminas planas.
        def skin(width, height, radius):
            region = _rounded(m, 0, front_y - 1.55 + .5, z(8.0), width, height, 3.1, radius)
            if not m.booleanOperation(region, m.copy(solid), adsk.fusion.BooleanTypes.IntersectionBooleanType):
                raise RuntimeError("No se pudo recortar el visor con la carcasa.")
            if not m.booleanOperation(region, m.copy(hollow), adsk.fusion.BooleanTypes.DifferenceBooleanType):
                raise RuntimeError("No se pudo dejar el visor en 3 mm.")
            return region

        frame = skin(r(21.4), z(12.8), z(3.0))
        visor = skin(r(20.0), z(11.4), z(2.4))
        for target, tool, label in ((shell, frame, "marco"), (frame, visor, "visor")):
            if not m.booleanOperation(target, m.copy(tool), adsk.fusion.BooleanTypes.DifferenceBooleanType):
                raise RuntimeError("No se pudo encajar " + label + ".")
        _append(specs, shell, "01_CARCASA_BLANCA_REDONDEADA", WHITE)
        _append(specs, frame, "02_MARCO_FRONTAL_NEGRO", BLACK)
        _append(specs, visor, "03_VISOR_ACRILICO_TINTADO", DARK)

        # iPhone 12 Pro Max (16,08 x 7,81 x 0,74 cm), giro tipo libro: eje en
        # su borde largo, a la altura del centro del visor. Su cara va ~9 mm
        # por detras del visor (y 7,70): el frente de la cabeza se curva hacia
        # atras y, mas adelante, sus extremos se saldrian. Modo CARA arriba
        # (pantalla al frente, ojos en la mitad alta del visor); modo VISION
        # abajo (camaras traseras al frente, junto al eje).
        hinge_z = z(8.0)
        phone_front = 7.70
        phone_back = phone_front - .74
        phone_x, phone_w = 8.04, 7.81
        hinge_y = (phone_front + phone_back) / 2
        phone = _box(m, 0, hinge_y, hinge_z + phone_w / 2, 2 * phone_x, .74, phone_w)
        _append(specs, phone, "04_IPHONE_12_PRO_MAX", BLACK)
        # Guias en semicirculo a cada lado, hacia dentro de la cabeza (por
        # ellas corre un pasador de la cuna); recortadas al hueco interior.
        for side, label in ((-1.0, "IZQ"), (1.0, "DER")):
            guide = _cylinder(m, _p(side * (phone_x + .1), hinge_y, hinge_z),
                              _p(side * (phone_x + .5), hinge_y, hinge_z), phone_w + .2)
            back_half = _box(m, side * (phone_x + .3), hinge_y - 5.0, hinge_z, .6, 10.0, 20.0)
            for tool in (back_half, m.copy(hollow)):
                if not m.booleanOperation(guide, tool, adsk.fusion.BooleanTypes.IntersectionBooleanType):
                    raise RuntimeError("No se pudo formar la guia del iPhone.")
            _append(specs, guide, f"05_GUIA_IPHONE_{label}", DARK)
        # Servo MG90S detras del barrido (en el eje no cabe: ahi la cara ya se
        # curva); mueve la cuna con un engranaje o una varilla (a definir).
        servo = _box(m, phone_x + 1.6, hinge_y - 9.0, hinge_z, 2.3, 1.22, 2.85)
        _append(specs, servo, "05_SERVO_VOLTEO_MG90S", DARK)

        # Ojos: dibujo de la pantalla del iPhone en modo cara (mitad alta).
        eye_z = hinge_z + phone_w / 2
        eye_x = r(4.55)
        for side, label in ((-1.0, "IZQ"), (1.0, "DER")):
            ring = _ring_y(m, side * eye_x, phone_front, phone_front + .05, eye_z, z(2.05), z(1.80))
            _append(specs, ring, f"06_OJO_CIAN_{label}", CYAN)
            pupil = _cylinder(m, _p(side * eye_x, phone_front, eye_z),
                              _p(side * eye_x, phone_front + .05, eye_z), z(.40))
            _append(specs, pupil, f"06_PUPILA_CIAN_{label}", CYAN)

        # Rejilla trasera: 7 ranuras verticales en el dorso, a media altura.
        for index in range(7):
            slot = _box(m, -3.0 + index * 1.0, back_y + .2, z(8.0), .4, 2.0, z(5.0))
            if not m.booleanOperation(shell, slot, adsk.fusion.BooleanTypes.DifferenceBooleanType):
                raise RuntimeError("No se pudo abrir la rejilla trasera.")

        # Tapa posterior blanca; el propio borde de Fusion marca una junta
        # fina, sin el marco negro grueso de la versión anterior.
        # Recortar contra la envolvente curva evita la placa plana flotando
        # por detras del casco que sobresalia en las vistas laterales.
        # 4.1.1: sin tapa posterior. Con el dorso redondo de la 4.1.0 quedaba
        # casi entera dentro del casco y solo asomaban sus esquinas; la lamina
        # y el render muestran el dorso liso.
        for side, label in ((-1.0, "IZQ"), (1.0, "DER")):
            cx = side * (width / 2 + r(.12))
            camera = _rounded_side(m, cx, 0, z(8.4), d(5.2), z(5.2), r(.55), z(.9))
            _append(specs, camera, f"06_PANEL_LATERAL_{label}", BLACK)
            lens = _cylinder(m, _p(cx, -d(.05), z(8.4)), _p(cx + side * r(.42), -d(.05), z(8.4)), r(1.15))
            _append(specs, lens, f"07_LENTE_LATERAL_{label}", DARK)
        bottom = _ring(m, z(0), z(1.4), (r(7.2), d(5.1)), (r(5.8), d(3.9)))
        _append(specs, bottom, "08_ANILLO_INFERIOR_CUELLO", BLACK)
        appearances = {WHITE: _appearance(app, design, "TORETO Blanco satinado", WHITE), BLACK: _appearance(app, design, "TORETO Negro profundo", BLACK), DARK: _appearance(app, design, "TORETO Grafito", DARK), CYAN: _appearance(app, design, "TORETO Cian", CYAN)}
        # Construir todas las formas temporales antes de retirar la revision
        # anterior: un fallo de una interseccion conserva la cabeza existente.
        replaced = _replace(component)
        feature = component.features.baseFeatures.add()
        if not feature: raise RuntimeError("Fusion no pudo crear la función de cabeza.")
        feature.name = FEATURE_NAME; persisted = []; feature.startEdit()
        try:
            for temp, name, color in specs:
                body = component.bRepBodies.add(temp, feature)
                if not body: raise RuntimeError(f"Fusion no pudo añadir {name}.")
                body.name = name
                if appearances.get(color): body.appearance = appearances[color]
                # 4.2.1: el acrilico tintado deja ver el iPhone y sus ojos.
                if name.endswith("VISOR_ACRILICO_TINTADO"):
                    try:
                        body.opacity = .35
                    except Exception:
                        pass
                body.isLightBulbOn = True; persisted.append(body)
        finally: feature.finishEdit()
        component.attributes.add("RobotToreto", "cabeza_95cm_version", VERSION)
        design.rootComponent.attributes.add("RobotToreto", "ultimo_modulo", "06_CABEZA")
        app.activeViewport.fit()
        ui.messageBox(("Cabeza exterior actualizada." if replaced else "Cabeza exterior creada.") + f"\n\nCuerpos exteriores: {len(persisted)}\nAltura: {height * 10:.0f} mm (Z 790-965)\niPhone 12 Pro Max con giro tipo libro, visor de acrilico, cabeza hueca.", "Robot Toreto 95 cm")
    except Exception:
        ui.messageBox("No se pudo crear la cabeza:\n\n" + traceback.format_exc(), "Robot Toreto 95 cm - Error")
    finally:
        _GEOMETRY_Z = 0.0


def stop(context): pass
