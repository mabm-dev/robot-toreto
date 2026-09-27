"""Juntas de la mano izquierda, copiada por simetría en Fusion (v12). Puro.

El usuario montó el robot así (27-09-2026): borró el brazo antiguo, insertó
el brazo v11 con la mano de 4 motores y creó el izquierdo con Crear >
Simetría respecto al plano YZ (X = 0). La simetría copia la geometría pero
NO las juntas ni las relaciones: la mano izquierda queda rígida.

Este módulo calcula dónde deben estar los ejes de la mano izquierda. Al
reflejar, un punto va a M·p, con M = diag(-1, 1, 1). Un EJE DE GIRO no: es un
pseudovector. Girar θ alrededor de `a` y luego reflejar equivale a reflejar y
girar θ alrededor de -M·a (porque M·R(a,θ)·M = R(det(M)·M·a, θ) y det(M) = -1).
Con -M·a y los mismos límites, cada dedo izquierdo cierra hacia su palma.
Tomar M·a haría que los dedos izquierdos se doblaran hacia fuera.
"""

MIRROR_X = ((-1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


def mirror_point(p):
    return (-p[0], p[1], p[2])


def mirror_axis(a):
    """Eje de giro reflejado en X = 0: -M·a."""
    return (a[0], -a[1], -a[2])


def base_name(name):
    """Nombre sin el sufijo que añade Fusion a las copias: 'X(Simetría)' -> 'X'."""
    return name.split('(')[0].strip()


def _det(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def matrix_from_array16_cm(array):
    """(L, t_mm) de una Matrix3D de Fusion (asArray, por filas, en cm)."""
    linear = tuple(tuple(array[r * 4 + c] for c in range(3)) for r in range(3))
    return linear, tuple(array[r * 4 + 3] * 10 for r in range(3))


def compose(outer, inner):
    """outer ∘ inner: primero inner, luego outer. Cada uno (L, t_mm)."""
    (lo, to), (li, ti) = outer, inner
    linear = tuple(tuple(sum(lo[i][k] * li[k][j] for k in range(3)) for j in range(3))
                   for i in range(3))
    shift = tuple(sum(lo[i][k] * ti[k] for k in range(3)) + to[i] for i in range(3))
    return linear, shift


def to_local_specs(specs, placement):
    """Juntas en coordenadas del robot -> coordenadas internas del componente
    colocado con `placement` (L, t_mm; L ortogonal, con o sin reflexión).

    Fusion hace la simetría de componentes guardando la geometría reflejada
    dentro del componente y colocándolo girado (en la v12 real: 180° en Y).
    Los bordes que ve el script están en esas coordenadas internas.
    """
    linear, shift = placement
    inverse = tuple(tuple(linear[k][i] for k in range(3)) for i in range(3))  # L^-1 = L^T
    sign = 1 if _det(inverse) > 0 else -1        # un eje es un pseudovector

    def apply(m, v):
        return tuple(sum(m[i][k] * v[k] for k in range(3)) for i in range(3))
    result = []
    for spec in specs:
        moved = dict(spec)
        moved['center_mm'] = list(apply(inverse, tuple(c - s for c, s in
                                                       zip(spec['center_mm'], shift))))
        moved['axis'] = [sign * v for v in apply(inverse, spec['axis'])]
        result.append(moved)
    return result


def mirrored_specs(specs, hand_rigid):
    """Juntas de la mano derecha colocada (hand_rigid) llevadas a la izquierda."""
    result = []
    for spec in specs:
        moved = dict(spec)
        moved['center_mm'] = list(mirror_point(hand_rigid.point(spec['center_mm'])))
        moved['axis'] = list(mirror_axis(hand_rigid.vector(spec['axis'])))
        result.append(moved)
    return result
