# Robot Toreto - V2 (alineado con la infografia de referencia)

V2 esta modelado para coincidir con la infografia "Robot Asistente
Inteligente" que definiste como prototipo objetivo: altura 95 cm, base de
40 cm, torso con pantalla tactil, brazo de 6 DOF, cabeza de 2 DOF y base
movil de 3 ruedas omnidireccionales con LIDAR.

Sigue siendo una **maqueta visual**: valida forma, proporcion y que cada
pieza entra en el volumen de impresion de la Bambu P1S. No es todavia un
diseno mecanico final con servos, reductoras y rodamientos reales
seleccionados.

## Archivos

- `toreto_v2.scad`: modelo parametrico OpenSCAD.
- `exports_v2/`: 27 piezas exportadas a STL + 2 renders de vista previa.
- `lista_piezas_v2.md`: mapeo pieza <-> numero de la infografia, materiales,
  cantidades y componentes no imprimibles.
- `STL_EXPORTADOS_V2.md`: bounding box real de cada STL y confirmacion de
  que cabe en la P1S.
- `guia_impresion_p1s.md`: como llevar estas piezas a la impresora paso a
  paso (perfiles, orientacion, soportes, montaje).

## Como generar/editar piezas

Abre `toreto_v2.scad` en OpenSCAD y cambia:

```scad
part = "assembly";
```

por cualquiera de los nombres listados en el selector al final del archivo
(por ejemplo `part = "torso_front_shell";`), o exporta todo por linea de
comandos:

```
openscad -o exports_v2/<pieza>.stl -D "part=\"<pieza>\"" toreto_v2.scad
```

Para ver el ensamblaje explosionado (util para revisar el orden de montaje):

```scad
exploded = true;
```

## Que cambio respecto a V0/V1

- Proporciones ajustadas para que coincidan exactamente con la infografia
  (altura 95 cm, base 40 cm).
- Se agrego `camera_mount` (pieza 2, soporte de camara RGB-D dentro de la
  cabeza), que no existia en V0/V1.
- Se agrego `arm_shoulder_support` (pieza 6) como pieza separada del
  `shoulder_pod` estetico, para reflejar el desglose de la infografia.
- `torso_h` se ajusto de 265 a 228 mm porque 265 mm no cabe en la P1S en
  ningun eje; `waist_h` creciodo para compensar la altura total. Ver
  `STL_EXPORTADOS_V2.md` para el detalle.
- Todas las 27 piezas se verificaron con bounding box real: ninguna excede
  256 x 256 x 256 mm.

## Siguientes pasos sugeridos

1. Imprimir la maqueta completa sin electronica para validar escala fisica.
2. Elegir motores/servos reales y adaptar `arm_shoulder_support`,
   `joint_disc_*` y `neck_column` a sus ejes y tornilleria exactos.
3. Montar la base movil con motores, encoders, bateria y parada de
   emergencia.
4. Integrar pantalla, camara, microfonos y conexion con tus agentes
   (API/MQTT/WebSocket).
5. Pasar de la pinza conceptual de 3 dedos a un diseno funcional con carga
   real (limitar a 300-500 g en la primera iteracion).
