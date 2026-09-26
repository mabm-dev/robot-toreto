"""Pure geometry-parameter checks; these do not replace Fusion BRep tests."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import toreto_clearance as clearance
import toreto_hand as hand


class ClearanceTests(unittest.TestCase):
    def test_narrow_hinges_fit_spacing_without_moving_joint_centers(self):
        data = json.loads(Path(__file__).with_name('hand_local_sections.json').read_text())
        self.assertLess(hand.MAIN_HINGE_LENGTH_MM + 2*hand.MAIN_PIN_OVERHANG_MM,
                        data['finger_root_spacing_mm'] - .7)
        specs = hand.joint_specs(data)
        for finger, path in enumerate(data['finger_paths_mm']):
            for joint, center in enumerate(path[:-1]):
                self.assertEqual(specs[finger*4+joint]['center_mm'], center)

    def test_trial_axes_preserve_centers_and_main_fingers(self):
        data = json.loads(Path(__file__).with_name('hand_local_sections.json').read_text())
        with patch.object(hand, 'THUMB_AXIS_ANGLES_DEG', (52.0, 128.0)):
            previous = hand.joint_specs(data)
        current = hand.joint_specs(data)
        self.assertEqual(current[:16], previous[:16])
        self.assertEqual(hand.THUMB_AXIS_ANGLES_DEG, (0.0, 76.0))
        for old, new in zip(previous[16:], current[16:]):
            self.assertEqual(old['center_mm'], new['center_mm'])
            self.assertEqual(old['minimum_deg'], new['minimum_deg'])
            self.assertEqual(old['maximum_deg'], new['maximum_deg'])
            self.assertNotEqual(old['axis'], new['axis'])
            self.assertAlmostEqual(sum(v * v for v in new['axis']), 1.0)

    def test_all_twenty_central_sleeves_match_generator(self):
        data = json.loads(Path(__file__).with_name('hand_local_sections.json').read_text())
        specs = hand.joint_specs(data)
        by_child = {s['child']: s for s in specs}
        self.assertEqual(len(specs), 20)
        for spec in specs:
            label = spec['pin_label'].replace('PASADOR', 'CASQUILLO_CENTRAL')
            with patch.object(hand, '_cylinder', side_effect=lambda *args: args):
                tools = clearance.sleeve_tools(None, hand, data, label, spec, .35)
            self.assertEqual(len(tools), 2)
            self.assertEqual(tools[0][1], spec['center_mm'])
            self.assertEqual(tools[0][2], spec['axis'])
            self.assertAlmostEqual(tools[1][5], 1.60)
            self.assertAlmostEqual(tools[0][3], -tools[0][4])
            if label.startswith('08_DEDO_'):
                self.assertAlmostEqual(tools[0][4], hand.MAIN_HINGE_LENGTH_MM*.21+.35)
            self.assertGreater(tools[0][5], 6.0)
            self.assertLessEqual(len(clearance.chain_for(spec['child'], by_child)), 4)

    def test_sampling_bound_scales_with_resolution(self):
        spec = {'center_mm': (0, 0, 0), 'minimum_deg': -60, 'maximum_deg': 0}
        coarse = clearance.displacement_bound([(10, 0, 0)], [spec], 60)
        fine = clearance.displacement_bound([(10, 0, 0)], [spec], 120)
        self.assertAlmostEqual(coarse, 2 * fine)
        self.assertGreater(fine, 0)


if __name__ == '__main__':
    unittest.main()
