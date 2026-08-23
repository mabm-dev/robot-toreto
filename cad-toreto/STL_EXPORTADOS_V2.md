# STL exportados - Robot Toreto V2

Carpeta de salida: `C:\Users\tarif\Desktop\cad-toreto\exports_v2`

Todas las piezas fueron generadas con `toreto_v2.scad` via el CLI de OpenSCAD
(`openscad -o exports_v2/<pieza>.stl -D "part=\"<pieza>\"" toreto_v2.scad`) y
sus dimensiones reales (bounding box) se midieron directamente sobre el STL
exportado, no son estimaciones.

## Piezas y bounding box real (mm)

Volumen de impresion Bambu P1S: **256 x 256 x 256 mm**. Todas las piezas
caben con margen; la mas ajustada es el torso (228 mm en su eje mas largo).

| Archivo | Cant. | X | Y | Z | Cabe en P1S |
| --- | ---: | ---: | ---: | ---: | :---: |
| `head_front_shell.stl` | 1 | 232.0 | 66.0 | 136.0 | Si |
| `head_back_shell.stl` | 1 | 232.0 | 66.0 | 136.0 | Si |
| `head_side_pod.stl` | 2 | 76.0 | 70.0 | 94.0 | Si |
| `camera_mount.stl` | 1 | 70.0 | 34.0 | 30.0 | Si |
| `neck_column.stl` | 1 | 104.0 | 104.0 | 108.0 | Si |
| `torso_front_shell.stl` | 1 | 245.0 | 89.0 | 228.0 | Si (mas ajustada) |
| `torso_back_shell.stl` | 1 | 245.0 | 89.0 | 228.0 | Si (mas ajustada) |
| `torso_front_bezel.stl` | 1 | 212.0 | 12.0 | 200.5 | Si |
| `torso_display_insert.stl` | 1 | 146.0 | 9.0 | 162.6 | Si |
| `shoulder_pod_left.stl` | 1 | 94.0 | 82.0 | 94.0 | Si |
| `shoulder_pod_right.stl` | 1 | 94.0 | 82.0 | 94.0 | Si |
| `arm_shoulder_support_left.stl` | 1 | 70.0 | 60.0 | 70.0 | Si |
| `arm_shoulder_support_right.stl` | 1 | 70.0 | 60.0 | 70.0 | Si |
| `upper_arm_shell.stl` | 2 | 64.0 | 48.0 | 205.0 | Si |
| `forearm_shell.stl` | 2 | 54.0 | 42.0 | 190.0 | Si |
| `joint_disc_shoulder.stl` | 2 | 58.0 | 60.0 | 58.0 | Si |
| `joint_disc_elbow.stl` | 2 | 48.0 | 48.0 | 48.0 | Si |
| `joint_disc_wrist.stl` | 2 | 38.0 | 40.0 | 38.0 | Si |
| `gripper_three_finger.stl` | 2 | 50.0 | 44.0 | 130.0 | Si |
| `neck_column_stack.stl` | 1 | 155.0 | 155.0 | 202.0 | Si |
| `electronics_box.stl` | 1 | 170.0 | 130.0 | 60.0 | Si |
| `base_upper_quadrant.stl` | 4 | 176.0 | 176.0 | 74.0 | Si |
| `base_lower_quadrant.stl` | 4 | 201.0 | 201.0 | 62.0 | Si |
| `front_sensor_panel.stl` | 1 | 154.0 | 24.0 | 38.0 | Si |
| `lidar_cap.stl` | 1 | 58.0 | 58.0 | 33.0 | Si |
| `wheel_pod_shell.stl` | 3 | 102.0 | 56.0 | 92.0 | Si |
| `omni_wheel_dummy.stl` | 3 | 99.0 | 99.0 | 88.0 | Si |

Total de piezas fisicas a imprimir (con repeticiones): 45.

## Vista previa

- `toreto_v2_preview.png`: vista de cabeza/torso.
- `toreto_v2_full_body.png`: vista de cuerpo completo.

## Nota sobre el torso

En la infografia original el torso mide 265 mm de alto, lo que no entra en
ningun eje de la P1S (256 mm de limite en X, Y y Z). En V2 `torso_h` se
redujo a 228 mm y `waist_h` crecio de 165 a 202 mm para compensar la altura
total del robot. Si prefieres mantener los 265 mm originales, la alternativa
es partir el torso en dos mitades (superior/inferior) con una pestana de
union, igual que ya se hace con la base en 4 cuadrantes.

## Antes de imprimir

Ver `guia_impresion_p1s.md` para orientacion, perfiles de Bambu Studio,
soportes y secuencia de montaje pieza por pieza.
