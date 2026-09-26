"""Conservative palm-only clearance trial; no document or occurrence mutation.

The 121 samples follow each digit's existing coupled motion. Inflated enclosing
boxes include a Lipschitz displacement bound between samples plus 0.35 mm.
Central sleeves use their generating cylinders instead of enclosing boxes.
This is a clearance candidate, not a strength or manufacturing validation.
"""
import itertools
import math

SAMPLES = 120
CLEARANCE_MM = 0.35
PALM = 'MANO_00_PALMA'


def diagnose_exact_thumb(manager, hand, pending, data, report_path):
    """Sample exact thumb solids against a temporary palm; never publish CAD.

    Zero extra clearance and discrete sampling are diagnostic only. Even a
    complete pass cannot authorize manufacturing or imply continuous clearance.
    """
    import adsk
    import adsk.fusion
    import json
    by_child = {s['child']: s for s in hand.joint_specs(data)}
    palm = manager.copy(next(b for b, label, _, _ in pending
                             if label == '06_PALMA_Y_CONECTOR'))
    original_volume = palm.volume
    report = {'mode': 'exact_thumb_independent_poses_only', 'extra_clearance_mm': 0,
              'samples_per_body': SAMPLES + 1, 'status': 'running', 'completed': [],
              'body_results': []}

    def record():
        report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')

    record()
    for body, label, _, group in pending:
        if not group.startswith('MANO_05_'):
            continue
        chain = chain_for(group, by_child)
        result = {'body': label, 'max_intrusion_mm3': 0, 'split_samples': []}
        for sample in range(SAMPLES + 1):
            report.update(body=label, sample=sample)
            if sample % 10 == 0:
                record()
                adsk.doEvents()
            placed = pose(manager, body, chain, sample / SAMPLES)
            if not overlaps(palm, placed):
                continue
            candidate = manager.copy(palm)
            try:
                success = manager.booleanOperation(candidate, placed,
                    adsk.fusion.BooleanTypes.DifferenceBooleanType)
            except RuntimeError as error:
                report.update(status='kernel_error', error=str(error))
                record()
                return report
            if not success or not candidate.isValid:
                report.update(status='invalid_boolean')
                record()
                return report
            if not candidate.isSolid or candidate.lumps.count != 1:
                result['split_samples'].append(sample)
            intrusion = max(0, original_volume - candidate.volume) * 1000
            if intrusion > result['max_intrusion_mm3']:
                result.update(max_intrusion_mm3=intrusion, worst_sample=sample)
            # Deliberately do not accumulate cuts: isolate each exact pose.
        report['completed'].append(label)
        report['body_results'].append(result)
    report.update(status='independent_poses_complete_not_clearance_validated')
    record()
    return report


def distance(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def chain_for(group, by_child):
    chain = []
    while group != PALM:
        spec = by_child[group]
        chain.append(spec)
        group = spec['parent']
        if len(chain) > 4:
            raise ValueError('Cadena cinematica ciclica o inesperada')
    return list(reversed(chain))


def displacement_bound(corners_mm, chain, samples=SAMPLES):
    """Upper bound to nearest sample for any point in the uninflated box."""
    reach = max(distance(p, chain[-1]['center_mm']) for p in corners_mm)
    speed = 0.0
    for index in range(len(chain) - 1, -1, -1):
        if index < len(chain) - 1:
            reach += distance(chain[index]['center_mm'], chain[index + 1]['center_mm'])
        speed += reach * math.radians(abs(signed_travel(chain[index])))
    return speed / (2.0 * samples)


def signed_travel(spec):
    return spec['minimum_deg'] if spec['minimum_deg'] < 0 else spec['maximum_deg']


def corners(box):
    result = []
    for signs in itertools.product((-1, 1), repeat=3):
        p = box.centerPoint.copy()
        for sign, direction, size in zip(signs,
                (box.lengthDirection, box.widthDirection, box.heightDirection),
                (box.length, box.width, box.height)):
            v = direction.copy()
            v.scaleBy(sign * size * 0.5)
            p.translateBy(v)
        result.append((p.x * 10, p.y * 10, p.z * 10))
    return result


def pose(manager, body, chain, fraction):
    import adsk.core
    result = manager.copy(body)
    if not result:
        raise RuntimeError('No se pudo copiar herramienta')
    # Local rotations first, then ancestors around their neutral world axes.
    for spec in reversed(chain):
        transform = adsk.core.Matrix3D.create()
        center = adsk.core.Point3D.create(*(v * .1 for v in spec['center_mm']))
        axis = adsk.core.Vector3D.create(*spec['axis'])
        if not transform.setToRotation(math.radians(signed_travel(spec) * fraction), axis, center):
            raise RuntimeError('Rotacion invalida')
        if not manager.transform(result, transform):
            raise RuntimeError('No se pudo transformar herramienta')
    return result


def overlaps(a, b):
    aa, bb = a.boundingBox, b.boundingBox
    return all(getattr(aa.minPoint, axis) <= getattr(bb.maxPoint, axis) and
               getattr(bb.minPoint, axis) <= getattr(aa.maxPoint, axis)
               for axis in ('x', 'y', 'z'))


def intersection_volume(manager, a, b):
    import adsk.fusion
    if not overlaps(a, b):
        return 0.0
    copy = manager.copy(a)
    if not copy or not manager.booleanOperation(copy, b, adsk.fusion.BooleanTypes.IntersectionBooleanType):
        raise RuntimeError('Fallo de interseccion; no se presume ausencia de colision')
    return copy.volume if copy.isValid and copy.lumps.count else 0.0


def sleeve_tools(manager, hand, data, label, spec, padding_mm):
    """Enclose the exact sleeve + stop-rail primitives, including clearance.

    The bore need not be retained in a cutter. Both cylinders are expanded
    radially and axially; this contains a padding-radius neighbourhood.
    Dimensions deliberately come from the same generator as the moving body.
    """
    if label.startswith('08_DEDO_'):
        finger = int(label.split('_')[2])
        joint = int(label.split('_')[4])
        path = data['finger_paths_mm'][finger - 1]
        left = hand.FINGER_DIMENSIONS_MM[max(0, joint - 2)]
        right = hand.FINGER_DIMENSIONS_MM[min(3, joint - 1)]
        total = hand.MAIN_HINGE_LENGTH_MM
        radius = 5.8
    elif label.startswith('10_PULGAR_'):
        path = data['thumb_path_mm']
        radius,total,_,_=hand.hinge_dimensions(spec)
    else:
        raise ValueError('Casquillo desconocido: ' + label)
    direction = hand._unit(tuple(path[-1][i] - path[0][i] for i in range(3)))
    center = spec['center_mm']
    rail_center = tuple(center[i] + direction[i] *
                        (radius - hand.HINGE_STOP_RADIAL_OVERLAP_MM) for i in range(3))
    half = total * .42 * .5 + padding_mm
    return [hand._cylinder(manager, c, spec['axis'], -half, half, r + padding_mm, label)
            for c, r in ((center, radius), (rail_center, hand.HINGE_STOP_RADIUS_MM))]


def repair(manager, hand, pending, data, progress=None):
    import adsk.core
    import adsk.fusion
    app = adsk.core.Application.get()
    specs = hand.joint_specs(data)
    by_child = {spec['child']: spec for spec in specs}
    palm_index = next(i for i, item in enumerate(pending) if item[1] == '06_PALMA_Y_CONECTOR')
    original = pending[palm_index][0]
    palm = manager.copy(original)
    original_volume = palm.volume
    cutters = []
    for body, label, appearance, group in pending:
        if group == PALM:
            continue
        chain = chain_for(group, by_child)
        axis = adsk.core.Vector3D.create(*chain[-1]['axis'])
        helper = adsk.core.Vector3D.create(0, 1, 0)
        if abs(axis.dotProduct(helper)) > .9:
            helper = adsk.core.Vector3D.create(1, 0, 0)
        other = axis.crossProduct(helper)
        other.normalize()
        box = app.measureManager.getOrientedBoundingBox(body, axis, other)
        if not box:
            raise RuntimeError('Sin envolvente: ' + label)
        padding_mm = CLEARANCE_MM + displacement_bound(corners(box), chain)
        if label.endswith('CASQUILLO_CENTRAL'):
            for index, tool in enumerate(sleeve_tools(
                    manager, hand, data, label, chain[-1], padding_mm)):
                cutters.append((tool, chain, label + '_ENV_' + str(index), None))
            continue
        enlarged = adsk.core.OrientedBoundingBox3D.create(
            box.centerPoint, box.lengthDirection, box.widthDirection,
            box.length + padding_mm * .2, box.width + padding_mm * .2,
            box.height + padding_mm * .2)
        tool = manager.createBox(enlarged)
        if not tool:
            raise RuntimeError('Sin herramienta: ' + label)
        cutters.append((tool, chain, label, enlarged))
    cuts = 0
    retries = []
    for tool, chain, label, box in cutters:
        if progress:
            progress(label, cuts, palm.volume / original_volume * 100)
        # Base sleeve's circular cylinder is invariant about its own axis.
        # Cutting it 121 times creates coincident faces without adding clearance.
        samples = (0,) if len(chain) == 1 and label.endswith('_ENV_0') else range(SAMPLES + 1)
        for sample in samples:
            placed = pose(manager, tool, chain, sample / SAMPLES)
            if not overlaps(palm, placed):
                continue
            # Failed boolean operations may leave their target unusable. Commit
            # only a successful copy. A larger box still contains the original
            # swept envelope: no sample or clearance region is silently omitted.
            last_error = None
            for extra_mm in ((0, .01, .025, .05) if box else (0,)):
                candidate = manager.copy(palm)
                if not candidate:
                    raise RuntimeError('No se pudo copiar la palma para el corte')
                if extra_mm:
                    expanded = adsk.core.OrientedBoundingBox3D.create(
                        box.centerPoint, box.lengthDirection, box.widthDirection,
                        box.length + extra_mm * .2, box.width + extra_mm * .2,
                        box.height + extra_mm * .2)
                    retry_tool = manager.createBox(expanded)
                    if not retry_tool:
                        raise RuntimeError('No se pudo crear la envolvente ampliada')
                    placed = pose(manager, retry_tool, chain, sample / SAMPLES)
                try:
                    succeeded = manager.booleanOperation(candidate, placed, adsk.fusion.BooleanTypes.DifferenceBooleanType)
                except RuntimeError as error:
                    last_error = str(error)
                    continue
                if not succeeded:
                    last_error = 'booleanOperation devolvio False'
                    continue
                palm = candidate
                if extra_mm:
                    retries.append((label, sample, extra_mm))
                break
            else:
                raise RuntimeError('Corte rechazado: {} muestra {}: {}'.format(label, sample, last_error))
            cuts += 1
            if not palm.isValid or not palm.isSolid or palm.lumps.count != 1:
                raise RuntimeError('CORTE RECHAZADO: palma dividida por {} en muestra {}'.format(label, sample))
        adsk.doEvents()
    if palm.volume < original_volume * .65:
        raise RuntimeError('CORTE RECHAZADO: se retiraria mas del 35% de la palma')
    # Retain connection to the eight fixed finger sleeves and two thumb sleeves.
    supports = [(body, label) for body, label, _, group in pending
                if group == PALM and label.endswith(('CASQUILLO_A', 'CASQUILLO_B'))]
    for body, label in supports:
        if progress:
            progress('CHECK_SUPPORT_' + label, cuts, palm.volume / original_volume * 100)
        before = intersection_volume(manager, original, body)
        after = intersection_volume(manager, palm, body)
        if before <= 1e-6 or after < max(.01, before * .1):
            raise RuntimeError('CORTE RECHAZADO: apoyo insuficiente en ' + label)
    result = list(pending)
    item = pending[palm_index]
    result[palm_index] = (palm, item[1], item[2], item[3])
    return result, ('Holguras de prueba: {} cortes; {:.1f}% volumen conservado; '
        'envolventes conservadoras, 121 posturas por cadena y margen 0.35 mm. '
        'Ejes y cuerpos moviles intactos. NO validado para fabricar. '
        'Reintentos con margen adicional (mm): {}').format(
            cuts, palm.volume / original_volume * 100, retries)
