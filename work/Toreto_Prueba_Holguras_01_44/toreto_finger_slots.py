"""Trial phalanx hinge seats; neutral placement and joint axes unchanged.

Full coaxial cylinders bound opposing sleeves and their rails at every angle.
Only phalanges are cut. Own-group sleeve attachment is checked independently.
No document modifications; no claim of manufacturing strength.
"""


def repair(manager, hand, pending, data):
    import adsk.fusion
    difference = adsk.fusion.BooleanTypes.DifferenceBooleanType
    specs = hand.joint_specs(data)
    result = list(pending)
    gap = hand.HINGE_AXIAL_GAP_MM
    clearance = .35
    supports = []

    def overlap(a, b):
        candidate = manager.copy(a)
        if not manager.booleanOperation(candidate, manager.copy(b), difference) or not candidate.isValid:
            raise RuntimeError('No se pudo verificar el apoyo')
        return max(0, a.volume - candidate.volume)

    for index, (body, label, appearance, group) in enumerate(pending):
        if not label.startswith(('07_DEDO_', '09_PULGAR_FALANGE_')):
            continue
        candidate = manager.copy(body)
        for spec in specs:
            is_thumb = spec['name'].startswith('JUNTA_PULGAR_')
            total = 20.0 if is_thumb else hand.MAIN_HINGE_LENGTH_MM
            half, central = total / 2, total * .42 / 2
            radius = (6.2 if is_thumb else 5.8) + hand.HINGE_STOP_RADIUS_MM - hand.HINGE_STOP_RADIAL_OVERLAP_MM + clearance
            if spec['child'] == group:
                intervals = [(-half-clearance, -central-gap+clearance),
                             (central+gap-clearance, half+clearance)]
            elif spec['parent'] == group:
                intervals = [(-central-clearance, central+clearance)]
            else:
                continue
            for start, end in intervals:
                tool = hand._cylinder(manager, spec['center_mm'], spec['axis'],
                                      start, end, radius, label+'_ALOJAMIENTO')
                trial = manager.copy(candidate)
                if not manager.booleanOperation(trial, tool, difference):
                    raise RuntimeError('Fallo de alojamiento: '+label)
                if not trial.isValid or not trial.isSolid or trial.lumps.count != 1:
                    raise RuntimeError('Alojamiento divide la falange: '+label)
                candidate = trial
        if candidate.volume < body.volume * .65:
            raise RuntimeError('Alojamiento elimina mas del 35%: '+label)
        for sleeve, sleeve_label, _, sleeve_group in pending:
            if sleeve_group != group or 'CASQUILLO' not in sleeve_label:
                continue
            before, after = overlap(body, sleeve), overlap(candidate, sleeve)
            if before <= 1e-6 or after < max(.01, before * .1):
                raise RuntimeError('Apoyo insuficiente: '+label+' / '+sleeve_label)
            supports.append(dict(phalanx=label, sleeve=sleeve_label,
                                 overlap_mm3=after*1000))
        result[index] = (candidate, label, appearance, group)
    return result, supports
