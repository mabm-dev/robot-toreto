"""Offline kinematic screening for broad thumb/index pad contact.

This is an approximation of the longitudinal flat portions of the lofts,
not a solid-intersection test or a validated Fusion pose. It never imports
Fusion, writes files, or changes the production generator.
"""
import itertools
import json
import math
from pathlib import Path

import toreto_hand as hand


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def scale(a, k):
    return tuple(x * k for x in a)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def norm(a):
    return math.sqrt(dot(a, a))


def unit(a):
    return scale(a, 1 / norm(a))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def rotate(vector, axis, angle):
    axis = unit(axis)
    radians = math.radians(angle)
    return add(add(scale(vector, math.cos(radians)),
                   scale(cross(axis, vector), math.sin(radians))),
               scale(axis, dot(axis, vector) * (1 - math.cos(radians))))


def rotate_point(point, center, axis, angle):
    return add(center, rotate(sub(point, center), axis, angle))


def place_point(point, joints):
    for center_, axis, angle in reversed(joints):
        point = rotate_point(point, center_, axis, angle)
    return point


def place_vector(vector, joints):
    for _, axis, angle in reversed(joints):
        vector = rotate(vector, axis, angle)
    return vector


def frame(first, second, trim_start, trim_end, width, depth):
    ray = unit(sub(second, first))
    start = add(first, scale(ray, trim_start))
    length = norm(sub(second, first)) - trim_start - trim_end
    lateral = unit((ray[2], 0, -ray[0]))
    face = unit(cross(ray, lateral))
    return (start, lateral, face, ray, length, width / 2, depth / 2)


def place(frame_, joints):
    origin, lateral, face, ray, length, half_width, half_depth = frame_
    # Exactly the order used by the Fusion trial: distal joint, ancestors.
    for center, axis, angle in reversed(joints):
        origin = rotate_point(origin, center, axis, angle)
        lateral = rotate(lateral, axis, angle)
        face = rotate(face, axis, angle)
        ray = rotate(ray, axis, angle)
    return (origin, lateral, face, ray, length, half_width, half_depth)


def center(frame_, along=0.39):
    return add(frame_[0], scale(frame_[3], frame_[4] * along))


def pad_samples(frame_, axis_name, sign):
    origin, lateral, face, ray, length, half_width, half_depth = frame_
    if axis_name == 'x':
        normal, tangent, half_normal, half_tangent = lateral, face, half_width, half_depth
    else:
        normal, tangent, half_normal, half_tangent = face, lateral, half_depth, half_width
    # The source loft has near-full sections through 68% of its length.
    # Sample only its broad straight sides, away from the curved tip.
    for along, sideways in itertools.product((0.18, 0.3, 0.42, 0.54, 0.64),
                                             (-0.7, -0.35, 0, 0.35, 0.7)):
        point = add(add(add(origin, scale(ray, length * along)),
                        scale(tangent, half_tangent * sideways)),
                    scale(normal, sign * half_normal * (1 - 0.1 * along)))
        yield point, along, sideways


def classify_face(normal, bend):
    toward_bend = dot(normal, unit(bend))
    if toward_bend >= .7:
        return 'palmar'
    if toward_bend <= -.7:
        return 'dorsal'
    return 'lateral'


def palmar_normal(frame_, bend):
    faces = (frame_[1], scale(frame_[1], -1),
             frame_[2], scale(frame_[2], -1))
    return max(faces, key=lambda normal: dot(normal, bend))


def score(thumb, index, thumb_axis, index_axis, thumb_bend, index_bend):
    displacement = sub(center(index), center(thumb))
    thumb_direction = thumb[1 if thumb_axis == 'x' else 2]
    index_direction = index[1 if index_axis == 'x' else 2]
    thumb_sign = 1 if dot(displacement, thumb_direction) >= 0 else -1
    index_sign = -1 if dot(displacement, index_direction) >= 0 else 1
    thumb_normal = scale(thumb_direction, thumb_sign)
    index_normal = scale(index_direction, index_sign)
    opposed = -dot(thumb_normal, index_normal)
    thumb_face = list(pad_samples(thumb, thumb_axis, thumb_sign))
    index_face = list(pad_samples(index, index_axis, index_sign))
    nearest = min(((norm(sub(a[0], b[0])), a[1], b[1], a[2], b[2], a[0], b[0])
                   for a in thumb_face for b in index_face), key=lambda row: row[0])
    gap_vector = sub(nearest[6], nearest[5])
    signed_gap = dot(gap_vector, thumb_normal)
    # A negative value indicates face crossing: do not rank it as a contact.
    return dict(distance=nearest[0], opposed=opposed, signed_gap=signed_gap,
                thumb_along=nearest[1], index_along=nearest[2],
                thumb_side=nearest[3], index_side=nearest[4],
                thumb_axis=thumb_axis, index_axis=index_axis,
                thumb_sign=thumb_sign, index_sign=index_sign,
                thumb_face=classify_face(thumb_normal, thumb_bend),
                index_face=classify_face(index_normal, index_bend))


def plausible_interior_pad(result):
    """Conservative screen, not proof of actual BRep contact or clearance."""
    return (result['opposed'] >= .7 and 0 <= result['signed_gap'] <= 2
            and result['distance'] <= 2
            and result['thumb_along'] <= .54 and result['index_along'] <= .54
            and abs(result['thumb_side']) <= .35
            and abs(result['index_side']) <= .35)


def main():
    data = json.loads(Path(__file__).with_name('hand_local_sections.json').read_text(encoding='utf-8'))
    specs = {s['name']: s for s in hand.joint_specs(data)}
    index_path = data['finger_paths_mm'][0]
    thumb_path = data['thumb_path_mm']
    gimbal_end, _ = hand._thumb_mechanism(thumb_path)
    index_frame = frame(index_path[3], index_path[4], 4.2, 0.3,
                        *hand.FINGER_DIMENSIONS_MM[3])
    thumb_frame = frame(thumb_path[2], thumb_path[3], 3.0, 0.3,
                        *hand.THUMB_DIMENSIONS_MM[2])
    def index_at(fraction):
        index_joints = [(specs[f'JUNTA_DEDO_1_{j}']['center_mm'],
                         specs[f'JUNTA_DEDO_1_{j}']['axis'],
                         -hand.INDEX_FLEXION_LIMITS_DEG[j - 1] * fraction)
                        for j in range(1, 5)]
        placed = place(index_frame, index_joints)
        axis = place_vector(specs['JUNTA_DEDO_1_4']['axis'], index_joints)
        bend = scale(cross(axis, placed[3]), -1)
        return placed, bend
    placed_index = index_at(.75)
    thumb_centers = (thumb_path[0], gimbal_end, thumb_path[1], thumb_path[2])
    thumb_axes = tuple(specs[f'JUNTA_PULGAR_{j}']['axis'] for j in range(1, 5))

    v9 = json.loads(Path(__file__).with_name('vista_pinza_v9.json').read_text(encoding='utf-8'))
    for label, joint_names, angles in (
        ('07_DEDO_1_FALANGE_4', [f'JUNTA_DEDO_1_{j}' for j in range(1, 5)],
         tuple(-value * .75 for value in hand.INDEX_FLEXION_LIMITS_DEG)),
        ('09_PULGAR_FALANGE_3', [f'JUNTA_PULGAR_{j}' for j in range(1, 5)],
         (30, 30, 26.25, 15))):
        saved = v9['falanges_frente_al_ensayo'][label]
        joints = [(specs[name]['center_mm'], specs[name]['axis'], angle)
                  for name, angle in zip(joint_names, angles)]
        predicted = place_point(saved['fusion_mm'], joints)
        error = norm(sub(predicted, saved['ensayo_mm']))
        # A bounding-box centre does not rotate rigidly with a loft. This is
        # only a rough pose sanity check, not an exact validation.
        print('Chequeo aproximado centro de envolvente v9:', label,
              'diferencia mm', round(error, 4))

    def evaluate(angles, index=placed_index):
        joints = list(zip(thumb_centers, thumb_axes, angles))
        placed_thumb = place(thumb_frame, joints)
        axis = place_vector(thumb_axes[3], joints)
        bend = cross(axis, placed_thumb[3])
        return [score(placed_thumb, index[0], thumb_axis, index_axis,
                      bend, index[1])
                for thumb_axis, index_axis in itertools.product('xy', repeat=2)]

    baseline = (30.0, 30.0, 26.25, 15.0)
    print('Base v9: indice 0.75, pulgar', baseline)
    for result in evaluate(baseline):
        print('  Caras', result['thumb_axis'], result['index_axis'],
              result['thumb_face'], result['index_face'],
              'distancia_mm', round(result['distance'], 3),
              'desalineacion_deg', round(math.degrees(math.acos(result['opposed'])), 1),
              'punto_pulgar', result['thumb_along'], result['thumb_side'])
    old_candidates = ((.83, (30, 10, 5, 5), 'palmar', 'lateral'),
                      (.83, (25, 40, 15, 5), 'dorsal', 'lateral'),
                      (.8, (25, 20, 35, 20), 'dorsal', 'palmar'))
    for index_fraction in (.65, .75, .8, .83, .9):
        index = index_at(index_fraction)
        broad = 0
        for angles in itertools.product((20, 25, 30), range(10, 41, 5),
                                        range(5, 36, 5), range(0, 21, 5)):
            for result in evaluate(angles, index):
                broad += plausible_interior_pad(result)
        print('Indice', index_fraction, 'caras/puntos que pasan la criba:', broad)
    for index_fraction, angles, thumb_face, index_face in old_candidates:
        valid = [result for result in evaluate(angles, index_at(index_fraction))
                 if plausible_interior_pad(result)]
        if not valid:
            raise AssertionError('La candidata dejo de pasar la criba: ' + str(angles))
        result = min(valid, key=lambda item: item['distance'])
        if (result['thumb_face'], result['index_face']) != (thumb_face, index_face):
            raise AssertionError('Cambio de cara de contacto: ' + str(angles))
        print('CRIBA_ANTERIOR', index_fraction, angles,
              'distancia_mm', round(result['distance'], 3),
              'desalineacion_deg', round(math.degrees(math.acos(result['opposed'])), 1),
              'caras', result['thumb_axis'], result['index_axis'],
              result['thumb_face'], result['index_face'],
              'punto_pulgar', result['thumb_along'], result['thumb_side'],
              'punto_indice', result['index_along'], result['index_side'])
    native = (30, 10, 8.75, 5)
    native_result = min((result for result in evaluate(native, index_at(.83))
                         if result['thumb_face'] == 'palmar'
                         and result['index_face'] == 'lateral'),
                        key=lambda result: result['distance'])
    print('RELACIONES_ACTUALES indice 0.83, pulgar', native,
          'distancia_mm', round(native_result['distance'], 3),
          'desalineacion_deg', round(math.degrees(math.acos(native_result['opposed'])), 1),
          'punto_pulgar', native_result['thumb_along'], native_result['thumb_side'],
          'punto_indice', native_result['index_along'], native_result['index_side'],
          'interior', plausible_interior_pad(native_result))
    native_interior = []
    for index_step in range(78, 91):
        fraction = index_step / 100
        index = index_at(fraction)
        for motor_step in range(15, 41):
            motor_fraction = motor_step / 100
            angles = (30,) + tuple(limit * motor_fraction
                                   for limit in hand.THUMB_FLEXION_LIMITS_DEG[1:])
            for result in evaluate(angles, index):
                if result['thumb_face'] == 'palmar' and result['index_face'] == 'lateral' \
                        and plausible_interior_pad(result):
                    native_interior.append((fraction, motor_fraction, result))
    print('RELACIONES_ACTUALES apoyos interiores en barrido fino:', len(native_interior))
    for fraction, motor_fraction, result in sorted(
            native_interior, key=lambda item: item[2]['distance'])[:5]:
        print('RELACIONES_ACTUALES alternativa', fraction, motor_fraction,
              'distancia_mm', round(result['distance'], 3),
              'desalineacion_deg', round(math.degrees(math.acos(result['opposed'])), 1),
              'punto_pulgar', result['thumb_along'], result['thumb_side'],
              'punto_indice', result['index_along'], result['index_side'])
    index_palmar = []
    for index_step in range(21):
        fraction = index_step / 20
        index, bend = index_at(fraction)
        index_palmar.append((fraction, palmar_normal(index, bend)))
    best = (180.0, None, None)
    best_by_index = {fraction: (180.0, None) for fraction, _ in index_palmar}
    for angles in itertools.product(range(0, 31, 5), range(0, 41, 5),
                                    range(0, 36, 5), range(0, 21, 5)):
        joints = list(zip(thumb_centers, thumb_axes, angles))
        thumb = place(thumb_frame, joints)
        axis = place_vector(thumb_axes[3], joints)
        normal = palmar_normal(thumb, cross(axis, thumb[3]))
        for fraction, index_normal in index_palmar:
            opposed = max(-1.0, min(1.0, -dot(normal, index_normal)))
            angle = math.degrees(math.acos(opposed))
            if angle < best[0]:
                best = (angle, angles, fraction)
            if angle < best_by_index[fraction][0]:
                best_by_index[fraction] = (angle, angles)
    print('MEJOR ALINEACION PALMAR/PALMAR EN REJILLA:', best)
    for fraction in (0.0, .65, .7, .75, .8, .85, .9, 1.0):
        print('MEJOR PALMAR/PALMAR indice', fraction, best_by_index[fraction])


if __name__ == '__main__':
    main()
