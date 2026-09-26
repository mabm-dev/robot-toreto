"""Read-only transient-solid diagnostic; discrete coordinated motion only."""
import json


def run(manager, hand, clearance, pending, data, report_path, intervals=12):
    import adsk
    import adsk.fusion
    specs = {s['child']: s for s in hand.joint_specs(data)}
    bodies = [(b, label, group, clearance.chain_for(group, specs))
              for b, label, _, group in pending
              if label != '06_PALMA_Y_CONECTOR']
    report = dict(status='running', intervals=intervals, tolerance_mm3=0.01,
                  excluded='Main palm and same-rigid-group pairs',
                  limitation='Discrete synchronized closing only; not independent digit motion or continuous clearance',
                  axes_deg=hand.THUMB_AXIS_ANGLES_DEG, pairs=[], errors=[])
    collisions = {}

    def record():
        report['pairs'] = sorted(collisions.values(), key=lambda p: -p['max_volume_mm3'])
        report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')

    record()
    for sample in range(intervals + 1):
        report['sample'] = sample
        placed = [clearance.pose(manager, b, chain, sample / intervals)
                  for b, _, _, chain in bodies]
        for i, a in enumerate(placed):
            for j in range(i + 1, len(placed)):
                if bodies[i][2] == bodies[j][2] or not clearance.overlaps(a, placed[j]):
                    continue
                try:
                    difference = manager.copy(a)
                    ok = manager.booleanOperation(difference, manager.copy(placed[j]),
                        adsk.fusion.BooleanTypes.DifferenceBooleanType)
                    if not ok or not difference.isValid:
                        raise RuntimeError('Invalid difference; collision unresolved')
                    volume = max(0.0, a.volume - difference.volume) * 1000
                    if volume > report['tolerance_mm3']:
                        key = (i, j)
                        previous = collisions.get(key)
                        if previous is None or volume > previous['max_volume_mm3']:
                            collisions[key] = dict(a=bodies[i][1], b=bodies[j][1],
                                group_a=bodies[i][2], group_b=bodies[j][2],
                                max_volume_mm3=volume, worst_sample=sample)
                except Exception as error:
                    report['errors'].append(dict(a=bodies[i][1], b=bodies[j][1],
                                                sample=sample, error=str(error)))
        record()
        adsk.doEvents()
    report['status'] = ('collisions_detected' if collisions else
                        'unresolved_kernel_errors' if report['errors'] else
                        'sampled_path_clear_not_full_validation')
    record()
    return report
