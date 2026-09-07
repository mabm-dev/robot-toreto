"""Rebuild only the four thumb hinges with a rotated crossed-axis cardan."""
import importlib.util
import json
import math
import traceback
from pathlib import Path

import adsk.core
import adsk.fusion


ROOT=Path(__file__).resolve().parent
TARGET_NAME='94_BRAZO_MARCOS_LOCALES_PRUEBA_01_35'
HAND_NAME='06_MANO_ARTICULABLE'
REVISION='PULGAR_CARDAN_MENOS_10_GRADOS_01_37'
THUMB_LIMITS_DEG=(30.0,40.0,35.0,20.0)


def _occurrence_by_name(collection,name):
    for occurrence in collection:
        if occurrence.component.name==name:
            return occurrence
    return None


def _item_by_name(collection,name):
    for item in collection:
        if item.name==name:
            return item
    return None


def _group_map(hand_component):
    names=(
        'MANO_00_PALMA','MANO_05_PULGAR_CARDAN',
        'MANO_05_PULGAR_FALANGE_01','MANO_05_PULGAR_FALANGE_02',
        'MANO_05_PULGAR_FALANGE_03')
    result={}
    for name in names:
        occurrence=_occurrence_by_name(hand_component.occurrences,name)
        if not occurrence:
            raise RuntimeError('No se encontro el componente '+name)
        result[name]=occurrence
    return result


def _delete_old_kinematics(hand_component):
    for index in range(2,5):
        name='RELACION_CIERRE_PULGAR_1_A_{}'.format(index)
        link=_item_by_name(hand_component.motionLinks,name)
        if not link or not link.deleteMe():
            raise RuntimeError('No se pudo retirar '+name)
    for index in range(1,5):
        name='JUNTA_PULGAR_{}'.format(index)
        joint=_item_by_name(hand_component.asBuiltJoints,name)
        if not joint or not joint.deleteMe():
            raise RuntimeError('No se pudo retirar '+name)


def _new_hinge_geometry(hand_module,data):
    manager=adsk.fusion.TemporaryBRepManager.get()
    path=data['thumb_path_mm']
    gimbal_end,axes=hand_module._thumb_mechanism(path)
    direction=hand_module._unit(tuple(
        path[-1][index]-path[0][index] for index in range(3)))
    centers=(path[0],gimbal_end,path[1],path[2])
    generated=[]
    for index,(center,axis,limit) in enumerate(
            zip(centers,axes,THUMB_LIMITS_DEG),1):
        label='10_PULGAR_NUDILLO_{}'.format(index)
        for temporary,suffix in hand_module._articulated_hinge(
                manager,center,axis,direction,6.2,20.0,limit,label):
            generated.append((index,temporary,suffix,label+'_'+suffix))
    if len(generated)!=16:
        raise RuntimeError('No se generaron las 16 piezas de las bisagras.')
    return generated,centers,axes


def _replace_hinge_bodies(hand_component,groups,generated,design):
    parents=(
        'MANO_00_PALMA','MANO_05_PULGAR_CARDAN',
        'MANO_05_PULGAR_FALANGE_01','MANO_05_PULGAR_FALANGE_02')
    children=(
        'MANO_05_PULGAR_CARDAN','MANO_05_PULGAR_FALANGE_01',
        'MANO_05_PULGAR_FALANGE_02','MANO_05_PULGAR_FALANGE_03')
    for _,_,_,label in generated:
        for occurrence in groups.values():
            old=_item_by_name(occurrence.component.bRepBodies,label)
            if old:
                if not old.deleteMe():
                    raise RuntimeError('No se pudo retirar '+label)
                break
        else:
            raise RuntimeError('No se encontro el cuerpo anterior '+label)

    records={}
    by_group={}
    for joint_index,temporary,suffix,label in generated:
        group=(children[joint_index-1] if suffix=='CASQUILLO_CENTRAL'
               else parents[joint_index-1])
        by_group.setdefault(group,[]).append((temporary,label))
    appearance=design.appearances.itemByName('TORETO Negro profundo')
    for group_name,items in by_group.items():
        component=groups[group_name].component
        base=component.features.baseFeatures.add()
        if not base or not base.startEdit():
            raise RuntimeError('No se pudo editar '+group_name)
        try:
            for temporary,label in items:
                body=component.bRepBodies.add(temporary,base)
                if not body:
                    raise RuntimeError('No se pudo importar '+label)
                body.name=label
                if appearance:
                    body.appearance=appearance
                records[label]=(body,groups[group_name])
        finally:
            base.finishEdit()
    if len(records)!=16:
        raise RuntimeError('No se importaron las 16 piezas nuevas.')
    return records


def _pin_axis_edge(body_proxy,expected_axis):
    best=None
    for edge in body_proxy.edges:
        circle=adsk.core.Circle3D.cast(edge.geometry)
        if not circle:
            continue
        ok,_,normal,radius=circle.getData()
        if not ok or abs(radius-.2)>.005:
            continue
        alignment=(normal.x*expected_axis[0]+normal.y*expected_axis[1]+
                   normal.z*expected_axis[2])
        if best is None or abs(alignment)>abs(best[1]):
            best=(edge,alignment)
    if best is None or abs(best[1])<.98:
        raise RuntimeError('No se encontro un borde circular alineado del pasador.')
    return best


def _create_joints(hand_component,groups,records,centers,axes):
    parents=(
        'MANO_00_PALMA','MANO_05_PULGAR_CARDAN',
        'MANO_05_PULGAR_FALANGE_01','MANO_05_PULGAR_FALANGE_02')
    children=(
        'MANO_05_PULGAR_CARDAN','MANO_05_PULGAR_FALANGE_01',
        'MANO_05_PULGAR_FALANGE_02','MANO_05_PULGAR_FALANGE_03')
    result=[]
    signs={}
    for index,(center,axis,limit) in enumerate(
            zip(centers,axes,THUMB_LIMITS_DEG),1):
        pin_label='10_PULGAR_NUDILLO_{}_PASADOR'.format(index)
        body,owner=records[pin_label]
        proxy=body.createForAssemblyContext(owner)
        if not proxy:
            raise RuntimeError('No se pudo contextualizar '+pin_label)
        edge,alignment=_pin_axis_edge(proxy,axis)
        geometry=adsk.fusion.JointGeometry.createByCurve(
            edge,adsk.fusion.JointKeyPointTypes.CenterKeyPoint)
        joint_input=hand_component.asBuiltJoints.createInput(
            groups[children[index-1]],groups[parents[index-1]],geometry)
        if not joint_input or not joint_input.setAsRevoluteJointMotion(
                adsk.fusion.JointDirections.CustomJointDirection,
                adsk.core.Vector3D.create(*axis)):
            raise RuntimeError('No se pudo preparar JUNTA_PULGAR_{}'.format(index))
        joint=hand_component.asBuiltJoints.add(joint_input)
        if not joint:
            raise RuntimeError('No se pudo crear JUNTA_PULGAR_{}'.format(index))
        joint.name='JUNTA_PULGAR_{}'.format(index)
        motion=adsk.fusion.RevoluteJointMotion.cast(joint.jointMotion)
        limits=motion.rotationLimits
        minimum=0.0
        maximum=math.radians(limit)
        if alignment<0:
            minimum,maximum=-maximum,-minimum
        limits.minimumValue=minimum
        limits.maximumValue=maximum
        limits.isMinimumValueEnabled=True
        limits.isMaximumValueEnabled=True
        joint.isLightBulbOn=False
        result.append(joint)
        signs[joint.name]=(-1 if alignment<0 else 1)
    return result,signs


def _create_motion_links(hand_component,joints,signs):
    rotation=adsk.fusion.JointMotionTypes.RevoluteJointRotateMotionType
    master=joints[0]
    for index in range(2,5):
        follower=joints[index-1]
        link_input=hand_component.motionLinks.createInput(master,follower)
        if not link_input:
            raise RuntimeError('No se pudo preparar la relacion del pulgar {}.'.format(index))
        link_input.motionOne=rotation
        link_input.motionTwo=rotation
        link_input.valueOne=adsk.core.ValueInput.createByString('30 deg')
        link_input.valueTwo=adsk.core.ValueInput.createByString(
            '{} deg'.format(THUMB_LIMITS_DEG[index-1]))
        link_input.isReversed=(signs[master.name]!=signs[follower.name])
        link=hand_component.motionLinks.add(link_input)
        if not link:
            raise RuntimeError('No se pudo crear la relacion del pulgar {}.'.format(index))
        link.name='RELACION_CIERRE_PULGAR_1_A_{}'.format(index)


def run(context):
    app=adsk.core.Application.get()
    try:
        design=adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            raise RuntimeError('Abre el documento del robot antes del ajuste.')
        target=_occurrence_by_name(design.rootComponent.occurrences,TARGET_NAME)
        if not target:
            raise RuntimeError('No se encontro '+TARGET_NAME+'.')
        if target.component.attributes.itemByName('RobotToreto','revision_pulgar_1037'):
            app.userInterface.messageBox('El ajuste 1.0.37 ya esta aplicado; no se duplica.')
            return
        hand_occurrence=_occurrence_by_name(target.component.occurrences,HAND_NAME)
        if not hand_occurrence:
            raise RuntimeError('No se encontro '+HAND_NAME+'.')
        hand_component=hand_occurrence.component
        groups=_group_map(hand_component)

        module_spec=importlib.util.spec_from_file_location(
            'toreto_hand_1037',ROOT/'toreto_hand.py')
        hand_module=importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(hand_module)
        data=json.loads((ROOT/'hand_local_sections.json').read_text(encoding='utf-8'))
        generated,centers,axes=_new_hinge_geometry(hand_module,data)

        _delete_old_kinematics(hand_component)
        records=_replace_hinge_bodies(
            hand_component,groups,generated,design)
        joints,signs=_create_joints(
            hand_component,groups,records,centers,axes)
        _create_motion_links(hand_component,joints,signs)
        target.component.attributes.add(
            'RobotToreto','revision_pulgar_1037',REVISION)
        design.computeAll()
        app.userInterface.messageBox(
            'Correccion geometrica 1.0.37 aplicada.\n\n'
            'Los cuatro ejes del pulgar se han reconstruido 10 grados mas '
            'hacia la perpendicular, conservando 76 grados entre los dos '
            'ejes del cardan. Los recorridos vuelven a 30/40/35/20 grados.\n\n'
            'Solo se sustituyeron las cuatro bisagras y sus relaciones. La '
            'palma, las falanges, los cuatro dedos y el brazo no se regeneraron.\n\n'
            'Comprueba Animar relaciones de union en JUNTA_PULGAR_1.',
            'Robot Toreto - pulgar 1.0.37')
    except Exception:
        app.userInterface.messageBox(
            traceback.format_exc(),'Error al corregir el pulgar 1.0.37')


def stop(context):
    pass
