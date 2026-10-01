"""Maqueta SOLO PARA MIRAR: ROG Ally X en el pecho y movil en la cabeza.

No modifica ningun modulo del robot. Crea (o rehace) un unico componente
90_MAQUETA_ALLY_PECHO con:
  - el pecho ensanchado de 252 a 321 mm (interior 304) hacia el hueco de los
    discos del hombro, con un aro negro fino en lugar de los discos; los
    brazos no se mueven. Se genera con el mismo _build() del pecho 2.9.0;
  - la ROG Ally X como volumen (290 x 121 x 27,5/50,9 mm, ficha oficial);
  - por hombro: reductora cicloidal O60 x 40, eje de entrada, polea, correa
    y motor NEMA17 + driver MKS SERVO42D (volumenes);
  - el movil en la cabeza (volumen provisional 160 x 90 x 12).
Mide los choques de esos volumenes con el pecho nuevo y con los brazos, y
los guarda en maqueta_ally_pecho.json junto al script.

Para verlo: ocultar 04_PECHO_HOMBROS (y 06_CABEZA para ver el movil).
"""

import importlib.util
import json
import traceback
from pathlib import Path

import adsk.core
import adsk.fusion

ROOT = Path(__file__).resolve().parent
NAME = "90_MAQUETA_ALLY_PECHO"
VERSION = "1.2.2"
CHEST_WIDTH_MM = 327.0          # interior 310: Ally 290 + 10 mm de aire por lado (1.2.1)
SHOULDER_Z_MM = 540.0 + 190.0 / 22.8 * 18.1   # 690,83, eje del conector
ALLY_FACE_Y = -106.0            # frente del pecho en y -110
ALLY_Z = (566.0, 687.0)         # 121 mm de alto, bajo el asiento del cuello (694)

WHITE = (238, 239, 237)
BLACK = (18, 21, 24)
DARK = (43, 48, 53)
CYAN = (0, 174, 235)
MOTOR = (70, 90, 130)
ALLY = (60, 60, 66)
NAMES = {WHITE: "TORETO Blanco satinado", BLACK: "TORETO Negro profundo",
         DARK: "TORETO Grafito", CYAN: "TORETO Cian", MOTOR: "TORETO Maqueta motor",
         ALLY: "TORETO Maqueta Ally"}


def _chest_module():
    path = ROOT.parent / "Toreto_Pecho_Hombros_95cm" / "Toreto_Pecho_Hombros_95cm.py"
    spec = importlib.util.spec_from_file_location("toreto_pecho_maqueta", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _p(x, y, z):
    return adsk.core.Point3D.create(x * .1, y * .1, z * .1)


def _box(m, x1, x2, y1, y2, z1, z2):
    bounds = adsk.core.OrientedBoundingBox3D.create(
        _p((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2),
        adsk.core.Vector3D.create(1, 0, 0), adsk.core.Vector3D.create(0, 1, 0),
        abs(x2 - x1) * .1, abs(y2 - y1) * .1, abs(z2 - z1) * .1)
    return m.createBox(bounds)


def _cyl_x(m, x1, x2, y, z, radius):
    return m.createCylinderOrCone(_p(x1, y, z), radius * .1, _p(x2, y, z), radius * .1)


def _rounded_xz(m, x, y, z, width, height, depth, radius):
    """Panel de esquinas redondeadas visto de frente, extruido en Y."""
    union = adsk.fusion.BooleanTypes.UnionBooleanType
    body = _box(m, x - width / 2 + radius, x + width / 2 - radius, y - depth / 2, y + depth / 2,
                z - height / 2, z + height / 2)
    m.booleanOperation(body, _box(m, x - width / 2, x + width / 2, y - depth / 2, y + depth / 2,
                                  z - height / 2 + radius, z + height / 2 - radius), union)
    for sx in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            cx = x + sx * (width / 2 - radius)
            cz = z + sz * (height / 2 - radius)
            corner = m.createCylinderOrCone(_p(cx, y - depth / 2, cz), radius * .1,
                                            _p(cx, y + depth / 2, cz), radius * .1)
            m.booleanOperation(body, corner, union)
    return body


def _appearance(app, design, rgb):
    name = NAMES[rgb]
    existing = design.appearances.itemByName(name)
    if existing:
        return existing
    library = app.materialLibraries.itemById("BA5EE55E-9982-449B-9D66-9F036540E140")
    generic = library.appearances.itemById("Prism-129") if library else None
    for index in range(app.materialLibraries.count):
        if generic:
            break
        generic = app.materialLibraries.item(index).appearances.itemById("Prism-129")
    if not generic:
        return None
    appearance = design.appearances.addByCopy(generic, name)
    color = appearance.appearanceProperties.itemById("opaque_albedo")
    if color:
        color.value = adsk.core.Color.create(*rgb, 255)
    return appearance


def _mockup_bodies(m):
    """Volumenes (mm, coordenadas del montaje; el frente del robot es -Y)."""
    items = []
    z0 = SHOULDER_Z_MM
    # ROG Ally X a la vista (1.1.0): cara frontal 4 mm por dentro del frente
    # del pecho (y -110), mandos asomando por la ventana. Cuerpo 27,5 mm y
    # empunaduras de 50,9 mm a los lados (ficha oficial 290 x 121).
    face = ALLY_FACE_Y
    z1, z2 = ALLY_Z
    ally = _box(m, -145, 145, face, face + 27.5, z1, z2)
    for side in (-1.0, 1.0):
        grip = _box(m, side * 85, side * 145, face, face + 50.9, z1, z2)
        m.booleanOperation(ally, grip, adsk.fusion.BooleanTypes.UnionBooleanType)
    items.append((ally, "01_ROG_ALLY_X", ALLY, "ally"))
    zc = (z1 + z2) / 2
    items.append((_box(m, -77.5, 77.5, face - .6, face, zc - 43.5, zc + 43.5),
                  "02_ALLY_PANTALLA_7", CYAN, "ally"))
    # Mandos (posicion aproximada, a medir en la Ally real): joystick
    # izquierdo y botones ABXY arriba, cruceta y joystick derecho abajo.
    for name, x, z in (("JOYSTICK_IZQ", -118, zc + 25), ("CRUCETA", -118, zc - 28),
                       ("ABXY", 118, zc + 25), ("JOYSTICK_DER", 118, zc - 28)):
        radius = 11.0 if "JOYSTICK" in name else 10.0
        knob = m.createCylinderOrCone(_p(x, face, z), radius * .1, _p(x, face - 10, z), radius * .1)
        items.append((knob, "03_ALLY_" + name, BLACK, "mando"))
    for side, label in ((-1.0, "IZQ"), (1.0, "DER")):
        s = side
        items.append((_cyl_x(m, s * 102, s * 142, 0, z0, 30),
                      f"10_REDUCTORA_CICLOIDAL_{label}", DARK, "hombro"))
        shaft = _cyl_x(m, s * 142, s * 168.6, 0, z0, 20)
        items.append((shaft, f"11_EJE_SALIDA_{label}", BLACK, "hombro"))
        items.append((_cyl_x(m, s * CHEST_WIDTH_MM / 2, s * 168.6, 0, z0, 39),
                      f"12_ARO_NEGRO_{label}", BLACK, "aro"))
        items.append((_cyl_x(m, s * 168.6, s * 196.5, 0, z0, 36.5),
                      f"13_EJE_AL_BRAZO_{label}", BLACK, "aro"))
        items.append((_cyl_x(m, s * 72, s * 102, 0, z0, 4),
                      f"14_EJE_ENTRADA_{label}", BLACK, "hombro"))
        items.append((_cyl_x(m, s * 72, s * 82, 0, z0, 19),
                      f"15_POLEA_60T_{label}", DARK, "hombro"))
        motor_z = z0 - 70.0
        items.append((_cyl_x(m, s * 72, s * 82, 0, motor_z, 6.4),
                      f"16_POLEA_20T_{label}", DARK, "hombro"))
        items.append((_box(m, s * 74, s * 80, -19, 19, motor_z, z0),
                      f"17_CORREA_GT2_{label}", BLACK, "hombro"))
        items.append((_box(m, s * 82, s * 130, -21, 21, motor_z - 21, motor_z + 21),
                      f"18_NEMA17_{label}", MOTOR, "hombro"))
        items.append((_box(m, s * 130, s * 145, -21, 21, motor_z - 21, motor_z + 21),
                      f"19_DRIVER_MKS_SERVO42D_{label}", MOTOR, "hombro"))
    # iPhone 12 Pro Max (160,8 x 78,1 x 7,4) con giro tipo libro: eje en su
    # borde largo, en la linea media del visor (Z 870), pegado al visor
    # (frente de la cabeza en y -89; acrilico de 3 mm). Modo cara: abajo,
    # pantalla al frente. Modo vision: arriba, camaras traseras al frente.
    hinge_z, front = 870.0, -86.0
    half_x, width, thick = 80.4, 78.1, 7.4
    items.append((_box(m, -half_x, half_x, front, front + thick, hinge_z - width, hinge_z),
                  "30_IPHONE_MODO_CARA", ALLY, "cabeza"))
    items.append((_box(m, -half_x, half_x, front, front + thick, hinge_z, hinge_z + width),
                  "31_IPHONE_MODO_VISION", ALLY, "fantasma"))
    # Semicirculo que barre al girar (hacia dentro de la cabeza, +Y).
    back_half = lambda x1, x2: _box(m, x1, x2, front + thick / 2, front + 150,
                                    hinge_z - 100, hinge_z + 100)
    sweep = _cyl_x(m, -half_x, half_x, front + thick / 2, hinge_z, width + 2)
    m.booleanOperation(sweep, back_half(-half_x - 1, half_x + 1),
                       adsk.fusion.BooleanTypes.IntersectionBooleanType)
    items.append((sweep, "32_IPHONE_BARRIDO", MOTOR, "fantasma"))
    # Guias en semicirculo a cada lado (ranura por la que corre un pasador).
    for side, label in ((-1.0, "IZQ"), (1.0, "DER")):
        plate = _cyl_x(m, side * (half_x + 1), side * (half_x + 5), front + thick / 2,
                       hinge_z, width + 8)
        m.booleanOperation(plate, back_half(-150, 150),
                           adsk.fusion.BooleanTypes.IntersectionBooleanType)
        items.append((plate, "33_GUIA_SEMICIRCULO_" + label, DARK, "fantasma"))
    # Cono de la ultra gran angular (108 x 85 grados) en modo vision; el
    # bloque de camaras queda junto al borde-eje, a ~25 mm de un extremo.
    lens = (-half_x + 25, front, hinge_z + 25)
    length = 120.0
    cone = m.createEllipticalCylinderOrCone(
        _p(*lens), .005, .005 * .665, _p(lens[0], front - length, lens[2]),
        length * 1.376 * .1, adsk.core.Vector3D.create(1, 0, 0))
    if cone:
        items.append((cone, "34_CONO_ULTRA_GRAN_ANGULAR", CYAN, "fantasma"))

    # 1.2.0: ZONAS RESERVADAS para cables y aire. Nada puede ocuparlas; la
    # comprobacion de choques avisa si algo las invade.
    # Canal central detras de la Ally: columna 2020 + mazo de cables hacia la
    # cintura y hacia el cuello.
    items.append((_box(m, -30, 30, -70, 60, 560, 694), "40_RESERVA_CANAL_CENTRAL", CYAN, "reserva"))
    items.append((_box(m, -10, 10, 0, 20, 470, 790), "41_COLUMNA_2020", DARK, "fantasma"))
    # Doblado de los dos USB-C de la Ally (conector en angulo) por encima.
    # 1.2.2: los puertos (USB4 x2 y jack) estan arriba a la IZQUIERDA (vista
    # de frente: X negativa), fuera del bloque del cuello (X +-67,5).
    items.append((_box(m, -145, -70, -99, -55, ALLY_Z[1], ALLY_Z[1] + 30),
                  "42_RESERVA_CABLES_ALLY", CYAN, "reserva"))
    # Aire de entrada de la Ally por los costados: >= 10 mm hasta la pared.
    for side, label in ((-1.0, "IZQ"), (1.0, "DER")):
        items.append((_box(m, side * 145, side * 155, -106, -55, ALLY_Z[0], ALLY_Z[1]),
                      "43_RESERVA_AIRE_ENTRADA_" + label, CYAN, "reserva"))
        # Rejilla de salida en el techo del pecho, al lado del cuello.
        items.append((_box(m, side * 72, side * 140, -95, 60, 718, 731),
                      "44_REJILLA_SALIDA_TECHO_" + label, CYAN, "fantasma"))
        # Paso de cables por dentro del eje del hombro (hueco O12).
        items.append((_cyl_x(m, side * 72, side * 196.5, 0, SHOULDER_Z_MM, 6),
                      "45_CABLES_EJE_HOMBRO_" + label, CYAN, "fantasma"))
    # Rejilla trasera de la cabeza, detras del iPhone (dorso en y ~ +124).
    items.append((_box(m, -70, 70, 95, 130, 830, 910), "46_REJILLA_TRASERA_CABEZA", CYAN, "fantasma"))
    return items


def _intersection_mm3(m, a, b):
    ca, cb = m.copy(a), m.copy(b)
    if not m.booleanOperation(ca, cb, adsk.fusion.BooleanTypes.IntersectionBooleanType):
        return 0.0
    return round(ca.volume * 1000.0, 1)


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Abre el montaje del robot.")
            return
        root = design.rootComponent
        chest = _chest_module()
        chest._GEOMETRY_Z = 54.0
        m = adsk.fusion.TemporaryBRepManager.get()
        old_screen = ("07_CONECTOR_HOMBRO", "04_MARCO_PANTALLA", "05_PANTALLA", "06_")
        chest_specs = [s for s in chest._build(m, CHEST_WIDTH_MM * .1, 34.0, 22.0, 19.0,
                                                16.0, 9.0, 1.2, 0.3)
                       if not any(k in s[1] for k in old_screen)]
        mock = _mockup_bodies(m)
        shell = next(b for b, n, _ in chest_specs if n.endswith("01_CARCASA_RECTANGULAR_REDONDEADA"))
        # Ventana de la Ally: su silueta + 2 mm, esquinas R12, atravesando la
        # pared frontal.
        window = _rounded_xz(m, 0, -105, sum(ALLY_Z) / 2, 294, ALLY_Z[1] - ALLY_Z[0] + 4, 30, 12)
        if not m.booleanOperation(shell, window, adsk.fusion.BooleanTypes.DifferenceBooleanType):
            raise RuntimeError("No se pudo abrir la ventana de la Ally.")

        # Choques: volumenes internos contra el pecho nuevo, entre si y
        # contra los cuerpos de los brazos del montaje.
        report = dict(version=VERSION, ancho_pecho_mm=CHEST_WIDTH_MM, choques=[])
        chest_solids = [(b, n) for b, n, _ in chest_specs]
        arm_solids = []
        for occurrence in root.allOccurrences:
            if "Brazo_Mano" not in occurrence.fullPathName.split("+")[0]:
                continue
            for body in occurrence.component.bRepBodies:
                if body.isSolid:
                    arm_solids.append((m.copy(body.createForAssemblyContext(occurrence)),
                                       occurrence.fullPathName.split("+")[0] + "/" + body.name))
        internal = [(b, n) for b, n, _, g in mock if g in ("ally", "hombro")]
        reserved = [(b, n) for b, n, _, g in mock if g == "reserva"]
        # Zonas reservadas: nada del pecho ni de dentro puede ocuparlas.
        for body, name in reserved:
            for other, other_name in chest_solids + internal:
                volume = _intersection_mm3(m, body, other)
                if volume > .05:
                    report["choques"].append([name, other_name, volume])
        for body, name in internal:
            for other, other_name in chest_solids:
                # El eje de salida atraviesa la pared a proposito (su taladro).
                if "EJE_SALIDA" in name and "01_CARCASA" in other_name:
                    continue
                volume = _intersection_mm3(m, body, other)
                if volume > .05:
                    report["choques"].append([name, other_name, volume])
        for i, (body, name) in enumerate(internal):
            for other, other_name in internal[i + 1:]:
                # Las piezas de un mismo hombro se tocan a proposito; la Ally
                # contra cualquier pieza de hombro si se comprueba.
                ally_pair = "ALLY" in name or "ALLY" in other_name
                same_side = name.split("_")[-1] == other_name.split("_")[-1]
                if ("ALLY" in name and "ALLY" in other_name) or (same_side and not ally_pair):
                    continue
                volume = _intersection_mm3(m, body, other)
                if volume > .05:
                    report["choques"].append([name, other_name, volume])
        for body, name in [(shell, "PECHO_NUEVO")] + [(b, n) for b, n, _, g in mock if g == "aro"]:
            for other, other_name in arm_solids:
                volume = _intersection_mm3(m, body, other)
                if volume > .05:
                    report["choques"].append([name, other_name, volume])

        # Rehacer el componente de la maqueta (solo el suyo).
        for index in range(root.occurrences.count - 1, -1, -1):
            occurrence = root.occurrences.item(index)
            if occurrence.component.name == NAME:
                occurrence.deleteMe()
        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        component = occurrence.component
        component.name = NAME
        feature = component.features.baseFeatures.add()
        feature.name = "MAQUETA_ALLY_PECHO"
        feature.startEdit()
        try:
            for body, name, color in chest_specs:
                added = component.bRepBodies.add(body, feature)
                added.name = "MAQ_" + name
                appearance = _appearance(app, design, color)
                if appearance:
                    added.appearance = appearance
                if name.endswith("01_CARCASA_RECTANGULAR_REDONDEADA"):
                    try:
                        added.opacity = .35
                    except Exception:
                        pass
            for body, name, color, group in mock:
                added = component.bRepBodies.add(body, feature)
                added.name = "MAQ_" + name
                appearance = _appearance(app, design, color)
                if appearance:
                    added.appearance = appearance
                if group in ("fantasma", "reserva"):
                    try:
                        added.opacity = .3
                    except Exception:
                        pass
        finally:
            feature.finishEdit()

        path = ROOT / "maqueta_ally_pecho.json"
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        lines = ["{} / {}: {} mm3".format(*c) for c in report["choques"][:12]]
        ui.messageBox(
            "Maqueta creada en {} (no se ha tocado ningun modulo).\n\n"
            "Pecho {:.0f} mm, Ally a la vista con los mandos fuera, reductoras O60, NEMA17.\n"
            "iPhone con giro tipo libro: modo cara abajo; modo vision, barrido, guias y cono\n"
            "en transparente. Zonas reservadas de cables y aire (1.2.0).\n"
            "Choques: {}\n{}\n\n"
            "Para verla: oculta 04_PECHO_HOMBROS (y 06_CABEZA para ver el movil).\n"
            "Detalles: {}".format(NAME, CHEST_WIDTH_MM, len(report["choques"]),
                                  "\n".join(lines) or "ninguno", path.name),
            "Toreto - maqueta Ally en el pecho " + VERSION)
    except Exception:
        ui.messageBox("No se pudo crear la maqueta:\n\n" + traceback.format_exc(),
                      "Toreto - maqueta Ally en el pecho")


def stop(context):
    pass
