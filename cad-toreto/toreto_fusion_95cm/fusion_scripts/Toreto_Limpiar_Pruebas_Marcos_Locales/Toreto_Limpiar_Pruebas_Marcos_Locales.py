"""Remove obsolete generated arm trials while preserving the current version."""
import re
import traceback

import adsk.core
import adsk.fusion


KEEP_NAME='94_BRAZO_MARCOS_LOCALES_PRUEBA_01_35'
TRIAL_PATTERN=re.compile(r'^94_BRAZO_MARCOS_LOCALES_PRUEBA_01_\d+$')


def run(context):
    app=adsk.core.Application.get()
    try:
        design=adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            raise RuntimeError('Abre el documento del robot antes de ejecutar la limpieza.')

        root=design.rootComponent
        obsolete=[]
        for occurrence in root.occurrences:
            name=occurrence.component.name
            if TRIAL_PATTERN.fullmatch(name) and name!=KEEP_NAME:
                obsolete.append((occurrence,name))

        removed=[]
        failed=[]
        for occurrence,name in obsolete:
            if occurrence.isValid and occurrence.deleteMe():
                removed.append(name)
            else:
                failed.append(name)

        if failed:
            raise RuntimeError(
                'No se pudieron eliminar estos componentes:\n- '+
                '\n- '.join(failed))

        if removed:
            detail='\n- '+'\n- '.join(sorted(removed))
            app.userInterface.messageBox(
                'Limpieza terminada.\n\n'
                'Eliminados: {} componentes antiguos.{}\n\n'
                'Conservado: {}\n\n'
                'Guarda el documento y vuelve a abrirlo para que Fusion libere '
                'la memoria y recalcule solo los componentes vigentes.'.format(
                    len(removed),detail,KEEP_NAME),
                'Robot Toreto - limpieza')
        else:
            app.userInterface.messageBox(
                'No se encontraron pruebas antiguas para eliminar.\n\n'
                'Se conserva: {}'.format(KEEP_NAME),
                'Robot Toreto - limpieza')
    except Exception:
        app.userInterface.messageBox(
            traceback.format_exc(),'Error al limpiar pruebas antiguas')


def stop(context):
    pass
