"""v10: one lateral pinch trial with transient solids; never publish CAD.

The v8 open-hand and solo-motor reports are reused as prior evidence, not
rerun or silently relabelled. This run checks every moving pair at 13 sampled
poses and stops at the first contact or an earlier unintended collision.

Afinado: al aparecer el primer contacto, se biseca entre la última muestra
limpia y esa (REFINE_STEPS veces) y la cara se clasifica en la postura más
temprana con choque. Con 12 muestras el índice avanza 8 puntos por paso; en
la v8 eso llevó de 15 a 868 mm3 entre dos muestras, y un solape tan grande
invade esquinas y deja la cara indeterminada. Las 13 muestras no cambian.
"""
import json

REFINE_STEPS = 5

# v10b: en la v10 el contacto afinado era tan rozante que la penetración
# (volumen del pulgar menos el del pulgar recortado: dos números de miles de
# mm3) no coincidió con la intersección directa, y se abortó la cara sin
# guardar los volúmenes. Ahora manda la intersección directa, los dos
# volúmenes se guardan siempre y la diferencia es un aviso.
# Además se clasifica la cara en hasta MAX_CONTACT_STATES posturas con
# contacto (la más temprana primero) para ver si la respuesta es estable.
MAX_CONTACT_STATES = 3


def _intersection_box(manager, a, b):
    """Intersection volume and world AABB of the *actual* transient solids."""
    import adsk.fusion
    overlap = manager.copy(a)
    if not overlap or not manager.booleanOperation(
            overlap, manager.copy(b), adsk.fusion.BooleanTypes.IntersectionBooleanType):
        raise RuntimeError('Interseccion BRep fallida; cara de contacto NO resuelta')
    if not overlap.isValid or not overlap.isSolid or overlap.lumps.count != 1:
        raise RuntimeError('Interseccion BRep no solida/unica ({} trozos, {:.4f} mm3); '
                           'cara NO resuelta'.format(overlap.lumps.count,
                                                     overlap.volume * 1000))
    box = overlap.boundingBox
    low = tuple(getattr(box.minPoint, axis) * 10 for axis in 'xyz')
    high = tuple(getattr(box.maxPoint, axis) * 10 for axis in 'xyz')
    return overlap.volume * 1000, low, high


def run(manager, hand, clearance, groups, base, faces, pending, data, report_path,
        intervals=12):
    import adsk
    if intervals != 12:
        raise ValueError('v10 requiere las 12 divisiones comparables con v8')
    name, description, fractions_at = groups.LATERAL_PINCH_SCENARIO
    specs = {spec['child']: spec for spec in hand.joint_specs(data)}
    bodies = [(body, label, group, clearance.chain_for(group, specs))
              for body, label, _, group in pending if label != base.PALM_BODY]
    labels = [label for _, label, _, _ in bodies]
    moving = [groups.moves_in(chain, fractions_at, intervals)
              for _, _, _, chain in bodies]
    pairs = [(i, j) for i in range(len(bodies)) for j in range(i + 1, len(bodies))
             if (moving[i] or moving[j]) and bodies[i][2] != bodies[j][2]]
    report = dict(version='v10b', status='running', scenario=name,
                  description=description, intervals=intervals,
                  tolerance_mm3=0.01,
                  flexion_ratio=groups.LATERAL_FLEXION_RATIO,
                  moving_bodies=sum(moving), checked_pairs=len(pairs),
                  reused_evidence='Mano abierta y motores solos: v8, sin repetir.',
                  excluded='Palma principal y pares del mismo grupo rigido.',
                  limitation=('Muestras discretas, palma excluida. La caja de la '
                              'interseccion localiza el contacto pero no mide area '
                              'de apoyo ni certifica holgura continua o resistencia.'),
                  samples=[], refinement=[], first_contact=None,
                  prior_collisions=[], errors=[], warnings=[])

    def record():
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                               encoding='utf-8')

    def evaluate(t):
        fractions = fractions_at(t)
        placed = [(base._pose(manager, groups, clearance, body, chain, fractions)
                   if moving[k] else opened[k])
                  for k, (body, _, _, chain) in enumerate(bodies)]
        collisions = []
        errors = []
        for i, j in pairs:
            if not clearance.overlaps(placed[i], placed[j]):
                continue
            try:
                volume = base._penetration_mm3(manager, placed[i], placed[j])
            except Exception as error:
                errors.append(dict(a=labels[i], b=labels[j], error=str(error)))
                continue
            if volume > report['tolerance_mm3']:
                collisions.append(dict(a=labels[i], b=labels[j],
                                       volume_mm3=round(volume, 3), indices=[i, j]))
        contacts = [item for item in collisions
                    if groups.is_pinch_contact(item['a'], item['b'])]
        others = [item for item in collisions if item not in contacts]
        return dict(t=t, fractions=fractions, placed=placed, contacts=contacts,
                    others=others, errors=errors)

    def pure_contact(state):
        return state['contacts'] and not state['others'] and not state['errors']

    def describe(state, sample):
        """Cara de cada contacto de una postura, por intersección directa."""
        details = []
        for item in state['contacts']:
            thumb_index = item['indices'][0] if item['a'].startswith(
                groups.THUMB_PHALANX_PREFIX) else item['indices'][1]
            index_index = item['indices'][1] if thumb_index == item['indices'][0] \
                else item['indices'][0]
            thumb_label, index_label = labels[thumb_index], labels[index_index]
            try:
                volume, low, high = _intersection_box(
                    manager, state['placed'][thumb_index], state['placed'][index_index])
            except Exception as error:
                report['errors'].append(dict(sample=sample, fraction=round(state['t'], 5),
                                             a=thumb_label, b=index_label,
                                             penetration_mm3=item['volume_mm3'],
                                             error=str(error)))
                continue
            detail = dict(a=thumb_label, b=index_label,
                          penetration_mm3=item['volume_mm3'],
                          intersection_mm3=round(volume, 4),
                          overlap_box_mm={'min': [round(v, 3) for v in low],
                                          'max': [round(v, 3) for v in high]})
            if abs(volume - item['volume_mm3']) > max(.1, volume * .05):
                report['warnings'].append(dict(
                    sample=sample, fraction=round(state['t'], 5), a=thumb_label,
                    b=index_label, penetration_mm3=item['volume_mm3'],
                    intersection_mm3=round(volume, 4),
                    note='Penetracion por diferencia y interseccion directa no '
                         'coinciden; manda la interseccion directa.'))
            if volume <= report['tolerance_mm3']:
                detail['pulgar'] = detail['indice'] = {'region': 'contacto_no_confirmado'}
            else:
                detail['pulgar'] = faces.classify_overlap(
                    data, state['fractions'], 'pulgar', thumb_label, low, high,
                    hand, clearance, groups)
                detail['indice'] = faces.classify_overlap(
                    data, state['fractions'], 'indice', index_label, low, high,
                    hand, clearance, groups)
            details.append(detail)
        return details

    def refine(sample, state):
        """Bisección entre la última muestra limpia y la del primer contacto.
        Devuelve la postura más temprana con algún choque encontrada."""
        contact_states.append(state)
        low, high = (sample - 1) / intervals, sample / intervals
        for step in range(REFINE_STEPS):
            middle = (low + high) / 2
            probe = evaluate(middle)
            report['refinement'].append(dict(
                step=step + 1, fraction=round(middle, 5), motors=probe['fractions'],
                contact_pairs=len(probe['contacts']),
                unintended_pairs=len(probe['others']), errors=len(probe['errors'])))
            if probe['errors']:
                # Sin resolver: se conserva la última postura conocida y el
                # error deja el resultado como cara no resuelta.
                report['errors'].extend(dict(sample=sample, refine_fraction=middle, **entry)
                                        for entry in probe['errors'])
                break
            if probe['contacts'] or probe['others']:
                high, state = middle, probe
                contact_states.append(probe)
            else:
                low = middle
            record()
            adsk.doEvents()
        report['refined_bracket'] = dict(last_clean_fraction=round(low, 5),
                                         first_collision_fraction=round(high, 5))
        return state

    record()
    opened = [manager.copy(body) for body, _, _, _ in bodies]
    contact_states = []
    for sample in range(intervals + 1):
        state = evaluate(sample / intervals)
        contacts, others, errors = state['contacts'], state['others'], state['errors']
        sample_report = dict(sample=sample, fraction=round(sample / intervals, 4),
                             motors=state['fractions'], contact_pairs=len(contacts),
                             unintended_pairs=len(others), errors=len(errors))
        report['samples'].append(sample_report)
        report['errors'].extend(dict(sample=sample, **entry) for entry in errors)
        if errors:
            report['status'] = 'errores_nucleo_sin_resolver'
            record()
            break
        if contacts and sample > 0:
            # La muestra anterior fue limpia (si no, el bucle ya habría parado).
            state = refine(sample, state)
            contacts, others = state['contacts'], state['others']
            if not contacts:
                # Entre muestras apareció antes un choque ajeno a la pinza.
                report['prior_collisions'].extend(
                    dict(sample=sample, refine_fraction=round(state['t'], 5),
                         a=item['a'], b=item['b'], volume_mm3=item['volume_mm3'])
                    for item in others)
                report['status'] = ('cara_no_resuelta' if report['errors']
                                     else 'choque_previo_a_contacto')
                record()
                break
        fractions, placed = state['fractions'], state['placed']
        if others:
            report['prior_collisions'].extend(
                dict(sample=sample, a=item['a'], b=item['b'],
                     volume_mm3=item['volume_mm3']) for item in others)
        if contacts:
            contact_details = describe(state, sample)
            report['first_contact'] = dict(sample=sample,
                                           fraction=round(state['t'], 5),
                                           coarse_fraction=round(sample / intervals, 4),
                                           motors=fractions,
                                           pairs=contact_details)
            # El estado lo decide la postura más temprana; un error en las
            # comprobaciones de estabilidad solo la marca como no consistente.
            primary_errors = bool(report['errors'])
            record()
            # Estabilidad: la misma clasificación en las siguientes posturas
            # con contacto limpio (sin choques ajenos), más cerradas.
            later = sorted((s for s in contact_states
                            if s is not state and s['t'] > state['t'] and pure_contact(s)),
                           key=lambda s: s['t'])[:MAX_CONTACT_STATES - 1]
            checks = [dict(fraction=round(state['t'], 5), pairs=[
                dict(pulgar=d['pulgar']['region'], indice=d['indice']['region'],
                     intersection_mm3=d['intersection_mm3']) for d in contact_details])]
            for extra in later:
                checks.append(dict(fraction=round(extra['t'], 5), pairs=[
                    dict(pulgar=d['pulgar']['region'], indice=d['indice']['region'],
                         intersection_mm3=d['intersection_mm3'])
                    for d in describe(extra, sample)]))
            regions = [tuple((p['pulgar'], p['indice']) for p in check['pairs'])
                       for check in checks]
            consistent = len(checks) > 1 and all(r == regions[0] for r in regions)
            report['first_contact']['stability'] = dict(
                postures=checks, consistent=consistent)
            if primary_errors:
                report['status'] = 'cara_no_resuelta'
            elif others or report['prior_collisions']:
                report['status'] = 'choques_antes_o_en_contacto'
            elif len(contact_details) != 1:
                report['status'] = 'contactos_simultaneos_ambiguos'
            else:
                detail = contact_details[0]
                thumb_region = detail['pulgar']['region']
                index_region = detail['indice']['region']
                if thumb_region == 'palmar' and index_region == 'lateral':
                    report['status'] = ('apoyo_palmar_lateral_en_muestra' if consistent
                                        else 'apoyo_palmar_lateral_sin_confirmar_estabilidad')
                else:
                    report['status'] = 'contacto_cara_no_deseada_o_indeterminada'
            record()
            break
        if others:
            report['status'] = 'choque_previo_a_contacto'
            record()
            break
        record()
        adsk.doEvents()
    else:
        report['status'] = 'sin_contacto_en_12_pasos'
        record()
    return report
