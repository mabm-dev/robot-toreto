"""Shoulder and wrist interfaces derived from the separated end profiles."""
import math


def _point(values):
    import adsk.core
    return adsk.core.Point3D.create(*(value*.1 for value in values))


def _frame(item):
    lower,upper=item['front_axis'][1],item['front_axis'][0]
    dx=upper[0]-lower[0]
    dz=upper[2]-lower[2]
    length=math.hypot(dx,dz)
    direction=(dx/length,dz/length)
    normal=(direction[1],-direction[0])
    return lower,direction,normal


def _world_center(item,section,master_y_mm):
    lower,direction,normal=_frame(item)
    z,x,y=section[:3]
    return (
        lower[0]+normal[0]*x*10+direction[0]*z*10,
        master_y_mm+y*10,
        lower[2]+normal[1]*x*10+direction[1]*z*10,
    )


def _axis_points(center,axis,length_mm):
    half=length_mm*.5
    return (
        tuple(center[i]-axis[i]*half for i in range(3)),
        tuple(center[i]+axis[i]*half for i in range(3)),
    )


def parameters(parts,master_y_mm,shoulder_center=None,shoulder_size=None,
               shoulder_axis=None,shoulder_axle_radius=None,shoulder_axle_span=None):
    """shoulder_center (mm, marco plano): v11 coloca el eje del hombro en el
    pivote de la lamina, dentro de la cabeza de la carcasa. Sin el, se usa el
    perfil superior como antes.
    shoulder_size=(largo_mm, radio_mm): en el pivote el perfil superior ya no
    sirve para dimensionar (es la punta, 18 mm de ancho); v11 da el ancho de
    la carcasa a esa altura y el radio del disco dibujado en la lamina.
    v13, encaje en el pecho: shoulder_axis (X exacta, coaxial con el conector
    del pecho), shoulder_axle_radius (radio del conector: el taladro queda a su
    medida mas la holgura) y shoulder_axle_span=(desde_mm, hasta_mm) a lo largo
    del eje desde el centro: el eje propio del brazo se reduce a una tapa en la
    cara exterior, porque el conector del pecho ocupa el resto."""
    upper=parts['upper']
    forearm=parts['forearm']
    shoulder_section=upper['sections'][-1]
    wrist_terminal=forearm['sections'][0]
    wrist_reference=forearm['sections'][1]
    # El perfil terminal incluye la protuberancia lateral de la antigua horquilla.
    # Conservamos su cota longitudinal, pero tomamos el centro transversal del
    # primer perfil estable para que la rotula quede sobre el eje resistente.
    wrist_section=(
        wrist_terminal[0],wrist_reference[1],wrist_reference[2],
        wrist_terminal[3],wrist_terminal[4],wrist_terminal[5])
    if shoulder_center is None:
        shoulder_center=_world_center(upper,shoulder_section,master_y_mm)
    else:
        shoulder_center=tuple(shoulder_center)
    wrist_center=_world_center(forearm,wrist_section,master_y_mm)
    _,_,upper_normal=_frame(upper)
    _,forearm_direction,_=_frame(forearm)
    default_shoulder_axis=(upper_normal[0],0,upper_normal[1])
    wrist_axis=(0,1,0)
    shoulder_outer_length=shoulder_section[3]*20
    shoulder_outer_radius=shoulder_section[4]*10
    if shoulder_size is not None:
        shoulder_outer_length,shoulder_outer_radius=shoulder_size
    wrist_outer_length=wrist_section[4]*20
    wrist_outer_radius=wrist_section[3]*10
    result={
        'shoulder':{
            'center':shoulder_center,
            'axis':default_shoulder_axis if shoulder_axis is None else tuple(shoulder_axis),
            'outer_length':shoulder_outer_length,'outer_radius':shoulder_outer_radius,
            'axle_radius':shoulder_outer_radius*.56,
        },
        'wrist':{
            'center':wrist_center,'axis':wrist_axis,
            'outer_length':wrist_outer_length,'outer_radius':wrist_outer_radius,
            'axle_radius':wrist_outer_radius*.42,
            'exit_axis':(-forearm_direction[0],0,-forearm_direction[1]),
            'connector_radius':13.0,
            'center_reference':'primer perfil estable del nucleo del antebrazo',
        },
    }
    if shoulder_axle_radius is not None:
        result['shoulder']['axle_radius']=shoulder_axle_radius
    for item in result.values():
        item['outer_p1'],item['outer_p2']=_axis_points(item['center'],item['axis'],item['outer_length'])
        item['axle_length']=item['outer_length']+4.0
        item['axle_p1'],item['axle_p2']=_axis_points(item['center'],item['axis'],item['axle_length'])
    if shoulder_axle_span is not None:
        item=result['shoulder']
        start,end=shoulder_axle_span
        item['axle_p1']=tuple(item['center'][i]+item['axis'][i]*start for i in range(3))
        item['axle_p2']=tuple(item['center'][i]+item['axis'][i]*end for i in range(3))
        item['axle_length']=end-start
    return result


def _integrate(manager,shell,spec,label,clearance_mm=0.8,margin_mm=2.0):
    import adsk.fusion

    outer=manager.createCylinderOrCone(
        _point(spec['outer_p1']),spec['outer_radius']*.1,
        _point(spec['outer_p2']),spec['outer_radius']*.1)
    if not outer or not manager.booleanOperation(shell,outer,adsk.fusion.BooleanTypes.UnionBooleanType):
        raise RuntimeError('No se pudo integrar el alojamiento de '+label)
    cutter_p1,cutter_p2=_axis_points(
        spec['center'],spec['axis'],spec['outer_length']+margin_mm*2)
    bore_radius=spec['axle_radius']+clearance_mm
    cutter=manager.createCylinderOrCone(
        _point(cutter_p1),bore_radius*.1,_point(cutter_p2),bore_radius*.1)
    if not cutter or not manager.booleanOperation(shell,cutter,adsk.fusion.BooleanTypes.DifferenceBooleanType):
        raise RuntimeError('No se pudo taladrar el alojamiento de '+label)
    if not shell.isSolid or shell.lumps.count!=1:
        raise RuntimeError('El alojamiento de '+label+' dividio la carcasa')
    axle=manager.createCylinderOrCone(
        _point(spec['axle_p1']),spec['axle_radius']*.1,
        _point(spec['axle_p2']),spec['axle_radius']*.1)
    if not axle or not axle.isSolid:
        raise RuntimeError('No se pudo crear el eje de '+label)
    report=('{}: alojamiento R{:.2f} x L{:.2f} mm; eje R{:.2f} x L{:.2f} mm; '
            'holgura {:.2f} mm').format(
                label,spec['outer_radius'],spec['outer_length'],spec['axle_radius'],
                spec['axle_length'],clearance_mm)
    return axle,report


def _integrate_closed_wrist(manager,shell,spec,clearance_mm=0.8,margin_mm=4.0):
    """Closed ball housing with one centered outlet toward the hand."""
    import adsk.fusion

    outer=manager.createSphere(_point(spec['center']),spec['outer_radius']*.1)
    if not outer or not manager.booleanOperation(shell,outer,adsk.fusion.BooleanTypes.UnionBooleanType):
        raise RuntimeError('No se pudo integrar la envolvente cerrada de muneca')

    cavity_radius=spec['axle_radius']+clearance_mm
    cavity=manager.createSphere(_point(spec['center']),cavity_radius*.1)
    if not cavity or not manager.booleanOperation(shell,cavity,adsk.fusion.BooleanTypes.DifferenceBooleanType):
        raise RuntimeError('No se pudo crear la cavidad esferica de muneca')

    axis=spec['exit_axis']
    start=tuple(spec['center'][i]-axis[i]*cavity_radius*.5 for i in range(3))
    end=tuple(spec['center'][i]+axis[i]*(spec['outer_radius']+margin_mm) for i in range(3))
    tunnel=manager.createCylinderOrCone(
        _point(start),(spec['connector_radius']+clearance_mm)*.1,
        _point(end),(spec['connector_radius']+clearance_mm)*.1)
    if not tunnel or not manager.booleanOperation(shell,tunnel,adsk.fusion.BooleanTypes.DifferenceBooleanType):
        raise RuntimeError('No se pudo abrir la salida central de muneca')
    if not shell.isSolid or shell.lumps.count!=1:
        raise RuntimeError('La envolvente cerrada de muneca dividio el antebrazo')

    ball=manager.createSphere(_point(spec['center']),spec['axle_radius']*.1)
    if not ball or not ball.isSolid:
        raise RuntimeError('No se pudo crear la rotula negra de muneca')
    report=('muneca: envolvente blanca esferica cerrada R{:.2f} mm; rotula negra R{:.2f} mm; '
            'unica salida central R{:.2f} mm; centro transversal tomado del primer perfil estable; '
            'holgura {:.2f} mm').format(
                spec['outer_radius'],spec['axle_radius'],
                spec['connector_radius']+clearance_mm,clearance_mm)
    return ball,report


def build(manager,upper_body,forearm_body,parts,master_y_mm,shoulder_center=None,
          shoulder_size=None,**shoulder_overrides):
    specs=parameters(parts,master_y_mm,shoulder_center=shoulder_center,
                     shoulder_size=shoulder_size,**shoulder_overrides)
    shoulder,shoulder_report=_integrate(manager,upper_body,specs['shoulder'],'hombro')
    wrist,wrist_report=_integrate_closed_wrist(manager,forearm_body,specs['wrist'])
    return shoulder,wrist,[shoulder_report,wrist_report]
