"""Brazo en la postura y las medidas de la lámina (v11). Módulo puro: sin adsk.

Decisión del usuario (27-09-2026): el brazo toma las medidas de la lámina
ya; se ajustará cuando se elijan los servos. El modelo se construye en la
postura de la lámina y esa postura es el cero de las juntas (opción a).

Qué corrige respecto al brazo de prueba (ver
`medicion_brazo/MEDICION_BRAZO_LAMINA.md`):
  - el antebrazo se construía con su longitud PROYECTADA en la vista
    frontal; se alarga hasta la de la lámina (del codo al final de carcasa);
  - el eje del hombro estaba en lo alto de la carcasa; pasa al pivote que
    dibuja la lámina, dentro de la cabeza redondeada del brazo;
  - brazo superior y antebrazo se inclinan en profundidad como en la lámina.

Cómo: todo se sigue construyendo en el marco plano de siempre (la mano y sus
ensayos no cambian) y, antes de publicar, se aplican dos movimientos rígidos:
  T_brazo(p)     = S_lamina + R(eje_hombro, th_hombro) (p - S_plano)
  T_antebrazo(p) = T_brazo(E + R(eje_codo, th_codo) (p - E))
Los ejes de hombro y codo del brazo de prueba ya van de lado a lado (~X),
como en la lámina, así que la postura es literalmente un giro de cada junta.
"""
import copy
import math

# Brazo derecho, lámina calibrada; mm. Lectura sobre rejilla (±3 mm), ver
# medicion_brazo/. El codo es un solo eje, en el centro de la pieza negra de
# enlace: punto medio entre sus dos fijaciones.
LAMINA_MM = {
    'hombro': (196.0, 16.0, 690.0),
    'fijacion_codo_brazo': (228.0, 47.0, 575.5),
    'fijacion_codo_antebrazo': (239.5, 58.6, 509.5),
    'fin_antebrazo': (265.0, -27.5, 402.5),
    'muneca': (268.0, -34.0, 389.0),
}
LAMINA_MM['codo'] = tuple(
    (a + b) / 2 for a, b in zip(LAMINA_MM['fijacion_codo_brazo'],
                                LAMINA_MM['fijacion_codo_antebrazo']))

# Disco oscuro del hombro en el lateral de la lámina: unos 90 mm de diámetro
# (lat_der_brazo_sup.jpg). Es el radio del alojamiento del eje en el pivote.
SHOULDER_DISC_RADIUS_MM = 45.0
# Margen mínimo entre el disco y la cara delantera/trasera de la carcasa.
SHOULDER_WALL_MM = 3.0

# v13: conector negro del hombro DERECHO del pecho, tal como lo genera
# `Toreto_Pecho_Hombros_95cm` 2.5.0 con sus parámetros por defecto (ancho_pecho
# 340, alto_pecho 190 y base+tronco+cintura = 540 mm): cilindro en el eje X de
# cx - r(0,55) a cx + r(2,5), cx = r(17,15), a Y = 0 y Z = 540 + z(18,1),
# radio r(3,65); r = 340/34 mm, z = 190/22,8 mm. El brazo se encaja en él: su
# eje de hombro es coaxial con el conector (dirección X, por Y 0 y Z 690,8).
_R = 340.0 / 34.0
_Z = 190.0 / 22.8
CHEST_CONNECTOR = {
    'x_inner': _R * 17.15 - _R * .55,        # 166,0
    'x_outer': _R * 17.15 + _R * 2.5,        # 196,5
    'y': 0.0,
    'z': 540.0 + _Z * 18.1,                  # 690,83
    'radius': _R * 3.65,                     # 36,5
}
# Holgura radial entre el conector y el taladro del hombro del brazo, y hueco
# entre el extremo del conector y la tapa del eje en la cara exterior.
SHOULDER_CLEARANCE_MM = 0.8
CAP_GAP_MM = 0.8
# Margen del taladro más allá de cada extremo (conector por dentro, alojamiento
# por fuera).
BORE_MARGIN_MM = 2.0

# Tolerancia con la que se comparan las articulaciones con la lámina: la
# lectura es de ±3 mm y los dos laterales discrepan entre sí (38° / 46°).
TOLERANCE_MM = 8.0


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def _scale(a, k):
    return tuple(x * k for x in a)


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _unit(a):
    n = math.sqrt(_dot(a, a))
    return _scale(a, 1 / n)


def rotation(axis, degrees):
    """Matriz 3x3 de giro (regla de la mano derecha) alrededor de `axis`."""
    x, y, z = _unit(axis)
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    t = 1 - c
    return ((t * x * x + c, t * x * y - s * z, t * x * z + s * y),
            (t * x * y + s * z, t * y * y + c, t * y * z - s * x),
            (t * x * z - s * y, t * y * z + s * x, t * z * z + c))


def _apply(matrix, v):
    return tuple(_dot(row, v) for row in matrix)


def _matmul(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3))
                 for i in range(3))


class Rigid:
    """p -> R p + t (mm)."""

    def __init__(self, matrix, translation):
        self.matrix, self.translation = matrix, translation

    @staticmethod
    def about(point, matrix, target=None):
        """Giro `matrix` alrededor de `point`, que acaba en `target`."""
        target = point if target is None else target
        return Rigid(matrix, _sub(target, _apply(matrix, point)))

    def point(self, p):
        return _add(_apply(self.matrix, p), self.translation)

    def vector(self, v):
        return _apply(self.matrix, v)

    def then(self, other):
        """Primero self, luego other."""
        return Rigid(_matmul(other.matrix, self.matrix),
                     _add(_apply(other.matrix, self.translation), other.translation))

    def array16_cm(self):
        """Matriz 4x4 por filas para Matrix3D.setWithArray (Fusion usa cm)."""
        m, t = self.matrix, self.translation
        return [m[0][0], m[0][1], m[0][2], t[0] * .1,
                m[1][0], m[1][1], m[1][2], t[1] * .1,
                m[2][0], m[2][1], m[2][2], t[2] * .1,
                0.0, 0.0, 0.0, 1.0]


def translation(v):
    return Rigid(((1, 0, 0), (0, 1, 0), (0, 0, 1)), tuple(v))


def scale_forearm(parts, factor):
    """Alarga el antebrazo `factor` veces manteniendo fijo su extremo del codo.

    Las secciones van en cm a lo largo del eje, medidas desde el extremo de
    la muñeca; la última es la terminal del codo. Solo cambian las cotas
    longitudinales: anchos, grosores y centros transversales se conservan.
    """
    result = copy.deepcopy(parts)
    sections = result['forearm']['sections']
    top = sections[-1][0]
    for section in sections:
        section[0] = top + (section[0] - top) * factor
    result['forearm']['length_factor'] = factor
    return result


def stable_like_original(local_filter, original_sections, scaled_sections):
    """Misma selección de perfiles estables que en el antebrazo original.

    Alargar reduce los cocientes de transición y `stable_run` admitiría un
    perfil terminal más junto al codo. Eso cambiaría la forma del loft, que
    no se ha probado en Fusion: se conservan los mismos índices. (Con más
    distancia entre perfiles el loft es, si acaso, más seguro de plegar.)
    """
    original = local_filter.stable_run(original_sections)
    start, stop = original['start'], original['stop']
    result = dict(original)
    result['sections'] = scaled_sections[start:stop]
    return result


def section_at(sections, z_cm):
    """Perfil interpolado a la cota `z_cm` del eje (mismas unidades que los
    perfiles: cm). Devuelve (ancho_mm, grosor_mm)."""
    for a, b in zip(sections, sections[1:]):
        if a[0] <= z_cm <= b[0]:
            t = (z_cm - a[0]) / (b[0] - a[0])
            rx = a[3] + (b[3] - a[3]) * t
            ry = a[4] + (b[4] - a[4]) * t
            return rx * 20, ry * 20
    raise ValueError('Cota fuera de los perfiles medidos: {:.2f} cm'.format(z_cm))


def _bisect(fn, low, high, steps=80):
    """Raíz de fn (monótona) en [low, high]."""
    f_low = fn(low)
    for _ in range(steps):
        middle = (low + high) / 2
        if (fn(middle) > 0) == (f_low > 0):
            low, f_low = middle, fn(middle)
        else:
            high = middle
    return (low + high) / 2


def _best_angle(error_fn):
    """Ángulo (grados) que minimiza error_fn: barrido de 0,5° y refinado."""
    best = min((error_fn(a / 2), a / 2) for a in range(-360, 361))[1]
    step = .5
    for _ in range(40):
        step /= 2
        best = min((best - step, best, best + step), key=error_fn)
    return best


def solve(parts, master_y_mm, terminals, outer_joints, lamina=LAMINA_MM,
          chest=CHEST_CONNECTOR):
    """Longitud del antebrazo, pivote del hombro y giros de la postura.

    `terminals` y `outer_joints` son los módulos del generador (sus funciones
    de parámetros son puras). Devuelve un dict con todo lo necesario para
    construir y colocar el brazo, y los residuos frente a la lámina.

    chest (v13, por defecto): el hombro se encaja en el conector del pecho:
    pivote en su eje, eje de giro en X, taladro a su medida y el eje propio
    del brazo reducido a una tapa exterior. chest=None reproduce la v11.
    """
    elbow_l, forearm_end_l, shoulder_l = lamina['codo'], lamina['fin_antebrazo'], lamina['hombro']
    upper_length = math.dist(elbow_l, shoulder_l)
    if chest is not None:
        # Mismo X que la lámina (el pivote es un punto del eje X del conector).
        shoulder_l = (shoulder_l[0], chest['y'], chest['z'])

    def flat_points(factor):
        # Final del antebrazo = centro de la rótula: está en el eje del núcleo
        # a la cota del perfil terminal. El centro del perfil terminal no
        # sirve: incluye la protuberancia lateral de la antigua horquilla (el
        # generador ya lo evita para la muñeca, ver toreto_outer_joints).
        scaled = scale_forearm(parts, factor)
        elbow = terminals.elbow_parameters(scaled, master_y_mm)
        end = outer_joints.parameters(scaled, master_y_mm)['wrist']['center']
        return scaled, elbow, end

    target_forearm = math.dist(elbow_l, forearm_end_l)
    factor = _bisect(lambda k: math.dist(flat_points(k)[1]['center'], flat_points(k)[2])
                     - target_forearm, .5, 3.0)
    scaled, elbow, forearm_end_f = flat_points(factor)
    elbow_f = elbow['center']

    # Pivote del hombro en el marco plano: sobre el eje del brazo superior, a
    # la distancia codo-hombro de la lámina.
    lower, upper = scaled['upper']['front_axis'][1], scaled['upper']['front_axis'][0]
    up = _unit((upper[0] - lower[0], 0.0, upper[2] - lower[2]))
    shoulder_f = _add(elbow_f, _scale(up, upper_length))

    # Alojamiento del eje del hombro en el pivote: tan largo como ancha es la
    # carcasa a esa altura (el taladro sale por los dos costados, hacia el
    # pecho) y con el radio del disco de la lámina, sin salirse por delante
    # ni por detrás.
    along_cm = _dot(_sub(shoulder_f, lower), up) * .1
    width_mm, depth_mm = section_at(scaled['upper']['sections'], along_cm)
    outer_radius = min(SHOULDER_DISC_RADIUS_MM, depth_mm / 2 - SHOULDER_WALL_MM)
    shoulder_overrides = {}
    if chest is None:
        shoulder_size = (width_mm, outer_radius)
    else:
        # Eje en X exacta: atraviesa la carcasa en diagonal (la carcasa baja
        # inclinada ~15° en la vista frontal), así que el alojamiento es algo
        # más largo que el ancho del perfil.
        shoulder_size = (width_mm / abs(up[2]), outer_radius)
        # Taladro = conector + holgura (lo hace outer_joints con axle+0,8);
        # el eje propio del brazo queda como tapa, desde justo después del
        # extremo del conector hasta la cara exterior.
        cap_start = chest['x_outer'] + CAP_GAP_MM - shoulder_l[0]
        cap_end = (shoulder_size[0] + 4.0) / 2
        # v13b: el taladro empieza BORE_MARGIN_MM antes del extremo interior
        # del conector. La carcasa baja inclinada ~15° y, con el taladro solo
        # del largo del alojamiento, rozaba el conector (1807 mm3 en el montaje).
        bore_start = chest['x_inner'] - BORE_MARGIN_MM - shoulder_l[0]
        bore_end = shoulder_size[0] / 2 + BORE_MARGIN_MM
        shoulder_overrides = dict(shoulder_axis=(1.0, 0.0, 0.0),
                                  shoulder_axle_radius=chest['radius'],
                                  shoulder_axle_span=(cap_start, cap_end),
                                  shoulder_bore_span=(bore_start, bore_end))

    joints = outer_joints.parameters(scaled, master_y_mm, shoulder_center=shoulder_f,
                                     shoulder_size=shoulder_size, **shoulder_overrides)
    shoulder_axis = joints['shoulder']['axis']
    elbow_axis = (elbow['normal'][0], 0.0, elbow['normal'][1])
    wrist_f = joints['wrist']['center']

    def upper_pose(theta):
        return Rigid.about(shoulder_f, rotation(shoulder_axis, theta), shoulder_l)

    theta_shoulder = _best_angle(
        lambda a: math.dist(upper_pose(a).point(elbow_f), elbow_l))
    upper_t = upper_pose(theta_shoulder)

    def forearm_pose(theta):
        return Rigid.about(elbow_f, rotation(elbow_axis, theta)).then(upper_t)

    theta_elbow = _best_angle(
        lambda a: math.dist(forearm_pose(a).point(forearm_end_f), forearm_end_l))
    forearm_t = forearm_pose(theta_elbow)

    # La mano se construye pegada a la muñeca ORIGINAL; al alargar el
    # antebrazo la muñeca baja por su eje y la mano la sigue.
    original_wrist = outer_joints.parameters(parts, master_y_mm)['wrist']['center']
    hand_shift = _sub(wrist_f, original_wrist)
    hand_t = translation(hand_shift).then(forearm_t)

    placed = {
        'hombro': upper_t.point(shoulder_f),
        'codo': upper_t.point(elbow_f),
        'fin_antebrazo': forearm_t.point(forearm_end_f),
    }
    placed['muneca_rotula'] = placed['fin_antebrazo']
    # La pieza negra del hombro: el eje entero (v11) o la tapa exterior (v13).
    cap_center_f = tuple((a + b) / 2 for a, b in zip(joints['shoulder']['axle_p1'],
                                                     joints['shoulder']['axle_p2']))
    placed['tapa_hombro'] = upper_t.point(cap_center_f)
    residuals = {name: round(math.dist(placed[name], lamina[key]), 2)
                 for name, key in (('hombro', 'hombro'), ('codo', 'codo'),
                                   ('fin_antebrazo', 'fin_antebrazo'))}
    fit = None
    if chest is not None:
        s = placed['hombro']
        fit = dict(
            pivote_a_eje_conector_mm=round(math.hypot(s[1] - chest['y'], s[2] - chest['z']), 3),
            eje_hombro=[round(v, 6) for v in upper_t.vector(shoulder_axis)],
            taladro_radio_mm=round(chest['radius'] + SHOULDER_CLEARANCE_MM, 2),
            pared_alojamiento_mm=round(outer_radius - chest['radius'] - SHOULDER_CLEARANCE_MM, 2),
            alojamiento_x_mm=[round(s[0] - shoulder_size[0] / 2, 1),
                              round(s[0] + shoulder_size[0] / 2, 1)],
            conector_x_mm=[round(chest['x_inner'], 1), round(chest['x_outer'], 1)],
            taladro_x_mm=[round(s[0] + shoulder_overrides['shoulder_bore_span'][0], 1),
                          round(s[0] + shoulder_overrides['shoulder_bore_span'][1], 1)],
            desplazamiento_hombro_frente_a_lamina_mm=residuals['hombro'])
    return dict(
        parts=scaled, forearm_factor=factor, shoulder_center_flat=shoulder_f,
        shoulder_size_mm=shoulder_size, shoulder_section_mm=(width_mm, depth_mm),
        shoulder_overrides=shoulder_overrides, chest_fit=fit,
        shoulder_cap_center_flat=cap_center_f,
        elbow_center_flat=elbow_f, wrist_center_flat=wrist_f,
        shoulder_axis=shoulder_axis, elbow_axis=elbow_axis,
        theta_shoulder_deg=theta_shoulder, theta_elbow_deg=theta_elbow,
        upper=upper_t, forearm=forearm_t, hand=hand_t, hand_shift_mm=hand_shift,
        placed_mm=placed, residuals_mm=residuals,
        # La rótula va al final de la carcasa; la lámina dibuja debajo unos
        # anillos negros hasta la mano. Se informa, no se exige.
        wrist_vs_lamina_mm=round(math.dist(placed['muneca_rotula'], lamina['muneca']), 2),
        lengths_mm=dict(
            hombro_codo=round(math.dist(shoulder_f, elbow_f), 2),
            codo_fin_antebrazo=round(math.dist(elbow_f, forearm_end_f), 2),
            codo_rotula=round(math.dist(elbow_f, wrist_f), 2)))
