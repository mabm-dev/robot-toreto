"""Palm and articulated humanoid digits aligned from the wrist connector."""
import math


FINGER_DIMENSIONS_MM=((15.5,14.5),(15.0,14.0),(14.5,13.5),(16.0,15.0))
THUMB_DIMENSIONS_MM=((18.0,16.0),(16.5,15.0),(16.0,15.0))
HINGE_PIN_RADIUS_MM=2.0
HINGE_RADIAL_CLEARANCE_MM=0.35
HINGE_AXIAL_GAP_MM=0.40
HINGE_STOP_RADIUS_MM=1.25
HINGE_STOP_RADIAL_OVERLAP_MM=0.75
MAIN_FLEXION_LIMITS_DEG=(60.0,60.0,50.0,40.0)
THUMB_FLEXION_LIMITS_DEG=(30.0,40.0,35.0,20.0)


def _point(values):
    import adsk.core
    return adsk.core.Point3D.create(*(value*.1 for value in values))


def _placement(axis,y_mm):
    import adsk.core

    distal,proximal=axis[1],axis[0]
    dx=proximal[0]-distal[0]
    dz=proximal[2]-distal[2]
    length=math.hypot(dx,dz)
    direction=(dx/length,dz/length)
    normal=(direction[1],-direction[0])
    matrix=adsk.core.Matrix3D.create()
    if not matrix.setWithCoordinateSystem(
            _point((distal[0],y_mm,distal[2])),
            adsk.core.Vector3D.create(normal[0],0,normal[1]),
            adsk.core.Vector3D.create(0,1,0),
            adsk.core.Vector3D.create(direction[0],0,direction[1])):
        raise RuntimeError('No se pudo definir el marco local de la mano')
    return matrix


def _capsule(manager,start,end,radius_mm):
    import adsk.fusion

    result=manager.createCylinderOrCone(_point(start),radius_mm*.1,_point(end),radius_mm*.1)
    if not result:
        raise RuntimeError('No se pudo crear un enlace redondeado de la mano')
    for center in (start,end):
        sphere=manager.createSphere(_point(center),radius_mm*.1)
        if not sphere or not manager.booleanOperation(result,sphere,adsk.fusion.BooleanTypes.UnionBooleanType):
            raise RuntimeError('No se pudo cerrar un enlace redondeado de la mano')
    return result


def _transverse_axis(path):
    """Axis across a digit; rotation around it closes the digit into the palm."""
    vector=tuple(path[-1][i]-path[0][i] for i in range(3))
    # Cross global palm normal Y with the digit ray.
    axis=(vector[2],0,-vector[0])
    length=math.sqrt(axis[0]*axis[0]+axis[2]*axis[2])
    if length<1e-8:
        raise ValueError('Direccion de dedo invalida')
    return (axis[0]/length,0,axis[2]/length)


def _thumb_mechanism(path):
    """Return the short gimbal endpoint and its two crossed hinge directions."""
    root=path[0]
    ray=_unit(tuple(path[-1][index]-root[index] for index in range(3)))
    first_direction=_unit(tuple(path[1][index]-root[index] for index in range(3)))
    gimbal_end=tuple(root[index]+first_direction[index]*8.0 for index in range(3))
    # Build an orthonormal basis around the open thumb ray. The fitted directions
    # keep the proximal links in front of the palm while producing opposition.
    across=_unit((-ray[2],0.0,ray[0]))
    depth=_unit((
        ray[1]*across[2]-ray[2]*across[1],
        ray[2]*across[0]-ray[0]*across[2],
        ray[0]*across[1]-ray[1]*across[0],
    ))
    sweep_angle=math.radians(52.0)
    flex_angle=math.radians(128.0)
    sweep_axis=_unit(tuple(
        math.cos(sweep_angle)*across[index]+math.sin(sweep_angle)*depth[index]
        for index in range(3)))
    flex_axis=_unit(tuple(
        math.cos(flex_angle)*across[index]+math.sin(flex_angle)*depth[index]
        for index in range(3)))
    return gimbal_end,(sweep_axis,flex_axis,flex_axis,flex_axis)


def _axis_point(center,axis,distance_mm):
    return tuple(center[i]+axis[i]*distance_mm for i in range(3))


def _unit(vector):
    length=math.sqrt(sum(value*value for value in vector))
    if length<1e-8:
        raise ValueError('Vector de longitud nula')
    return tuple(value/length for value in vector)


def _rotate_about_axis(vector,axis,degrees):
    """Rodrigues rotation used to position the fixed flexion stop."""
    axis=_unit(axis)
    vector=_unit(vector)
    radians=math.radians(degrees)
    cosine=math.cos(radians)
    sine=math.sin(radians)
    cross=(
        axis[1]*vector[2]-axis[2]*vector[1],
        axis[2]*vector[0]-axis[0]*vector[2],
        axis[0]*vector[1]-axis[1]*vector[0],
    )
    dot=sum(axis[i]*vector[i] for i in range(3))
    return tuple(
        vector[i]*cosine+cross[i]*sine+axis[i]*dot*(1.0-cosine)
        for i in range(3))


def _cylinder(manager,center,axis,start_mm,end_mm,radius_mm,label):
    body=manager.createCylinderOrCone(
        _point(_axis_point(center,axis,start_mm)),radius_mm*.1,
        _point(_axis_point(center,axis,end_mm)),radius_mm*.1)
    if not body or not body.isSolid:
        raise RuntimeError('No se pudo crear '+label)
    return body


def _sleeve(manager,center,axis,start_mm,end_mm,outer_radius_mm,label):
    import adsk.fusion

    sleeve=_cylinder(manager,center,axis,start_mm,end_mm,outer_radius_mm,label)
    bore=_cylinder(
        manager,center,axis,start_mm-.6,end_mm+.6,
        HINGE_PIN_RADIUS_MM+HINGE_RADIAL_CLEARANCE_MM,label+'_TALADRO')
    if not manager.booleanOperation(
            sleeve,bore,adsk.fusion.BooleanTypes.DifferenceBooleanType):
        raise RuntimeError('No se pudo taladrar '+label)
    if not sleeve.isSolid or sleeve.lumps.count!=1:
        raise RuntimeError(label+' no produjo un casquillo valido')
    return sleeve


def _add_stop_rail(manager,sleeve,center,axis,start_mm,end_mm,
                   outer_radius_mm,radial_direction,label):
    """Fuse a longitudinal rail to a sleeve; paired rails form a hard stop."""
    import adsk.fusion

    radial_distance=outer_radius_mm-HINGE_STOP_RADIAL_OVERLAP_MM
    rail_center=tuple(
        center[i]+radial_direction[i]*radial_distance for i in range(3))
    rail=_cylinder(
        manager,rail_center,axis,start_mm,end_mm,HINGE_STOP_RADIUS_MM,label)
    if not manager.booleanOperation(
            sleeve,rail,adsk.fusion.BooleanTypes.UnionBooleanType):
        raise RuntimeError('No se pudo integrar '+label)
    if not sleeve.isSolid or sleeve.lumps.count!=1:
        raise RuntimeError(label+' no quedo unido al casquillo')


def _articulated_hinge(manager,center,axis,digit_direction,outer_radius_mm,
                       total_length_mm,flexion_limit_deg,label):
    """Three coaxial sleeves, removable pin and paired mechanical stops."""
    half=total_length_mm*.5
    center_length=total_length_mm*.42
    center_half=center_length*.5
    gap=HINGE_AXIAL_GAP_MM
    intervals=(
        (-half,-center_half-gap,'CASQUILLO_A'),
        (-center_half,center_half,'CASQUILLO_CENTRAL'),
        (center_half+gap,half,'CASQUILLO_B'),
    )
    result=[]
    sleeves={}
    for start,end,suffix in intervals:
        sleeve=_sleeve(
            manager,center,axis,start,end,outer_radius_mm,label+'_'+suffix)
        sleeves[suffix]=(sleeve,start,end)
        result.append((sleeve,suffix))
    radial_distance=outer_radius_mm-HINGE_STOP_RADIAL_OVERLAP_MM
    contact_angle=math.degrees(math.asin(
        min(0.99,HINGE_STOP_RADIUS_MM/radial_distance)))*2.0
    moving_direction=_unit(digit_direction)
    # The contact compensation must follow the requested rotation direction.
    # Otherwise a negative limit would place the fixed rail on the old side.
    signed_contact=math.copysign(contact_angle,flexion_limit_deg)
    fixed_direction=_rotate_about_axis(
        moving_direction,axis,flexion_limit_deg+signed_contact)
    central,central_start,central_end=sleeves['CASQUILLO_CENTRAL']
    _add_stop_rail(
        manager,central,center,axis,central_start,central_end,outer_radius_mm,
        moving_direction,label+'_TOPE_MOVIL')
    for suffix in ('CASQUILLO_A','CASQUILLO_B'):
        sleeve,start,end=sleeves[suffix]
        _add_stop_rail(
            manager,sleeve,center,axis,start,end,outer_radius_mm,
            fixed_direction,label+'_TOPE_FIJO_'+suffix[-1])
    pin=_cylinder(
        manager,center,axis,-half-1.0,half+1.0,HINGE_PIN_RADIUS_MM,
        label+'_PASADOR')
    result.append((pin,'PASADOR'))
    return result


def _trimmed(first,second,start_trim_mm,end_trim_mm=None):
    if end_trim_mm is None:
        end_trim_mm=start_trim_mm
    vector=tuple(second[i]-first[i] for i in range(3))
    length=math.sqrt(sum(value*value for value in vector))
    if length<=start_trim_mm+end_trim_mm:
        raise ValueError('Falange demasiado corta')
    unit=tuple(value/length for value in vector)
    return (
        tuple(first[i]+unit[i]*start_trim_mm for i in range(3)),
        tuple(second[i]-unit[i]*end_trim_mm for i in range(3)),
    )


def _phalanx(manager,flat,first,second,width_mm,depth_mm,label,trim_mm=0.6,
             end_trim_mm=None,rounded_tip=False):
    import adsk.core
    import adsk.fusion

    start,end=_trimmed(first,second,trim_mm,end_trim_mm)
    vector=tuple(end[i]-start[i] for i in range(3))
    length=math.sqrt(sum(value*value for value in vector))
    direction=tuple(value/length for value in vector)
    x_axis=(direction[2],0,-direction[0])
    x_length=math.sqrt(sum(value*value for value in x_axis))
    if x_length<1e-8:
        x_axis=(1,0,0)
    else:
        x_axis=tuple(value/x_length for value in x_axis)
    y_axis=(
        direction[1]*x_axis[2]-direction[2]*x_axis[1],
        direction[2]*x_axis[0]-direction[0]*x_axis[2],
        direction[0]*x_axis[1]-direction[1]*x_axis[0],
    )
    y_length=math.sqrt(sum(value*value for value in y_axis))
    y_axis=tuple(value/y_length for value in y_axis)
    matrix=adsk.core.Matrix3D.create()
    if not matrix.setWithCoordinateSystem(
            _point(start),
            adsk.core.Vector3D.create(*x_axis),
            adsk.core.Vector3D.create(*y_axis),
            adsk.core.Vector3D.create(*direction)):
        raise RuntimeError('No se pudo orientar '+label)
    if rounded_tip:
        sections=(
            (0,0,0,width_mm*.05,depth_mm*.05,3),
            (length*.068,0,0,width_mm*.05*.98,depth_mm*.05*.98,3),
            (length*.09,0,0,width_mm*.05*.76,depth_mm*.05*.80,3),
            (length*.1,0,0,width_mm*.05*.18,depth_mm*.05*.22,3),
        )
    else:
        sections=(
            (0,0,0,width_mm*.05,depth_mm*.05,3),
            (length*.1,0,0,width_mm*.05*.94,depth_mm*.05*.94,3),
        )
    body=flat.loft(manager,sections,label)
    if not manager.transform(body,matrix):
        raise RuntimeError('No se pudo colocar '+label)
    if not body or not body.isSolid:
        raise RuntimeError('No se pudo crear '+label)
    return body


def joint_specs(data):
    """Return 20 revolute relationships using the validated hinge axes."""
    specs=[]
    palm_group='MANO_00_PALMA'
    for finger_index,path in enumerate(data['finger_paths_mm'],1):
        axis=_transverse_axis(path)
        for joint_index,center in enumerate(path[:-1],1):
            parent=(palm_group if joint_index==1 else
                    'MANO_0{}_FALANGE_0{}'.format(finger_index,joint_index-1))
            child='MANO_0{}_FALANGE_0{}'.format(finger_index,joint_index)
            specs.append({
                'name':'JUNTA_DEDO_{}_{}'.format(finger_index,joint_index),
                'parent':parent,
                'child':child,
                'pin_label':'08_DEDO_{}_NUDILLO_{}_PASADOR'.format(
                    finger_index,joint_index),
                'center_mm':center,
                'axis':axis,
                'minimum_deg':-MAIN_FLEXION_LIMITS_DEG[joint_index-1],
                'maximum_deg':0.0,
                'travel_deg':MAIN_FLEXION_LIMITS_DEG[joint_index-1],
            })
    thumb_path=data['thumb_path_mm']
    gimbal_group='MANO_05_PULGAR_CARDAN'
    gimbal_end,thumb_axes=_thumb_mechanism(thumb_path)
    thumb_centers=(thumb_path[0],gimbal_end,thumb_path[1],thumb_path[2])
    thumb_parents=(palm_group,gimbal_group,
                   'MANO_05_PULGAR_FALANGE_01','MANO_05_PULGAR_FALANGE_02')
    thumb_children=(gimbal_group,'MANO_05_PULGAR_FALANGE_01',
                    'MANO_05_PULGAR_FALANGE_02','MANO_05_PULGAR_FALANGE_03')
    for joint_index,center in enumerate(thumb_centers,1):
        specs.append({
            'name':'JUNTA_PULGAR_{}'.format(joint_index),
            'parent':thumb_parents[joint_index-1],
            'child':thumb_children[joint_index-1],
            'pin_label':'10_PULGAR_NUDILLO_{}_PASADOR'.format(joint_index),
            'center_mm':center,
            'axis':thumb_axes[joint_index-1],
            'minimum_deg':0.0,
            'maximum_deg':THUMB_FLEXION_LIMITS_DEG[joint_index-1],
            'travel_deg':THUMB_FLEXION_LIMITS_DEG[joint_index-1],
        })
    if len(specs)!=20:
        raise RuntimeError('Numero inesperado de juntas de la mano')
    return specs


def build(manager,flat,data):
    import adsk.fusion

    palm=flat.loft(manager,data['palm_sections'],'06_PALMA_LOCAL')
    if not manager.transform(palm,_placement(data['front_axis'],data['master_plane_y_mm'])):
        raise RuntimeError('No se pudo colocar la palma en la postura frontal')
    connector=_capsule(manager,*data['palm_connector_mm'],data['wrist_connector_radius_mm'])
    if not manager.booleanOperation(palm,connector,adsk.fusion.BooleanTypes.UnionBooleanType):
        raise RuntimeError('El conector de muneca no solapa con la palma')
    for finger_index,path in enumerate(data['finger_paths_mm'],1):
        root=path[0]
        vector=tuple(path[-1][i]-root[i] for i in range(3))
        length=math.sqrt(sum(value*value for value in vector))
        direction=tuple(value/length for value in vector)
        inside=tuple(root[i]-direction[i]*6.0 for i in range(3))
        socket=_capsule(manager,inside,root,7.0)
        if not manager.booleanOperation(palm,socket,adsk.fusion.BooleanTypes.UnionBooleanType):
            raise RuntimeError('La cuna del dedo {} no solapa con la palma'.format(finger_index))
    thumb_path=data['thumb_path_mm']
    thumb_metacarpal=_capsule(
        manager,data['thumb_anchor_mm'],thumb_path[0],data['thumb_base_radius_mm'])
    if not manager.booleanOperation(palm,thumb_metacarpal,adsk.fusion.BooleanTypes.UnionBooleanType):
        raise RuntimeError('La base reforzada del pulgar no solapa con la palma')
    gimbal_end,_=_thumb_mechanism(thumb_path)
    gimbal_clearance=_capsule(manager,thumb_path[0],gimbal_end,10.0)
    if not manager.booleanOperation(
            palm,gimbal_clearance,adsk.fusion.BooleanTypes.DifferenceBooleanType):
        raise RuntimeError('No se pudo abrir la cuna de movimiento del cardan')
    palm_group='MANO_00_PALMA'
    pending=[(palm,'06_PALMA_Y_CONECTOR','TORETO Negro profundo',palm_group)]

    for finger_index,path in enumerate(data['finger_paths_mm'],1):
        transverse=_transverse_axis(path)
        digit_direction=_unit(tuple(path[-1][i]-path[0][i] for i in range(3)))
        for segment_index,(first,second) in enumerate(zip(path,path[1:]),1):
            label='07_DEDO_{}_FALANGE_{}'.format(finger_index,segment_index)
            group='MANO_0{}_FALANGE_0{}'.format(finger_index,segment_index)
            width_mm,depth_mm=FINGER_DIMENSIONS_MM[segment_index-1]
            terminal=(segment_index==4)
            body=_phalanx(
                manager,flat,first,second,width_mm,depth_mm,label,
                trim_mm=3.0,end_trim_mm=(0.3 if terminal else 3.0),
                rounded_tip=terminal)
            appearance='TORETO Blanco satinado' if terminal else 'TORETO Negro profundo'
            pending.append((body,label,appearance,group))
        for joint_index,center in enumerate(path[:-1],1):
            left=FINGER_DIMENSIONS_MM[max(0,joint_index-2)]
            right=FINGER_DIMENSIONS_MM[min(3,joint_index-1)]
            width=max(left[0],right[0])
            label='08_DEDO_{}_NUDILLO_{}'.format(finger_index,joint_index)
            parent_group=(palm_group if joint_index==1 else
                          'MANO_0{}_FALANGE_0{}'.format(finger_index,joint_index-1))
            child_group='MANO_0{}_FALANGE_0{}'.format(finger_index,joint_index)
            for part,suffix in _articulated_hinge(
                    manager,center,transverse,digit_direction,5.8,width+4.0,
                    -MAIN_FLEXION_LIMITS_DEG[joint_index-1],label):
                group=child_group if suffix=='CASQUILLO_CENTRAL' else parent_group
                pending.append((part,label+'_'+suffix,'TORETO Negro profundo',group))

    gimbal_end,thumb_axes=_thumb_mechanism(thumb_path)
    thumb_segments=((gimbal_end,thumb_path[1]),
                    (thumb_path[1],thumb_path[2]),
                    (thumb_path[2],thumb_path[3]))
    gimbal_direction=_unit(tuple(
        gimbal_end[index]-thumb_path[0][index] for index in range(3)))
    gimbal_body=_capsule(
        manager,
        tuple(thumb_path[0][index]+gimbal_direction[index]*3.0 for index in range(3)),
        tuple(gimbal_end[index]-gimbal_direction[index]*3.0 for index in range(3)),
        4.2)
    pending.append((gimbal_body,'09_PULGAR_CARDAN_INTERMEDIO',
                    'TORETO Negro profundo','MANO_05_PULGAR_CARDAN'))
    for segment_index,(first,second) in enumerate(thumb_segments,1):
        label='09_PULGAR_FALANGE_{}'.format(segment_index)
        group='MANO_05_PULGAR_FALANGE_0{}'.format(segment_index)
        width_mm,depth_mm=THUMB_DIMENSIONS_MM[segment_index-1]
        terminal=(segment_index==3)
        body=_phalanx(
            manager,flat,first,second,width_mm,depth_mm,label,
            trim_mm=3.0,end_trim_mm=(0.3 if terminal else 3.0),
            rounded_tip=terminal)
        appearance='TORETO Blanco satinado' if terminal else 'TORETO Negro profundo'
        pending.append((body,label,appearance,group))
    thumb_direction=_unit(tuple(
        thumb_path[-1][i]-thumb_path[0][i] for i in range(3)))
    thumb_centers=(thumb_path[0],gimbal_end,thumb_path[1],thumb_path[2])
    thumb_parents=(palm_group,'MANO_05_PULGAR_CARDAN',
                   'MANO_05_PULGAR_FALANGE_01','MANO_05_PULGAR_FALANGE_02')
    thumb_children=('MANO_05_PULGAR_CARDAN','MANO_05_PULGAR_FALANGE_01',
                    'MANO_05_PULGAR_FALANGE_02','MANO_05_PULGAR_FALANGE_03')
    for joint_index,center in enumerate(thumb_centers,1):
        label='10_PULGAR_NUDILLO_{}'.format(joint_index)
        parent_group=thumb_parents[joint_index-1]
        child_group=thumb_children[joint_index-1]
        for part,suffix in _articulated_hinge(
                manager,center,thumb_axes[joint_index-1],thumb_direction,6.2,20.0,
                THUMB_FLEXION_LIMITS_DEG[joint_index-1],label):
            group=child_group if suffix=='CASQUILLO_CENTRAL' else parent_group
            pending.append((part,label+'_'+suffix,'TORETO Negro profundo',group))
    if any(not body.isSolid or body.lumps.count!=1 for body,_,_,_ in pending):
        raise RuntimeError('La mano contiene un cuerpo no solido')
    report=('Mano: palma axial plana de {} perfiles (L60 mm, ancho 76-38 mm, profundidad 20-26 mm), '
            'conector central de muneca R{} mm, base lateral reforzada de pulgar R{} mm con horquilla abierta R10 mm, '
            'cuatro dedos rectos de cuatro falanges articulables (tres negras y terminal blanca), '
            'nudillos cilindricos orientados a traves del ancho local para cerrar hacia la palma, '
            'rayos paralelos al eje de salida de la muneca y cuatro cunas redondeadas separadas, '
            'arco palmar ulnar de hasta 5 mm, terminales blancas obtenidas por loft abombado sin esferas, '
            'y pulgar reforzado de tres falanges con cardan intermedio y cuatro bisagras, incluidas dos direcciones cruzadas en la base; cada nudillo usa tres casquillos coaxiales, '
            'pasador R{:.2f} mm, holgura radial {:.2f} mm y separacion axial {:.2f} mm; '
            'topes mecanicos integrados R{:.2f} mm invierten los cuatro nudillos principales a -60/-60/-50/-40 grados '
            'y las cuatro del pulgar a 30/40/35/20 grados; '
            '{} cuerpos repartidos en 21 componentes mecanicos').format(
                len(data['palm_sections']),data['wrist_connector_radius_mm'],
                data['thumb_base_radius_mm'],HINGE_PIN_RADIUS_MM,
                HINGE_RADIAL_CLEARANCE_MM,HINGE_AXIAL_GAP_MM,
                HINGE_STOP_RADIUS_MM,len(pending))
    return pending,report
