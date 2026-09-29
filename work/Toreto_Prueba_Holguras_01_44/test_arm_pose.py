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
# v11: la misma postura sin encajar en el pecho (hombro en el punto de la lámina).
V11 = pose.solve(ARM['parts'], ARM['master_plane_y_mm'], terminals, outer_joints, chest=None)


class LaminaFitTests(unittest.TestCase):
    def test_joints_land_on_the_lamina(self):
        residuals = V11['residuals_mm']
        self.assertLess(residuals['hombro'], 1.0)
        self.assertLess(residuals['codo'], 5.0)
        self.assertLess(residuals['fin_antebrazo'], pose.TOLERANCE_MM)

    def test_segment_lengths_are_the_lamina_ones(self):
        lamina = pose.LAMINA_MM
        self.assertAlmostEqual(V11['lengths_mm']['hombro_codo'],
                               math.dist(lamina['hombro'], lamina['codo']), places=1)
        self.assertAlmostEqual(V11['lengths_mm']['codo_rotula'],
                               math.dist(lamina['codo'], lamina['fin_antebrazo']), places=1)

    def test_pose_angles_are_the_drawn_ones(self):
        # Brazo superior algo hacia atrás y codo doblado hacia delante; los
        # signos dependen del sentido de los ejes, las magnitudes no.
        for result in (V11, RESULT):
            self.assertTrue(8 <= abs(result['theta_shoulder_deg']) <= 25, result['theta_shoulder_deg'])
            self.assertTrue(35 <= abs(result['theta_elbow_deg']) <= 60, result['theta_elbow_deg'])

    def test_shoulder_and_elbow_axes_are_side_to_side(self):
        for axis in (V11['shoulder_axis'], RESULT['shoulder_axis'], RESULT['elbow_axis']):
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
        # v13: el eje va en X y cruza la carcasa en diagonal: algo más largo.
        self.assertGreaterEqual(length, width)
        self.assertAlmostEqual(V11['shoulder_size_mm'][0], V11['shoulder_section_mm'][0])
        # v11 (sin pecho): el disco cabe en la carcasa.
        v11_depth = V11['shoulder_section_mm'][1]
        self.assertLessEqual(V11['shoulder_size_mm'][1], v11_depth / 2 - pose.SHOULDER_WALL_MM)
        # v14: la cápsula blanca redonda es más ancha que el brazo, como en la
        # lámina lateral y el render, pero solo unos milímetros.
        self.assertEqual(radius, pose.SHOULDER_CAP_RADIUS_MM)
        self.assertLessEqual(radius - depth / 2, 5.0)
        # El disco negro deja un aro blanco visible alrededor.
        self.assertGreaterEqual(radius - pose.SHOULDER_FACE['radius'], 8.0)
        spec = outer_joints.parameters(
            RESULT['parts'], ARM['master_plane_y_mm'],
            shoulder_center=RESULT['shoulder_center_flat'],
            shoulder_size=RESULT['shoulder_size_mm'],
            **RESULT['shoulder_overrides'])['shoulder']
        self.assertGreater(spec['outer_length'] + 4, width)   # el taladro sale por los dos lados

    def test_default_shoulder_is_unchanged(self):
        default = outer_joints.parameters(ARM['parts'], ARM['master_plane_y_mm'])
        self.assertAlmostEqual(default['shoulder']['center'][2], 742.1, places=0)

    def test_hand_moves_with_the_wrist(self):
        # La mano se construyó pegada a la muñeca original: tras colocarla,
        # su muñeca coincide con la rótula del antebrazo colocado.
        wrist = RESULT['hand'].point(HAND['wrist_center_mm'])
        self.assertLess(math.dist(wrist, RESULT['placed_mm']['muneca_rotula']), 1e-6)


class ChestFitTests(unittest.TestCase):
    """v13: el hombro encaja en el conector del pecho."""

    def setUp(self):
        self.fit = RESULT['chest_fit']
        self.chest = pose.CHEST_CONNECTOR

    def test_connector_matches_the_chest_generator(self):
        # Toreto_Pecho_Hombros_95cm 2.6.0 con sus parámetros por defecto.
        self.assertAlmostEqual(self.chest['x_inner'], 157.0)
        self.assertAlmostEqual(self.chest['x_outer'], 196.5)
        self.assertAlmostEqual(self.chest['z'], 690.833, places=2)
        self.assertAlmostEqual(self.chest['radius'], 36.5)

    def test_shoulder_pivot_and_axis_are_the_connector_ones(self):
        self.assertLess(self.fit['pivote_a_eje_conector_mm'], 1e-6)
        self.assertEqual(self.fit['eje_hombro'], [1.0, 0.0, 0.0])
        shoulder = RESULT['placed_mm']['hombro']
        self.assertAlmostEqual(shoulder[1], self.chest['y'], places=6)
        self.assertAlmostEqual(shoulder[2], self.chest['z'], places=6)

    def test_bore_receives_the_connector_with_a_wall(self):
        self.assertGreaterEqual(self.fit['taladro_radio_mm'], self.chest['radius'] + .5)
        self.assertGreaterEqual(self.fit['pared_alojamiento_mm'], 5.0)
        low, high = self.fit['alojamiento_x_mm']
        self.assertLess(low, self.chest['x_outer'])     # el conector entra en el brazo
        self.assertGreater(high, self.chest['x_outer'])

    def test_connector_lies_entirely_inside_the_bore(self):
        # v13b: si el conector está dentro del cilindro que se le quita a la
        # carcasa, la carcasa no puede tocarlo, tenga la forma que tenga.
        # (v13 dejaba 1,4 mm fuera y la carcasa inclinada lo rozaba: 1807 mm3.)
        spec = outer_joints.parameters(
            RESULT['parts'], ARM['master_plane_y_mm'],
            shoulder_center=RESULT['shoulder_center_flat'],
            shoulder_size=RESULT['shoulder_size_mm'],
            **RESULT['shoulder_overrides'])['shoulder']
        p1, p2 = (RESULT['upper'].point(p) for p in (spec['bore_p1'], spec['bore_p2']))
        for p in (p1, p2):                                   # coaxial con el conector
            self.assertAlmostEqual(p[1], self.chest['y'], places=6)
            self.assertAlmostEqual(p[2], self.chest['z'], places=6)
        low, high = sorted((p1[0], p2[0]))
        self.assertLess(low, self.chest['x_inner'])
        self.assertGreater(high, self.chest['x_outer'])
        bore_radius = spec['axle_radius'] + pose.SHOULDER_CLEARANCE_MM
        self.assertGreater(bore_radius, self.chest['radius'])

    def test_same_numbers_as_the_chest_generator_source(self):
        # Los discos y el eje se definen en el complemento del pecho y aquí:
        # se lee su código para que no puedan divergir.
        import ast
        source = (HERE.parents[1] / 'cad-toreto' / 'toreto_fusion_95cm' / 'fusion_scripts'
                  / 'Toreto_Pecho_Hombros_95cm' / 'Toreto_Pecho_Hombros_95cm.py')
        tree = ast.parse(source.read_text(encoding='utf-8'))
        parts = next(ast.literal_eval(node.value) for node in ast.walk(tree)
                     if isinstance(node, ast.Assign)
                     and getattr(node.targets[0], 'id', None) == 'shoulder_parts')
        mm = [tuple(v * 10 for v in part) for part in parts]      # r() = 10 mm
        for got, expected in zip(mm[:-1], pose.CHEST_SHOULDER_DISCS):
            for a, b in zip(got, expected):
                self.assertAlmostEqual(a, b)
        shaft = mm[-1]
        self.assertAlmostEqual(shaft[0], self.chest['x_inner'])
        self.assertAlmostEqual(shaft[1], self.chest['x_outer'])
        self.assertAlmostEqual(shaft[2], self.chest['radius'])

    def test_shoulder_discs_do_not_reach_the_arm_shell(self):
        # Los discos de la pieza de hombro (pecho 2.6.0) quedan fuera del
        # brazo: su X máxima, con margen, por debajo de la carcasa del brazo
        # (esquinas de sus perfiles, ya colocadas en la postura).
        up = RESULT['parts']['upper']
        corners = []
        for section in up['sections']:
            c, n, rx, ry = terminals._world_frame(up, section, ARM['master_plane_y_mm'])
            for sx in (-1, 1):
                for sy in (-1, 1):
                    corners.append(RESULT['upper'].point(
                        (c[0] + n[0] * rx * sx, c[1] + ry * sy, c[2] + n[1] * rx * sx)))
        shell_min_x = min(p[0] for p in corners)
        discs_max_x = max(end for _, end, _ in pose.CHEST_SHOULDER_DISCS)
        self.assertGreaterEqual(shell_min_x - discs_max_x, 2.0)
        # Y la pieza es continua: cada tramo empieza donde acaba el anterior,
        # y el eje sigue al último disco.
        edges = [(a, b) for a, b, _ in pose.CHEST_SHOULDER_DISCS]
        for (_, end), (start, _) in zip(edges, edges[1:]):
            self.assertAlmostEqual(end, start)
        self.assertAlmostEqual(edges[-1][1], self.chest['x_inner'])

    def test_cap_starts_after_the_connector_end(self):
        spec = outer_joints.parameters(
            RESULT['parts'], ARM['master_plane_y_mm'],
            shoulder_center=RESULT['shoulder_center_flat'],
            shoulder_size=RESULT['shoulder_size_mm'],
            **RESULT['shoulder_overrides'])['shoulder']
        cap_x = sorted(RESULT['upper'].point(p)[0] for p in (spec['axle_p1'], spec['axle_p2']))
        self.assertGreater(cap_x[0], self.chest['x_outer'])
        self.assertAlmostEqual(cap_x[0], self.chest['x_outer'] + pose.CAP_GAP_MM, places=6)

    def test_elbow_and_forearm_stay_close_to_the_lamina(self):
        self.assertLess(RESULT['residuals_mm']['codo'], 10.0)
        self.assertLess(RESULT['residuals_mm']['fin_antebrazo'], pose.TOLERANCE_MM)


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
