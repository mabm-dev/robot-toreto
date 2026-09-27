"""v11: brazo en la postura y medidas de la lámina. Sin Fusion."""
import json
import math
import sys
import types
from pathlib import Path
import unittest

# Los módulos del generador importan adsk solo dentro de las funciones que
# crean geometría; las de parámetros son puras.
if 'adsk' not in sys.modules:
    _adsk = types.ModuleType('adsk')
    _adsk.core, _adsk.fusion = types.SimpleNamespace(), types.SimpleNamespace()
    sys.modules.update({'adsk': _adsk, 'adsk.core': _adsk.core,
                        'adsk.fusion': _adsk.fusion})

import toreto_arm_pose as pose
import toreto_local_section_filter as local_filter
import toreto_local_terminals as terminals
import toreto_outer_joints as outer_joints

HERE = Path(__file__).parent
ARM = json.loads((HERE / 'link_local_sections.json').read_text(encoding='utf-8'))
HAND = json.loads((HERE / 'hand_local_sections.json').read_text(encoding='utf-8'))
RESULT = pose.solve(ARM['parts'], ARM['master_plane_y_mm'], terminals, outer_joints)


class LaminaFitTests(unittest.TestCase):
    def test_joints_land_on_the_lamina(self):
        residuals = RESULT['residuals_mm']
        self.assertLess(residuals['hombro'], 1.0)
        self.assertLess(residuals['codo'], 5.0)
        self.assertLess(residuals['fin_antebrazo'], pose.TOLERANCE_MM)

    def test_segment_lengths_are_the_lamina_ones(self):
        lamina = pose.LAMINA_MM
        self.assertAlmostEqual(RESULT['lengths_mm']['hombro_codo'],
                               math.dist(lamina['hombro'], lamina['codo']), places=1)
        self.assertAlmostEqual(RESULT['lengths_mm']['codo_rotula'],
                               math.dist(lamina['codo'], lamina['fin_antebrazo']), places=1)

    def test_pose_angles_are_the_drawn_ones(self):
        # Brazo superior algo hacia atrás y codo doblado hacia delante; los
        # signos dependen del sentido de los ejes, las magnitudes no.
        self.assertTrue(8 <= abs(RESULT['theta_shoulder_deg']) <= 20, RESULT['theta_shoulder_deg'])
        self.assertTrue(35 <= abs(RESULT['theta_elbow_deg']) <= 60, RESULT['theta_elbow_deg'])

    def test_shoulder_and_elbow_axes_are_side_to_side(self):
        for axis in (RESULT['shoulder_axis'], RESULT['elbow_axis']):
            self.assertGreater(abs(axis[0]), .9)
            self.assertEqual(axis[1], 0.0)


class GeometryTests(unittest.TestCase):
    def test_forearm_scaling_keeps_elbow_end_and_cross_sections(self):
        original = ARM['parts']['forearm']['sections']
        scaled = RESULT['parts']['forearm']['sections']
        self.assertEqual(scaled[-1][0], original[-1][0])
        for old, new in zip(original, scaled):
            self.assertEqual(old[1:], new[1:])
        self.assertIsNot(RESULT['parts'], ARM['parts'])
        self.assertNotIn('length_factor', ARM['parts']['forearm'])

    def test_scaled_forearm_uses_the_same_stable_profiles(self):
        # Sin forzarlo, alargar añadiría un perfil terminal junto al codo
        # (15 -> 16): se detectó con esta prueba. Se conservan los índices.
        original = ARM['parts']['forearm']['sections']
        scaled = RESULT['parts']['forearm']['sections']
        old = local_filter.stable_run(original)
        new = pose.stable_like_original(local_filter, original, scaled)
        self.assertEqual((old['start'], old['stop']), (new['start'], new['stop']))
        self.assertEqual(len(new['sections']), len(old['sections']))
        # Y el tramo alargado sigue siendo seguro para el loft.
        worst = max(local_filter.transition_ratio(a, b)
                    for a, b in zip(new['sections'], new['sections'][1:]))
        self.assertLessEqual(worst, old['maximum_ratio'])

    def test_elbow_geometry_still_valid_after_scaling(self):
        spec = terminals.elbow_parameters(RESULT['parts'], ARM['master_plane_y_mm'])
        self.assertTrue(12 <= spec['radius'] <= 22)

    def test_shoulder_housing_fits_the_shell_at_the_pivot(self):
        # En el pivote, el perfil superior (18 mm de ancho) ya no sirve: el
        # taladro no saldría por los costados y el disco sobresaldría.
        width, depth = RESULT['shoulder_section_mm']
        length, radius = RESULT['shoulder_size_mm']
        self.assertAlmostEqual(length, width)
        self.assertLessEqual(radius, depth / 2 - pose.SHOULDER_WALL_MM)
        self.assertEqual(radius, pose.SHOULDER_DISC_RADIUS_MM)
        spec = outer_joints.parameters(
            RESULT['parts'], ARM['master_plane_y_mm'],
            shoulder_center=RESULT['shoulder_center_flat'],
            shoulder_size=RESULT['shoulder_size_mm'])['shoulder']
        self.assertGreater(spec['axle_length'], width)   # el eje atraviesa la carcasa

    def test_default_shoulder_is_unchanged(self):
        default = outer_joints.parameters(ARM['parts'], ARM['master_plane_y_mm'])
        self.assertAlmostEqual(default['shoulder']['center'][2], 742.1, places=0)

    def test_hand_moves_with_the_wrist(self):
        # La mano se construyó pegada a la muñeca original: tras colocarla,
        # su muñeca coincide con la rótula del antebrazo colocado.
        wrist = RESULT['hand'].point(HAND['wrist_center_mm'])
        self.assertLess(math.dist(wrist, RESULT['placed_mm']['muneca_rotula']), 1e-6)


class RigidTests(unittest.TestCase):
    def test_transforms_are_rigid(self):
        points = [HAND['wrist_center_mm'], HAND['thumb_path_mm'][0],
                  HAND['finger_paths_mm'][0][-1], HAND['finger_paths_mm'][3][-1]]
        for name in ('upper', 'forearm', 'hand'):
            t = RESULT[name]
            m = t.matrix
            for i in range(3):
                for j in range(3):
                    self.assertAlmostEqual(sum(m[k][i] * m[k][j] for k in range(3)),
                                           1.0 if i == j else 0.0, places=9)
            for a in points:
                for b in points:
                    self.assertAlmostEqual(math.dist(t.point(a), t.point(b)),
                                           math.dist(a, b), places=6)

    def test_array16_is_row_major_in_cm(self):
        t = RESULT['forearm']
        array = t.array16_cm()
        p = (10.0, 20.0, 30.0)
        moved = tuple(sum(array[r * 4 + c] * p[c] * .1 for c in range(3)) + array[r * 4 + 3]
                      for r in range(3))
        for got, expected in zip(moved, t.point(p)):
            self.assertAlmostEqual(got * 10, expected, places=6)
        self.assertEqual(array[12:], [0.0, 0.0, 0.0, 1.0])


if __name__ == '__main__':
    unittest.main()
