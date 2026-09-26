"""Mano adaptativa de CUATRO motores: qué mueve cada motor y qué prueba la v7.

Decisión del usuario, 26-09-2026: la mano debe coger como una humana (un
boli con pulgar e índice, una pelota pequeña, un vaso). Un único motor rígido
solo tiene una postura cerrada y no puede; cuatro motores sí:

  indice           -> JUNTA_DEDO_1_1..4   (DEDO_1 = índice, ver abajo)
  resto            -> JUNTA_DEDO_2..4_*   (corazón, anular y meñique juntos)
  pulgar_flexion   -> JUNTA_PULGAR_2..4
  pulgar_rotacion  -> JUNTA_PULGAR_1      (el cardán: lo pone enfrente o al
                                            lado del índice)

DEDO_1 es el índice porque su base es la más cercana a la del pulgar (55 mm
frente a 58/64/73 mm, `hand_local_sections.json`). Lo comprueba una prueba
unitaria, para que si alguien reordena los dedos falle en vez de probar la
pinza con el dedo equivocado.

Por qué cambia el ensayo: con un solo motor, el cierre simultáneo de toda la
mano ERA el movimiento real. Con cuatro motores no: cada motor se mueve por
su cuenta, y cerrar los cinco dedos a la vez hasta el final exige algo que la
mano no hará nunca (y que ninguna mano con pulgar oponible puede hacer sin
que el pulgar acabe dentro de los dedos). Ese ensayo se sustituye por:

  - cada motor solo, con el resto de la mano quieta y abierta;
  - la pinza del boli: pulgar girado enfrente del índice, y pulgar e índice
    cerrando a la vez.

Módulo puro: no importa adsk, para poder probarlo fuera de Fusion.
"""

INDEX_FINGER = 1

MOTORS = ('indice', 'resto', 'pulgar_flexion', 'pulgar_rotacion')

THUMB_PHALANX_PREFIX = '09_PULGAR_FALANGE_'
INDEX_PHALANX_PREFIX = '07_DEDO_{}_FALANGE_'.format(INDEX_FINGER)
THUMB_TIP = '09_PULGAR_FALANGE_3'
INDEX_TIP = '07_DEDO_{}_FALANGE_4'.format(INDEX_FINGER)


def motor_of(joint_name):
    """Motor que acciona una articulación del generador (`joint_specs`)."""
    if joint_name.startswith('JUNTA_DEDO_{}_'.format(INDEX_FINGER)):
        return 'indice'
    if joint_name.startswith('JUNTA_DEDO_'):
        return 'resto'
    if joint_name == 'JUNTA_PULGAR_1':
        return 'pulgar_rotacion'
    if joint_name.startswith('JUNTA_PULGAR_'):
        return 'pulgar_flexion'
    raise ValueError('Articulacion sin motor asignado: ' + joint_name)


def _solo(motor):
    return lambda t: {motor: t}


def _pinch(t):
    # El cardán va entero desde la primera muestra: la pinza empieza con el
    # pulgar ya colocado enfrente del índice, y solo entonces cierran ambos.
    # Corazón, anular y meñique se quedan extendidos, fuera del camino.
    return {'pulgar_rotacion': 1.0, 'indice': t, 'pulgar_flexion': t}


# (nombre, descripción, fracción de cada motor en función de t = 0..1).
# Un motor ausente del diccionario está a 0: mano abierta en esa parte.
SCENARIOS = (
    ('indice_solo',
     'Solo el indice cierra; el resto de la mano quieta y abierta.',
     _solo('indice')),
    ('resto_solo_senalar',
     'Corazon, anular y menique cierran con el indice extendido: '
     'es la postura de SENALAR.',
     _solo('resto')),
    ('pulgar_flexion_solo',
     'Solo se flexiona el pulgar, sin girar el cardan.',
     _solo('pulgar_flexion')),
    ('pulgar_rotacion_solo',
     'Solo gira el cardan del pulgar. Comprueba tambien la correccion del '
     'taladro: el unico choque con la mano abierta de la v6 estaba aqui.',
     _solo('pulgar_rotacion')),
    ('pinza_boli',
     'Pulgar girado enfrente del indice; indice y flexion del pulgar cierran '
     'a la vez; corazon, anular y menique extendidos.',
     _pinch),
)

SOLO_SCENARIOS = tuple(name for name, _, _ in SCENARIOS if name != 'pinza_boli')


def joint_angles(chain, fractions, signed_travel):
    """Ángulos (grados) a aplicar, en el orden en que los aplica `pose`.

    Mismo orden que `toreto_clearance.pose`: primero la articulación más
    distal, luego sus antecesoras, cada una sobre su eje en posición neutra.
    Si todos los motores tienen la misma fracción, el resultado es idéntico
    al del ensayo sincronizado anterior (lo comprueba una prueba unitaria).
    """
    return [(spec['name'],
             signed_travel(spec) * fractions.get(motor_of(spec['name']), 0.0))
            for spec in reversed(chain)]


# Articulación maestra de cada motor en Fusion. Las demás del mismo motor la
# siguen con una relación de movimiento directa (nunca en cadena).
MOTOR_MASTERS = {
    'indice': 'JUNTA_DEDO_{}_1'.format(INDEX_FINGER),
    'resto': 'JUNTA_DEDO_2_1',
    'pulgar_flexion': 'JUNTA_PULGAR_2',
    'pulgar_rotacion': 'JUNTA_PULGAR_1',
}

# Vista de la pinza (v9): muestra 9 de 12 del ensayo de la v8, la última
# antes del contacto (hueco entre puntas 0,28 mm). En la 10 ya solapan.
PINCH_VIEW_FRACTION = 9 / 12


def motion_link_plan(specs):
    """Pares (maestra, seguidora) de la mano de 4 motores: 3 + 11 + 2 + 0."""
    names = {spec['name'] for spec in specs}
    for master in MOTOR_MASTERS.values():
        if master not in names:
            raise ValueError('Falta la articulacion maestra ' + master)
    return [(MOTOR_MASTERS[motor_of(spec['name'])], spec['name'])
            for spec in specs
            if spec['name'] != MOTOR_MASTERS[motor_of(spec['name'])]]


def pose_angles(specs, fractions, signed_travel):
    """Ángulo (grados, sobre el eje de `spec`) de cada articulación en una
    postura. Son los mismos que aplica `joint_angles` en el ensayo."""
    return {spec['name']: signed_travel(spec) * fractions.get(motor_of(spec['name']), 0.0)
            for spec in specs}


def pinch_view_fractions():
    return _pinch(PINCH_VIEW_FRACTION)


def moves_in(chain, fraction_fn, intervals):
    """True si algún eslabón de la cadena sale de la postura abierta en algún
    momento del escenario. Si dos cuerpos no se mueven, su par ya está
    cubierto por la comprobación de mano abierta y no se repite."""
    for sample in range(intervals + 1):
        fractions = fraction_fn(sample / intervals)
        if any(fractions.get(motor_of(spec['name']), 0.0) != 0.0 for spec in chain):
            return True
    return False


def is_pinch_contact(label_a, label_b):
    """Contacto que ES la pinza: una falange del pulgar con una del índice.

    Casquillos, pasadores y cardán tocándose no son pinza, son choque del
    mecanismo, y se cuentan aparte."""
    thumb = lambda label: label.startswith(THUMB_PHALANX_PREFIX)
    index = lambda label: label.startswith(INDEX_PHALANX_PREFIX)
    return (thumb(label_a) and index(label_b)) or (thumb(label_b) and index(label_a))
