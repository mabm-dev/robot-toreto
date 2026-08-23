# Robot Toreto - Concepto CAD V0

Este paquete es un primer concepto CAD parametrico para convertir la idea de Robot Toreto en piezas modulares imprimibles en una Bambu P1S.

No es todavia un diseno mecanico final para montar motores reales. Es una base de trabajo para validar volumen, estetica, divisiones de impresion, posiciones de electronica y arquitectura general.

## Archivo principal

- `toreto_concept_v0.scad`: modelo parametrico OpenSCAD con selector de piezas.

Abre el archivo en OpenSCAD y cambia esta linea:

```scad
part = "assembly";
```

Por una de estas piezas:

```scad
part = "base_quadrant";
part = "base_center_plate";
part = "electronics_box";
part = "wheel_cover";
part = "sensor_panel";
part = "torso_front";
part = "torso_back";
part = "shoulder_mount_left";
part = "shoulder_mount_right";
part = "neck_column";
part = "head_front";
part = "head_back";
part = "head_side_pod";
part = "upper_arm_shell";
part = "forearm_shell";
part = "wrist_gripper_concept";
```

Despues renderiza y exporta a STL.

## Medidas base

- Altura objetivo: 950 mm.
- Diametro de base: 400 mm.
- Torso: 230 x 170 x 220 mm.
- Cabeza: 220 x 120 x 112 mm.
- Base dividida en 4 cuadrantes para entrar en la Bambu P1S.

## Material recomendado

- Carcasas exteriores: PETG.
- Soportes de brazo, cuello y hombros: PETG-CF o PA-CF, con boquilla endurecida.
- Piezas internas con carga: combinar impresion 3D con ejes metalicos, rodamientos, insertos termicos y tornilleria.

## Enfoque recomendado

1. Imprimir una maqueta sin electronica para validar tamano.
2. Hacer base movil con motores y bateria baja.
3. Montar cabeza con pantalla, microfonos, altavoz y camara.
4. Conectar con tus agentes por API, MQTT o WebSocket.
5. Anadir brazo sencillo antes de intentar brazo de 6 DOF con carga real.

## Aviso importante

El brazo de 6 DOF y la carga de 2 kg del concepto original requieren calculo mecanico serio. Para la primera version, recomiendo limitar la pinza a objetos ligeros de 300 a 500 g.
