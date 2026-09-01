"""Crea o actualiza los parámetros maestros del Robot Toreto de 95 cm.

Las cotas verticales son las medidas adoptadas de la lámina maestra calibrada.
"""

import traceback

import adsk.core
import adsk.fusion


VERSION = "1.2.0"

PARAMETERS = [
    ("altura_total", "950 mm", "Altura exterior total del robot"),
    ("diametro_base", "450 mm", "Diámetro exterior nominal de la base medida en el lienzo"),
    ("alto_base", "200 mm", "Altura exterior de la base"),
    ("alto_tronco", "190 mm", "Altura exterior del tronco"),
    ("alto_cintura", "150 mm", "Altura exterior de la cintura"),
    ("alto_pecho", "190 mm", "Altura exterior del pecho"),
    ("alto_cuello", "60 mm", "Altura exterior del cuello"),
    (
        "alto_cabeza",
        "altura_total-alto_base-alto_tronco-alto_cintura-alto_pecho-alto_cuello",
        "Altura calculada de la cabeza para cerrar 950 mm",
    ),
    ("ancho_pecho", "340 mm", "Separación exterior de hombros"),
    ("ancho_carcasa_pecho", "252 mm", "Anchura de la carcasa central del pecho"),
    ("fondo_pecho", "220 mm", "Profundidad máxima del pecho"),
    ("ancho_cabeza", "264 mm", "Anchura exterior medida en el lienzo frontal calibrado"),
    ("fondo_cabeza", "213 mm", "Fondo exterior medido en el lienzo lateral calibrado"),
    ("largo_brazo", "170 mm", "Longitud del brazo superior"),
    ("largo_antebrazo", "150 mm", "Longitud del antebrazo"),
    ("espesor_pared", "3.2 mm", "Espesor nominal de las carcasas"),
]


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Abre un diseño de Fusion antes de ejecutar el script.", "Robot Toreto 95 cm")
            return

        created = 0
        updated = 0
        for name, expression, comment in PARAMETERS:
            parameter = design.userParameters.itemByName(name)
            if parameter:
                parameter.expression = expression
                parameter.comment = comment
                updated += 1
            else:
                parameter = design.userParameters.add(
                    name, adsk.core.ValueInput.createByString(expression), "mm", comment
                )
                if not parameter:
                    raise RuntimeError(f"Fusion no pudo crear el parámetro: {name}")
                created += 1
            try:
                parameter.isFavorite = True
            except Exception:
                pass

        head = design.userParameters.itemByName("alto_cabeza")
        total = design.userParameters.itemByName("altura_total")
        if not head or not total or abs(head.value * 10 - 160.0) > 0.01:
            raise RuntimeError("La suma vertical no cierra en 950 mm; revisa las expresiones.")

        ui.messageBox(
            "Parámetros maestros 95 cm aplicados.\n\n"
            f"Creados: {created}\nActualizados: {updated}\n"
            "Z: base 200 · tronco 390 · cintura 540 · pecho 730 · cuello 790 · total 950 mm\n"
            "Cabeza calculada: 160 mm\n"
            "Contorno cabeza: 264 mm frontal · 213 mm lateral",
            "Robot Toreto 95 cm",
        )
    except Exception:
        ui.messageBox("No se pudieron aplicar los parámetros:\n\n" + traceback.format_exc(), "Robot Toreto 95 cm - Error")


def stop(context):
    pass
