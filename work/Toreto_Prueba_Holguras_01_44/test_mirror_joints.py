"""v12: juntas de la mano copiada por simetría. Sin Fusion."""
import json
import math
import sys
import types
from pathlib import Path
import unittest

if 'adsk' not in sys.modules:
    _adsk = types.ModuleType('adsk')
    _adsk.core, _adsk.fusion = types.SimpleNamespace(), types.SimpleNamespace()
    sys.modules.update({'adsk': _adsk, 'adsk.core': _adsk.core,
                        'adsk.fusion': _adsk.fusion})

import toreto_arm_pose as pose
import toreto_hand as hand
import toreto_local_terminals as terminals
import toreto_mirror_joints as mirror
import toreto_outer_joints as outer_joints

HERE = Path(__file__).parent
ARM = json.loads((HERE / 'link_local_sections.json').read_text(encoding='utf-8'))
HAND = json.loads((HERE / 'hand_local_sections.json').read_text(encoding='utf-8'))
POSE = pose.solve(ARM['parts'], ARM['master_plane_y_mm'], terminals, outer_joints)
SPECS = hand.joint_specs(HAND)


def rotate_about(p, center, axis, degrees):
    r = pose.rotation(axis, degrees)
    v = tuple(a - b for a, b in zip(p, center))
    return tuple(c + sum(r[i][k] * v[k] for k in range(3)) for i, c in enumerate(center))


class MirrorTests(unittest.TestCase):
    def test_mirrored_flexion_is_the_mirror_of_the_right_flexion(self):
        # Para cada junta: flexionar la mano derecha y reflejar = reflejar y
        # flexionar la izquierda alrededor del eje calculado.
        right = [dict(s, center_mm=POSE['hand'].point(s['center_mm']),
                      axis=POSE['hand'].vector(s['axis'])) for s in SPECS]
        left = mirror.mirrored_specs(SPECS, POSE['hand'])
        probe = POSE['hand'].point(HAND['finger_paths_mm'][1][-1])
        for r, l in zip(right, left):
            for degrees in (-40.0, 25.0):
                a = mirror.mirror_point(rotate_about(probe, r['center_mm'], r['axis'], degrees))
                b = rotate_about(mirror.mirror_point(probe), l['center_mm'], l['axis'], degrees)
                self.assertLess(math.dist(a, b), 1e-9, r['name'])

    def test_naive_mirror_of_the_axis_would_bend_the_other_way(self):
        # Reflejar el eje como un punto (M·a) da el giro contrario: la prueba
        # anterior existe para que nadie "simplifique" mirror_axis.
        s = SPECS[0]
        c = POSE['hand'].point(s['center_mm'])
        a = POSE['hand'].vector(s['axis'])
        probe = POSE['hand'].point(HAND['finger_paths_mm'][0][-1])
        good = rotate_about(mirror.mirror_point(probe), mirror.mirror_point(c),
                            mirror.mirror_axis(a), -30)
        naive = rotate_about(mirror.mirror_point(probe), mirror.mirror_point(c),
                             mirror.mirror_point(a), -30)
        expected = mirror.mirror_point(rotate_about(probe, c, a, -30))
        self.assertLess(math.dist(good, expected), 1e-9)
        self.assertGreater(math.dist(naive, expected), 5.0)

    def test_limits_and_names_are_kept(self):
        for r, l in zip(SPECS, mirror.mirrored_specs(SPECS, POSE['hand'])):
            for key in ('name', 'parent', 'child', 'pin_label', 'minimum_deg',
                        'maximum_deg', 'travel_deg'):
                self.assertEqual(r[key], l[key])

    def test_local_coordinates_reproduce_the_fusion_measurement(self):
        # v12 en Fusion (27-09-2026): esperado en coordenadas del robot
        # (-272.578, -79.936, 313.928), medido dentro del componente
        # (272.578, -79.936, -313.928): el componente está girado 180° en Y.
        left = mirror.mirrored_specs(SPECS, POSE['hand'])
        turn_y = ((-1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, -1.0))
        local = mirror.to_local_specs(left, (turn_y, (0.0, 0.0, 0.0)))
        for got, expected in zip(local[0]['center_mm'], (272.578, -79.936, -313.928)):
            self.assertAlmostEqual(got, expected, places=2)

    def test_local_axes_keep_the_flexion_sense(self):
        # Girar en coordenadas internas alrededor del eje transformado y
        # volver a colocar = girar en el robot alrededor del eje original.
        left = mirror.mirrored_specs(SPECS, POSE['hand'])
        for linear in (((-1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, -1.0)),   # giro
                       ((-1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))):   # reflexión
            placement = (linear, (12.0, -3.0, 40.0))
            local = mirror.to_local_specs(left, placement)
            probe_world = mirror.mirror_point(POSE['hand'].point(HAND['finger_paths_mm'][2][-1]))
            to_world = lambda p: tuple(sum(linear[i][k] * p[k] for k in range(3)) + placement[1][i]
                                       for i in range(3))
            inverse = tuple(tuple(linear[k][i] for k in range(3)) for i in range(3))
            probe_local = tuple(sum(inverse[i][k] * (probe_world[k] - placement[1][k])
                                    for k in range(3)) for i in range(3))
            for w, l in zip(left, local):
                a = rotate_about(probe_world, w['center_mm'], w['axis'], -35)
                b = to_world(rotate_about(probe_local, l['center_mm'], l['axis'], -35))
                self.assertLess(math.dist(a, b), 1e-9, w['name'])

    def test_compose_and_array_reading(self):
        array = [0, 0, 1, 1.0, 0, 1, 0, 2.0, -1, 0, 0, 3.0, 0, 0, 0, 1]
        linear, shift = mirror.matrix_from_array16_cm(array)
        self.assertEqual(shift, (10.0, 20.0, 30.0))
        identity = (((1, 0, 0), (0, 1, 0), (0, 0, 1)), (0.0, 0.0, 0.0))
        self.assertEqual(mirror.compose(identity, (linear, shift)), (linear, shift))

    def test_base_name_strips_the_fusion_copy_suffix(self):
        self.assertEqual(mirror.base_name('MANO_00_PALMA(Simetría)'), 'MANO_00_PALMA')
        self.assertEqual(mirror.base_name('08_DEDO_1_NUDILLO_1_PASADOR'),
                         '08_DEDO_1_NUDILLO_1_PASADOR')


if __name__ == '__main__':
    unittest.main()
