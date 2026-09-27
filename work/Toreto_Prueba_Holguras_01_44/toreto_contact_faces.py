"""Classify the first solid overlap against the terminal gripping faces.

Pure geometry: no Fusion import. The overlap is located with its world-space
bounding box, so corner or flat-to-curved transitions are reported as
uncertain rather than silently called palmar contact.
"""
import itertools
import math

def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def scale(a, factor):
    return tuple(x * factor for x in a)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def unit(a):
    length = math.sqrt(dot(a, a))
    if length < 1e-9:
        raise ValueError('Vector nulo al clasificar contacto')
    return scale(a, 1 / length)


def rotate(vector, axis, degrees):
    axis = unit(axis)
    radians = math.radians(degrees)
    return add(add(scale(vector, math.cos(radians)),
                   scale(cross(axis, vector), math.sin(radians))),
               scale(axis, dot(axis, vector) * (1 - math.cos(radians))))


def terminal_frame(data, fractions, digit, hand, clearance, groups):
    """Posed frame (origin, side, depth, ray, length, width/2, depth/2, bend)."""
    if digit == 'pulgar':
        path = data['thumb_path_mm']
        first, second = path[2:4]
        trim_start, trim_end = 3.0, 0.3
        width, depth = hand.THUMB_DIMENSIONS_MM[2]
        group = 'MANO_05_PULGAR_FALANGE_03'
    elif digit == 'indice':
        path = data['finger_paths_mm'][groups.INDEX_FINGER - 1]
        first, second = path[3:5]
        trim_start, trim_end = 4.2, 0.3
        width, depth = hand.FINGER_DIMENSIONS_MM[3]
        group = 'MANO_01_FALANGE_04'
    else:
        raise ValueError('Digito desconocido: ' + digit)
    ray = unit(sub(second, first))
    origin = add(first, scale(ray, trim_start))
    length = math.dist(first, second) - trim_start - trim_end
    side = unit((ray[2], 0, -ray[0]))
    depth_axis = unit(cross(ray, side))
    by_child = {spec['child']: spec for spec in hand.joint_specs(data)}
    chain = clearance.chain_for(group, by_child)
    last_axis = chain[-1]['axis']
    by_name = {spec['name']: spec for spec in chain}
    for name, degrees in groups.joint_angles(chain, fractions, clearance.signed_travel):
        if degrees == 0:
            continue
        spec = by_name[name]
        center = spec['center_mm']
        origin = add(center, rotate(sub(origin, center), spec['axis'], degrees))
        side = rotate(side, spec['axis'], degrees)
        depth_axis = rotate(depth_axis, spec['axis'], degrees)
        ray = rotate(ray, spec['axis'], degrees)
        last_axis = rotate(last_axis, spec['axis'], degrees)
    bend_sign = 1 if digit == 'pulgar' else -1
    bend = unit(scale(cross(last_axis, ray), bend_sign))
    return origin, side, depth_axis, ray, length, width / 2, depth / 2, bend


def world_point(frame, along, side, depth):
    """Useful for the offline simulator and unit tests; dimensions are mm."""
    return add(add(add(frame[0], scale(frame[3], along)),
                   scale(frame[1], side)), scale(frame[2], depth))


def _box_points(box_min_mm, box_max_mm):
    return itertools.product(*zip(box_min_mm, box_max_mm))


def classify_overlap(data, fractions, digit, label, box_min_mm, box_max_mm,
                     hand, clearance, groups):
    terminal = groups.THUMB_TIP if digit == 'pulgar' else groups.INDEX_TIP
    if label != terminal:
        return {'region': 'otra_falange', 'label': label}
    frame = terminal_frame(data, fractions, digit, hand, clearance, groups)
    origin, side, depth_axis, ray, length, half_width, half_depth, bend = frame
    point = tuple((low + high) / 2 for low, high in zip(box_min_mm, box_max_mm))
    relative = sub(point, origin)
    x, y, z = dot(relative, side), dot(relative, depth_axis), dot(relative, ray)
    axial = [dot(sub(corner, origin), ray) / length
             for corner in _box_points(box_min_mm, box_max_mm)]
    axial_min, axial_max = min(axial), max(axial)
    detail = {'label': label, 'local_mm': [round(x, 3), round(y, 3), round(z, 3)],
              'axial_fraction': round(z / length, 3),
              'axial_span': [round(axial_min, 3), round(axial_max, 3)]}
    if axial_min < 0 or axial_max > 1:
        detail['region'] = 'borde_o_fuera_de_falange'
        return detail
    # The source loft starts tapering at 68% and ends in a curved tip.
    if axial_min >= .68:
        detail['region'] = 'punta'
        return detail
    if axial_max >= .68:
        detail['region'] = 'transicion_plano_punta'
        return detail
    nx, ny = abs(x) / half_width, abs(y) / half_depth
    detail['radial_fraction'] = [round(nx, 3), round(ny, 3)]
    if max(nx, ny) < .5:
        detail['region'] = 'interior_indeterminado'
        return detail
    if abs(nx - ny) < .12:
        detail['region'] = 'esquina_indeterminada'
        return detail
    face = scale(side if nx > ny else depth_axis, 1 if (x if nx > ny else y) >= 0 else -1)
    alignment = dot(face, bend)
    detail['region'] = ('palmar' if alignment >= .7 else
                        'dorsal' if alignment <= -.7 else 'lateral')
    detail['flexion_alignment'] = round(alignment, 3)
    return detail
