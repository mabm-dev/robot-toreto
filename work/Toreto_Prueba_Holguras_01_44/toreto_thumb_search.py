"""Bounded axis comparison on transient geometry; never publishes components."""
import json

CANDIDATES = ((52, 128), (30, 106), (15, 91), (0, 76), (-15, 61))


def evaluate(manager, hand, clearance, bodies, data, samples, progress):
    import adsk
    import adsk.fusion
    palm = next(b for b, name, _, _ in bodies if name == '06_PALMA_Y_CONECTOR')
    by_child = {s['child']: s for s in hand.joint_specs(data)}
    results = []
    for body, label, _, group in bodies:
        if not group.startswith('MANO_05_'):
            continue
        chain = clearance.chain_for(group, by_child)
        maximum = 0.0
        worst = 0
        for sample in range(samples + 1):
            placed = clearance.pose(manager, body, chain, sample / samples)
            if not clearance.overlaps(palm, placed):
                continue
            target = manager.copy(palm)
            if not target:
                raise RuntimeError('No se pudo copiar la palma')
            try:
                ok = manager.booleanOperation(target, placed,
                    adsk.fusion.BooleanTypes.DifferenceBooleanType)
            except RuntimeError as error:
                return {'status': 'kernel_error', 'body': label,
                        'sample': sample, 'error': str(error)}
            if not ok or not target.isValid:
                return {'status': 'invalid_boolean', 'body': label, 'sample': sample}
            intrusion = max(0, palm.volume - target.volume) * 1000
            if intrusion > maximum:
                maximum, worst = intrusion, sample
        results.append({'body': label, 'max_intrusion_mm3': maximum, 'worst_sample': worst})
        progress(label)
        adsk.doEvents()
    return {'status': 'sampled', 'samples_per_body': samples + 1,
            'max_intrusion_mm3': max(r['max_intrusion_mm3'] for r in results),
            'sum_body_maxima_mm3': sum(r['max_intrusion_mm3'] for r in results),
            'bodies': results}


def run(manager, flat, hand, clearance, data, path):
    report = {'status': 'running', 'scope': 'thumb_to_palm_only_no_clearance',
              'open_centers_preserved': True, 'candidates': []}
    original_angles = hand.THUMB_AXIS_ANGLES_DEG

    def write(label=''):
        report['current_body'] = label
        path.write_text(json.dumps(report, indent=2), encoding='utf-8')

    try:
        for angles in CANDIDATES:
            report['current_angles_deg'] = angles
            write('building')
            hand.THUMB_AXIS_ANGLES_DEG = angles
            bodies, _ = hand.build(manager, flat, data)
            result = evaluate(manager, hand, clearance, bodies, data, 24, write)
            report['candidates'].append({'angles_deg': angles, **result})
            write()
        valid = [r for r in report['candidates'] if r['status'] == 'sampled']
        if not valid:
            report['status'] = 'no_evaluable_candidate'
            return report
        best = min(valid, key=lambda r: r['sum_body_maxima_mm3'])
        report['best_coarse_angles_deg'] = best['angles_deg']
        hand.THUMB_AXIS_ANGLES_DEG = best['angles_deg']
        bodies, _ = hand.build(manager, flat, data)
        report['fine_result'] = evaluate(manager, hand, clearance, bodies, data, 120, write)
        report['status'] = 'comparison_complete_not_full_hand_validation'
        return report
    finally:
        hand.THUMB_AXIS_ANGLES_DEG = original_angles
        write()
