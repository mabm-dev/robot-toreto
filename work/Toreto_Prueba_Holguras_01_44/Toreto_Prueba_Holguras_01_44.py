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
SCRIPT_VERSION='v14'
# 'ensayo'    -> ensayo de colisiones de la v8, sin crear piezas.
# 'ver_pinza' -> publica la mano (4 motores) en la pinza al 75%, para mirarla.
# 'ensayo_lateral' -> SOLO pinza lateral (v10b); no publica ni mueve componentes.
# 'ver_brazo' -> v11: brazo con las medidas y la postura de la lamina y la
#                mano abierta (toreto_arm_pose.py); publica para mirarlo.
#                v13: con el hombro encajado en el conector del pecho.
#                v14: disco negro del hombro visible y colores.
# 'alturas'      -> v14: en el MONTAJE, SOLO LECTURA: alturas de cada modulo y
#                cuerpo y huecos entre modulos (alturas_montaje_v14.json).
# 'comprobar'  -> v14: alturas + interferencias juntas (solo lectura).
# 'cadera'     -> v14: gira en memoria lo de encima de la cadera 5..85 grados
#                con el eje a Z 380/400/420 y mide choques (solo lectura).
# 'interferencias' -> v14: en el MONTAJE, SOLO LECTURA: choques de cada cuerpo
#                de los brazos con el resto (interferencias_brazos_v14.json).
# 'juntas_espejo' -> v12: en el MONTAJE, anade juntas y relaciones a la mano
#                izquierda copiada por simetria. No crea ni mueve geometria.
MODE='cadera'


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


# v14: colores de los modulos. Antes solo se aplicaba la apariencia si ya
# existia en el documento; el brazo se publica en un documento nuevo, donde no
# existe, y quedaba con el acero gris por defecto.
_COLORS={'TORETO Blanco satinado':(238,239,237),'TORETO Negro profundo':(18,21,24),
         'TORETO Grafito':(43,48,53),'TORETO Cian':(0,174,235)}


def _appearance(design,name):
    existing=design.appearances.itemByName(name)
    if existing or name not in _COLORS:
        return existing
    try:
        app=adsk.core.Application.get()
        generic=None
        library=app.materialLibraries.itemById('BA5EE55E-9982-449B-9D66-9F036540E140')
        if library:
            generic=library.appearances.itemById('Prism-129')
        for index in range(app.materialLibraries.count):
            if generic:
                break
            generic=app.materialLibraries.item(index).appearances.itemById('Prism-129')
        if not generic:
            return None
        appearance=design.appearances.addByCopy(generic,name)
        color=appearance.appearanceProperties.itemById('opaque_albedo')
        if color:
            color.value=adsk.core.Color.create(*_COLORS[name],255)
        return appearance
    except Exception:
        return None


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
            appearance=_appearance(design,appearance_name)
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
                           hand_bodies,hand_data,fractions,placement=None):
    """Centro de cada falange en la pinza segun el MISMO calculo del ensayo,
    para comprobar despues que Fusion ha colocado la mano igual.
    placement (v11): la pieza calculada se mueve a la postura de la lamina
    ANTES de medir su caja. Girar el centro de la caja no vale: la caja
    alineada con los ejes de una pieza asimetrica cambia al girarla (la v11
    en Fusion dio 0,1-2 mm segun la forma de cada falange por eso)."""
    specs={s['child']:s for s in hand.joint_specs(hand_data)}
    centers={}
    for temp,label,_,group in hand_bodies:
        if not (label.startswith('07_DEDO_') or label.startswith('09_PULGAR_')):
            continue
        chain=clearance.chain_for(group,specs)
        posed=motor_validation._pose(manager,groups,clearance,temp,chain,fractions)
        if placement is not None and not manager.transform(posed,_matrix3d(placement)):
            raise RuntimeError('No se pudo colocar la referencia de '+label)
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


# v11: que pieza del brazo acompana a cada tramo al colocarlo como la lamina.
ARM_GROUPS={'01_BRAZO_LOCAL_SIN_REBAJES':'upper','03_EJE_Y_ENLACE_CODO':'upper',
            '04_EJE_HOMBRO':'upper','02_ANTEBRAZO_LOCAL_SIN_REBAJES':'forearm',
            '05_EJE_MUNECA':'forearm'}


def _matrix3d(rigid):
    matrix=adsk.core.Matrix3D.create()
    if not matrix.setWithArray(rigid.array16_cm()):
        raise RuntimeError('No se pudo definir la matriz de colocacion')
    return matrix


def place_like_lamina(manager,pending,hand_bodies,arm_pose):
    """Mueve los cuerpos temporales (aun sin importar) a la postura de la
    lamina: brazo superior, antebrazo y mano, cada uno con su giro rigido."""
    if set(label for _,label,_ in pending)!=set(ARM_GROUPS):
        raise RuntimeError('Piezas del brazo inesperadas: no se coloca')
    for body,label,_ in pending:
        if not manager.transform(body,_matrix3d(arm_pose[ARM_GROUPS[label]])):
            raise RuntimeError('No se pudo colocar '+label)
    hand_matrix=_matrix3d(arm_pose['hand'])
    for body,label,_,_ in hand_bodies:
        if not manager.transform(body,hand_matrix):
            raise RuntimeError('No se pudo colocar '+label)


def placed_specs(specs,rigid):
    """Juntas de la mano con centros y ejes llevados a la postura de la lamina."""
    result=[]
    for spec in specs:
        moved=dict(spec)
        moved['center_mm']=list(rigid.point(spec['center_mm']))
        moved['axis']=list(rigid.vector(spec['axis']))
        result.append(moved)
    return result


def arm_check(arm_bodies,arm_pose):
    """Donde quedaron de verdad, en Fusion, el eje del hombro y la rotula de
    la muneca (piezas simetricas: el centro de su caja es su centro)."""
    result={}
    for label,key in (('04_EJE_HOMBRO','tapa_hombro'),('05_EJE_MUNECA','muneca_rotula')):
        got=_center_mm(arm_bodies[label].boundingBox)
        expected=[round(v,3) for v in arm_pose['placed_mm'][key]]
        result[key]=dict(esperado_mm=expected,fusion_mm=got,
                         distancia_mm=round(math.dist(expected,got),3))
    return result


def publish_pinch_view(design,root,pending,hand_bodies,hand,clearance,groups,
                       motor_validation,hand_data,manager,report_path,
                       fractions=None,arm_pose=None,version='v9',mode='ver_pinza'):
    """v9: publica brazo y mano en el documento VACIO y deja la mano en la
    pinza al 75%. Sin clearance.repair(): la palma NO esta recortada ni
    validada. Devuelve el informe (tambien escrito en report_path).
    v11: con arm_pose, brazo y mano se colocan en la postura de la lamina
    antes de importarlos; fractions={} deja la mano abierta."""
    fractions=groups.pinch_view_fractions() if fractions is None else fractions
    joint_definitions=hand.joint_specs(hand_data)
    plan=groups.motion_link_plan(joint_definitions)
    angles=groups.pose_angles(joint_definitions,fractions,clearance.signed_travel)
    # Antes de importar: los cuerpos temporales siguen intactos.
    expected=expected_pinch_centers(manager,hand,clearance,groups,motor_validation,
                                    hand_bodies,hand_data,fractions,
                                    placement=arm_pose['hand'] if arm_pose else None)
    report=dict(version=version,modo=mode,estado='publicando',
                fracciones=fractions,
                aviso=('Solo para mirar. Palma sin recorte y NO validada; sin '
                       'holgura continua, resistencia ni tendones.'))
    if arm_pose:
        place_like_lamina(manager,pending,hand_bodies,arm_pose)
        joint_definitions=placed_specs(joint_definitions,arm_pose['hand'])
        report['brazo_lamina']=dict(
            giro_hombro_deg=round(arm_pose['theta_shoulder_deg'],3),
            giro_codo_deg=round(arm_pose['theta_elbow_deg'],3),
            factor_antebrazo=round(arm_pose['forearm_factor'],4),
            largos_mm=arm_pose['lengths_mm'],
            residuos_frente_a_lamina_mm=arm_pose['residuals_mm'],
            rotula_frente_a_muneca_dibujada_mm=arm_pose['wrist_vs_lamina_mm'],
            encaje_pecho=arm_pose['chest_fit'])

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
    if arm_pose:
        report['brazo_lamina']['comprobacion_fusion']=arm_check(arm_bodies,arm_pose)
        record()

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
    worst_joint=max([abs(v['diferencia_deg']) for v in report['juntas_en_pinza'].values()]+[0.0])
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


def _load(name,filename):
    spec=importlib.util.spec_from_file_location(name,ROOT/filename)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _placement_candidates(occurrence,mirror):
    """Colocaciones posibles de la mano copiada respecto al robot, (nombre,
    (L, t_mm)). No esta claro si transform2 de una ocurrencia anidada es
    respecto al robot o a su padre: se ofrecen ambas y la identidad."""
    identity=(((1.0,0.0,0.0),(0.0,1.0,0.0),(0.0,0.0,1.0)),(0.0,0.0,0.0))
    result=[]
    try:
        result.append(('transform2',mirror.matrix_from_array16_cm(
            list(occurrence.transform2.asArray()))))
    except Exception:
        pass
    try:
        chain=identity
        current=occurrence
        while current is not None:
            native=getattr(current,'nativeObject',None) or current
            relative=mirror.matrix_from_array16_cm(list(native.transform2.asArray()))
            chain=mirror.compose(relative,chain)
            current=getattr(current,'assemblyContext',None)
        result.append(('cadena_de_padres',chain))
    except Exception:
        pass
    result.append(('identidad',identity))
    return result


COLUMN_MODULES=('01_BASE','02_TRONCO','03_CINTURA','04_PECHO_HOMBROS','05_CUELLO','06_CABEZA')
COLUMN_NOMINAL_MM={'01_BASE':(0,200),'02_TRONCO':(200,390),'03_CINTURA':(390,540),
                   '04_PECHO_HOMBROS':(540,730),'05_CUELLO':(730,790),'06_CABEZA':(790,965)}  # cabeza 4.2.0: 175 mm


def report_heights(design,report_path):
    """Solo lectura (v14): altura minima y maxima de cada modulo del montaje y
    de cada uno de sus cuerpos, y los huecos o solapes entre modulos seguidos
    de la columna. No crea, mueve ni borra nada."""
    report=dict(version='v14',modo='alturas',modulos={},huecos_mm={})

    def z_range(box):
        return [round(box.minPoint.z*10,3),round(box.maxPoint.z*10,3)]
    for occurrence in design.rootComponent.occurrences:
        name=occurrence.component.name
        entry=dict(ocurrencia=occurrence.name,z_mm=z_range(occurrence.boundingBox),cuerpos={})
        for body in occurrence.component.bRepBodies:
            try:
                proxy=body.createForAssemblyContext(occurrence)
                entry['cuerpos'][body.name]=z_range(proxy.boundingBox)
            except Exception as error:
                entry['cuerpos'][body.name]='error: '+str(error)
        if name in COLUMN_NOMINAL_MM:
            entry['nominal_z_mm']=list(COLUMN_NOMINAL_MM[name])
        report['modulos'][name]=entry
    for lower,upper in zip(COLUMN_MODULES,COLUMN_MODULES[1:]):
        if lower in report['modulos'] and upper in report['modulos']:
            top=report['modulos'][lower]['z_mm'][1]
            bottom=report['modulos'][upper]['z_mm'][0]
            report['huecos_mm'][lower+' -> '+upper]=round(bottom-top,3)
    report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    return report


def report_arm_interference(design,report_path,min_mm3=0.01):
    """Solo lectura (v14): volumen de cada choque entre un cuerpo de un brazo
    (incluida la mano) y un cuerpo de otro modulo del montaje. No crea, mueve
    ni borra nada: trabaja con copias temporales."""
    manager=adsk.fusion.TemporaryBRepManager.get()
    report=dict(version='v14',modo='interferencias',choques=[],errores=[])
    arm_bodies=[]
    other_bodies=[]
    for occurrence in design.rootComponent.allOccurrences:
        path=occurrence.fullPathName
        top=path.split('+')[0]
        is_arm='Brazo_Mano' in top
        for body in occurrence.component.bRepBodies:
            if not body.isSolid:
                continue
            try:
                proxy=body.createForAssemblyContext(occurrence)
            except Exception as error:
                report['errores'].append(path+'/'+body.name+': '+str(error))
                continue
            (arm_bodies if is_arm else other_bodies).append((top,body.name,proxy))

    def overlap(a,b):
        return all(a.minPoint.asArray()[i]<b.maxPoint.asArray()[i] and
                   b.minPoint.asArray()[i]<a.maxPoint.asArray()[i] for i in range(3))
    for arm_top,arm_name,arm_proxy in arm_bodies:
        for other_top,other_name,other_proxy in other_bodies:
            if not overlap(arm_proxy.boundingBox,other_proxy.boundingBox):
                continue
            try:
                a=manager.copy(arm_proxy)
                b=manager.copy(other_proxy)
                if not manager.booleanOperation(a,b,adsk.fusion.BooleanTypes.IntersectionBooleanType):
                    continue
                volume=a.volume*1000.0
            except Exception as error:
                report['errores'].append(arm_name+' x '+other_name+': '+str(error))
                continue
            if volume>=min_mm3:
                report['choques'].append(dict(brazo=arm_top,cuerpo_brazo=arm_name,
                    modulo=other_top,cuerpo_modulo=other_name,volumen_mm3=round(volume,2)))
    report['choques'].sort(key=lambda c:-c['volumen_mm3'])
    report['cuerpos_brazo']=len(arm_bodies)
    report['cuerpos_resto']=len(other_bodies)
    report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    return report


HIP_UPPER=('03_CINTURA','04_PECHO_HOMBROS','05_CUELLO','06_CABEZA')
HIP_LOWER=('01_BASE','02_TRONCO')


def report_hip_sweep(design,report_path,pivots_mm=(400.0,),
                     max_deg=85,step_deg=5,min_mm3=0.5,skip_inner_waist=False):
    """Solo lectura (v14): gira en memoria todo lo que va por encima de la
    cadera (cintura, pecho, cuello, cabeza y brazos) alrededor de un eje en X
    (y = 0, Z = pivote), hacia delante, y mide los choques con tronco y base.
    v14 (cintura 2.3.0 / tronco 1.7.0): eje elegido a Z 400 y TODA la
    cintura gira (antes se excluia la parte dentro del collar, Z < 462).
    Bajo el eje van 2 mm de holgura y fondo en arco R70."""
    manager=adsk.fusion.TemporaryBRepManager.get()
    upper=[]
    lower=[]
    for occurrence in design.rootComponent.allOccurrences:
        top=occurrence.fullPathName.split('+')[0]
        name=top.split(':')[0]
        moving='Brazo_Mano' in top or name in HIP_UPPER
        if not moving and name not in HIP_LOWER:
            continue
        for body in occurrence.component.bRepBodies:
            if not body.isSolid:
                continue
            proxy=body.createForAssemblyContext(occurrence)
            if (skip_inner_waist and moving and name=='03_CINTURA'
                    and proxy.boundingBox.maxPoint.z*10<462):
                continue
            (upper if moving else lower).append((body.name,manager.copy(proxy)))

    def overlap(a,b):
        return all(a.minPoint.asArray()[i]<b.maxPoint.asArray()[i] and
                   b.minPoint.asArray()[i]<a.maxPoint.asArray()[i] for i in range(3))
    report=dict(version='v14',modo='cadera',cuerpos_que_giran=len(upper),
                cuerpos_fijos=len(lower),pivotes={})
    for pivot in pivots_mm:
        entry=dict(primer_choque_deg=None,libre_hasta_deg=0,choques={})
        for angle in range(step_deg,max_deg+1,step_deg):
            matrix=adsk.core.Matrix3D.create()
            matrix.setToRotation(math.radians(angle),adsk.core.Vector3D.create(1,0,0),
                                 adsk.core.Point3D.create(0,0,pivot*.1))
            hits=[]
            for name,body in upper:
                moved=manager.copy(body)
                manager.transform(moved,matrix)
                for other_name,other in lower:
                    if not overlap(moved.boundingBox,other.boundingBox):
                        continue
                    a=manager.copy(moved)
                    if not manager.booleanOperation(a,manager.copy(other),
                            adsk.fusion.BooleanTypes.IntersectionBooleanType):
                        continue
                    volume=a.volume*1000.0
                    if volume>=min_mm3:
                        hits.append([name,other_name,round(volume,1)])
            if hits:
                hits.sort(key=lambda h:-h[2])
                entry['choques'][str(angle)]=hits[:10]
                if entry['primer_choque_deg'] is None:
                    entry['primer_choque_deg']=angle
            elif entry['primer_choque_deg'] is None:
                entry['libre_hasta_deg']=angle
        report['pivotes'][str(int(pivot))]=entry
        report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    return report


def add_mirror_joints(design,report_path):
    """v12: juntas y relaciones de la mano IZQUIERDA, creada por el usuario con
    Crear > Simetria (plano YZ) en el montaje. Excepcion autorizada por el
    usuario (27-09-2026) a 'solo documento vacio': NO crea ni mueve geometria;
    solo anade juntas a esa mano, y solo si TODAS las comprobaciones pasan."""
    hand=_load('toreto_hand','toreto_hand.py')
    groups=_load('toreto_motor_groups','toreto_motor_groups.py')
    terminals=_load('toreto_local_terminals','toreto_local_terminals.py')
    outer=_load('toreto_outer_joints','toreto_outer_joints.py')
    arm_pose_module=_load('toreto_arm_pose','toreto_arm_pose.py')
    mirror=_load('toreto_mirror_joints','toreto_mirror_joints.py')
    data=json.loads((ROOT/'link_local_sections.json').read_text(encoding='utf-8'))
    hand_data=json.loads((ROOT/'hand_local_sections.json').read_text(encoding='utf-8'))
    arm_pose=arm_pose_module.solve(data['parts'],data['master_plane_y_mm'],terminals,outer)
    specs=mirror.mirrored_specs(hand.joint_specs(hand_data),arm_pose['hand'])
    report=dict(version='v12',modo='juntas_espejo',estado='comprobando',
                errores=[],pasadores={})

    def record():
        report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')

    def refuse(message):
        report['errores'].append(message)
        report['estado']='rechazado_sin_cambios'
        record()
        return report

    # 1. La mano copiada: el unico 06_MANO_ARTICULABLE sin juntas ni relaciones.
    candidates={}
    with_joints=0
    for occurrence in design.rootComponent.allOccurrences:
        component=occurrence.component
        if mirror.base_name(component.name)!='06_MANO_ARTICULABLE':
            continue
        key=getattr(component,'entityToken',None) or component.name
        if component.asBuiltJoints.count or component.joints.count or component.motionLinks.count:
            with_joints+=1
            continue
        candidates[key]=(component,occurrence)
    report.update(manos_con_juntas=with_joints,manos_sin_juntas=len(candidates))
    if len(candidates)!=1:
        return refuse('Se esperaba exactamente UNA mano sin juntas; hay {}'.format(len(candidates)))
    hand_component,hand_occurrence=next(iter(candidates.values()))
    report['componente']=hand_component.name
    placements=_placement_candidates(hand_occurrence,mirror)

    # 2. Sus 21 piezas y sus 20 pasadores, por nombre.
    occurrences={}
    for occurrence in hand_component.occurrences:
        occurrences[mirror.base_name(occurrence.component.name)]=occurrence
    expected_groups={s['child'] for s in specs}|{s['parent'] for s in specs}
    if set(occurrences)!=expected_groups:
        return refuse('Piezas de la mano distintas de las 21 esperadas: sobran {} faltan {}'.format(
            sorted(set(occurrences)-expected_groups),sorted(expected_groups-set(occurrences))))
    body_records={}
    for occurrence in occurrences.values():
        for body in occurrence.component.bRepBodies:
            body_records[mirror.base_name(body.name)]=(body,occurrence)

    # 3. Cada pasador donde debe estar y con su borde circular alineado.
    # Los bordes se leen en coordenadas internas de la mano copiada; Fusion
    # coloca las copias por simetria giradas (v12 real: 180 grados en Y). Se
    # prueba cada colocacion candidata y solo vale la que cuadra los 20.
    measured={}
    for spec in specs:
        record_=body_records.get(spec['pin_label'])
        if not record_ or record_[1] is not occurrences[spec['parent']]:
            return refuse('Falta el pasador '+spec['pin_label']+' en '+spec['parent'])
        body,occurrence=record_
        proxy=body.createForAssemblyContext(occurrence)
        measured[spec['name']]=(proxy,_center_mm(proxy.boundingBox))
    tried=[]
    chosen=None
    for name,placement in placements:
        local=mirror.to_local_specs(specs,placement)
        worst=max(math.dist(measured[s['name']][1],s['center_mm']) for s in local)
        tried.append(dict(colocacion=name,peor_pasador_mm=round(worst,3)))
        if worst<=1.5 and chosen is None:
            chosen=(name,local,worst)
    report['colocaciones_probadas']=tried
    if chosen is None:
        spec=specs[0]
        report['pasadores'][spec['name']]=dict(
            esperado_robot_mm=[round(v,3) for v in spec['center_mm']],
            fusion_interno_mm=measured[spec['name']][1])
        return refuse('Ninguna colocacion hace coincidir los 20 pasadores: '+', '.join(
            '{} {:.1f} mm'.format(t['colocacion'],t['peor_pasador_mm']) for t in tried))
    placement_name,specs,worst=chosen
    for spec in specs:
        proxy,got=measured[spec['name']]
        report['pasadores'][spec['name']]=dict(
            esperado_mm=[round(v,3) for v in spec['center_mm']],fusion_mm=got,
            distancia_mm=round(math.dist(got,spec['center_mm']),3))
        try:
            pin_axis_edge(proxy,spec['axis'],hand.hinge_dimensions(spec)[2]*.1)
        except RuntimeError as error:
            return refuse(spec['name']+': '+str(error))
    report.update(estado='comprobado',colocacion=placement_name,peor_pasador_mm=round(worst,3))
    record()

    # 4. Solo ahora se crea algo: 20 juntas y las 16 relaciones de 4 motores.
    joints,flexion_signs=create_revolute_joints(
        hand_component,occurrences,body_records,specs,
        lambda spec:hand.hinge_dimensions(spec)[2])
    plan=groups.motion_link_plan(specs)
    travel_degrees={s['name']:s['travel_deg'] for s in specs}
    links=create_digit_motion_links(hand_component,joints,flexion_signs,travel_degrees,plan)
    report.update(estado='juntas_creadas',juntas=len(joints),relaciones=len(links),
                  signos_eje={k:v for k,v in flexion_signs.items() if v<0})
    record()
    return report


def run(context):
    app=adsk.core.Application.get()
    output=None
    try:
        design=adsk.fusion.Design.cast(app.activeProduct)
        if not design: raise RuntimeError('Abre el documento del robot')
        if MODE not in ('ensayo', 'ver_pinza', 'ensayo_lateral', 'ver_brazo', 'juntas_espejo',
                        'alturas', 'interferencias', 'comprobar', 'cadera'):
            raise RuntimeError('Modo de ensayo desconocido: '+MODE)
        if MODE=='cadera':
            result=report_hip_sweep(design,ROOT/'cadera_giro_v14.json')
            lines=['Giran {} cuerpos; fijos (tronco y base) {}.'.format(
                result['cuerpos_que_giran'],result['cuerpos_fijos']),'']
            for pivot,entry in result['pivotes'].items():
                first=entry['primer_choque_deg']
                if first is None:
                    lines.append('Eje en Z {}: LIBRE hasta 85 grados.'.format(pivot))
                    continue
                lines.append('Eje en Z {}: libre hasta {} grados; primer choque a {}:'.format(
                    pivot,entry['libre_hasta_deg'],first))
                lines.extend('   {} / {}: {} mm3'.format(*h) for h in entry['choques'][str(first)][:4])
            app.userInterface.messageBox(
                'Solo lectura: no se ha cambiado nada.\n\n'+'\n'.join(lines)+
                '\n\nDetalles: cadera_giro_v14.json','Toreto '+SCRIPT_VERSION+' - giro de la cadera')
            return
        if MODE=='comprobar':
            heights=report_heights(design,ROOT/'alturas_montaje_v14.json')
            clashes=report_arm_interference(design,ROOT/'interferencias_brazos_v14.json')
            lines=['{}: {} mm'.format(k,v) for k,v in heights['huecos_mm'].items()]
            lines.append('')
            lines.append('Choques brazos-resto: {} (cuerpos de brazo {}, resto {})'.format(
                len(clashes['choques']),clashes['cuerpos_brazo'],clashes['cuerpos_resto']))
            lines.extend('{} / {}: {} mm3'.format(c['cuerpo_brazo'],c['cuerpo_modulo'],c['volumen_mm3'])
                         for c in clashes['choques'][:10])
            app.userInterface.messageBox(
                'Solo lectura: no se ha cambiado nada.\n\nHuecos (+) o solapes (-) entre modulos:\n'+
                '\n'.join(lines)+'\n\nDetalles: alturas_montaje_v14.json e interferencias_brazos_v14.json',
                'Toreto '+SCRIPT_VERSION+' - comprobar montaje')
            return
        if MODE=='interferencias':
            result=report_arm_interference(design,ROOT/'interferencias_brazos_v14.json')
            lines=['{} / {}: {} mm3'.format(c['cuerpo_brazo'],c['cuerpo_modulo'],c['volumen_mm3'])
                   for c in result['choques'][:12]]
            app.userInterface.messageBox(
                'Solo lectura: no se ha cambiado nada.\n\n'
                'Choques brazo-resto del robot: {} (cuerpos de brazo {}, resto {}).\n'.format(
                    len(result['choques']),result['cuerpos_brazo'],result['cuerpos_resto'])+
                '\n'.join(lines)+('\n...' if len(result['choques'])>12 else '')+
                '\n\nDetalles: interferencias_brazos_v14.json',
                'Toreto '+SCRIPT_VERSION+' - interferencias de los brazos')
            return
        if MODE=='alturas':
            result=report_heights(design,ROOT/'alturas_montaje_v14.json')
            lines=['{}: {} mm'.format(k,v) for k,v in result['huecos_mm'].items()]
            app.userInterface.messageBox(
                'Solo lectura: no se ha cambiado nada.'+'\n\n'+'Huecos (+) o solapes (-) entre modulos:'+'\n'+
                '\n'.join(lines)+'\n\n'+'Detalles: alturas_montaje_v14.json',
                'Toreto '+SCRIPT_VERSION+' - alturas del montaje')
            return
        if MODE=='juntas_espejo':
            result=add_mirror_joints(design,ROOT/'juntas_espejo_v12.json')
            if result['estado']=='juntas_creadas':
                message=('Mano izquierda: {} juntas y {} relaciones creadas.\n'
                         'Pasadores comprobados antes de crear nada: el peor a {} mm.\n\n'
                         'Prueba: clic derecho en JUNTA_DEDO_1_1 de la mano izquierda > '
                         'Animar relaciones de union. El indice debe cerrar hacia su palma.').format(
                             result['juntas'],result['relaciones'],result['peor_pasador_mm'])
            else:
                message='NO se ha cambiado nada en el montaje.\n\n'+'\n'.join(result['errores'])
            app.userInterface.messageBox(message+'\n\nDetalles: juntas_espejo_v12.json',
                                         'Toreto '+SCRIPT_VERSION+' - juntas de la mano izquierda')
            return
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
        # v11: con 'ver_brazo' el antebrazo se alarga y el hombro va a su
        # pivote de la lamina; el resto de modos construye el brazo de siempre.
        arm_pose=None
        parts=data['parts']
        if MODE=='ver_brazo':
            pose_spec=importlib.util.spec_from_file_location('toreto_arm_pose',ROOT/'toreto_arm_pose.py')
            arm_pose_module=importlib.util.module_from_spec(pose_spec)
            pose_spec.loader.exec_module(arm_pose_module)
            arm_pose=arm_pose_module.solve(data['parts'],data['master_plane_y_mm'],
                                           terminals,outer_joints)
            parts=arm_pose['parts']
        for key,label in (('upper','01_BRAZO_LOCAL_SIN_REBAJES'),('forearm','02_ANTEBRAZO_LOCAL_SIN_REBAJES')):
            item=parts[key]
            if arm_pose and key=='forearm':
                selected=arm_pose_module.stable_like_original(
                    local_filter,data['parts'][key]['sections'],item['sections'])
            else:
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
        joint,joint_report,joint_spec=terminals.build_elbow(manager,parts,data['master_plane_y_mm'])
        seat_report=terminals.integrate_elbow(manager,pending[0][0],pending[1][0],joint_spec)
        pending.append((joint,'03_EJE_Y_ENLACE_CODO','TORETO Negro profundo'))
        reports.append(joint_report)
        reports.append(seat_report)
        shoulder,wrist,outer_reports=outer_joints.build(
            manager,pending[0][0],pending[1][0],parts,data['master_plane_y_mm'],
            shoulder_center=arm_pose['shoulder_center_flat'] if arm_pose else None,
            shoulder_size=arm_pose['shoulder_size_mm'] if arm_pose else None,
            **(arm_pose['shoulder_overrides'] if arm_pose else {}))
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
        if MODE=='ver_brazo':
            # v11: la misma mano (slots.repair si, clearance.repair NO), abierta.
            hand_bodies,_=slots.repair(manager,hand,hand_bodies,hand_data)
            view_path=ROOT/'vista_brazo_v11.json'
            try:
                output,view=publish_pinch_view(
                    design,root,pending,hand_bodies,hand,clearance,motor_groups,
                    motor_validation,hand_data,manager,view_path,
                    fractions={},arm_pose=arm_pose,version='v11',mode='ver_brazo')
            except Exception:
                try:
                    partial=json.loads(view_path.read_text(encoding='utf-8'))
                except Exception:
                    partial={'version':'v11','modo':'ver_brazo'}
                partial.update(estado_alcanzado=partial.get('estado'),estado='error',
                               traceback=traceback.format_exc())
                view_path.write_text(json.dumps(partial,indent=2,ensure_ascii=False),encoding='utf-8')
                raise
            arm=view['brazo_lamina']
            fusion=arm['comprobacion_fusion']
            fit=arm_pose['chest_fit'] or {}
            app.userInterface.messageBox(
                'Brazo con las medidas de la lamina ENCAJADO en el conector del pecho '
                '(v14: disco negro del hombro visible y colores blanco/negro), mano abierta.\n\n'
                'Hombro: eje en X sobre el eje del conector ({} mm); taladro R{} mm para '
                'el conector R36,5; pared {} mm. Queda {} mm del punto de la lamina.\n'
                'Giros de la postura: hombro {} grados, codo {} grados.\n'
                'Largos: hombro-codo {} mm, codo-final del antebrazo {} mm.\n'
                'Frente a la lamina: codo {} mm, final del antebrazo {} mm.\n\n'
                'Comprobado en Fusion: tapa del hombro a {} mm y rotula a {} mm de donde '
                'deben estar.\n'
                'Mano en su sitio respecto al ensayo: {} (peor falange {} mm).\n\n'
                'Guardalo como Toreto_Brazo_Mano_v14 y en el montaje usa Reemplazar componente.\n'
                'Detalles: vista_brazo_v11.json'.format(
                    fit.get('pivote_a_eje_conector_mm'),fit.get('taladro_radio_mm'),
                    fit.get('pared_alojamiento_mm'),
                    fit.get('desplazamiento_hombro_frente_a_lamina_mm'),
                    arm['giro_hombro_deg'],arm['giro_codo_deg'],
                    arm['largos_mm']['hombro_codo'],arm['largos_mm']['codo_fin_antebrazo'],
                    arm['residuos_frente_a_lamina_mm']['codo'],
                    arm['residuos_frente_a_lamina_mm']['fin_antebrazo'],
                    fusion['tapa_hombro']['distancia_mm'],fusion['muneca_rotula']['distancia_mm'],
                    'SI' if view['resumen']['pose_igual_al_ensayo'] else 'NO - revisar',
                    view['resumen']['peor_distancia_falange_mm']),
                'Toreto '+SCRIPT_VERSION+' - brazo como la lamina')
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
