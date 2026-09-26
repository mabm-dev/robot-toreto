# Reparacion experimental de mano — punto de control

Estado: **trabajo en curso, no funcional ni listo para fabricar**.

Esta carpeta contiene el generador aislado y los diagnosticos reproducibles.
No sustituye al generador principal ni modifica el robot original.
Ejecutar solamente desde Fusion en un documento de prueba vacio. El script
rechaza documentos con cuerpos u ocurrencias y retorna antes de publicar
un ensamblaje. No guarda documentos de Fusion.

## Ultimo resultado (26-09-2026)

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

`python -m unittest discover -s work/Toreto_Prueba_Holguras_01_44 -p test_clearance.py -v`

Cuatro pruebas de parametros; no reemplazan los ensayos BRep en Fusion.
Los JSON son resultados de diagnostico, no un archivo F3D de la mano.
