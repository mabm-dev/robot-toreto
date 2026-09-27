"""Recorre SIN Fusion la publicación de la v11 (`MODE='ver_brazo'`).

A diferencia del simulador de la v9, aquí cada cuerpo falso tiene una
posición y una orientación reales, y las matrices de colocación las mueven de
verdad. Así se comprueba de punta a punta lo que puede fallar al colocar el
brazo como la lámina sin verlo en Fusion:
  - matrices en cm y por filas (`Rigid.array16_cm` -> `Matrix3D.setWithArray`);
  - que el eje del hombro y la rótula acaben donde dice `toreto_arm_pose`;
  - que los pasadores de la mano, ya girados, sigan encontrando sus bordes
    circulares con los ejes transformados (`placed_specs`);
  - que la mano quede, falange a falange, donde la pone el cálculo.

Qué NO hace: geometría real (lofts, booleanas) ni el aspecto del brazo.

Uso (desde esta carpeta):
    python simular_brazo_sin_fusion.py
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
import adsk  # noqa: E402  (el falso)

IDENTITY = ((1, 0, 0), (0, 1, 0), (0, 0, 1))


def _mat_vec(m, v):
    return tuple(sum(m[i][k] * v[k] for k in range(3)) for i in range(3))


def _mat_mul(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3))
                 for i in range(3))


class Mat:
    """Matrix3D falsa: giro (para _pose) o matriz 4x4 por filas en cm."""

    def __init__(self):
        self.deg, self.rows, self.shift = 0.0, IDENTITY, (0.0, 0.0, 0.0)

    def setToRotation(self, rad, axis, center):
        self.deg = math.degrees(rad)
        return True

    def setWithArray(self, array):
        if len(array) != 16 or list(array[12:]) != [0.0, 0.0, 0.0, 1.0]:
            return False
        self.rows = tuple(tuple(array[r * 4 + c] for c in range(3)) for r in range(3))
        self.shift = tuple(array[r * 4 + 3] for r in range(3))
        return True


class Body(base_sim.Body):
    """Cuerpo falso con centro (cm) y orientación acumulada."""

    def __init__(self, label, center_cm=(0.0, 0.0, 0.0), rot=IDENTITY, closure=0.0):
        super().__init__(label, closure)
        self.center, self.rot = tuple(center_cm), rot

    @property
    def boundingBox(self):
        c = self.center
        return types.SimpleNamespace(minPoint=base_sim.P(*(v - .1 for v in c)),
                                     maxPoint=base_sim.P(*(v + .1 for v in c)))

    @boundingBox.setter
    def boundingBox(self, value):
        pass  # la base asigna una caja fija; aquí la caja sale del centro


class Mgr(base_sim.Mgr):
    def copy(self, b):
        return Body(b.label, b.center, b.rot, b.closure)

    def transform(self, b, m):
        if m.deg:
            b.closure += abs(m.deg)          # giro de _pose (no se usa: mano abierta)
            return True
        b.center = tuple(a + t for a, t in zip(_mat_vec(m.rows, b.center), m.shift))
        b.rot = _mat_mul(m.rows, b.rot)
        return True


class BRepBody(sp.BRepBody):
    """Cuerpo importado: su caja y sus pasadores siguen al temporal."""

    @property
    def boundingBox(self):
        return self.temp.boundingBox

    def createForAssemblyContext(self, occurrence):
        proxy = super().createForAssemblyContext(occurrence)
        for edge in proxy.edges:
            if isinstance(edge.geometry, sp.Circle):
                n = edge.geometry.normal
                edge.geometry.normal = base_sim.P(*_mat_vec(self.temp.rot, (n.x, n.y, n.z)))
        proxy.boundingBox = self.temp.boundingBox
        return proxy


def _load_script():
    import importlib.util
    spec = importlib.util.spec_from_file_location('toreto_script_v11',
                                                  SRC / 'Toreto_Prueba_Holguras_01_44.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(script=None, pose_hook=None):
    """Publica con fakes y devuelve (report, pose). `pose_hook` permite
    estropear la postura a propósito para comprobar que se detecta."""
    sp._extend_fake_adsk()
    adsk.core.Matrix3D = types.SimpleNamespace(create=Mat)
    sp.BRepBody = BRepBody
    import toreto_hand as hand
    import toreto_clearance as clearance
    import toreto_motor_groups as groups
    import toreto_motor_validation as validation
    import toreto_local_terminals as terminals
    import toreto_outer_joints as outer_joints
    import toreto_arm_pose as arm_pose
    script = script or _load_script()

    arm = json.loads((SRC / 'link_local_sections.json').read_text(encoding='utf-8'))
    data = json.loads((SRC / 'hand_local_sections.json').read_text(encoding='utf-8'))
    pose = arm_pose.solve(arm['parts'], arm['master_plane_y_mm'], terminals, outer_joints)
    if pose_hook:
        pose_hook(pose)
    specs = hand.joint_specs(data)
    sp.AXES.update({s['pin_label']: s['axis'] for s in specs})
    sp.RADII_CM.update({s['pin_label']: hand.hinge_dimensions(s)[2] * .1 for s in specs})

    # Piezas del brazo: el eje del hombro y la rótula en sus centros reales.
    centers = {'04_EJE_HOMBRO': pose['shoulder_cap_center_flat'],
               '05_EJE_MUNECA': pose['wrist_center_flat'],
               '03_EJE_Y_ENLACE_CODO': pose['elbow_center_flat'],
               '01_BRAZO_LOCAL_SIN_REBAJES': pose['elbow_center_flat'],
               '02_ANTEBRAZO_LOCAL_SIN_REBAJES': pose['wrist_center_flat']}
    pending = [(Body(label, tuple(v * .1 for v in center)), label, 'TORETO Blanco satinado')
               for label, center in centers.items()]
    # Mano: cada cuerpo en un punto distinto cerca de la muñeca original.
    hand_bodies = []
    for index, (body, label, appearance, group) in enumerate(base_sim._fake_pending(hand, data)):
        w = data['wrist_center_mm']
        center = (w[0] + index % 7, w[1] - index % 5, w[2] - index)
        hand_bodies.append((Body(label, tuple(v * .1 for v in center)), label, appearance, group))

    root = sp.Component()
    design = types.SimpleNamespace(rootComponent=root, appearances=types.SimpleNamespace(
        itemByName=lambda name: None))
    out = Path(tempfile.gettempdir()) / 'toreto_simulacion_vista_brazo.json'
    _, report = script.publish_pinch_view(
        design, root, pending, hand_bodies, hand, clearance, groups, validation, data,
        Mgr(), out, fractions={}, arm_pose=pose, version='v11', mode='ver_brazo')
    json.loads(out.read_text(encoding='utf-8'))
    return report, pose


def main():
    report, pose = run()
    arm = report['brazo_lamina']
    check = arm['comprobacion_fusion']
    assert report['estado'] == 'publicado', report['estado']
    assert report['juntas'] == 20 and report['relaciones'] == 16, report
    assert check['tapa_hombro']['distancia_mm'] < .01, check
    assert check['muneca_rotula']['distancia_mm'] < .01, check
    assert math.dist(check['tapa_hombro']['fusion_mm'], pose['placed_mm']['tapa_hombro']) < 1e-3
    assert report['resumen']['pose_igual_al_ensayo'], report['resumen']
    assert report['resumen']['peor_distancia_falange_mm'] < .01, report['resumen']
    print('Brazo simulado: OK')
    print('  giros hombro/codo:', arm['giro_hombro_deg'], arm['giro_codo_deg'],
          '| factor antebrazo', arm['factor_antebrazo'])
    print('  frente a la lamina (mm):', arm['residuos_frente_a_lamina_mm'])
    print('  en el Fusion falso: tapa del hombro', check['tapa_hombro']['fusion_mm'],
          ' rotula', check['muneca_rotula']['fusion_mm'])
    print('  juntas de la mano con ejes girados:', report['juntas'],
          '| relaciones', report['relaciones'])


if __name__ == '__main__':
    main()
