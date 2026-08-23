# Guia de impresion - Robot Toreto V2 en Bambu P1S

Esta guia lleva las 27 piezas de `exports_v2/` desde el STL hasta piezas
impresas y atornillables. Volumen de impresion de la P1S: **256 x 256 x
256 mm**. Todas las piezas de V2 caben (ver `STL_EXPORTADOS_V2.md`), asi que
no hace falta cortar nada con un splitter de mallas.

## 1. Preparar la impresora

- **Boquilla**: PETG-CF y PA-CF son abrasivos y desgastan una boquilla de
  latón/acero inoxidable en pocas horas. Usa una boquilla de **acero
  endurecido** (o CHT endurecida) de 0.4 mm para todas las piezas marcadas
  como PETG-CF en `lista_piezas_v2.md`. Si solo tienes la boquilla estandar,
  imprime primero todo lo que sea PETG normal y cambia la boquilla antes de
  las piezas CF.
- **Placa**: usa la placa texturizada PEI (Textured PEI) o la Cool Plate
  SuperTack. El PETG se adhiere muy fuerte a la placa lisa PEI y puede
  arrancar el recubrimiento al despegarlo; la texturizada da un agarre
  suficiente y una superficie facil de despegar en frio.
- **Recinto**: cierra la puerta/top del P1S para PETG-CF (ayuda a la
  adherencia de piezas grandes como los cuadrantes de base) pero no hace
  falta calefaccion activa como con ABS.

## 2. Perfiles en Bambu Studio

Crea dos perfiles de proceso a partir del "0.20mm Standard @BBL P1S":

| Ajuste | Piezas cosmeticas (PETG) | Piezas estructurales (PETG-CF) |
| --- | --- | --- |
| Filamento base | Generic PETG / Bambu PETG HF | Bambu PETG-CF / Generic PETG-CF |
| Nozzle temp | 230-235 C (240 C primera capa) | 250-260 C (fabricante suele dar rango exacto) |
| Bed temp | 70-75 C | 75-80 C |
| Paredes | 3 | 4-5 |
| Relleno | 15-20 % rejilla (grid) | 30-40 % gyroid |
| Altura de capa | 0.20 mm | 0.20 mm (usa 0.16 mm en `joint_disc_*` y `neck_column` para que los agujeros M4 queden mas precisos) |
| Ventilador de piezas | 100 % tras capa 2 | 30-50 % (el CF no necesita tanto enfriamiento pero ayuda al puente en los agujeros horizontales) |
| Brim | Ninguno salvo piezas de base (outer brim 5 mm) | Outer brim 5 mm en `neck_column_stack`, `base_*_quadrant` |

Filamento de color: blanco PETG para carcasas exteriores, negro PETG/PETG-CF
para columna, cuello, torso trasero y discos de junta, azul/traslucido solo
si vas a imprimir los ojos o el visor con un filamento distinto (opcional,
tambien puedes pintar).

## 3. Orientacion por pieza

Regla general para las carcasas tipo concha (cabeza, torso): **la cara plana
de corte (el "seam") va contra la cama**, boca abajo. Así la superficie
curva exterior imprime sin soportes y las costuras quedan limpias para
encolar/atornillar la pieza opuesta.

| Pieza | Orientacion | Soportes |
| --- | --- | --- |
| `head_front_shell`, `head_back_shell` | Cara plana (seam) contra la cama | Soporte de arbol solo en los resaltes de tornillo internos (activa "soportes solo en la placa" = No) |
| `torso_front_shell`, `torso_back_shell` | Cara plana contra la cama | Igual que cabeza |
| `torso_front_bezel` | De pie sobre el borde inferior recto | No |
| `torso_display_insert` | Tumbada, cara plana grande contra la cama | No |
| `head_side_pod`, `shoulder_pod_*` | Cara de union (la que se atornilla al torso/cabeza) contra la cama | Arbol ligero en el saliente cilindrico |
| `camera_mount` | Base plana contra la cama | No |
| `neck_column`, `neck_column_stack` | Vertical, eje del cilindro en Z | No (los agujeros M4 horizontales son pequenos, quedan bien con puente) |
| `upper_arm_shell`, `forearm_shell` | **Tumbada**, el eje largo (190-205 mm) apoyado en el plano XY | No. Tumbarlas alinea las capas con el sentido de flexion del brazo y es mas resistente que imprimirlas de pie |
| `joint_disc_*` | Plana, cara circular contra la cama | No |
| `arm_shoulder_support_*` | Cara de anclaje contra la cama | Arbol ligero |
| `gripper_three_finger` | De pie, base circular contra la cama | Arbol/organico en los dedos (son el unico voladizo real de la pieza) |
| `electronics_box` | Boca hacia arriba (abierta), base contra la cama | No |
| `base_upper_quadrant`, `base_lower_quadrant` | Cara curva exterior contra la cama (como sale del modelo) | No, son piezas robustas y planas |
| `front_sensor_panel`, `lidar_cap`, `wheel_pod_shell` | Cara de montaje contra la cama | No o minimo |
| `omni_wheel_dummy` | Tumbada sobre el lateral plano | No |

En Bambu Studio, selecciona cada pieza y usa **"Colocar sobre la cara"**
para clicar directamente la cara que quieres contra la placa; es mas rapido
y preciso que rotar a mano.

## 4. Tolerancias y ajuste

El modelo ya incluye una holgura de union de 0.35 mm entre mitades (frontal/
trasera) y ejes M3 (3.25 mm) / M4 (4.35 mm) como agujeros piloto. Con estos
diametros:

- **Tornillo autorroscante directo en PETG/PETG-CF**: funciona bien para
  piezas cosmeticas que no se van a desmontar muchas veces (carcasas de
  cabeza y torso).
- **Insertos termicos**: para piezas que aprietan estructura real
  (`arm_shoulder_support_*`, `neck_column`, `base_*_quadrant`,
  `joint_disc_*`), taladra el agujero a 4.0 mm (para insertos M3) o 5.0 mm
  (para insertos M4) y coloca un inserto termico con soldador a temperatura
  controlada (~220 C). Es mucho mas fiable que roscar directo sobre PETG-CF
  cuando vas a montar/desmontar el brazo varias veces durante las pruebas.

Antes de imprimir en serie, imprime una sola vez `joint_disc_elbow.stl` y
comprueba que un tornillo M4 real pasa limpio por el agujero; ajusta
`m4_hole()` en `toreto_v2.scad` (linea del diametro `4.35`) si tu tornillo
concreto pide mas o menos holgura, y vuelve a exportar.

## 5. Secuencia de impresion recomendada

1. **Piezas de base** (`base_lower_quadrant` x4, `base_upper_quadrant` x4):
   son las mas grandes y planas; sirven para validar primera capa y
   adherencia antes de comprometer piezas mas complejas.
2. **Piezas estructurales PETG-CF** (`neck_column`, `neck_column_stack`,
   `arm_shoulder_support_*`, `joint_disc_*`, `gripper_three_finger`):
   agrupa todas juntas para no ir cambiando de filamento/temperatura a cada
   rato.
3. **Carcasas cosmeticas PETG** (cabeza, torso, hombros, brazo, laterales):
   pueden ir en el AMS con blanco/negro segun la tabla de
   `lista_piezas_v2.md`, combinando varias piezas por plato ya que ninguna
   pasa de 245 mm.
4. **Piezas pequenas** (`camera_mount`, `front_sensor_panel`, `lidar_cap`,
   `wheel_pod_shell` x3): imprimir juntas al final, aprovechando huecos de
   plato.

Con un plato de 256 x 256 mm caben comodamente 2-3 piezas medianas por
impresion (por ejemplo, `torso_front_shell` + `torso_back_shell` en el mismo
plato ya llenan casi todo el ancho; mejor imprimirlas por separado o en
plato con `head_side_pod` de relleno).

## 6. Montaje

1. Base: atornilla los 4 cuadrantes inferiores entre si (agujeros M4 en las
   esquinas), luego los 4 superiores, y une ambos anillos. Monta ruedas,
   motores y LIDAR reales antes de cerrar (son piezas no impresas, items
   13-14).
2. Columna central (`neck_column_stack`) sobre la base.
3. Torso: unir `torso_front_shell` + `torso_back_shell` con tornillos en los
   resaltes internos (`screw_boss`), intercalando `torso_front_bezel` y
   `torso_display_insert` en la abertura frontal antes de cerrar.
4. Caja electronica dentro del torso, en los insertos previstos.
5. Hombros: `shoulder_pod_*` + `arm_shoulder_support_*` al lateral del
   torso, luego la cadena de brazo (`joint_disc_shoulder` -> `upper_arm_shell`
   -> `joint_disc_elbow` -> `forearm_shell` -> `joint_disc_wrist` ->
   `gripper_three_finger`).
6. Cuello (`neck_column`) sobre el torso, cabeza (`head_front_shell` +
   `head_back_shell` + `head_side_pod` x2) sobre el cuello, con
   `camera_mount` fijado por dentro antes de cerrar las dos mitades.

## 7. Lo que esta guia no resuelve todavia

- Alojamientos exactos para los servos/motores reales del brazo y del
  cuello: hoy son cilindros genericos (`joint_disc`). Cuando elijas modelo
  de servo, dime las medidas (o el modelo comercial) y ajusto esas piezas.
- Anclaje de motores/reductoras de las 3 ruedas omnidireccionales a la base
  impresa.
- Calculo de resistencia del brazo con carga real (esto es una maqueta
  visual; para 300-500 g en la pinza probablemente vaya bien con PETG-CF al
  40 % de relleno, pero no esta verificado con calculo estructural).
