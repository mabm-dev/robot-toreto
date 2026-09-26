"""Recorre SIN Fusion el tramo de publicación de la v9 (`MODE='ver_pinza'`).

Complementa a `simular_sin_fusion.py`, que recorre el ensayo. Este recorre
`publish_pinch_view()`: componentes, 20 juntas, 16 relaciones de los 4
motores, la pose de la pinza y la lectura de vuelta.

El Fusion falso es estricto donde puede fallar la lógica de signos:
  - algunos pasadores tienen el círculo con la normal INVERTIDA respecto al
    eje de la junta (como pasa en Fusion), para ejercitar `flexion_signs`;
  - las juntas RECORTAN el valor a sus límites, como Fusion;
  - las relaciones mueven la seguidora con la razón y el sentido pedidos.
Si un signo estuviera mal, la pose quedaría recortada y la lectura de vuelta
no coincidiría con el ensayo.

Qué NO hace: geometría. No sabe si Fusion gira en el sentido que supone el
script (eso solo se ve en Fusion) ni coloca cuerpos de verdad.

Uso (desde esta carpeta):
    python simular_publicacion_sin_fusion.py
"""
import json
import math
import re
import sys
import tempfile
import types
from pathlib import Path

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))

import simular_sin_fusion as base_sim  # noqa: E402

base_sim._install_fake_adsk()
import adsk  # noqa: E402  (el falso)

AXES = {}          # pin_label -> eje de la junta (lo rellena main)
RADII_CM = {}      # pin_label -> radio REAL del pasador (hinge_dimensions)
FLIPPED = {'08_DEDO_1_NUDILLO_2_PASADOR', '08_DEDO_3_NUDILLO_1_PASADOR',
           '10_PULGAR_NUDILLO_1_PASADOR', '10_PULGAR_NUDILLO_3_PASADOR'}


class Named:
    def __init__(s): s.name, s.isLightBulbOn = '', True


class Attributes:
    def __init__(s): s.items = {}
    def add(s, group, key, value): s.items[key] = value


class Collection(list):
    @property
    def count(s): return len(s)
    def item(s, i): return s[i]


class Circle:
    def __init__(s, normal, radius): s.normal, s.radius = normal, radius
    def getData(s): return True, base_sim.P(), s.normal, s.radius


class Edge:
    def __init__(s, geometry): s.geometry = geometry


class BRepBody(Named):
    def __init__(s, temp):
        super().__init__()
        s.temp, s.appearance = temp, None

    def createForAssemblyContext(s, occurrence):
        edges = []
        if s.temp.label in AXES:
            axis = AXES[s.temp.label]
            sign = -1 if s.temp.label in FLIPPED else 1
            normal = base_sim.P(*(sign * v for v in axis))
            across = base_sim.P(axis[1], -axis[0], 0.0)   # perpendicular al eje
            # Señuelos: el taladro (coaxial, 0,35 mm mayor) y un círculo de
            # 4 mm NO alineado, que atraparía el antiguo radio fijo de 0,2 cm.
            edges.append(Edge(Circle(across, 0.2)))
            edges.append(Edge(Circle(normal, RADII_CM[s.temp.label] + 0.035)))
            edges.append(Edge(Circle(normal, RADII_CM[s.temp.label])))
            edges.append(Edge('arista recta'))
        return types.SimpleNamespace(edges=edges, boundingBox=base_sim.Box(),
                                     label=s.temp.label)


class BaseFeature(Named):
    def __init__(s): super().__init__(); s.bodies = Collection()
    def startEdit(s): return True
    def finishEdit(s): return True


class BaseFeatures:
    def add(s): return BaseFeature()


class BRepBodies(Collection):
    def add(s, temp, feature):
        body = BRepBody(temp)
        s.append(body)
        feature.bodies.append(body)
        return body


class Motion:
    def __init__(s):
        s.rotationLimits = types.SimpleNamespace(
            minimumValue=0.0, maximumValue=0.0,
            isMinimumValueEnabled=False, isMaximumValueEnabled=False)
        s._value, s.followers = 0.0, []

    @property
    def rotationValue(s): return s._value

    @rotationValue.setter
    def rotationValue(s, value):
        lim = s.rotationLimits
        if lim.isMinimumValueEnabled: value = max(value, lim.minimumValue)
        if lim.isMaximumValueEnabled: value = min(value, lim.maximumValue)
        s._value = value
        for follower, ratio in s.followers:
            follower.rotationValue = value * ratio


class Joint(Named):
    def __init__(s, joint_input):
        super().__init__()
        s.occurrenceOne, s.occurrenceTwo = joint_input.one, joint_input.two
        s.jointMotion = Motion()


class JointInput:
    def __init__(s, one, two, geometry):
        s.one, s.two, s.geometry, s.revolute = one, two, geometry, False

    def setAsRevoluteJointMotion(s, direction):
        s.revolute = True
        return True


class Joints(Collection):
    def createInput(s, one, two, geometry): return JointInput(one, two, geometry)

    def add(s, joint_input):
        assert joint_input.revolute
        joint = Joint(joint_input)
        s.append(joint)
        return joint


def _deg(value_input):
    return float(re.fullmatch(r'(-?[\d.]+) deg', value_input).group(1))


class MotionLinks(Collection):
    def createInput(s, one, two):
        return types.SimpleNamespace(one=one, two=two, motionOne=None, motionTwo=None,
                                     valueOne=None, valueTwo=None, isReversed=False)

    def add(s, link_input):
        ratio = _deg(link_input.valueTwo) / _deg(link_input.valueOne)
        if link_input.isReversed:
            ratio = -ratio
        link_input.one.jointMotion.followers.append((link_input.two.jointMotion, ratio))
        link = Named()
        s.append(link)
        return link


class Component(Named):
    def __init__(s):
        super().__init__()
        s.attributes, s.features = Attributes(), types.SimpleNamespace(baseFeatures=BaseFeatures())
        s.bRepBodies, s.occurrences = BRepBodies(), Occurrences()
        s.asBuiltJoints, s.motionLinks = Joints(), MotionLinks()


class Occurrence:
    def __init__(s):
        s.component, s.isGroundToParent, s.isValid = Component(), False, True


class Occurrences(Collection):
    def addNewComponent(s, matrix):
        occurrence = Occurrence()
        s.append(occurrence)
        return occurrence


def _extend_fake_adsk():
    core, fusion = adsk.core, adsk.fusion
    core.Circle3D = types.SimpleNamespace(cast=lambda g: g if isinstance(g, Circle) else None)
    core.ValueInput = types.SimpleNamespace(createByString=lambda text: text)
    core.Application = types.SimpleNamespace(get=lambda: types.SimpleNamespace(
        measureManager=types.SimpleNamespace(
            measureMinimumDistance=lambda a, b: types.SimpleNamespace(value=0.028))))
    fusion.JointGeometry = types.SimpleNamespace(createByCurve=lambda edge, key: ('eje', edge))
    fusion.JointKeyPointTypes = types.SimpleNamespace(CenterKeyPoint=0)
    fusion.JointDirections = types.SimpleNamespace(ZAxisJointDirection=2)
    fusion.JointMotionTypes = types.SimpleNamespace(RevoluteJointRotateMotionType=0)
    fusion.RevoluteJointMotion = types.SimpleNamespace(cast=lambda m: m)
    fusion.Design = types.SimpleNamespace(cast=lambda p: p)
    fusion.TemporaryBRepManager = types.SimpleNamespace(get=base_sim.Mgr)


def _load_script():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'toreto_script', SRC / 'Toreto_Prueba_Holguras_01_44.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    _extend_fake_adsk()
    import toreto_hand as hand
    import toreto_clearance as clearance
    import toreto_motor_groups as groups
    import toreto_motor_validation as validation
    script = _load_script()
    assert script.MODE == 'ver_pinza', 'El script no esta en modo ver_pinza'

    data = json.loads((SRC / 'hand_local_sections.json').read_text())
    specs = hand.joint_specs(data)
    AXES.update({spec['pin_label']: spec['axis'] for spec in specs})
    RADII_CM.update({spec['pin_label']: hand.hinge_dimensions(spec)[2] * .1 for spec in specs})
    assert RADII_CM['10_PULGAR_NUDILLO_1_PASADOR'] != RADII_CM['08_DEDO_1_NUDILLO_1_PASADOR']
    hand_bodies = base_sim._fake_pending(hand, data)
    arm = [(base_sim.Body(label), label, 'TORETO Blanco satinado')
           for label in ('01_BRAZO', '02_ANTEBRAZO', '03_CODO', '04_HOMBRO', '05_MUNECA')]
    root = Component()
    design = types.SimpleNamespace(rootComponent=root, appearances=types.SimpleNamespace(
        itemByName=lambda name: None))
    out = Path(tempfile.gettempdir()) / 'toreto_simulacion_vista_pinza.json'

    output, report = script.publish_pinch_view(
        design, root, arm, hand_bodies, hand, clearance, groups, validation, data,
        base_sim.Mgr(), out)

    hand_component = output.component.occurrences[0].component
    assert report['estado'] == 'publicado', report['estado']
    assert report['juntas'] == 20 and report['relaciones'] == 16
    assert hand_component.asBuiltJoints.count == 20
    assert hand_component.motionLinks.count == 16
    assert hand_component.occurrences.count == 21
    readback = report['juntas_en_pinza']
    bad = {k: v for k, v in readback.items() if abs(v['diferencia_deg']) > 1e-6}
    assert not bad, 'Pose recortada o con signo mal: {}'.format(bad)
    assert set(report['signos_eje']) == {
        'JUNTA_DEDO_1_2', 'JUNTA_DEDO_3_1', 'JUNTA_PULGAR_1', 'JUNTA_PULGAR_3'}
    assert report['resumen']['pose_igual_al_ensayo']
    json.loads(out.read_text(encoding='utf-8'))

    print('Publicacion simulada: OK')
    print('  juntas={juntas} relaciones={relaciones} cuerpos_mano={cuerpos_mano}'.format(**report))
    print('  juntas con eje invertido:', sorted(report['signos_eje']))
    for name in ('JUNTA_PULGAR_1', 'JUNTA_PULGAR_2', 'JUNTA_PULGAR_4',
                 'JUNTA_DEDO_1_1', 'JUNTA_DEDO_1_2', 'JUNTA_DEDO_1_4', 'JUNTA_DEDO_3_1'):
        print('  {:16} {}'.format(name, readback[name]))
    print('  resumen:', report['resumen'])
    print('JSON escrito y legible:', out)


if __name__ == '__main__':
    main()
