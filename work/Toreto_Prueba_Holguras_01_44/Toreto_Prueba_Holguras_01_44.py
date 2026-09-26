"""Trial arm links reconstructed in local frames from existing traces."""
import importlib.util
import json
import math
import traceback
from pathlib import Path
import adsk.core
import adsk.fusion

ROOT=Path(__file__).resolve().parent
NAME='94_BRAZO_HOLGURAS_PRUEBA_01_44'


def placement(axis,y_mm):
    lower,upper=axis[1],axis[0]
    dx=upper[0]-lower[0]
    dz=upper[2]-lower[2]
    length=math.hypot(dx,dz)
    if length<=0: raise ValueError('Eje frontal invalido')
    direction=(dx/length,dz/length)
    normal=(direction[1],-direction[0])
    matrix=adsk.core.Matrix3D.create()
    if not matrix.setWithCoordinateSystem(
            adsk.core.Point3D.create(lower[0]*.1,y_mm*.1,lower[2]*.1),
            adsk.core.Vector3D.create(normal[0],0,normal[1]),
            adsk.core.Vector3D.create(0,1,0),
            adsk.core.Vector3D.create(direction[0],0,direction[1])):
        raise RuntimeError('No se pudo definir el marco local')
    return matrix


def import_temp_bodies(component,items,feature_name,design):
    """Import transient bodies into one component without changing coordinates."""
    base=component.features.baseFeatures.add()
    base.name=feature_name
    if not base.startEdit():
        raise RuntimeError('No se pudo iniciar '+feature_name)
    try:
        for temp,label,appearance_name in items:
            body=component.bRepBodies.add(temp,base)
            if not body:
                raise RuntimeError('No se pudo crear '+label)
            body.name=label
            appearance=design.appearances.itemByName(appearance_name)
            if appearance:
                body.appearance=appearance
            body.isLightBulbOn=True
    finally:
        base.finishEdit()
    results=base.bodies
    if results.count!=len(items):
        raise RuntimeError(feature_name+': numero inesperado de cuerpos')
    for index,(_,label,_) in enumerate(items):
        results.item(index).name=label
    return {label:results.item(index) for index,(_,label,_) in enumerate(items)}


def pin_axis_edge(body_proxy,expected_axis,pin_radius_cm=.2):
    """Find a circular pin edge and report whether its normal matches the axis."""
    best=None
    for edge in body_proxy.edges:
        circle=adsk.core.Circle3D.cast(edge.geometry)
        if not circle:
            continue
        ok,_,normal,radius=circle.getData()
        if not ok or abs(radius-pin_radius_cm)>.005:
            continue
        alignment=(normal.x*expected_axis[0]+normal.y*expected_axis[1]+
                   normal.z*expected_axis[2])
        if best is None or abs(alignment)>abs(best[1]):
            best=(edge,alignment)
    if best is None or abs(best[1])<.98:
        raise RuntimeError('No se encontro un borde circular alineado en el pasador')
    return best


def create_revolute_joints(hand_component,occurrences,bodies,specs):
    """Create 20 as-built revolute joints without moving the validated pose."""
    collection=hand_component.asBuiltJoints
    created=[]
    flexion_signs={}
    for spec in specs:
        parent=occurrences[spec['parent']]
        child=occurrences[spec['child']]
        native_body,owner_occurrence=bodies[spec['pin_label']]
        proxy=native_body.createForAssemblyContext(owner_occurrence)
        if not proxy:
            raise RuntimeError('No se pudo contextualizar '+spec['pin_label'])
        edge,alignment=pin_axis_edge(proxy,spec['axis'])
        geometry=adsk.fusion.JointGeometry.createByCurve(
            edge,adsk.fusion.JointKeyPointTypes.CenterKeyPoint)
        if not geometry:
            raise RuntimeError('No se pudo definir el eje de '+spec['name'])
        # Fusion moves occurrenceOne relative to occurrenceTwo when the joint is
        # animated. The distal phalanx must therefore be supplied first.
        joint_input=collection.createInput(child,parent,geometry)
        if not joint_input:
            raise RuntimeError('No se pudo preparar '+spec['name'])
        if not joint_input.setAsRevoluteJointMotion(
                adsk.fusion.JointDirections.ZAxisJointDirection):
            raise RuntimeError('No se pudo configurar '+spec['name'])
        joint=collection.add(joint_input)
        if not joint:
            raise RuntimeError('No se pudo crear '+spec['name'])
        joint.name=spec['name']
        motion=adsk.fusion.RevoluteJointMotion.cast(joint.jointMotion)
        if not motion:
            raise RuntimeError(spec['name']+' no produjo movimiento revoluto')
        limits=motion.rotationLimits
        minimum=math.radians(spec['minimum_deg'])
        maximum=math.radians(spec['maximum_deg'])
        if alignment<0:
            minimum,maximum=-maximum,-minimum
        limits.minimumValue=minimum
        limits.maximumValue=maximum
        limits.isMinimumValueEnabled=True
        limits.isMaximumValueEnabled=True
        joint.isLightBulbOn=False
        created.append(joint)
        flexion_signs[joint.name]=(-1 if alignment<0 else 1)
    if len(created)!=20 or collection.count!=20:
        raise RuntimeError('No se crearon las 20 juntas revolutas previstas')
    return created,flexion_signs


def create_digit_motion_links(hand_component,joints,flexion_signs,travel_degrees):
    """Couple every digit using the requested progressive flexion ratios."""
    collection=hand_component.motionLinks
    by_name={joint.name:joint for joint in joints}
    rotation=adsk.fusion.JointMotionTypes.RevoluteJointRotateMotionType
    created=[]
    chains=[('JUNTA_DEDO_{}'.format(index),4) for index in range(1,5)]
    chains.append(('JUNTA_PULGAR',4))
    for prefix,joint_count in chains:
        master_name=prefix+'_1'
        master=by_name[master_name]
        for joint_index in range(2,joint_count+1):
            follower_name=prefix+'_{}'.format(joint_index)
            follower=by_name[follower_name]
            link_input=collection.createInput(master,follower)
            if not link_input:
                raise RuntimeError('No se pudo preparar la relacion '+follower_name)
            link_input.motionOne=rotation
            link_input.motionTwo=rotation
            link_input.valueOne=adsk.core.ValueInput.createByString(
                '{} deg'.format(travel_degrees[master_name]))
            link_input.valueTwo=adsk.core.ValueInput.createByString(
                '{} deg'.format(travel_degrees[follower_name]))
            link_input.isReversed=(
                flexion_signs[master_name]!=flexion_signs[follower_name])
            link=collection.add(link_input)
            if not link:
                raise RuntimeError('No se pudo crear la relacion '+follower_name)
            link.name='RELACION_CIERRE_{}_1_A_{}'.format(
                prefix.replace('JUNTA_',''),joint_index)
            created.append(link)
    if len(created)!=15 or collection.count!=15:
        raise RuntimeError('No se crearon las 15 relaciones de cierre previstas')
    return created


def run(context):
    app=adsk.core.Application.get()
    output=None
    try:
        design=adsk.fusion.Design.cast(app.activeProduct)
        if not design: raise RuntimeError('Abre el documento del robot')
        root=design.rootComponent
        if root.occurrences.count or root.bRepBodies.count:
            raise RuntimeError('SOLO documento nuevo vacio: no se modifica el montaje existente')
        if any(o.component.name==NAME for o in root.occurrences):
            app.userInterface.messageBox('La prueba de marcos locales ya existe; no se duplica.')
            return
        spec=importlib.util.spec_from_file_location('toreto_flat_local',ROOT/'toreto_flat_profile_geometry.py')
        flat=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(flat)
        filter_spec=importlib.util.spec_from_file_location('toreto_local_filter',ROOT/'toreto_local_section_filter.py')
        local_filter=importlib.util.module_from_spec(filter_spec)
        filter_spec.loader.exec_module(local_filter)
        terminal_spec=importlib.util.spec_from_file_location('toreto_local_terminals',ROOT/'toreto_local_terminals.py')
        terminals=importlib.util.module_from_spec(terminal_spec)
        terminal_spec.loader.exec_module(terminals)
        outer_spec=importlib.util.spec_from_file_location('toreto_outer_joints',ROOT/'toreto_outer_joints.py')
        outer_joints=importlib.util.module_from_spec(outer_spec)
        outer_spec.loader.exec_module(outer_joints)
        hand_spec=importlib.util.spec_from_file_location('toreto_hand',ROOT/'toreto_hand.py')
        hand=importlib.util.module_from_spec(hand_spec)
        hand_spec.loader.exec_module(hand)
        data=json.loads((ROOT/'link_local_sections.json').read_text(encoding='utf-8'))
        hand_data=json.loads((ROOT/'hand_local_sections.json').read_text(encoding='utf-8'))
        if data.get('units')!='cm' or set(data.get('parts',{}))!={'upper','forearm'}:
            raise RuntimeError('Datos locales invalidos')
        manager=adsk.fusion.TemporaryBRepManager.get()
        pending=[]
        reports=[]
        for key,label in (('upper','01_BRAZO_LOCAL_SIN_REBAJES'),('forearm','02_ANTEBRAZO_LOCAL_SIN_REBAJES')):
            item=data['parts'][key]
            selected=local_filter.stable_run(item['sections'])
            body=flat.loft(manager,selected['sections'],label)
            body,terminal_reports=terminals.extend_to_measured_limits(
                manager,flat,body,item['sections'],selected,label,
                extend_before=(key!='forearm'),extend_after=(key!='upper'))
            transform=placement(item['front_axis'],data['master_plane_y_mm'])
            if not manager.transform(body,transform):
                raise RuntimeError(label+': no se pudo colocar en la postura frontal')
            if not body.isSolid or body.lumps.count!=1 or body.volume<=1e-6:
                raise RuntimeError(label+': resultado local invalido')
            pending.append((body,label,'TORETO Blanco satinado'))
            reports.append(
                '{}: {} perfiles estables; extremos aplazados {}/{}'.format(
                    label, len(selected['sections']), selected['omitted_before'], selected['omitted_after']))
            reports.extend(terminal_reports)
        joint,joint_report,joint_spec=terminals.build_elbow(manager,data['parts'],data['master_plane_y_mm'])
        seat_report=terminals.integrate_elbow(manager,pending[0][0],pending[1][0],joint_spec)
        pending.append((joint,'03_EJE_Y_ENLACE_CODO','TORETO Negro profundo'))
        reports.append(joint_report)
        reports.append(seat_report)
        shoulder,wrist,outer_reports=outer_joints.build(
            manager,pending[0][0],pending[1][0],data['parts'],data['master_plane_y_mm'])
        pending.append((shoulder,'04_EJE_HOMBRO','TORETO Negro profundo'))
        pending.append((wrist,'05_EJE_MUNECA','TORETO Negro profundo'))
        reports.extend(outer_reports)
        hand_bodies,hand_report=hand.build(manager,flat,hand_data)
        clearance_spec=importlib.util.spec_from_file_location('toreto_clearance',ROOT/'toreto_clearance.py')
        clearance=importlib.util.module_from_spec(clearance_spec)
        clearance_spec.loader.exec_module(clearance)
        pair_spec=importlib.util.spec_from_file_location('toreto_pair_validation',ROOT/'toreto_pair_validation.py')
        pair_validation=importlib.util.module_from_spec(pair_spec)
        pair_spec.loader.exec_module(pair_validation)
        slots_spec=importlib.util.spec_from_file_location('toreto_finger_slots',ROOT/'toreto_finger_slots.py')
        slots=importlib.util.module_from_spec(slots_spec)
        slots_spec.loader.exec_module(slots)
        diagnostic_path=ROOT/'prueba_alojamientos_pulgar_v3.json'
        try:
            hand_bodies, supports = slots.repair(manager,hand,hand_bodies,hand_data)
            diagnostic = pair_validation.run(manager, hand, clearance, hand_bodies,
                hand_data, diagnostic_path)
            diagnostic['finger_supports']=supports
        except Exception as error:
            diagnostic={'status':'rejected_finger_slots','error':str(error)}
        diagnostic_path.write_text(json.dumps(diagnostic,indent=2),encoding='utf-8')
        app.userInterface.messageBox(
            'Diagnostico temporal, sin crear piezas ni guardar Fusion.\n' +
            'Estado: ' + diagnostic['status'] + '\n' + diagnostic.get('error', '') +
            '\nDetalles: prueba_alojamientos_pulgar_v3.json', 'Alojamientos del pulgar v3')
        return  # Diagnostic mode deliberately cannot publish an unvalidated hand.
        hand_bodies,clearance_report=clearance.repair(manager,hand,hand_bodies,hand_data)
        reports.append(clearance_report)
        reports.append(hand_report)
        output=root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        if not output:
            raise RuntimeError('No se pudo crear el componente superior del brazo')
        output.isGroundToParent=True
        component=output.component
        component.name=NAME
        arm_bodies=import_temp_bodies(
            component,pending,'SECCIONES_LOCALES_POSTURA_FRONTAL',design)

        hand_occurrence=component.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        if not hand_occurrence:
            raise RuntimeError('No se pudo crear el conjunto de la mano')
        hand_component=hand_occurrence.component
        hand_component.name='06_MANO_ARTICULABLE'
        hand_occurrence.isGroundToParent=True
        grouped={}
        for temp,label,appearance_name,group_name in hand_bodies:
            grouped.setdefault(group_name,[]).append((temp,label,appearance_name))
        if len(grouped)!=21:
            raise RuntimeError('La mano no produjo los 21 grupos mecanicos previstos')
        hand_count=0
        occurrences={}
        body_records={}
        for group_name,items in grouped.items():
            occurrence=hand_component.occurrences.addNewComponent(adsk.core.Matrix3D.create())
            if not occurrence:
                raise RuntimeError('No se pudo crear '+group_name)
            occurrence.component.name=group_name
            occurrence.component.attributes.add('RobotToreto','grupo_cinematico',group_name)
            occurrences[group_name]=occurrence
            imported=import_temp_bodies(
                occurrence.component,items,'GEOMETRIA_'+group_name,design)
            hand_count+=len(imported)
            for label,native_body in imported.items():
                body_records[label]=(native_body,occurrence)
        if len(arm_bodies)!=len(pending) or hand_count!=len(hand_bodies):
            raise RuntimeError('Recuento inesperado al organizar los componentes')
        occurrences['MANO_00_PALMA'].isGroundToParent=True
        joint_definitions=hand.joint_specs(hand_data)
        joints,flexion_signs=create_revolute_joints(
            hand_component,occurrences,body_records,joint_definitions)
        travel_degrees={
            definition['name']:definition['travel_deg']
            for definition in joint_definitions}
        motion_links=create_digit_motion_links(
            hand_component,joints,flexion_signs,travel_degrees)
        hand_component.attributes.add('RobotToreto','estructura','PALMA_CARDAN_MAS_19_FALANGES')
        hand_component.attributes.add('RobotToreto','juntas_revolutas',str(len(joints)))
        hand_component.attributes.add('RobotToreto','relaciones_cierre',str(len(motion_links)))
        component.attributes.add('RobotToreto','estado','PRUEBA_20_JUNTAS_PULGAR_CARDAN')
        component.attributes.add('RobotToreto','referencia','FRONTAL_POSTURA_MAESTRA_LATERAL_SOLO_PROFUNDIDAD')
        component.attributes.add('RobotToreto','filtrado_terminal','RATIO_CAMBIO_LOCAL_MAX_1_5')
        component.attributes.add('RobotToreto','articulacion_dedos','PASADOR_D4_BORE_D4_7_GAP_AXIAL_0_4')
        component.attributes.add('RobotToreto','topes_dedos','PRINCIPALES_NEG_60_60_50_40_PULGAR_POS_30_40_35_20')
        app.userInterface.messageBox(
            'Creado 94_BRAZO_HOLGURAS_PRUEBA_01_44.\n\n'
            'Brazo y antebrazo se midieron perpendicularmente a sus propios ejes y se emparejaron por posicion normalizada. '
            'Se colocan en la postura frontal, sobre un plano Y=45 mm. El lateral aporta profundidad, no postura.\n\n'
            'Fusion autointersectaba el loft al plegar los perfiles terminales. Esta ejecucion conserva las medidas en el JSON, '
            'crea los tramos estables y trata los perfiles extremos abruptos como articulaciones separadas. El codo validado se conserva; '
            'el alojamiento blanco de hombro conserva su geometria. La muneca usa una envolvente blanca cerrada en todas sus caras, '
            'con cavidad de rotula y una unica salida inferior centrada para el conector negro R13 mm. '
            'El centro transversal de la muneca se toma del primer perfil estable del nucleo del antebrazo, eliminando el desplazamiento lateral de 23,49 mm que introducia el perfil terminal. '
            'La mano usa otra parametrizacion local. La palma negra se alarga y se estrecha desde los nudillos hasta la muneca para eliminar la silueta de campana; '
            'el conector de muneca y la base lateral reforzada del pulgar forman parte de la palma, con una horquilla abierta de 10 mm para liberar el cardan; '
            'la palma se orienta con el eje del conector de muneca y elimina su desplazamiento lateral interno; '
            'la fila de nudillos queda perpendicular a ese eje y los cuatro dedos salen rectos y paralelos a el; '
            'los ejes cilindricos atraviesan el ancho local de cada dedo, por lo que su giro produce flexion hacia la palma; '
            'las terminales blancas se construyen como lofts alargados y abombados, sin esferas independientes; '
            'cuatro cunas separadas suavizan la salida desde una palma negra aplanada: 20 mm de profundidad junto a dedos de 14-15 mm, aumentando solo hasta 26 mm en la conexion de muneca; '
            'el lado cubital conserva un arco progresivo de hasta 5 mm para permitir el cierre; '
            'cada uno de los 20 nudillos se divide en dos casquillos exteriores, uno central y un pasador desmontable de 4 mm; '
            'los taladros tienen 4,70 mm, con 0,35 mm de holgura radial y 0,40 mm entre casquillos; '
            'cada casquillo central incorpora un tope movil y los dos exteriores un tope fijo: los cuatro dedos principales invierten su cierre con limites -60/-60/-50/-40 grados, mientras el pulgar conserva 30/40/35/20 grados y su giro hacia dentro; '
            'el pulgar aumenta su seccion y termina en una falange blanca redondeada; anclaje, cardan y falanges se reflejan juntos hacia la cara Y positiva, opuesta al cierre ascendente de los dedos principales, y los ejes tambien se reflejan para conservar el giro y dirigir la yema hacia el centro de la palma; '
            'las falanges son carcasas rectangulares redondeadas, ligeramente decrecientes y permanecen separadas:\n- '+ '\n- '.join(reports) +'\n\n'
            'Las falanges, los casquillos y los pasadores permanecen como cuerpos separados. Los topes forman parte de los casquillos y no aumentan el numero de piezas; los conductos de accionamiento se incorporaran despues. '
            'La mano se organiza bajo 06_MANO_ARTICULABLE en 21 componentes: una palma, un cardan intermedio del pulgar, dieciseis falanges principales y tres falanges del pulgar. '
            'Los casquillos exteriores y el pasador pertenecen al componente proximal; el casquillo central pertenece al componente distal. '
            'Se crean 20 juntas revolutas reales sobre los bordes circulares de los pasadores. La palma queda fijada al conjunto y cada falange conserva solo su giro asignado; los limites digitales coinciden con los topes fisicos. '
            'La pieza distal se registra como primer componente de cada junta para que Fusion mueva el dedo y mantenga inmovil la palma durante la animacion. Quince relaciones de movimiento enlazan cada cadena con cierre progresivo: los dedos principales recorren el lado angular opuesto con magnitudes 60/60/50/40 y el pulgar conserva 30/40/35/20 hacia dentro. El componente superior, el conjunto de mano y la palma quedan fijados durante esta validacion para que ninguna junta secundaria desplace el brazo. '
            'No se han cambiado lienzos ni componentes anteriores.')
    except Exception:
        error=traceback.format_exc()
        if output and output.isValid:
            error+='\nSalida parcial SOLO en documento nuevo; no se elimina automaticamente.'
        app.userInterface.messageBox(error,'Error de marcos locales')


def stop(context):
    pass
