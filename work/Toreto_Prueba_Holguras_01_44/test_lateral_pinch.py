"""v10 scenario and contact-face checks, without Fusion."""
import json
from pathlib import Path
import unittest

import toreto_contact_faces as faces
import toreto_clearance as clearance
import toreto_hand as hand
import toreto_motor_groups as groups


DATA = json.loads(Path(__file__).with_name('hand_local_sections.json').read_text())


def tiny_box(point, half=0.01):
    return ([value - half for value in point],
            [value + half for value in point])


class LateralScenarioTests(unittest.TestCase):
    def test_v8_scenarios_are_unchanged(self):
        self.assertEqual(len(groups.SCENARIOS), 5)
        self.assertEqual(groups.SCENARIOS[-1][0], 'pinza_boli')
        self.assertEqual(groups.LATERAL_PINCH_SCENARIO[0], 'pinza_lateral')

    def test_cardan_is_prepositioned_and_only_two_motors_close(self):
        start = groups.lateral_pinch(0)
        end = groups.lateral_pinch(1)
        self.assertEqual(start, {'pulgar_rotacion': 1, 'indice': 0,
                                 'pulgar_flexion': 0})
        self.assertEqual(end, {'pulgar_rotacion': 1, 'indice': 1,
                               'pulgar_flexion': .26})
        for step in range(13):
            fractions = groups.lateral_pinch(step / 12)
            self.assertAlmostEqual(fractions['pulgar_flexion'],
                                   .26 * fractions['indice'])
            self.assertNotIn('resto', fractions)

    def test_existing_ratios_at_contact_range(self):
        specs = hand.joint_specs(DATA)
        from toreto_clearance import signed_travel
        for step in (10, 11):
            t = step / 12
            angles = groups.pose_angles(specs, groups.lateral_pinch(t), signed_travel)
            self.assertEqual(angles['JUNTA_PULGAR_1'], 30)
            self.assertAlmostEqual(angles['JUNTA_PULGAR_2'], 40 * .26 * t)
            self.assertAlmostEqual(angles['JUNTA_PULGAR_3'], 35 * .26 * t)
            self.assertAlmostEqual(angles['JUNTA_PULGAR_4'], 20 * .26 * t)
            self.assertAlmostEqual(angles['JUNTA_DEDO_1_1'], -54 * t)

    def test_fraction_outside_range_is_rejected(self):
        for value in (-.01, 1.01):
            with self.assertRaises(ValueError):
                groups.lateral_pinch(value)


class ContactFaceTests(unittest.TestCase):
    def setUp(self):
        self.fractions = groups.lateral_pinch(10 / 12)
        self.frame = faces.terminal_frame(DATA, self.fractions, 'pulgar',
                                          hand, clearance, groups)
        _, side, depth, _, length, half_width, half_depth, bend = self.frame
        choices = [(side, half_width, 'side'), (depth, half_depth, 'depth')]
        axis, half, name = max(choices, key=lambda row: abs(faces.dot(row[0], bend)))
        self.assertGreaterEqual(abs(faces.dot(axis, bend)), .7)
        self.palmar_axis = faces.scale(axis, 1 if faces.dot(axis, bend) > 0 else -1)
        self.palmar_half = half
        lateral = next(row for row in choices if row[2] != name)
        self.lateral_axis, self.lateral_half = lateral[:2]
        self.length = length

    def classify(self, point, half=.01, label=groups.THUMB_TIP):
        low, high = tiny_box(point, half)
        return faces.classify_overlap(DATA, self.fractions, 'pulgar', label,
                                      low, high, hand, clearance, groups)

    def test_palmar_dorsal_and_lateral_are_distinct(self):
        for direction, expected in ((self.palmar_axis, 'palmar'),
                                    (faces.scale(self.palmar_axis, -1), 'dorsal'),
                                    (self.lateral_axis, 'lateral')):
            magnitude = (self.lateral_half if expected == 'lateral'
                         else self.palmar_half) * .9
            point = faces.add(faces.world_point(self.frame, self.length * .4, 0, 0),
                              faces.scale(direction, magnitude))
            self.assertEqual(self.classify(point)['region'], expected)

    def test_tip_and_transition_are_not_called_palmar(self):
        base = faces.world_point(self.frame, self.length * .82, 0, 0)
        point = faces.add(base, faces.scale(self.palmar_axis,
                                           self.palmar_half * .7))
        self.assertEqual(self.classify(point)['region'], 'punta')
        edge = faces.world_point(self.frame, self.length * .68, 0, 0)
        self.assertEqual(self.classify(edge, half=.2)['region'],
                         'transicion_plano_punta')

    def test_nonterminal_contact_is_explicit(self):
        point = faces.world_point(self.frame, self.length * .4, 0, 0)
        self.assertEqual(self.classify(point, label='09_PULGAR_FALANGE_2')['region'],
                         'otra_falange')

    def test_corner_and_outside_are_not_mistaken_for_a_grip_face(self):
        corner = faces.world_point(self.frame, self.length * .4,
                                   self.frame[5] * .9, self.frame[6] * .9)
        self.assertEqual(self.classify(corner)['region'],
                         'esquina_indeterminada')
        outside = faces.world_point(self.frame, self.length * 1.02, 0, 0)
        self.assertEqual(self.classify(outside)['region'],
                         'borde_o_fuera_de_falange')


if __name__ == '__main__':
    unittest.main()
