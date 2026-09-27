"""Exercise the v10/v10b transient-solid control flow with INVENTED overlaps.

No Fusion geometry is validated. The output goes to the system temp folder.
"""
import json
import importlib.util
import sys
import tempfile
import types
from pathlib import Path

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))
import simular_sin_fusion as old_sim


class Manager(old_sim.Mgr):
    def __init__(self, contact_point_mm, early_collision=False, no_contact=False,
                 broken_intersection=False, between_threshold=None,
                 intersection_scale=1.0):
        self.contact_point_mm = contact_point_mm
        # v10b: la interseccion directa mide distinto que la penetracion por
        # diferencia (lo que abortó la v10 en Fusion); 0 = interseccion vacia.
        self.intersection_scale = intersection_scale
        self.early_collision = early_collision
        self.no_contact = no_contact
        self.broken_intersection = broken_intersection
        # Choque ajeno a la pinza que empieza ENTRE las muestras 9 y 10,
        # antes del contacto: solo el afinado puede verlo como previo.
        self.between_threshold = between_threshold

    def penetration(self, a, b):
        pair = {a.label, b.label}
        if self.between_threshold is not None and pair == {
                '10_PULGAR_NUDILLO_4_CASQUILLO_A', '07_DEDO_1_FALANGE_4'}:
            return max(0.0, a.closure + b.closure - self.between_threshold)
        if self.early_collision and pair == {
                '09_PULGAR_CARDAN_INTERMEDIO', '10_PULGAR_NUDILLO_1_PASADOR'}:
            return 5.0 if max(a.closure, b.closure) > 20 else 0.0
        if not self.no_contact and pair == {
                '09_PULGAR_FALANGE_3', '07_DEDO_1_FALANGE_4'}:
            return max(0.0, a.closure + b.closure - 205)
        return 0.0

    def booleanOperation(self, target, tool, kind):
        volume = self.penetration(target, tool) / 1000
        if kind == 1:  # Difference
            target.volume -= volume
        elif kind == 2:  # Intersection
            if self.broken_intersection:
                return False
            target.volume = volume * self.intersection_scale
            point = self.contact_point_mm
            target.boundingBox = types.SimpleNamespace(
                minPoint=old_sim.P(*(value / 10 - .001 for value in point)),
                maxPoint=old_sim.P(*(value / 10 + .001 for value in point)))
            target.isSolid = True
            target.lumps = types.SimpleNamespace(count=1)
        else:
            raise AssertionError('Operador booleano no simulado')
        return True


def contact_point(data, fractions, face_name):
    import toreto_contact_faces as faces
    import toreto_hand as hand
    import toreto_clearance as clearance
    import toreto_motor_groups as groups
    frame = faces.terminal_frame(data, fractions, 'pulgar',
                                 hand, clearance, groups)
    _, side, depth, _, length, half_width, half_depth, bend = frame
    choices = ((side, half_width), (depth, half_depth))
    axis, radius = max(choices, key=lambda item: abs(faces.dot(item[0], bend)))
    sign = 1 if faces.dot(axis, bend) > 0 else -1
    if face_name == 'dorsal':
        sign *= -1
    elif face_name != 'palmar':
        raise ValueError(face_name)
    return faces.add(faces.world_point(frame, length * .4, 0, 0),
                     faces.scale(axis, sign * radius * .9))


def main():
    old_sim._install_fake_adsk()
    script_spec = importlib.util.spec_from_file_location(
        'toreto_script_v10', SRC / 'Toreto_Prueba_Holguras_01_44.py')
    script = importlib.util.module_from_spec(script_spec)
    script_spec.loader.exec_module(script)
    # El modo activo puede ser otro (v11: 'ver_brazo'); el ensayo lateral no
    # cambia y se simula igual.
    assert script.SCRIPT_VERSION in ('v10b', 'v11', 'v12'), script.SCRIPT_VERSION
    import adsk.fusion
    adsk.fusion.BooleanTypes.IntersectionBooleanType = 2
    import toreto_hand as hand
    import toreto_clearance as clearance
    import toreto_motor_groups as groups
    import toreto_contact_faces as faces
    import toreto_motor_validation as base_validation
    import toreto_lateral_validation as validation
    data = json.loads((SRC / 'hand_local_sections.json').read_text(encoding='utf-8'))
    pending = old_sim._fake_pending(hand, data)
    fractions = groups.lateral_pinch(10 / 12)
    for face_name in ('palmar', 'dorsal'):
        point = contact_point(data, fractions, face_name)
        out = Path(tempfile.gettempdir()) / ('toreto_v10b_falso_' + face_name + '.json')
        report = validation.run(Manager(point), hand, clearance, groups,
                                base_validation, faces, pending, data, out)
        assert report['first_contact']['sample'] == 10, report
        assert report['first_contact']['pairs'][0]['pulgar']['region'] == face_name, report
        assert len(report['samples']) == 11
        # Afinado: 5 bisecciones entre 9/12 y 10/12; el contacto falso empieza
        # donde la suma de cierres pasa de 205 (t ~ 0,819).
        assert len(report['refinement']) == validation.REFINE_STEPS, report
        refined = report['first_contact']['fraction']
        bracket = report['refined_bracket']
        assert 9 / 12 < bracket['last_clean_fraction'] < refined <= 10 / 12, report
        assert refined - bracket['last_clean_fraction'] <= (1 / 12) / 2 ** 5 + 1e-9
        assert closure_sum(data, refined) > 205 >= closure_sum(
            data, bracket['last_clean_fraction']), report
        assert not report['prior_collisions'] and not report['errors'], report
        assert not report['warnings'], report
        stability = report['first_contact']['stability']
        assert len(stability['postures']) == validation.MAX_CONTACT_STATES, report
        assert stability['consistent'], report
        if face_name == 'palmar':
            assert report['status'] == 'apoyo_palmar_lateral_en_muestra', report
        assert json.loads(out.read_text(encoding='utf-8'))['status'] == report['status']
        if face_name == 'dorsal':
            assert report['status'] == 'contacto_cara_no_deseada_o_indeterminada'
        print('SIMULACION', face_name, report['status'], 'muestra',
              report['first_contact']['sample'], 'JSON', out)
    for case, options, expected in (
            ('choque_previo', {'early_collision': True}, 'choque_previo_a_contacto'),
            ('sin_contacto', {'no_contact': True}, 'sin_contacto_en_12_pasos'),
            ('interseccion_rota', {'broken_intersection': True}, 'cara_no_resuelta')):
        out = Path(tempfile.gettempdir()) / ('toreto_v10b_falso_' + case + '.json')
        point = contact_point(data, fractions, 'palmar')
        report = validation.run(Manager(point, **options), hand, clearance,
                                groups, base_validation, faces, pending, data, out)
        assert report['status'] == expected, report
        assert json.loads(out.read_text(encoding='utf-8'))['status'] == expected
        print('SIMULACION', case, expected, 'JSON', out)
    # Choque ajeno que empieza en t = 0,79, antes del contacto (t ~ 0,819).
    # Sin afinar, la muestra 10 mostraría ambos a la vez; afinando, el choque
    # aparece como PREVIO al contacto.
    threshold = closure_sum(data, .79, ('MANO_05_PULGAR_FALANGE_02', 'MANO_01_FALANGE_04'))
    out = Path(tempfile.gettempdir()) / 'toreto_v10b_falso_choque_entre_muestras.json'
    report = validation.run(Manager(contact_point(data, fractions, 'palmar'),
                                    between_threshold=threshold),
                            hand, clearance, groups, base_validation, faces,
                            pending, data, out)
    assert report['status'] == 'choque_previo_a_contacto', report
    assert report['first_contact'] is None, report
    first = report['prior_collisions'][0]
    assert .75 < first['refine_fraction'] < .8, report
    print('SIMULACION choque_entre_muestras', report['status'],
          'afinado', first['refine_fraction'], 'JSON', out)

    # v10b: lo que pasó en Fusion. La intersección directa mide un 30% de la
    # penetración: antes abortaba la cara; ahora avisa y clasifica igual.
    point = contact_point(data, fractions, 'palmar')
    out = Path(tempfile.gettempdir()) / 'toreto_v10b_falso_volumen_discrepante.json'
    report = validation.run(Manager(point, intersection_scale=.3), hand, clearance,
                            groups, base_validation, faces, pending, data, out)
    assert report['status'] == 'apoyo_palmar_lateral_en_muestra', report
    assert report['warnings'] and not report['errors'], report
    pair = report['first_contact']['pairs'][0]
    assert pair['intersection_mm3'] < pair['penetration_mm3'], report
    print('SIMULACION volumen_discrepante', report['status'], 'avisos',
          len(report['warnings']), 'JSON', out)
    # Intersección vacía: el contacto no se da por confirmado.
    out = Path(tempfile.gettempdir()) / 'toreto_v10b_falso_interseccion_vacia.json'
    report = validation.run(Manager(point, intersection_scale=0.0), hand, clearance,
                            groups, base_validation, faces, pending, data, out)
    assert report['first_contact']['pairs'][0]['pulgar']['region'] == 'contacto_no_confirmado'
    assert report['status'] == 'contacto_cara_no_deseada_o_indeterminada', report
    print('SIMULACION interseccion_vacia', report['status'], 'JSON', out)


def closure_sum(data, t, groups_=('MANO_05_PULGAR_FALANGE_03', 'MANO_01_FALANGE_04')):
    """Giro total aplicado a cada cuerpo falso, igual que Mgr.transform."""
    import toreto_hand as hand
    import toreto_clearance as clearance
    import toreto_motor_groups as groups
    by_child = {spec['child']: spec for spec in hand.joint_specs(data)}
    return sum(abs(degrees) for group in groups_
               for _, degrees in groups.joint_angles(
                   clearance.chain_for(group, by_child), groups.lateral_pinch(t),
                   clearance.signed_travel))


if __name__ == '__main__':
    main()
