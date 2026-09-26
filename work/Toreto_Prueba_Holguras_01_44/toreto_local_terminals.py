"""Controlled local-frame terminal extensions and elbow pivot geometry."""
import math


def _constant_section(source, z):
    return [z, source[1], source[2], source[3], source[4], source[5]]


def extend_to_measured_limits(manager, flat, body, all_sections, selected, label, overlap_cm=0.05,
                              extend_before=True,extend_after=True):
    """Extend a stable loft to the measured end planes with constant profiles.

    Abrupt terminal radii are deliberately not interpolated: their planes set
    the longitudinal limits, while the nearest stable profile sets the collar.
    A 0.5 mm overlap gives the boolean operation an unambiguous volume.
    """
    import adsk.fusion

    reports=[]
    start=selected['start']
    stop=selected['stop']
    stable=selected['sections']
    extensions=[]
    if start and extend_before:
        boundary=stable[0]
        sections=[
            _constant_section(boundary,all_sections[0][0]),
            _constant_section(boundary,boundary[0]+overlap_cm),
        ]
        extensions.append(('inferior',sections))
    if stop<len(all_sections) and extend_after:
        boundary=stable[-1]
        sections=[
            _constant_section(boundary,boundary[0]-overlap_cm),
            _constant_section(boundary,all_sections[-1][0]),
        ]
        extensions.append(('superior',sections))

    for end_name,sections in extensions:
        extension=flat.loft(manager,sections,label+'_COLLAR_'+end_name.upper())
        if not manager.booleanOperation(body,extension,adsk.fusion.BooleanTypes.UnionBooleanType):
            raise RuntimeError(label+': no se pudo unir el collar '+end_name)
        reports.append(
            '{} {} prolongado {:.2f} mm con perfil estable constante'.format(
                label,end_name,(sections[-1][0]-sections[0][0]-overlap_cm)*10))
    if not body.isSolid or body.lumps.count!=1:
        raise RuntimeError(label+': los collares no dejaron un unico solido')
    return body,reports


def _world_frame(item, section, master_y_mm):
    lower,upper=item['front_axis'][1],item['front_axis'][0]
    dx=upper[0]-lower[0]
    dz=upper[2]-lower[2]
    length=math.hypot(dx,dz)
    direction=(dx/length,dz/length)
    normal=(direction[1],-direction[0])
    local_z,local_x,local_y,rx,ry,_=section
    center=(
        lower[0]+normal[0]*local_x*10+direction[0]*local_z*10,
        master_y_mm+local_y*10,
        lower[2]+normal[1]*local_x*10+direction[1]*local_z*10,
    )
    return center,normal,rx*10,ry*10


def elbow_parameters(parts,master_y_mm):
    """Derive the pivot from the two opposing measured terminal planes."""
    upper,upper_normal,upper_half_width,_=_world_frame(parts['upper'],parts['upper']['sections'][0],master_y_mm)
    forearm,forearm_normal,forearm_half_width,_=_world_frame(parts['forearm'],parts['forearm']['sections'][-1],master_y_mm)
    gap=math.hypot(forearm[0]-upper[0],forearm[2]-upper[2])
    radius=gap*.5+1.5
    if not 12<=radius<=22:
        raise ValueError('Separacion de codo fuera del intervalo esperado: {:.2f} mm'.format(gap))
    normal=(upper_normal[0]+forearm_normal[0],upper_normal[1]+forearm_normal[1])
    normal_length=math.hypot(*normal)
    normal=(normal[0]/normal_length,normal[1]/normal_length)
    center=((upper[0]+forearm[0])*.5,(upper[1]+forearm[1])*.5,(upper[2]+forearm[2])*.5)
    boss_length=forearm_half_width*2
    boss_radius=min(forearm_half_width*.85,radius+12.0)
    # The frontal trace at the elbow endpoint measures a 47.57 mm central
    # opening inside a 65.35 mm envelope. Preserve that ratio as two cheeks.
    boss_opening_length=boss_length*(47.57/65.35)
    cheek_thickness=(boss_length-boss_opening_length)*.5
    axle_length=boss_length+4.0
    half_length=axle_length*.5
    p1=(center[0]-normal[0]*half_length,center[1],center[2]-normal[1]*half_length)
    p2=(center[0]+normal[0]*half_length,center[1],center[2]+normal[1]*half_length)
    boss_half=boss_length*.5
    boss_p1=(center[0]-normal[0]*boss_half,center[1],center[2]-normal[1]*boss_half)
    boss_p2=(center[0]+normal[0]*boss_half,center[1],center[2]+normal[1]*boss_half)
    return {'p1':p1,'p2':p2,'boss_p1':boss_p1,'boss_p2':boss_p2,
            'upper_terminal':upper,'forearm_terminal':forearm,'center':center,
            'normal':normal,'radius':radius,'boss_radius':boss_radius,'gap':gap,
            'length':axle_length,'boss_length':boss_length,
            'boss_opening_length':boss_opening_length,'cheek_thickness':cheek_thickness}


def _point(values):
    import adsk.core
    return adsk.core.Point3D.create(*(value*.1 for value in values))


def _capsule(manager,start,end,radius_mm):
    import adsk.fusion

    result=manager.createCylinderOrCone(_point(start),radius_mm*.1,_point(end),radius_mm*.1)
    if not result:
        raise RuntimeError('No se pudo crear el enlace del codo')
    for center in (start,end):
        sphere=manager.createSphere(_point(center),radius_mm*.1)
        if not sphere or not manager.booleanOperation(result,sphere,adsk.fusion.BooleanTypes.UnionBooleanType):
            raise RuntimeError('No se pudo redondear el enlace del codo')
    return result


def build_elbow(manager,parts,master_y_mm):
    import adsk.fusion

    spec=elbow_parameters(parts,master_y_mm)
    body=manager.createCylinderOrCone(
        _point(spec['p1']),spec['radius']*.1,_point(spec['p2']),spec['radius']*.1)
    if not body or not body.isSolid or body.lumps.count!=1:
        raise RuntimeError('No se pudo crear el eje transversal del codo')
    connector_radius=min(spec['radius']*.65,10.5)
    connector=_capsule(manager,spec['upper_terminal'],spec['center'],connector_radius)
    if not manager.booleanOperation(body,connector,adsk.fusion.BooleanTypes.UnionBooleanType):
        raise RuntimeError('El enlace superior no solapa con el eje del codo')
    report='Codo: eje L{:.2f} mm, R{:.2f} mm; enlace superior R{:.2f} mm; hueco {:.2f} mm'.format(
        spec['length'],spec['radius'],connector_radius,spec['gap'])
    return body,report,spec


def integrate_elbow(manager,upper_body,forearm_body,spec,clearance_mm=0.8,axial_margin_mm=2.0):
    """Add the forearm boss, its bore and full clearance in the upper shell."""
    import adsk.fusion

    p1=spec['boss_p1']
    p2=spec['boss_p2']
    axis=(p2[0]-p1[0],p2[1]-p1[1],p2[2]-p1[2])
    length=math.sqrt(sum(value*value for value in axis))
    unit=tuple(value/length for value in axis)
    center=spec['center']
    opening_half=spec['boss_opening_length']*.5
    inner_first=tuple(center[i]-unit[i]*opening_half for i in range(3))
    inner_second=tuple(center[i]+unit[i]*opening_half for i in range(3))
    for index,(outer,inner) in enumerate(((p1,inner_first),(inner_second,p2)),1):
        cheek=manager.createCylinderOrCone(
            _point(outer),spec['boss_radius']*.1,_point(inner),spec['boss_radius']*.1)
        if not cheek or not manager.booleanOperation(forearm_body,cheek,adsk.fusion.BooleanTypes.UnionBooleanType):
            raise RuntimeError('No se pudo integrar la mejilla {} con el antebrazo'.format(index))

    cutter_p1=tuple(p1[i]-unit[i]*axial_margin_mm for i in range(3))
    cutter_p2=tuple(p2[i]+unit[i]*axial_margin_mm for i in range(3))
    bore_radius=spec['radius']+clearance_mm
    for body,label,radius in (
            (forearm_body,'antebrazo',bore_radius),
            (upper_body,'brazo',spec['boss_radius']+clearance_mm)):
        cutter=manager.createCylinderOrCone(
            _point(cutter_p1),radius*.1,_point(cutter_p2),radius*.1)
        if not cutter:
            raise RuntimeError('No se pudo crear el cortador del alojamiento de '+label)
        if not manager.booleanOperation(body,cutter,adsk.fusion.BooleanTypes.DifferenceBooleanType):
            raise RuntimeError('No se pudo cortar el alojamiento del codo en '+label)
        if not body.isSolid or body.lumps.count!=1:
            raise RuntimeError(label+': el alojamiento dividio la carcasa')
    return ('Dos mejillas de antebrazo R{:.2f} mm x {:.2f} mm, abertura central {:.2f} mm, '
            'taladro R{:.2f} mm; brazo liberado; holgura radial {:.2f} mm').format(
                spec['boss_radius'],spec['cheek_thickness'],spec['boss_opening_length'],
                bore_radius,clearance_mm)
