"""Recorre SIN Fusion la v12 (`MODE='juntas_espejo'`): juntas de la mano
izquierda copiada por simetría en el montaje.

Monta en falso lo que hay en el documento del usuario: la mano derecha (con
juntas) y su copia en espejo (sin juntas), con los nombres que pone Fusion
("…(Simetría)") y los pasadores reflejados en su sitio. Comprueba:
  - que se crean 20 juntas y 16 relaciones con los dos sentidos posibles del
    círculo reflejado (no sabemos cuál da Fusion; el script debe servir con
    ambos) y que cada junta cierra hacia la palma izquierda;
  - que la pinza reflejada entra en los límites (nada se recorta);
  - que NO se crea nada si la mano está desplazada, si hay dos manos sin
    juntas o si falta un pasador.

Qué NO hace: geometría real ni el comportamiento de Fusion con componentes
copiados por simetría.

Uso (desde esta carpeta):
    python simular_espejo_sin_fusion.py
"""
import json
import math
import sys
import tempfile
import types
from pathlib import Path

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))

import simular_publicacion_sin_fusion as sp  # instala el adsk falso
import simular_sin_fusion as base_sim

SUFFIX = '(Simetría)'


class Pin:
    def __init__(self, name, center_mm, normal, radius_cm):
        self.name, self.center, self.normal, self.radius = name, center_mm, normal, radius_cm

    def createForAssemblyContext(self, occurrence):
        c = [v * .1 for v in self.center]
        box = types.SimpleNamespace(minPoint=base_sim.P(*(v - .05 for v in c)),
                                    maxPoint=base_sim.P(*(v + .05 for v in c)))
        edges = [sp.Edge(sp.Circle(base_sim.P(*self.normal), self.radius)),
                 sp.Edge('arista recta')]
        return types.SimpleNamespace(edges=edges, boundingBox=box)


def _component(name, joints=0):
    component = sp.Component()
    component.name = name
    component.joints = sp.Collection()
    for _ in range(joints):
        component.asBuiltJoints.append(object())
    return component


TURN_Y = ((-1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, -1.0))
IDENTITY = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


def _array(linear, shift_mm):
    return [linear[0][0], linear[0][1], linear[0][2], shift_mm[0] * .1,
            linear[1][0], linear[1][1], linear[1][2], shift_mm[1] * .1,
            linear[2][0], linear[2][1], linear[2][2], shift_mm[2] * .1, 0, 0, 0, 1]


def _to_local(linear, shift, p):
    return tuple(sum(linear[k][i] * (p[k] - shift[k]) for k in range(3)) for i in range(3))


def build_design(normal_sign=1, offset_mm=(0.0, 0.0, 0.0), extra_free_hand=False,
                 missing_pin=None, placement=(IDENTITY, (0.0, 0.0, 0.0)), nested=False):
    """placement: cómo coloca Fusion el componente de la mano copiada (en la
    v12 real, girado 180° en Y). nested=True: transform2 de la ocurrencia da
    solo la colocación respecto a su padre, que tiene otra."""
    import toreto_hand as hand
    import toreto_arm_pose as arm_pose
    import toreto_local_terminals as terminals
    import toreto_outer_joints as outer_joints
    import toreto_mirror_joints as mirror
    arm = json.loads((SRC / 'link_local_sections.json').read_text(encoding='utf-8'))
    data = json.loads((SRC / 'hand_local_sections.json').read_text(encoding='utf-8'))
    pose = arm_pose.solve(arm['parts'], arm['master_plane_y_mm'], terminals, outer_joints)
    specs = hand.joint_specs(data)

    left = _component('06_MANO_ARTICULABLE' + SUFFIX)
    occurrences = {}
    for group in {s['child'] for s in specs} | {s['parent'] for s in specs}:
        occurrence = sp.Occurrence()
        occurrence.component.name = group + SUFFIX
        occurrence.component.joints = sp.Collection()
        left.occurrences.append(occurrence)
        occurrences[group] = occurrence
    for spec in specs:
        if spec['pin_label'] == missing_pin:
            continue
        # Pasador de la mano derecha colocada, reflejado en X = 0.
        center = mirror.mirror_point(pose['hand'].point(spec['center_mm']))
        center = tuple(c + o for c, o in zip(center, offset_mm))
        circle = mirror.mirror_point(pose['hand'].vector(spec['axis']))
        normal = tuple(normal_sign * v for v in circle)
        # Fusion da los bordes en coordenadas internas del componente.
        center = _to_local(placement[0], placement[1], center)
        normal = _to_local(placement[0], (0.0, 0.0, 0.0), normal)
        occurrences[spec['parent']].component.bRepBodies.append(
            Pin(spec['pin_label'], center, normal, hand.hinge_dimensions(spec)[2] * .1))

    right = _component('06_MANO_ARTICULABLE', joints=20)
    matrix = lambda linear, shift: types.SimpleNamespace(asArray=lambda: _array(linear, shift))
    if nested:
        # El padre lleva el giro; la ocurrencia de la mano, un desplazamiento
        # propio. transform2 de la mano da SOLO su parte.
        own = (IDENTITY, (5.0, 0.0, 0.0))
        parent_shift = tuple(s - sum(placement[0][i][k] * own[1][k] for k in range(3))
                             for i, s in enumerate(placement[1]))
        parent = types.SimpleNamespace(transform2=matrix(placement[0], parent_shift),
                                       nativeObject=None, assemblyContext=None)
        hand_occurrence = types.SimpleNamespace(component=left, nativeObject=None,
                                                transform2=matrix(*own),
                                                assemblyContext=parent)
    else:
        hand_occurrence = types.SimpleNamespace(component=left, nativeObject=None,
                                                transform2=matrix(*placement),
                                                assemblyContext=None)
    all_occurrences = [types.SimpleNamespace(component=right), hand_occurrence]
    if extra_free_hand:
        all_occurrences.append(types.SimpleNamespace(
            component=_component('06_MANO_ARTICULABLE' + SUFFIX + ' 2')))
    root = types.SimpleNamespace(allOccurrences=all_occurrences)
    return types.SimpleNamespace(rootComponent=root), left, specs, pose


def _load_script():
    import importlib.util
    spec = importlib.util.spec_from_file_location('toreto_script_v12',
                                                  SRC / 'Toreto_Prueba_Holguras_01_44.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    sp._extend_fake_adsk()
    script = _load_script()
    import toreto_clearance as clearance
    import toreto_motor_groups as groups
    import toreto_mirror_joints as mirror
    out = Path(tempfile.gettempdir()) / 'toreto_simulacion_juntas_espejo.json'

    cases = [(sign, name, placement, nested)
             for sign in (1, -1)
             for name, placement, nested in (
                 ('sin girar', (IDENTITY, (0.0, 0.0, 0.0)), False),
                 ('girada 180 en Y (lo real)', (TURN_Y, (0.0, 0.0, 0.0)), False),
                 ('girada y anidada', (TURN_Y, (0.0, 30.0, -12.0)), True))]
    for normal_sign, case_name, placement, nested in cases:
        design, left, specs, pose = build_design(normal_sign, placement=placement,
                                                 nested=nested)
        report = script.add_mirror_joints(design, out)
        assert report['estado'] == 'juntas_creadas', report
        assert report['juntas'] == 20 and report['relaciones'] == 16, report
        assert left.asBuiltJoints.count == 20 and left.motionLinks.count == 16
        assert report['peor_pasador_mm'] < .01, report['peor_pasador_mm']
        # Cada junta debe girar alrededor de -M·a (hacia la palma izquierda):
        # el signo compensa el sentido del círculo, sea cual sea.
        signs = {name: -1 for name in report['signos_eje']}
        left_specs = mirror.mirrored_specs(specs, pose['hand'])
        local_specs = mirror.to_local_specs(left_specs, placement)
        for spec in local_specs:
            circle = tuple(normal_sign * v for v in
                           mirror.mirror_point(pose['hand'].vector(
                               next(s for s in specs if s['name'] == spec['name'])['axis'])))
            circle = _to_local(placement[0], (0.0, 0.0, 0.0), circle)
            effective = tuple(signs.get(spec['name'], 1) * v for v in circle)
            assert math.dist(effective, spec['axis']) < 1e-9, spec['name']
        # La pinza reflejada entra en los límites de las juntas creadas.
        by_name = {joint.name: joint for joint in left.asBuiltJoints}
        angles = groups.pose_angles(left_specs, groups.pinch_view_fractions(),
                                    clearance.signed_travel)
        plan = groups.motion_link_plan(left_specs)
        readback = script.apply_pose(list(by_name.values()),
                                     {n: signs.get(n, 1) for n in by_name}, plan, angles)
        bad = {k: v for k, v in readback.items() if abs(v['diferencia_deg']) > 1e-6}
        assert not bad, bad
        print('Mano izquierda simulada ({}, circulo {:+d}): 20 juntas, 16 relaciones, '
              'pinza dentro de limites; colocacion usada: {}'.format(
                  case_name, normal_sign, report['colocacion']))

    for name, kwargs, expected in (
            ('mano desplazada 10 mm', dict(offset_mm=(10.0, 0.0, 0.0)), 'Ninguna colocacion'),
            ('dos manos sin juntas', dict(extra_free_hand=True), 'exactamente UNA'),
            ('falta un pasador', dict(missing_pin='08_DEDO_2_NUDILLO_3_PASADOR'), 'Falta el pasador')):
        design, left, _, _ = build_design(**kwargs)
        report = script.add_mirror_joints(design, out)
        assert report['estado'] == 'rechazado_sin_cambios', report
        assert expected in report['errores'][0], report['errores']
        assert left.asBuiltJoints.count == 0 and left.motionLinks.count == 0
        print('Rechazo sin cambios:', name, '->', report['errores'][0][:60])
    design, left, _, _ = build_design(placement=(TURN_Y, (0.0, 0.0, 0.0)))
    hand_occurrence = design.rootComponent.allOccurrences[1]
    del hand_occurrence.transform2          # como si Fusion no la diera
    report = script.add_mirror_joints(design, out)
    assert report['estado'] == 'rechazado_sin_cambios', report
    assert 'Ninguna colocacion' in report['errores'][0] and 'identidad' in report['errores'][0], report['errores']
    assert left.asBuiltJoints.count == 0
    print('Rechazo sin cambios: caso real de la v12 sin colocacion ->', report['errores'][0][:70])


if __name__ == '__main__':
    main()
