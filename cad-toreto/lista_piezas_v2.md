# Lista de piezas - Robot Toreto V2

Version alineada con la infografia "Robot Asistente Inteligente" (altura 95 cm,
base 40 cm, brazo 6 DOF, cabeza 2 DOF, base movil de 3 ruedas + LIDAR).
Archivo fuente: `toreto_v2.scad`. STL en `exports_v2/`.

Es una **maqueta visual**: formas y proporciones fieles a la referencia, sin
mecanismo interno funcional (motores, reductoras, rodamientos reales) todavia.

## Piezas impresas (mapeadas al numero de la infografia)

| # infografia | Pieza infografia | Modulo / archivo STL | Cant. | Material sugerido | Nota |
| :---: | --- | --- | ---: | --- | --- |
| 1 | Carcasa cabeza | `head_front_shell.stl`, `head_back_shell.stl`, `head_side_pod.stl` (x2) | 4 | PETG blanco | Frontal con hueco de pantalla/ojos, trasera, dos orejas laterales |
| 2 | Soporte camara | `camera_mount.stl` | 1 | PETG negro | Bracket interno para camara RGB-D detras del visor |
| 3 | Cuello | `neck_column.stl` | 1 | PETG-CF negro | Paso de cables interior, 2 DOF de cabeza se montan aqui |
| 4 | Carcasa torax frontal | `torso_front_shell.stl`, `torso_front_bezel.stl`, `torso_display_insert.stl` | 1 + 1 + 1 | PETG blanco / negro / traslucido | Hueco de pantalla tactil con marco |
| 5 | Carcasa torax trasera | `torso_back_shell.stl` | 1 | PETG negro | Acceso a electronica y cableado |
| 6 | Soportes de brazo | `arm_shoulder_support_left.stl`, `arm_shoulder_support_right.stl` | 2 | PETG-CF | Anclaje hombro-torso, debe reforzarse con eje metalico |
| 7 | Brazo (estructura) | `upper_arm_shell.stl` (x2), `forearm_shell.stl` (x2), `joint_disc_shoulder/elbow/wrist.stl` (x2 c/u) | 2+2+6 | PETG-CF | Carcasas de brazo superior/antebrazo + discos de junta en 3 ejes |
| 8 | Pinza | `gripper_three_finger.stl` | 2 | PETG-CF | Pinza de 3 dedos, concepto ligero (300-500 g) |
| 9 | Columna central | `neck_column_stack.stl` | 1 | PETG-CF negro | Une base, cintura y torso |
| 10 | Caja electronica | `electronics_box.stl` | 1 | PETG | Aloja reguladores, hubs, controladores dentro del torso |
| 11 | Base superior | `base_upper_quadrant.stl` | 4 | PETG-CF blanco | Anillo superior de la base, 4 cuadrantes atornillados |
| 12 | Base inferior | `base_lower_quadrant.stl` | 4 | PETG-CF negro | Anillo inferior de la base, 4 cuadrantes atornillados |
| 15 | Tornilleria y rodamientos | -- | -- | -- | No impreso, ver lista de compra |
| -- | Frontal de sensores | `front_sensor_panel.stl` | 1 | PETG negro | Banda frontal de sensores de la base |
| -- | Tapa LIDAR | `lidar_cap.stl` | 1 | PETG blanco | Alojamiento impreso para el sensor LIDAR (item 14, no impreso) |
| -- | Cubierta rueda | `wheel_pod_shell.stl` | 3 | PETG blanco | Cubierta esteticas sobre cada rueda omni |
| -- | Rueda dummy | `omni_wheel_dummy.stl` | 3 | PETG negro | Solo referencia visual, no reemplaza la rueda real (item 13) |

## Componentes no imprimibles (items 13-15 + electronica)

| Componente | Cantidad orientativa | Nota |
| --- | ---: | --- |
| Ruedas omnidireccionales reales | 3 | Item 13 de la infografia, ~75 EUR c/u aprox., no imprimir como pieza funcional |
| Sensor LIDAR | 1 | Item 14, se aloja en `lidar_cap.stl` |
| Tornilleria M3/M4/M5 + rodamientos + insertos termicos | varios | Item 15 |
| Motores con encoder para base | 3 | Uno por rueda omni |
| Driver de motores | 1-3 | Segun motor elegido |
| Bateria 24 V 10 Ah | 1 | Li-ion/LiFePO4 con BMS, coincide con especificacion de la infografia |
| Reguladores DC-DC | 2-3 | 24 V a 12 V / 5 V / 19 V |
| Raspberry Pi 5 / Jetson Orin Nano | 1 | Procesador principal, segun especificacion |
| Camara RGB-D | 1 | Se monta en `camera_mount.stl` |
| Microfonos + altavoz/amplificador | 1 c/u | Voz e interaccion |
| Pantalla cabeza + pantalla torso | 1 c/u | Cara expresiva y pantalla tactil |
| IMU | 1 | Estabilidad y orientacion |
| Boton de parada de emergencia | 1 | Muy recomendado |

## Diferencias respecto a la infografia original

- `torso_h` se redujo de 265 mm a 228 mm (y `waist_h` crecio de 165 a 202 mm
  para compensar la altura total) porque 265 mm no entra en el volumen de
  impresion de la Bambu P1S (256 x 256 x 256 mm) en ninguna orientacion. Ver
  la guia de impresion para el detalle.
- El brazo de 6 DOF y la pinza son carcasas de maqueta visual. Los ejes reales
  (servos, reductoras) se definen en una fase posterior, cuando elijas los
  servos concretos.
