"""Crea la carcasa exterior del cuello Robot Toreto 95 cm."""

import traceback
import adsk.core
import adsk.fusion

COMPONENT_NAME = "05_CUELLO"
FEATURE_NAME = "CUELLO_EXTERIOR_TORETO_95CM"
BODY_PREFIX = "CUELLO95_"
VERSION = "1.2.0"
_GEOMETRY_Z = 0.0
BLACK = (18, 21, 24)
DARK = (43, 48, 53)


def _occ(root):
    for i in range(root.occurrences.count):
        o = root.occurrences.item(i)
        if o.component.name == COMPONENT_NAME:
            return o
    return None


def _value(design, name, fallback):
    p = design.userParameters.itemByName(name)
    return p.value if p else fallback


def _p(x, y, z): return adsk.core.Point3D.create(x, y, z + _GEOMETRY_Z)
def _v(x, y, z): return adsk.core.Vector3D.create(x, y, z)


def _ellipse(m, z1, z2, a1, b1, a2=None):
    if a2 is None: a2 = a1
    return m.createEllipticalCylinderOrCone(_p(0, 0, z1), a1, b1, _p(0, 0, z2), a2, _v(1, 0, 0))


def _ring(m, z1, z2, outer, inner):
    body = _ellipse(m, z1, z2, *outer)
    tool = _ellipse(m, z1 - .1, z2 + .1, *inner)
    if not m.booleanOperation(body, tool, adsk.fusion.BooleanTypes.DifferenceBooleanType):
        raise RuntimeError("No se pudo ahuecar el cuello.")
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
    a = component.attributes.itemByName("RobotToreto", "cuello_95cm_version")
    return a.value if a else None


def _replace(component):
    if not _has(component): return False
    feature = None
    for i in range(component.features.baseFeatures.count):
        f = component.features.baseFeatures.item(i)
        if f.name == FEATURE_NAME: feature = f; break
    if not feature or not feature.deleteMe() or _has(component):
        raise RuntimeError("No se pudo retirar el cuello anterior.")
    return True


def run(context):
    global _GEOMETRY_Z
    app = adsk.core.Application.get(); ui = app.userInterface
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design: ui.messageBox("Abre 00_Toreto_Ensamblaje_95cm antes de ejecutar."); return
        occurrence = _occ(design.rootComponent)
        if not occurrence: raise RuntimeError("Falta 05_CUELLO. Ejecuta Componentes primero.")
        component = occurrence.component
        if _version(component) == VERSION and _has(component):
            ui.messageBox("El cuello exterior ya existe; no se duplicó."); return
        replaced = _replace(component)
        height = _value(design, "alto_cuello", 5.5)
        _GEOMETRY_Z = sum(
            _value(design, name, fallback)
            for name, fallback in (
                ("alto_base", 22.5),
                ("alto_tronco", 18.5),
                ("alto_cintura", 10.0),
                ("alto_pecho", 19.0),
            )
        )
        rs = _value(design, "ancho_pecho", 34.0) / 34.0
        hs = height / 5.5
        r = lambda x: x * rs
        z = lambda x: x * hs
        m = adsk.fusion.TemporaryBRepManager.get()
        specs = []
        core = _ellipse(m, z(.4), z(5.5), r(4.1), r(3.2))
        _append(specs, core, "01_NUCLEO_NEGRO", BLACK)
        shell = _ring(m, z(0), z(5.5), (r(5.5), r(4.25)), (r(4.65), r(3.40)))
        _append(specs, shell, "02_CARCASA_NEGRA", BLACK)
        lower = _ring(m, z(0), z(1.0), (r(6.0), r(4.6)), (r(4.25), r(3.15)))
        _append(specs, lower, "03_ANILLO_INFERIOR_GRAFITO", DARK)
        upper = _ring(m, z(4.6), z(5.5), (r(5.3), r(4.05)), (r(4.1), r(3.05)))
        _append(specs, upper, "04_ANILLO_SUPERIOR_NEGRO", BLACK)
        for index, (z1, z2, major, minor) in enumerate(
            ((1.25, 1.75, 5.35, 4.10), (2.35, 2.85, 5.15, 3.95), (3.45, 3.95, 4.95, 3.80)),
            start=1,
        ):
            bellows = _ring(
                m, z(z1), z(z2), (r(major), r(minor)), (r(4.25), r(3.15))
            )
            _append(specs, bellows, f"05_FUELLE_{index:02d}", DARK)
        appearances = {
            BLACK: _appearance(app, design, "TORETO Negro profundo", BLACK),
            DARK: _appearance(app, design, "TORETO Grafito", DARK),
        }
        feature = component.features.baseFeatures.add()
        if not feature: raise RuntimeError("Fusion no pudo crear la función del cuello.")
        feature.name = FEATURE_NAME; persisted = []; feature.startEdit()
        try:
            for temp, name, color in specs:
                body = component.bRepBodies.add(temp, feature)
                if not body: raise RuntimeError(f"Fusion no pudo añadir {name}.")
                body.name = name
                if appearances.get(color): body.appearance = appearances[color]
                body.isLightBulbOn = True; persisted.append(body)
        finally: feature.finishEdit()
        component.attributes.add("RobotToreto", "cuello_95cm_version", VERSION)
        design.rootComponent.attributes.add("RobotToreto", "ultimo_modulo", "05_CUELLO")
        app.activeViewport.fit()
        ui.messageBox(("Cuello exterior actualizado." if replaced else "Cuello exterior creado.") + f"\n\nCuerpos exteriores: {len(persisted)}\nAltura: {height * 10:.0f} mm\n\nSin mecánica ni electrónica.", "Robot Toreto 95 cm")
    except Exception:
        ui.messageBox("No se pudo crear el cuello:\n\n" + traceback.format_exc(), "Robot Toreto 95 cm - Error")
    finally:
        _GEOMETRY_Z = 0.0


def stop(context): pass
