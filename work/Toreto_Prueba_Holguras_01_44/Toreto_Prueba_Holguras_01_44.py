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
SCRIPT_VERSION='v10b'
# 'ensayo'    -> ensayo de colisiones de la v8, sin crear piezas.
# 'ver_pinza' -> publica la mano (4 motores) en la pinza al 75%, para mirarla.
# 'ensayo_lateral' -> SOLO pinza lateral (v10b); no publica ni mueve componentes.
MODE='ensayo_lateral'


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


def pin_axis_edge(body_proxy,expected_axis,pin_radius_cm):
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
        raise RuntimeError('No se encontro un borde circular alineado de radio {} mm'.format(
            round(pin_radius_cm*10,3)))
    return best


def create_revolute_joints(hand_component,occurrences,bodies,specs,pin_radius_mm):
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
        # Cada pasador con su radio: el cardan y la base del pulgar son de
        # 2,8 mm, el resto de 4 mm (toreto_hand.hinge_dimensions).
        try:
            edge,alignment=pin_axis_edge(proxy,spec['axis'],pin_radius_mm(spec)*.1)
        except RuntimeError as error:
            raise RuntimeError(spec['name']+': '+str(error))
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


def create_digit_motion_links(hand_component,joints,flexion_signs,travel_degrees,plan):
    """Mano de 4 motores (v9): cada seguidora enlazada directamente a la
    maestra de su motor; el cardan (JUNTA_PULGAR_1) va suelto."""
    collection=hand_component.motionLinks
    by_name={joint.name:joint for joint in joints}
    rotation=adsk.fusion.JointMotionTypes.RevoluteJointRotateMotionType
    created=[]
    for master_name,follower_name in plan:
        link_input=collection.createInput(by_name[master_name],by_name[follower_name])
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
        link.name='RELACION_{}_A_{}'.format(
            master_name.replace('JUNTA_',''),follower_name.replace('JUNTA_',''))
        created.append(link)
    if len(created)!=len(plan) or collection.count!=len(plan):
        raise RuntimeError('No se crearon las {} relaciones previstas'.format(len(plan)))
    return created


def _center_mm(box):
    return [round((box.minPoint.x+box.maxPoint.x)*5,3),
            round((box.minPoint.y+box.maxPoint.y)*5,3),
            round((box.minPoint.z+box.maxPoint.z)*5,3)]


def expected_pinch_centers(manager,hand,clearance,groups,motor_validation,
                           hand_bodies,hand_data,fractions):
    """Centro de cada falange en la pinza segun el MISMO calculo del ensayo,
    para comprobar despues que Fusion ha colocado la mano igual."""
    specs={s['child']:s for s in hand.joint_specs(hand_data)}
    centers={}
    for temp,label,_,group in hand_bodies:
        if not (label.startswith('07_DEDO_') or label.startswith('09_PULGAR_')):
            continue
        chain=clearance.chain_for(group,specs)
        posed=motor_validation._pose(manager,groups,clearance,temp,chain,fractions)
        centers[label]=_center_mm(posed.boundingBox)
    return centers


def apply_pose(joints,flexion_signs,plan,angles):
    """Mueve solo las maestras (las seguidoras van por sus relaciones) y
    devuelve lo que Fusion dice que ha quedado en cada junta."""
    by_name={joint.name:joint for joint in joints}
    followers={follower for _,follower in plan}
    for name,degrees in angles.items():
        if name in followers or degrees==0.0:
            continue
        motion=adsk.fusion.RevoluteJointMotion.cast(by_name[name].jointMotion)
        motion.rotationValue=math.radians(degrees*flexion_signs[name])
    adsk.doEvents()
    readback={}
    for name,degrees in angles.items():
        motion=adsk.fusion.RevoluteJointMotion.cast(by_name[name].jointMotion)
        got=math.degrees(motion.rotationValue)*flexion_signs[name]
        readback[name]=dict(esperado_deg=round(degrees,3),fusion_deg=round(got,3),
                            diferencia_deg=round(got-degrees,3))
    return readback


def compare_centers(expected,body_records):
    result={}
    for label,center in expected.items():
        native_body,occurrence=body_records[label]
        proxy=native_body.createForAssemblyContext(occurrence)
        got=_center_mm(proxy.boundingBox)
        result[label]=dict(ensayo_mm=center,fusion_mm=got,
                           distancia_mm=round(math.dist(center,got),3))
    return result


def tip_gap_mm(body_records,groups):
    try:
        a=body_records[groups.THUMB_TIP]
        b=body_records[groups.INDEX_TIP]
        result=adsk.core.Application.get().measureManager.measureMinimumDistance(
            a[0].createForAssemblyContext(a[1]),b[0].createForAssemblyContext(b[1]))
        return round(result.value*10,3) if result else None
    except Exception:
        return None


def publish_pinch_view(design,root,pending,hand_bodies,hand,clearance,groups,
                       motor_validation,hand_data,manager,report_path):
    """v9: publica brazo y mano en el documento VACIO y deja la mano en la
    pinza al 75%. Sin clearance.repair(): la palma NO esta recortada ni
    validada. Devuelve el informe (tambien escrito en report_path)."""
    fractions=groups.pinch_view_fractions()
    joint_definitions=hand.joint_specs(hand_data)
    plan=groups.motion_link_plan(joint_definitions)
    angles=groups.pose_angles(joint_definitions,fractions,clearance.signed_travel)
    # Antes de importar: los cuerpos temporales siguen intactos.
    expected=expected_pinch_centers(manager,hand,clearance,groups,motor_validation,
                                    hand_bodies,hand_data,fractions)
    report=dict(version='v9',modo='ver_pinza',estado='publicando',
                fracciones=fractions,
                aviso=('Solo para mirar. Palma sin recorte y NO validada; sin '
                       'holgura continua, resistencia ni tendones.'))

    def record():
        report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    record()

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
    report.update(estado='piezas_creadas',cuerpos_mano=hand_count)
    record()

    joints,flexion_signs=create_revolute_joints(
        hand_component,occurrences,body_records,joint_definitions,
        lambda spec:hand.hinge_dimensions(spec)[2])
    travel_degrees={d['name']:d['travel_deg'] for d in joint_definitions}
    links=create_digit_motion_links(
        hand_component,joints,flexion_signs,travel_degrees,plan)
    report.update(estado='juntas_creadas',juntas=len(joints),relaciones=len(links),
                  signos_eje={k:v for k,v in flexion_signs.items() if v<0})
    record()

    report['juntas_en_pinza']=apply_pose(joints,flexion_signs,plan,angles)
    report['estado']='pose_aplicada'
    record()
    report['falanges_frente_al_ensayo']=compare_centers(expected,body_records)
    worst=max(v['distancia_mm'] for v in report['falanges_frente_al_ensayo'].values())
    worst_joint=max(abs(v['diferencia_deg']) for v in report['juntas_en_pinza'].values())
    report['hueco_puntas_mm']=tip_gap_mm(body_records,groups)
    report['resumen']=dict(
        peor_diferencia_junta_deg=worst_joint,
        peor_distancia_falange_mm=worst,
        pose_igual_al_ensayo=(worst_joint<.05 and worst<.5),
        hueco_puntas_en_ensayo_mm=0.28)
    report['estado']='publicado'
    record()

    hand_component.attributes.add('RobotToreto','estructura','PALMA_CARDAN_MAS_19_FALANGES')
    hand_component.attributes.add('RobotToreto','motores','INDICE_RESTO_FLEXION_PULGAR_CARDAN')
    hand_component.attributes.add('RobotToreto','juntas_revolutas',str(len(joints)))
    hand_component.attributes.add('RobotToreto','relaciones_motor',str(len(links)))
    hand_component.attributes.add('RobotToreto','palma','SIN_RECORTE_NO_VALIDADA')
    component.attributes.add('RobotToreto','estado','VISTA_PINZA_V9_NO_VALIDADA')
    component.attributes.add('RobotToreto','topes_dedos','INDICE_NEG_54_54_45_36_RESTO_NEG_60_60_50_40_PULGAR_POS_30_40_35_20')
    return output,report


def run(context):
    app=adsk.core.Application.get()
    output=None
    try:
        design=adsk.fusion.Design.cast(app.activeProduct)
        if not design: raise RuntimeError('Abre el documento del robot')
        if MODE not in ('ensayo', 'ver_pinza', 'ensayo_lateral'):
            raise RuntimeError('Modo de ensayo desconocido: '+MODE)
        root=design.rootComponent
        # Un diseno de PIEZA solo admite un componente; el script crea varios.
        intent=getattr(design,'designIntent',None)
        part_intent=getattr(getattr(adsk.fusion,'DesignIntentTypes',None),
                            'PartDesignIntentType',None)
        if intent is not None and part_intent is not None and intent==part_intent:
            raise RuntimeError('Este documento es un DISENO DE PIEZA. Hace falta un '
                               'documento vacio de diseno HIBRIDO (o de ensamblaje).')
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
        # v7: mano de 4 motores. Sustituye al cierre sincronizado de toda la
        # mano (toreto_pair_validation.py, conservado sin cambios).
        groups_spec=importlib.util.spec_from_file_location('toreto_motor_groups',ROOT/'toreto_motor_groups.py')
        motor_groups=importlib.util.module_from_spec(groups_spec)
        groups_spec.loader.exec_module(motor_groups)
        motor_spec=importlib.util.spec_from_file_location('toreto_motor_validation',ROOT/'toreto_motor_validation.py')
        motor_validation=importlib.util.module_from_spec(motor_spec)
        motor_spec.loader.exec_module(motor_validation)
        slots_spec=importlib.util.spec_from_file_location('toreto_finger_slots',ROOT/'toreto_finger_slots.py')
        slots=importlib.util.module_from_spec(slots_spec)
        slots_spec.loader.exec_module(slots)
        if MODE=='ensayo_lateral':
            face_spec=importlib.util.spec_from_file_location(
                'toreto_contact_faces_v10',ROOT/'toreto_contact_faces.py')
            faces=importlib.util.module_from_spec(face_spec)
            face_spec.loader.exec_module(faces)
            lateral_spec=importlib.util.spec_from_file_location(
                'toreto_lateral_validation',ROOT/'toreto_lateral_validation.py')
            lateral=importlib.util.module_from_spec(lateral_spec)
            lateral_spec.loader.exec_module(lateral)
            diagnostic_path=ROOT/'prueba_mano_4_motores_v10b.json'
            try:
                hand_bodies,_=slots.repair(manager,hand,hand_bodies,hand_data)
                diagnostic=lateral.run(manager,hand,clearance,motor_groups,
                    motor_validation,faces,hand_bodies,hand_data,diagnostic_path,
                    intervals=12)
            except Exception as error:
                try:
                    diagnostic=json.loads(diagnostic_path.read_text(encoding='utf-8'))
                except Exception:
                    diagnostic={'version':'v10b','scenario':'pinza_lateral'}
                diagnostic.update(status='error_no_resuelto',error=str(error),
                                  traceback=traceback.format_exc())
                diagnostic_path.write_text(json.dumps(
                    diagnostic,indent=2,ensure_ascii=False),encoding='utf-8')
            contact=diagnostic.get('first_contact')
            lines=['v10b: solo pinza lateral, sin publicar ni guardar Fusion.',
                   'Estado: '+diagnostic['status'],
                   'Primer contacto: muestra {} (afinado: indice al {:.1f}%)'.format(
                       contact['sample'],contact['fraction']*100)
                   if contact else 'Primer contacto: ninguno']
            if contact:
                for pair in contact.get('pairs',[]):
                    lines.append('Cara del pulgar: {}; cara del indice: {} ({} mm3)'.format(
                        pair['pulgar']['region'],pair['indice']['region'],
                        pair['intersection_mm3']))
                stability=contact.get('stability')
                if stability:
                    lines.append('Misma cara en {} posturas con contacto: {}'.format(
                        len(stability['postures']),
                        'SI' if stability['consistent'] else 'NO'))
            if diagnostic.get('warnings'):
                lines.append('Avisos de volumen: {} (ver JSON)'.format(
                    len(diagnostic['warnings'])))
            if diagnostic.get('error'):
                lines.append(diagnostic['error'])
            lines.append('Detalles: prueba_mano_4_motores_v10b.json')
            app.userInterface.messageBox('\n'.join(lines),'Toreto v10b - pinza lateral')
            return
        if MODE=='ver_pinza':
            # Misma geometria que midio la v8: slots.repair() si, clearance.repair() NO.
            hand_bodies,_=slots.repair(manager,hand,hand_bodies,hand_data)
            view_path=ROOT/'vista_pinza_v9.json'
            try:
                output,view=publish_pinch_view(
                    design,root,pending,hand_bodies,hand,clearance,motor_groups,
                    motor_validation,hand_data,manager,view_path)
            except Exception:
                try:
                    partial=json.loads(view_path.read_text(encoding='utf-8'))
                except Exception:
                    partial={'version':'v9','modo':'ver_pinza'}
                partial.update(estado_alcanzado=partial.get('estado'),estado='error',
                               traceback=traceback.format_exc())
                view_path.write_text(json.dumps(partial,indent=2,ensure_ascii=False),encoding='utf-8')
                raise
            summary=view['resumen']
            app.userInterface.messageBox(
                'Mano publicada en la pinza al 75% (v9, 4 motores).\n\n'
                'Pose igual a la del ensayo: {}\n'
                'Peor diferencia en juntas: {} grados\n'
                'Peor distancia de falange: {} mm\n'
                'Hueco entre puntas: {} mm (ensayo: 0,28 mm)\n\n'
                'Maestras para mover a mano: JUNTA_DEDO_1_1 (indice), JUNTA_DEDO_2_1 '
                '(resto), JUNTA_PULGAR_2 (flexion pulgar), JUNTA_PULGAR_1 (cardan).\n\n'
                'SOLO PARA MIRAR: palma sin recorte y NO validada.\n'
                'Detalles: vista_pinza_v9.json'.format(
                    'SI' if summary['pose_igual_al_ensayo'] else 'NO - revisar',
                    summary['peor_diferencia_junta_deg'],
                    summary['peor_distancia_falange_mm'],
                    view['hueco_puntas_mm']),
                'Toreto '+SCRIPT_VERSION+' - vista de la pinza')
            return
        # v8: el indice con su propio recorrido (90%), ver toreto_hand.py.
        diagnostic_path=ROOT/'prueba_mano_4_motores_v8.json'
        try:
            hand_bodies, supports = slots.repair(manager,hand,hand_bodies,hand_data)
            diagnostic = motor_validation.run(manager, hand, clearance, motor_groups,
                hand_bodies, hand_data, diagnostic_path, version='v8')
            diagnostic['finger_supports']=supports
        except Exception as error:
            diagnostic={'status':'rejected_finger_slots','error':str(error),
                        'traceback':traceback.format_exc()}
        diagnostic_path.write_text(json.dumps(diagnostic,indent=2,ensure_ascii=False),encoding='utf-8')
        lines=['Diagnostico temporal, sin crear piezas ni guardar Fusion.',
               'Estado global: '+diagnostic['status']]
        summary=diagnostic.get('summary')
        if summary:
            lines.append('Mano abierta: '+summary['mano_abierta'])
            for name,status in summary['motores_solos'].items():
                lines.append('  '+name+': '+status)
            lines.append('Pinza del boli: '+summary['pinza_boli'])
        if diagnostic.get('error'):
            lines.append(diagnostic['error'])
        lines.append('Detalles: prueba_mano_4_motores_v8.json')
        app.userInterface.messageBox('\n'.join(lines),'Mano de 4 motores v8')
        return  # El ensayo nunca publica; la vista la crea MODE='ver_pinza'.
    except Exception:
        error=traceback.format_exc()
        if output and output.isValid:
            error+='\nSalida parcial SOLO en documento nuevo; no se elimina automaticamente.'
        app.userInterface.messageBox(error,'Error de marcos locales')


def stop(context):
    pass
