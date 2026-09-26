"""Pruebas de la mano de 4 motores (v7). Parámetros puros, sin Fusion.

No sustituyen el ensayo BRep: comprueban que el reparto de motores y los
escenarios son los que se pretende, antes de gastar una ejecución en Fusion.
"""
import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch

import toreto_clearance as clearance
import toreto_hand as hand
import toreto_motor_groups as groups

DATA = json.loads(Path(__file__).with_name('hand_local_sections.json').read_text())


class MotorGroupTests(unittest.TestCase):
    def test_every_joint_has_exactly_one_motor(self):
        specs = hand.joint_specs(DATA)
        self.assertEqual(len(specs), 20)
        counts = {motor: 0 for motor in groups.MOTORS}
        for spec in specs:
            counts[groups.motor_of(spec['name'])] += 1
        self.assertEqual(counts, {'indice': 4, 'resto': 12,
                                  'pulgar_flexion': 3, 'pulgar_rotacion': 1})

    def test_index_is_the_finger_closest_to_the_thumb(self):
        # Si alguien reordena los dedos, la pinza se probaria con el dedo
        # equivocado. Esto lo detecta.
        thumb_base = DATA['thumb_path_mm'][0]
        distances = [math.dist(thumb_base, path[0]) for path in DATA['finger_paths_mm']]
        self.assertEqual(distances.index(min(distances)) + 1, groups.INDEX_FINGER)

    def test_tip_labels_match_generator_structure(self):
        # 07_DEDO_1_FALANGE_4 exige 4 segmentos; 09_PULGAR_FALANGE_3 exige que
        # thumb_path tenga 4 puntos (el generador arma 3 falanges desde ahi).
        index_path = DATA['finger_paths_mm'][groups.INDEX_FINGER - 1]
        self.assertEqual(len(index_path) - 1, int(groups.INDEX_TIP.rsplit('_', 1)[1]))
        self.assertEqual(len(DATA['thumb_path_mm']) - 1, int(groups.THUMB_TIP.rsplit('_', 1)[1]))

    def test_solo_scenarios_start_open_and_move_only_their_motor(self):
        for name, _, fraction_fn in groups.SCENARIOS:
            if name not in groups.SOLO_SCENARIOS:
                continue
            self.assertTrue(all(v == 0 for v in fraction_fn(0.0).values()), name)
            closed = fraction_fn(1.0)
            self.assertEqual([m for m, v in closed.items() if v], [next(iter(closed))], name)
            self.assertEqual(closed[next(iter(closed))], 1.0, name)

    def test_pinch_starts_with_thumb_rotated_and_keeps_other_fingers_open(self):
        pinch = next(fn for name, _, fn in groups.SCENARIOS if name == 'pinza_boli')
        start, end = pinch(0.0), pinch(1.0)
        self.assertEqual(start.get('pulgar_rotacion'), 1.0)
        self.assertEqual(start.get('indice'), 0.0)
        self.assertEqual(start.get('pulgar_flexion'), 0.0)
        self.assertEqual(end.get('indice'), 1.0)
        self.assertEqual(end.get('pulgar_flexion'), 1.0)
        self.assertEqual(start.get('resto', 0.0), 0.0)
        self.assertEqual(end.get('resto', 0.0), 0.0)

    def test_equal_fractions_reproduce_old_synchronized_pose(self):
        # Garantiza que la nueva postura por motores no cambia la cinematica:
        # con todos los motores a la misma fraccion, los angulos son los
        # mismos que aplicaba el ensayo sincronizado de la v6.
        specs = {s['child']: s for s in hand.joint_specs(DATA)}
        for group in specs:
            chain = clearance.chain_for(group, specs)
            for fraction in (0.0, 0.37, 1.0):
                same = {motor: fraction for motor in groups.MOTORS}
                new = groups.joint_angles(chain, same, clearance.signed_travel)
                old = [(s['name'], clearance.signed_travel(s) * fraction)
                       for s in reversed(chain)]
                self.assertEqual(new, old, group)

    def test_static_bodies_are_skipped_only_when_really_static(self):
        specs = {s['child']: s for s in hand.joint_specs(DATA)}
        index_chain = clearance.chain_for('MANO_01_FALANGE_04', specs)
        thumb_chain = clearance.chain_for('MANO_05_PULGAR_FALANGE_03', specs)
        scenarios = {name: fn for name, _, fn in groups.SCENARIOS}
        self.assertFalse(groups.moves_in(index_chain, scenarios['resto_solo_senalar'], 12))
        self.assertTrue(groups.moves_in(index_chain, scenarios['indice_solo'], 12))
        # En la pinza el cardan esta girado desde la muestra 0: el pulgar NO
        # esta en su postura abierta aunque la flexion empiece en 0.
        self.assertTrue(groups.moves_in(thumb_chain, scenarios['pinza_boli'], 12))
        self.assertFalse(groups.moves_in(thumb_chain, scenarios['indice_solo'], 12))

    def test_pinch_contact_counts_only_thumb_and_index_phalanges(self):
        self.assertTrue(groups.is_pinch_contact('09_PULGAR_FALANGE_3', '07_DEDO_1_FALANGE_4'))
        self.assertTrue(groups.is_pinch_contact('07_DEDO_1_FALANGE_3', '09_PULGAR_FALANGE_2'))
        # Dedo corazon: no es la pinza.
        self.assertFalse(groups.is_pinch_contact('09_PULGAR_FALANGE_3', '07_DEDO_2_FALANGE_4'))
        # Casquillos, pasadores y cardan: choque de mecanismo, no pinza.
        self.assertFalse(groups.is_pinch_contact('10_PULGAR_NUDILLO_2_CASQUILLO_B', '07_DEDO_1_FALANGE_4'))
        self.assertFalse(groups.is_pinch_contact('09_PULGAR_FALANGE_3', '08_DEDO_1_NUDILLO_4_PASADOR'))
        self.assertFalse(groups.is_pinch_contact('09_PULGAR_CARDAN_INTERMEDIO', '07_DEDO_1_FALANGE_1'))

    def test_unknown_joint_is_rejected(self):
        with self.assertRaises(ValueError):
            groups.motor_of('JUNTA_MUNECA_1')


class IndexLimitTests(unittest.TestCase):
    """v8: el indice con su propio recorrido (90%)."""

    # Ultima muestra limpia del indice solo en la v7: 11 de 12 (choque en la 12).
    V7_LAST_CLEAN_FRACTION = 11 / 12

    def test_index_travels_ninety_percent_of_the_other_fingers(self):
        for new, old in zip(hand.INDEX_FLEXION_LIMITS_DEG, hand.MAIN_FLEXION_LIMITS_DEG):
            self.assertAlmostEqual(new, old * hand.INDEX_TRAVEL_SCALE)

    def test_new_range_stays_inside_what_v7_measured_clean(self):
        # Si alguien sube la escala por encima del tramo medido limpio, falla.
        self.assertLessEqual(hand.INDEX_TRAVEL_SCALE, self.V7_LAST_CLEAN_FRACTION)

    def test_only_the_index_changes(self):
        specs = hand.joint_specs(DATA)
        for spec in specs:
            if not spec['name'].startswith('JUNTA_DEDO_'):
                continue
            finger, joint = (int(v) for v in spec['name'].split('_')[2:4])
            expected = (hand.INDEX_FLEXION_LIMITS_DEG if finger == hand.INDEX_FINGER
                        else hand.MAIN_FLEXION_LIMITS_DEG)[joint - 1]
            self.assertEqual(spec['travel_deg'], expected, spec['name'])
            self.assertEqual(spec['minimum_deg'], -expected, spec['name'])

    def test_new_index_motion_is_the_first_ninety_percent_of_v7(self):
        # El argumento del cambio, comprobado: el indice en t recorre lo mismo
        # que el de la v7 en 0,9*t. Todo su recorrido nuevo ya lo midio la v7.
        new_specs = {s['child']: s for s in hand.joint_specs(DATA)}
        with patch.object(hand, 'INDEX_FLEXION_LIMITS_DEG', hand.MAIN_FLEXION_LIMITS_DEG):
            old_specs = {s['child']: s for s in hand.joint_specs(DATA)}
        for group in ('MANO_01_FALANGE_01', 'MANO_01_FALANGE_02',
                      'MANO_01_FALANGE_03', 'MANO_01_FALANGE_04'):
            new_chain = clearance.chain_for(group, new_specs)
            old_chain = clearance.chain_for(group, old_specs)
            for step in range(13):
                t = step / 12
                new = groups.joint_angles(new_chain, {'indice': t}, clearance.signed_travel)
                old = groups.joint_angles(old_chain, {'indice': hand.INDEX_TRAVEL_SCALE * t},
                                          clearance.signed_travel)
                for (name_n, deg_n), (name_o, deg_o) in zip(new, old):
                    self.assertEqual(name_n, name_o)
                    self.assertAlmostEqual(deg_n, deg_o, places=9)

    def test_index_constant_matches_between_modules(self):
        self.assertEqual(hand.INDEX_FINGER, groups.INDEX_FINGER)


class PinchViewTests(unittest.TestCase):
    """v9: publicar la mano con 4 motores y colocarla en la pinza."""

    def setUp(self):
        self.specs = hand.joint_specs(DATA)
        self.by_name = {s['name']: s for s in self.specs}

    def test_link_plan_is_one_relation_per_follower(self):
        plan = groups.motion_link_plan(self.specs)
        self.assertEqual(len(plan), 16)
        followers = [f for _, f in plan]
        self.assertEqual(len(followers), len(set(followers)))
        # Nunca en cadena: ninguna maestra es a la vez seguidora.
        self.assertFalse(set(m for m, _ in plan) & set(followers))
        # El cardan va suelto.
        self.assertNotIn('JUNTA_PULGAR_1', followers)
        self.assertNotIn('JUNTA_PULGAR_1', [m for m, _ in plan])

    def test_links_never_cross_motors(self):
        for master, follower in groups.motion_link_plan(self.specs):
            self.assertEqual(groups.motor_of(master), groups.motor_of(follower))

    def test_link_ratio_reproduces_the_trial_pose(self):
        # Una relacion lineal maestra->seguidora con los recorridos de cada
        # junta da, a cualquier fraccion, el mismo angulo que el ensayo.
        for master, follower in groups.motion_link_plan(self.specs):
            m, f = self.by_name[master], self.by_name[follower]
            for t in (0.25, 0.75, 1.0):
                angles = groups.pose_angles(self.specs, {groups.motor_of(master): t},
                                            clearance.signed_travel)
                ratio = f['travel_deg'] / m['travel_deg']
                self.assertAlmostEqual(abs(angles[follower]),
                                       abs(angles[master]) * ratio, places=9)

    def test_view_is_sample_nine_of_the_v8_pinch(self):
        self.assertEqual(groups.PINCH_VIEW_FRACTION, 0.75)
        pinch = next(fn for name, _, fn in groups.SCENARIOS if name == 'pinza_boli')
        self.assertEqual(groups.pinch_view_fractions(), pinch(9 / 12))

    def test_pose_angles_match_the_trial_chains(self):
        fractions = groups.pinch_view_fractions()
        angles = groups.pose_angles(self.specs, fractions, clearance.signed_travel)
        specs = {s['child']: s for s in self.specs}
        for group in specs:
            chain = clearance.chain_for(group, specs)
            for name, degrees in groups.joint_angles(chain, fractions, clearance.signed_travel):
                self.assertEqual(angles[name], degrees, name)

    def test_pinch_view_angles(self):
        angles = groups.pose_angles(self.specs, groups.pinch_view_fractions(),
                                    clearance.signed_travel)
        self.assertAlmostEqual(angles['JUNTA_PULGAR_1'], 30.0)
        self.assertAlmostEqual(angles['JUNTA_PULGAR_2'], 30.0)
        self.assertAlmostEqual(angles['JUNTA_DEDO_1_1'], -40.5)
        self.assertEqual(angles['JUNTA_DEDO_2_1'], 0.0)


if __name__ == '__main__':
    unittest.main()
