# Reparacion experimental de mano — punto de control

Estado: **trabajo en curso, no funcional ni listo para fabricar**.

Esta carpeta contiene el generador aislado y los diagnosticos reproducibles.
No sustituye al generador principal ni modifica el robot original.
Ejecutar solamente desde Fusion en un documento de prueba vacio. El script
rechaza documentos con cuerpos u ocurrencias y retorna antes de publicar
un ensamblaje. No guarda documentos de Fusion.

## v8 (26-09-2026) — preparada, SIN ejecutar en Fusion

La v7 dio: mano abierta limpia, rotacion y flexion del pulgar limpias,
corazon+anular+menique limpio, y la pinza del boli lograda punta con punta
sin choques previos. Quedaba un unico choque: el indice, al cerrar del todo,
tocaba la falange 1 del pulgar en reposo (5,2 mm3). La v8 reduce el
recorrido del indice al 90% (54/54/45/36 grados) en su cinematica y en sus
topes fisicos. Detalle y justificacion en `RESULTADO_PRUEBA.md`. Informe:
`prueba_mano_4_motores_v8.json`. Pruebas unitarias: 19.

## v7: mano de 4 motores (26-09-2026)

Decision del usuario: la mano debe coger como una humana (boli con pulgar e
indice, pelota pequena, vaso). Un motor rigido no puede; se pasa a una mano
adaptativa de CUATRO motores: indice / corazon+anular+menique / flexion del
pulgar / rotacion del pulgar (el cardan). Ver `toreto_motor_groups.py`.

Se sustituye el cierre simultaneo de toda la mano: con cuatro motores no es
el movimiento real, y exigia que el pulgar no entrase en los dedos al cerrar
los cinco a la vez hasta el final, algo que ninguna mano con pulgar oponible
puede hacer (en la v6, 55 de 58 choques estaban en el tramo final del
cierre y el 87% del volumen era pulgar contra puntas).

La v7 prueba, en una sola ejecucion (`toreto_motor_validation.py`):
- mano abierta, todos los pares;
- cada motor solo, con el resto quieto y abierto: criterio CERO choques.
  El barrido de corazon+anular+menique con el indice quieto es la postura
  de SENALAR; el del cardan comprueba la correccion del taladro;
- pinza del boli: si las falanges de pulgar e indice llegan a tocarse,
  cuando, y si choca algo mas antes.
Registra el volumen muestra a muestra, no solo el maximo. Informe:
`prueba_mano_4_motores_v7.json`.

No comprueba la palma principal (excluida, como en la v6), ni holgura
continua, ni resistencia, ni agarres de objetos (vaso, pelota): eso
necesita simular el objeto y queda para la siguiente version.

## Resultado anterior (26-09-2026)

- Bisagras de los cuatro dedos estrechadas a 13.5 mm y pasadores con 0.25 mm
  de saliente; alojamientos de casquillos y extremos de falanges corregidos.
- Las tres falanges del pulgar reciben tambien alojamientos.
- `prueba_alojamientos_pulgar_v3.json`: 13 posturas sincronizadas, 65 pares
  con penetracion >0.01 mm3, cero errores del nucleo y 47 apoyos comprobados.
- No mover centros ni aplicar al original sin validar el conjunto.
- Pendientes: mecanismo de base del pulgar, choques durante el cierre,
  nueva prueba de palma con dimensiones actuales, movimiento independiente
  de dedos, holgura continua, resistencia y validacion visual del ensamblaje.

Los apoyos comprobados son controles geometricos heurísticos, no calculos
de resistencia. Los resultados anteriores de palma no certifican esta version.
`RESULTADO_PRUEBA.md` conserva la cronologia de ensayos, incluidos rechazos.

## Pruebas locales

`python -m unittest discover -s work/Toreto_Prueba_Holguras_01_44 -p "test_*.py" -v`

Diecinueve pruebas: cinco de parametros (`test_clearance.py`) y catorce del
reparto de motores y los limites del indice (`test_motor_groups.py`). Una de estas ultimas garantiza
que, con todos los motores a la misma fraccion, la postura es identica a la
del ensayo sincronizado anterior: la v7 no cambia la cinematica. No
reemplazan los ensayos BRep en Fusion.
Los JSON son resultados de diagnostico, no un archivo F3D de la mano.
