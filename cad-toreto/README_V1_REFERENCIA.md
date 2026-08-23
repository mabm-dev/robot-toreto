# Robot Toreto - V1 parecido a la referencia

Esta version intenta parecerse mas a la primera imagen que enviaste:

- cabeza blanca con pantalla negra grande
- ojos circulares azules
- laterales/orejas de cabeza
- torso blanco/negro con pantalla frontal
- hombros cilindricos grandes
- brazos segmentados con juntas negras
- base circular de dos niveles
- banda frontal negra de sensores
- ruedas tipo omni decorativas alrededor
- tapa superior tipo LiDAR

Archivo principal:

`toreto_reference_v1.scad`

Carpeta de STL:

`exports_v1`

## Importante

La V1 es mas fiel visualmente, pero sigue siendo un concepto. Antes de imprimir una version funcional hay que adaptar:

- motores reales de la base
- ruedas reales
- pantalla de cabeza
- pantalla del torso
- tornilleria exacta
- rodamientos y ejes
- bateria y caja electronica
- servos/motores del brazo

## Piezas repetidas

- `base_lower_quadrant.stl`: imprimir 4
- `base_upper_quadrant.stl`: imprimir 4
- `wheel_pod_shell.stl`: imprimir 3
- `omni_wheel_dummy.stl`: imprimir 3 solo si quieres maqueta visual
- `head_side_pod.stl`: imprimir 2
- `upper_arm_shell.stl`: imprimir 2
- `forearm_shell.stl`: imprimir 2
- `joint_disc_shoulder.stl`: imprimir 2
- `joint_disc_elbow.stl`: imprimir 2
- `joint_disc_wrist.stl`: imprimir 2
- `gripper_three_finger.stl`: imprimir 2

Para maqueta visual, PETG esta bien. Para piezas que soporten peso, usa PETG-CF o PA-CF con boquilla endurecida y refuerzos metalicos.
