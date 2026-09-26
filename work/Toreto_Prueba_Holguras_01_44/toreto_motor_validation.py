"""Ensayo de la mano de cuatro motores (desde la v7). Sólidos temporales, solo lectura.

Sustituye al cierre sincronizado de `toreto_pair_validation.py` (que se
conserva sin cambios como historial). Qué comprueba y qué NO:

  1. Mano abierta: todos los pares, una vez.
  2. Cada motor solo (`SOLO_SCENARIOS`): aquí el criterio es CERO choques.
     Un motor moviéndose solo no debería hacer que la mano choque consigo
     misma. Solo se repiten los pares en los que algún cuerpo se mueve.
  3. Pinza del boli: informa de si las falanges de pulgar e índice llegan a
     tocarse, en qué momento, y si choca algo más ANTES de que se toquen.

  NO comprueba: la palma principal (excluida, igual que en la v6; su prueba
  con las medidas actuales está pendiente), holgura continua entre muestras,
  resistencia, ni agarres de objetos (vaso, pelota), que necesitan simular
  el objeto y que cada dedo se detenga al tocarlo.

Un error del núcleo geométrico se registra como NO RESUELTO, nunca como
ausencia de choque. El informe se escribe tras cada muestra, para que un
cierre de Fusion a mitad de ensayo no pierda lo ya calculado.
"""
import json
import math

PALM_BODY = '06_PALMA_Y_CONECTOR'


def _pose(manager, groups, clearance, body, chain, fractions):
    import adsk.core
    result = manager.copy(body)
    if not result:
        raise RuntimeError('No se pudo copiar el cuerpo')
    by_name = {spec['name']: spec for spec in chain}
    for name, degrees in groups.joint_angles(chain, fractions, clearance.signed_travel):
        if degrees == 0.0:
            continue
        spec = by_name[name]
        transform = adsk.core.Matrix3D.create()
        center = adsk.core.Point3D.create(*(v * .1 for v in spec['center_mm']))
        axis = adsk.core.Vector3D.create(*spec['axis'])
        if not transform.setToRotation(math.radians(degrees), axis, center):
            raise RuntimeError('Rotacion invalida en ' + name)
        if not manager.transform(result, transform):
            raise RuntimeError('No se pudo girar ' + name)
    return result


def _penetration_mm3(manager, a, b):
    import adsk.fusion
    difference = manager.copy(a)
    ok = manager.booleanOperation(difference, manager.copy(b),
                                  adsk.fusion.BooleanTypes.DifferenceBooleanType)
    if not ok or not difference.isValid:
        raise RuntimeError('Diferencia invalida; choque NO resuelto')
    return max(0.0, a.volume - difference.volume) * 1000


def _gap_mm(a, b):
    """Distancia mínima entre dos cuerpos temporales, o None si Fusion no la
    da. Es informativa: la pinza se decide por contacto, no por esto."""
    import adsk.core
    try:
        result = adsk.core.Application.get().measureManager.measureMinimumDistance(a, b)
        return round(result.value * 10, 2) if result else None
    except Exception:
        return None


def run(manager, hand, clearance, groups, pending, data, report_path, intervals=12,
        version='v7'):
    import adsk
    specs = {s['child']: s for s in hand.joint_specs(data)}
    bodies = [(body, label, group, clearance.chain_for(group, specs))
              for body, label, _, group in pending if label != PALM_BODY]
    labels = [label for _, label, _, _ in bodies]
    tolerance = 0.01
    report = dict(
        version=version,
        flexion_limits_deg=dict(
            indice=list(hand.finger_flexion_limits(groups.INDEX_FINGER)),
            resto_de_dedos=list(hand.MAIN_FLEXION_LIMITS_DEG),
            pulgar=list(hand.THUMB_FLEXION_LIMITS_DEG)),
        mechanism=('Mano adaptativa de 4 motores: indice / corazon+anular+menique / '
                   'flexion del pulgar / rotacion del pulgar (cardan)'),
        status='running', intervals=intervals, tolerance_mm3=tolerance,
        excluded='Palma principal ({}) y pares del mismo grupo rigido'.format(PALM_BODY),
        limitation=('Posturas discretas. No valida holgura continua, resistencia '
                    'ni agarre de objetos. No es una mano funcional validada.'),
        axes_deg=list(hand.THUMB_AXIS_ANGLES_DEG),
        open_hand=dict(status='running', pairs=[], errors=[]),
        scenarios={})

    def record():
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                               encoding='utf-8')

    def check(i, j, a, b, sample, collisions, errors):
        if bodies[i][2] == bodies[j][2] or not clearance.overlaps(a, b):
            return
        try:
            volume = _penetration_mm3(manager, a, b)
        except Exception as error:
            errors.append(dict(a=labels[i], b=labels[j], sample=sample, error=str(error)))
            return
        if volume <= tolerance:
            return
        entry = collisions.setdefault((i, j), dict(
            a=labels[i], b=labels[j], group_a=bodies[i][2], group_b=bodies[j][2],
            first_sample=sample, worst_sample=sample, max_volume_mm3=0.0, by_sample=[]))
        entry['by_sample'].append([sample, round(volume, 3)])
        if volume > entry['max_volume_mm3']:
            entry.update(max_volume_mm3=round(volume, 3), worst_sample=sample)

    def ordered(collisions):
        return sorted(collisions.values(), key=lambda p: -p['max_volume_mm3'])

    def status_of(collisions, errors):
        return ('choques' if collisions else
                'errores_nucleo_sin_resolver' if errors else 'limpio')

    record()

    # 1. Mano abierta: una sola vez para todos los pares.
    opened = [manager.copy(body) for body, _, _, _ in bodies]
    collisions, errors = {}, []
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            check(i, j, opened[i], opened[j], 0, collisions, errors)
    report['open_hand'].update(status=status_of(collisions, errors),
                               pairs=ordered(collisions), errors=errors)
    record()
    adsk.doEvents()

    # 2 y 3. Cada escenario: solo pares en los que algo se mueve.
    for name, description, fraction_fn in groups.SCENARIOS:
        moving = [groups.moves_in(chain, fraction_fn, intervals)
                  for _, _, _, chain in bodies]
        pairs = [(i, j) for i in range(len(bodies)) for j in range(i + 1, len(bodies))
                 if (moving[i] or moving[j]) and bodies[i][2] != bodies[j][2]]
        scenario = dict(description=description, status='running', sample=0,
                        moving_bodies=sum(moving), checked_pairs=len(pairs),
                        pairs=[], errors=[])
        is_pinch = name == 'pinza_boli'
        if is_pinch:
            scenario['tip_gap_mm_by_sample'] = []
        report['scenarios'][name] = scenario
        collisions, errors = {}, []
        record()
        for sample in range(intervals + 1):
            fractions = fraction_fn(sample / intervals)
            placed = [(_pose(manager, groups, clearance, body, chain, fractions)
                       if moving[k] else opened[k])
                      for k, (body, _, _, chain) in enumerate(bodies)]
            for i, j in pairs:
                check(i, j, placed[i], placed[j], sample, collisions, errors)
            if is_pinch and groups.THUMB_TIP in labels and groups.INDEX_TIP in labels:
                scenario['tip_gap_mm_by_sample'].append([sample, _gap_mm(
                    placed[labels.index(groups.THUMB_TIP)],
                    placed[labels.index(groups.INDEX_TIP)])])
            scenario.update(sample=sample, pairs=ordered(collisions), errors=errors)
            record()
            adsk.doEvents()

        scenario['status'] = status_of(collisions, errors)
        if is_pinch:
            contacts = [p for p in collisions.values()
                        if groups.is_pinch_contact(p['a'], p['b'])]
            others = [p for p in collisions.values()
                      if not groups.is_pinch_contact(p['a'], p['b'])]
            if contacts:
                first = min(contacts, key=lambda p: p['first_sample'])
                contact_sample = first['first_sample']
                before = [p for p in others if p['first_sample'] <= contact_sample]
                scenario['pinch_contact'] = dict(
                    first_sample=contact_sample,
                    first_fraction=round(contact_sample / intervals, 3),
                    pair=[first['a'], first['b']])
                scenario['other_collisions_before_contact'] = sorted(
                    before, key=lambda p: -p['max_volume_mm3'])
                scenario['status'] = ('pinza_lograda' if not before and not errors else
                                      'pinza_con_choques_previos' if before else
                                      'pinza_con_errores_nucleo')
            else:
                scenario['pinch_contact'] = None
                scenario['other_collisions_before_contact'] = []
                scenario['status'] = ('sin_contacto_pulgar_indice' if not errors else
                                      'sin_contacto_con_errores_nucleo')
            # La penetración tras el contacto es esperable en la simulación:
            # en la mano real el controlador detiene ambos motores al tocar.
            scenario['note'] = ('Tras el primer contacto pulgar-indice la '
                                'penetracion es un artefacto: la mano real se '
                                'detiene al tocar.')
        scenario.pop('sample', None)
        record()

    solos = [report['scenarios'][name]['status'] for name in groups.SOLO_SCENARIOS]
    pinch = report['scenarios']['pinza_boli']['status']
    report['summary'] = dict(
        mano_abierta=report['open_hand']['status'],
        motores_solos={name: report['scenarios'][name]['status']
                       for name in groups.SOLO_SCENARIOS},
        pinza_boli=pinch)
    report['status'] = (
        'todo_limpio_y_pinza_lograda'
        if report['open_hand']['status'] == 'limpio'
        and all(s == 'limpio' for s in solos) and pinch == 'pinza_lograda'
        else 'con_pendientes')
    record()
    return report
