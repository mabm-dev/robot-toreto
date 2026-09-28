# Prueba en Fusion — 2026-09-24

## v14: alturas del montaje (solo lectura) — 29-09-2026

El usuario vio huecos entre cintura y tronco y entre cuello y cabeza (Medir:
5,00 mm cada uno). `MODE='alturas'` (no cambia nada) dio en el montaje:
tronco 200-385 (hecho con alto_tronco 185; el zócalo mide exactamente esa
escala) y cuello 730-785 (hecho con alto_cuello 55); base, cintura (390-540),
pecho (540-730) y cabeza (790-950) correctos. Solapes a propósito: torreta del
LIDAR sobre la base (204-229) y discos del hombro/inserto del cuello sobre el
pecho. Arreglo preparado: Tronco 1.3.1 y Cuello 1.2.1 (misma geometría, solo
versión, para que se regeneren con los parámetros actuales), copiados a
%APPDATA%. SIN ejecutar todavía. Informe: `alturas_montaje_v14.json`.

## v13c + pecho 2.6.0: RESULTADO en el montaje — 28-09-2026 — hombro unido al pecho

Pecho 2.6.0 ejecutado en el montaje (24 cuerpos, Z 540-737,8), brazo v13c
generado (todo a 0,0 mm) y reemplazado, mano izquierda rearticulada (20 juntas,
16 relaciones, 0,001 mm). Vista frontal: la pieza negra de hombro une pecho y
brazo en los dos lados, como en la lámina. Interferencia: ninguna entre brazo
y pecho. Nuevas filas carcasa del pecho - `07_CONECTOR_HOMBRO_IZQ/DER`
(11021,5 mm3 cada una): el disco junto al pecho entra 2 mm en la carcasa a
propósito (fijación), del mismo tipo que las demás piezas del pecho embutidas.

## v13c + pecho 2.6.0: pieza de hombro como la lámina — 28-09-2026

El usuario vio en el montaje un hueco de ~40 mm entre pecho y brazo: el
conector del pecho 2.5.0 solo existía DENTRO del brazo (X 166-196,5). La
interferencia salió limpia justo porque no se tocaban. En la lámina frontal
hay una pieza negra de hombro entre ambos (medida a mano sobre rejilla,
`medicion_brazo/hombro_frontal.jpg`). Pecho 2.6.0: disco R47 (X 124-130,
entra 2 mm en el pecho), disco R39 (130-138), cuello R29 (138-146), disco R39
(146-157) y el eje R36,5 (157-196,5), coaxiales con el eje del hombro (en la
lámina se dibujan inclinados con el brazo). La carcasa del brazo no baja de
X 159,3 (esquinas de sus perfiles ya colocados): los discos acaban en 157 y
solo el eje entra; el taladro del brazo (v13c) empieza en 155. Pruebas: los
discos a >= 2 mm de la carcasa, la pieza continua, el eje dentro del taladro
y los mismos números en el complemento del pecho y aquí (se lee su código).
Complemento del pecho copiado a `%APPDATA%` (respaldo de la 2.5.0 en el
scratchpad de la sesión). Al ejecutarlo en el montaje restablece los
parámetros del pecho a los de por defecto (340/190/220).

## v13b: RESULTADO en el montaje — 28-09-2026 — hombro sin tocar el pecho

Generado (todo a 0,0 mm), guardado como `Toreto_Brazo_Mano_v13b` y reemplazado
en el montaje `…_backup`; juntas de la mano izquierda rehechas (20 juntas, 16
relaciones, pasadores a 0,001 mm; Fusion añadió ' (2)' a nombres de cuerpos
de la copia y `base_name` lo absorbió). **Interferencia pecho-brazo: la fila
del conector contra la carcasa ha desaparecido en los dos brazos.** Quedan
solo las ajenas al encaje (pecho consigo mismo, rótula-conector de palma,
mano sin recortar).

## v13b: taladro del hombro prolongado, preparada el 28-09-2026

Interferencia en el montaje (los dos brazos, simétricos): la única pieza del
brazo que toca el pecho es su carcasa `01_BRAZO_LOCAL_SIN_REBAJES` contra
`PECHO95_07_CONECTOR_HOMBRO_DER/IZQ`, 1806,8 mm3. El taladro de la v13 empezaba
en X 167,4 y el conector en 166; además la carcasa baja inclinada ~15° y, por
encima y por debajo del taladro, su cara interior llega más cerca del pecho.
Arreglo: el taladro va de X 164,0 a 224,6 (2 mm más allá de cada extremo),
coaxial y con R37,3 > R36,5: el conector queda entero dentro del cilindro que
se quita a la carcasa, así que no puede tocarla (prueba
`test_connector_lies_entirely_inside_the_bore`, que falla con el taladro de la v13).

El resto de la tabla es ajeno al encaje: piezas del pecho solapadas entre sí
(vienen de su generador), casquillos y pasadores sobre su propia falange
(bloque rígido), la palma sin recortar contra las primeras falanges (prueba
de la palma pendiente) y la rótula de la muñeca contra el conector de la palma
(9531 mm3; son una sola pieza en una muñeca de rótula: el script puso la
rótula en el antebrazo y el conector en la mano; corregir al hacer las juntas
del brazo).

## v13: RESULTADO en Fusion — 27-09-2026 — hombro encajado, dos brazos articulados

`vista_brazo_v11.json` (modo ver_brazo, v13): pivote del hombro en el eje del
conector (0,0 mm), tapa del hombro y rótula a 0,0 mm dentro de Fusion, mano
en su sitio (0,0 mm, con la comprobación corregida). El usuario lo guardó
como `Toreto_Brazo_Mano_v13` y lo reemplazó en el montaje; la simetría del
brazo izquierdo se recalculó sola y sus juntas antiguas quedaron con errores
de referencia (geometría en caché). Se borraron y `juntas_espejo` las creó de
nuevo: 20 juntas y 16 relaciones, pasadores a 0,001 mm (`juntas_espejo_v12.json`).
Lección: al cambiar el brazo derecho, borrar las juntas de la mano izquierda
y volver a ejecutar `juntas_espejo`. Pendiente: Inspeccionar > Interferencia
entre brazo y pecho.

## v13: hombro encajado en el pecho, preparada el 27-09-2026 — SIN ejecutar

Pedido por el usuario tras confirmar que la mano izquierda cierra hacia su
palma. Conector del hombro derecho del pecho (`Toreto_Pecho_Hombros_95cm`
2.5.0 con parámetros por defecto: ancho 340, alto 190, base+tronco+cintura
540 mm): cilindro en X de 166 a 196,5 mm, Y 0, Z 690,83, radio 36,5 mm.

- El eje del hombro del brazo pasa a ser **coaxial con el conector**: X
  exacta (antes inclinado 15° con la carcasa) y pivote en Y 0, Z 690,83
  (16 mm del punto de la lámina: manda el pecho).
- Taladro del alojamiento R37,3 (conector + 0,8 mm), pared 7,7 mm; el
  alojamiento va de X 169,4 a 222,6, así que el conector entra en el brazo,
  como dibuja la lámina. El eje negro propio del brazo queda como tapa
  exterior desde X 197,3 (0,8 mm tras el extremo del conector).
- Postura reajustada alrededor del conector: hombro +19,6°, codo -48,0°;
  codo a 7,3 mm y final del antebrazo a 3,6 mm de la lámina.
- `chest=None` reproduce la v11 exacta (probado). 57 pruebas; simuladores OK.
- Sin comprobar: que los parámetros del pecho del montaje sean los de por
  defecto, y si la carcasa del brazo toca el pecho (Inspeccionar >
  Interferencia en el montaje).
- La v12 (juntas de la mano izquierda) calcula con esta postura: al cambiar
  el brazo derecho hay que rehacer la simetría y volver a ejecutarla.

## v12: RESULTADO en el montaje — 27-09-2026 — mano izquierda articulada

`juntas_espejo_v12.json`: 20 juntas y 16 relaciones creadas en la mano copiada
por simetría; los 20 pasadores a 0,001 mm con la colocación `transform2` (la
cadena de padres dio lo mismo; la identidad, 914 mm). El usuario comprobó
en Fusion que las relaciones se mueven. El robot tiene ya los dos brazos v11
con manos de 4 motores articuladas. Pendiente: el encaje del hombro en el
pecho (16 mm en Y y el taladro menor que el conector de 36,5 mm) y las juntas
del brazo, en el orden decidido: piezas → dimensiones → límites.

## v12: primera ejecución en el montaje — 27-09-2026 — RECHAZADA SIN CAMBIOS

La protección funcionó: encontró la mano copiada
(`06_MANO_ARTICULABLE(Simetría)`), sus 21 piezas y el pasador, pero midió
(272,6; -79,9; -313,9) donde esperaba (-272,6; -79,9; 313,9): el mismo punto
con X y Z cambiados de signo. Fusion guarda la mano reflejada dentro de su
componente y coloca el componente girado 180° en Y; el script leía los
bordes en coordenadas internas y comparaba con las del robot. Corregido: se
prueban las colocaciones candidatas (`transform2` de la ocurrencia, la cadena
de padres y la identidad), se pasan centros y ejes a coordenadas internas
(`to_local_specs`; un eje es pseudovector también aquí) y solo vale la que
cuadra los 20 pasadores. La medición real es ahora una prueba unitaria. El
simulador cubre el caso real, el anidado y los dos sentidos del círculo, y
sigue rechazando la mano girada sin datos de colocación.

## v12: juntas de la mano izquierda, preparada el 27-09-2026

Montaje real: documento `Toreto_hombro_encajado_sin_articulaciones`. El
usuario borró el brazo antiguo, insertó el v11 guardado como
`Toreto_Brazo_Mano_v11` y creó el izquierdo con Crear > Simetría (plano YZ).
La copia no tiene juntas ni relaciones. `MODE='juntas_espejo'` se las añade.

**Excepción autorizada por el usuario** a "solo documento vacío": este modo
trabaja en el montaje, pero NO crea ni mueve geometría; solo añade 20 juntas
y 16 relaciones a la única `06_MANO_ARTICULABLE` sin juntas. Antes de crear
nada comprueba que haya exactamente una, sus 21 piezas por nombre (admite el
sufijo "(Simetría)"), los 20 pasadores en su pieza, cada uno a menos de
1,5 mm de su posición reflejada y con su borde circular alineado. Si algo
falla, no cambia nada. Se pidió guardar una versión del montaje antes.

Al reflejar, el eje de giro no va a M·a sino a -M·a (pseudovector): con M·a
los dedos izquierdos se doblarían hacia fuera. Probado en
`test_mirror_joints.py` (y una prueba impide "simplificarlo").
`simular_espejo_sin_fusion.py`: 20 juntas y 16 relaciones con los dos
sentidos posibles del círculo reflejado, pinza reflejada dentro de límites,
y rechazo sin cambios con mano desplazada, dos manos libres o un pasador
ausente; detecta el eje reflejado como punto. No comprobado: cómo nombra y
coloca Fusion las copias por simetría (si difiere, el script se negará y lo
dirá en `juntas_espejo_v12.json`).

## v11: RESULTADO en Fusion — 27-09-2026 — brazo colocado como la lámina

`vista_brazo_v11.json`: publicado; 20 juntas y 16 relaciones de la mano
creadas con los ejes girados. **Eje del hombro y rótula a 0,0 mm de donde
deben estar, medido dentro de Fusion.** El aviso dio "mano en su sitio: NO"
(peor falange 2,055 mm), pero era un fallo de la comprobación: giraba el
centro de la caja alineada con los ejes, y esa caja cambia al girar una pieza
asimétrica. Lo delata el patrón: depende de la forma (falanges tipo caja
~0,12 mm, las cuatro puntas idénticas ~0,9 mm, falange 1 del pulgar 2 mm),
no de la distancia a la muñeca; y los 20 pasadores se encontraron con sus
ejes girados. Corregido: la pieza calculada se gira y luego se mide su caja.
Pendiente: comparar el lateral con la lámina a ojo.

## v11: brazo como la lámina, preparada el 27-09-2026

Decisión del usuario: el brazo toma ya las medidas de la lámina (se ajustará
con los servos) y se construye en su postura, que será el cero de las juntas.
Medición en `medicion_brazo/MEDICION_BRAZO_LAMINA.md`. `MODE='ver_brazo'`
publica brazo y mano abierta; los demás modos no cambian.

- `toreto_arm_pose.py` (puro): alarga el antebrazo ×1,365 (del codo al final
  de la carcasa, 164 mm como la lámina) dejando fijo el extremo del codo y
  con los MISMOS perfiles estables (sin forzarlo entraba uno más: lo detectó
  una prueba); lleva el eje del hombro a su pivote (156,6 mm del codo) con un
  alojamiento del ancho de la carcasa (51,3 mm) y el radio del disco de la
  lámina (45 mm); y calcula los giros de la postura: hombro +13,6°, codo
  -44,0°. Frente a la lámina: hombro 0 mm, codo 2,5 mm, final del
  antebrazo 7,3 mm (sobre todo en X).
- Todo se construye en el marco plano de siempre y, antes de importar, brazo
  superior, antebrazo y mano se mueven con giros rígidos. Los ejes de las
  juntas de la mano se transforman igual. La mano y sus ensayos no cambian.
- El JSON (`vista_brazo_v11.json`) comprueba en Fusion dónde quedan el eje
  del hombro y la rótula, y cada falange frente al cálculo.
- Validación: 45 pruebas; `simular_brazo_sin_fusion.py` con cuerpos falsos
  que sí se mueven, que detecta (probado rompiéndolo): ejes de la mano sin
  girar, mano sin colocar, matriz traspuesta, traslación en mm en vez de cm
  y antebrazo con la matriz del brazo.
- No comprobado: el loft del antebrazo alargado y el alojamiento del hombro
  en Fusion, ni si las carcasas de brazo y antebrazo se tocan en el codo con
  -44° (eso es el siguiente paso: juntas del brazo y ensayo de recorridos).

## v10b: RESULTADO en Fusion — 27-09-2026 — pinza lateral ACEPTADA

`prueba_mano_4_motores_v10b.json`: estado `contacto_cara_no_deseada_o_indeterminada`
porque el ensayo esperaba el costado PLANO del índice. Datos: primer contacto
entre 77,9% y 78,1% del índice (pulgar 20,3%), sin choques antes; pulgar
**palmar** (37-63% de la falange, alineación 0,97); índice en la **punta**
(69-89% de su falange, zona redondeada, cerca de la esquina costado/palmar);
intersección 0,163 mm3 frente a 2,955 mm3 de penetración por diferencia
(confirmada la hipótesis: la diferencia es ruido en contactos rozantes; a
83% coinciden, 89,9 mm3). La "estabilidad NO" no es informativa: las otras
posturas comprobadas tenían 40 y 550 veces más solape (fallo de diseño del
chequeo: debían ser posturas pegadas al contacto).

Vista en Fusion (modo `ver_pinza` + juntas a mano: cardán -30, pulgar -8,125,
índice 42,188): la cara plana del pulgar toca la esquina redondeada de la
punta del índice y se abre una V de unos 20-30°. **El usuario la acepta tal
cual** (`docs/DECISIONES.md`); yemas blandas y rugosas previstas.

## v10b: cara del contacto, preparada el 27-09-2026

**Resultado de la v10 en Fusion (27-09-2026): `cara_no_resuelta`**, con lo
demás bien: 0 choques en las muestras 0-9 (2.743 pares, 34 cuerpos móviles)
ni en el afinado; primer contacto SOLO entre `09_PULGAR_FALANGE_3` y
`07_DEDO_1_FALANGE_4`, acotado entre el 77,9% y el 78,1% del índice
(flexión del pulgar 20,3%, cardán 100%). Toques con contacto: 78,1%, 79,2%
y 83,3%, coherentes. Falló la comprobación "volumen de intersección no
coincide con la penetración", y el error no guardó los volúmenes. Hipótesis
(sin confirmar): en un contacto rozante, la penetración por diferencia resta
dos volúmenes de miles de mm3 y la imprecisión del cálculo de volumen la
desbarata; la intersección directa es la fiable. Informe conservado:
`prueba_mano_4_motores_v10.json`.

Cambios de la v10b (misma geometría, mismo escenario, mismo afinado):
- Manda la intersección directa; los dos volúmenes se guardan siempre y la
  diferencia pasa a aviso (`warnings`). Intersección <= 0,01 mm3: contacto
  no confirmado, nunca apoyo.
- La cara se clasifica en hasta 3 posturas con contacto (la más temprana
  decide; las otras dan `stability.consistent`). Apoyo palmar-lateral sin
  estabilidad confirmada: `apoyo_palmar_lateral_sin_confirmar_estabilidad`.
- Informe: `prueba_mano_4_motores_v10b.json`.
- Simulador: 8 casos, incluidos volumen discrepante (lo de la v10) e
  intersección vacía; con la comprobación estricta de la v10 falla.

## v10: pinza lateral, preparada el 27-09-2026 — SIN ejecutar en Fusion

`MODE='ensayo_lateral'`: cardán al 100% desde la muestra inicial; índice a
`t` y flexión del pulgar a `0,26*t`, en 12 divisiones. Se conservan las
relaciones, topes y geometría de la v8/v9. Solo se ejecuta este escenario;
la mano abierta y los motores solos de la v8 no se repiten ni se atribuyen a
la v10. Criterio: ningún choque ajeno antes del primer contacto de falanges
pulgar-índice.

En ese primer contacto muestreado, el ensayo intersecta los **sólidos
temporales reales** y registra volumen y caja de la intersección; la sitúa en
el marco de la falange final del pulgar y del índice. Distingue palmar,
dorsal, lateral, punta y transiciones/esquinas indeterminadas. Si contacta
otra falange o falla el booleano, no concede apoyo palmar. La caja localiza
la zona, pero no mide área de apoyo ni sustituye la inspección visual.

**Afinado del contacto (añadido el 27-09-2026, antes de ejecutar).** Con 12
divisiones el índice avanza 8 puntos por muestra; en la v8 eso llevó de 15 a
868 mm3 entre dos muestras, y un solape así invade esquinas y deja la cara
indeterminada. Al aparecer el primer contacto, el ensayo biseca 5 veces entre
la última muestra limpia y esa (paso final ~0,26% del índice) y clasifica la
cara en la postura más temprana con choque. Si en ese tramo aparece antes un
choque ajeno a la pinza, lo informa como previo. Las 13 muestras no cambian.
JSON: `refinement`, `refined_bracket` y `first_contact.fraction` (afinada;
`coarse_fraction` es la de la muestra).

Validación previa: 33 pruebas unitarias; simulador sin Fusion con contacto
palmar, contacto dorsal, choque previo, ausencia de contacto, error de
intersección y choque entre muestras (solo visible con el afinado; el
simulador falla si se desactiva), todos con informe JSON legible. Esos contactos son inventados;
**no hay resultado geométrico de la v10 todavía**. Informe esperado al
ejecutarla: `prueba_mano_4_motores_v10.json`. Si sale bien, la vista 3D con
recálculo de pose queda para otra ejecución, no esta.

## v9: vista de la pinza en 3D — 2026-09-26, ejecutada en Fusion

No es un ensayo: publica la mano de la v8 en el documento vacio para
mirarla (`MODE='ver_pinza'` en el script; `MODE='ensayo'` repite la v8).
Pose: muestra 9 de 12 de la pinza de la v8 (75%, hueco 0,28 mm), la ultima
antes del contacto, para ver si tocan por la yema o por el canto.

- 4 motores en Fusion: 16 relaciones, cada seguidora directa a su maestra
  (`JUNTA_DEDO_1_1`, `JUNTA_DEDO_2_1`, `JUNTA_PULGAR_2`); cardan suelto.
- Sin `clearance.repair()`: palma sin recorte y NO validada.
- `vista_pinza_v9.json`: angulos leidos de vuelta de Fusion y posicion de
  cada falange frente al calculo del ensayo (`pose_igual_al_ensayo`).
- Validado fuera de Fusion: 25 pruebas y `simular_publicacion_sin_fusion.py`,
  que detecta un signo de relacion o de pose mal puesto (comprobado
  rompiendolos a proposito). No puede comprobar el sentido de giro real de
  Fusion: si un dedo se dobla hacia atras, lo delatara la comparacion de
  posiciones del JSON.

**Primera ejecucion (26-09-2026): ERROR** al crear las juntas, con las
piezas ya importadas: "No se encontro un borde circular alineado en el
pasador". Causa: `pin_axis_edge()` buscaba siempre un pasador de 4 mm, pero
`JUNTA_PULGAR_1` y `_2` lo tienen de 2,8 mm (`hinge_dimensions`). Ese
codigo de publicacion era anterior a la reduccion del pasador del pulgar.
El simulador tampoco lo vio: creaba todos los pasadores de 4 mm. Corregido
en ambos: radio por junta en el script; en el simulador, radio real mas
circulos senuelo, y ahora reproduce el error con el codigo antiguo.

**Segunda ejecucion (26-09-2026), en documento de diseno HIBRIDO: PUBLICADA.**
101 cuerpos, 21 componentes, 20 juntas, 16 relaciones. `vista_pinza_v9.json`
dio `pose_igual_al_ensayo: NO`: las juntas guardaron los valores exactos
(indice 40,5; cardan y flexion del pulgar 30), pero las piezas seguian en la
postura abierta (comprobado: la hipotesis "nada se movio" encaja a 1,7 mm;
las de signo invertido fallan por 40-86 mm). Fusion aplico esos valores
guardados en cuanto el usuario acciono una junta a mano: al script le falta
forzar el recalculo tras la pose (pendiente, sin validar).
En la interfaz, "Animar relaciones de union" mueve cada dedo entero: las
relaciones de los 4 motores funcionan. El indice "atravesando" el pulgar al
animarlo era la pinza pasada del contacto (el pulgar ya estaba a -30/-30).

**Lo que se ve en la pinza al 75%:** el pulgar toca de PUNTA (extremo curvo
de su falange 3) contra la cara interior de la ultima falange del indice,
junto a su ultima articulacion. El usuario: el indice esta bien; el PULGAR
debe apoyar con la cara plana de su ultima falange, no con la curva (mas
superficie, el boli no gira). Caras de agarre rugosas. Ver
`docs/DECISIONES.md`. Cambiar la postura del pulgar exige ensayo nuevo.

Pista previa de los datos de la v8: en la muestra 11 la punta del indice
entra 868 mm3 en la falange MEDIA del pulgar, no en su punta: el indice
podria pasar por encima de la punta del pulgar (contacto de canto).

## v8: RESULTADO en Fusion — 2026-09-26 19:17 — TODO LIMPIO Y PINZA LOGRADA

`prueba_mano_4_motores_v8.json`: estado `todo_limpio_y_pinza_lograda`.
0 errores del nucleo en todo el ensayo, 50 apoyos verificados.

- Mano abierta, indice solo, corazon+anular+menique (senalar), flexion del
  pulgar sola y rotacion del pulgar sola: LIMPIOS. El choque de la v7 del
  indice contra la falange 1 del pulgar ha desaparecido.
- Pinza del boli: LOGRADA, punta con punta (07_DEDO_1_FALANGE_4 /
  09_PULGAR_FALANGE_3), cero choques antes del contacto. Contacto en la
  muestra 10 (83% del cierre) frente al 67% de la v7, como se esperaba al
  avanzar el indice mas despacio. Hueco entre puntas (mm): 77,7 / 69,1 /
  60,1 / 50,9 / 41,9 / 33,6 / 24,9 / 15,1 / 6,5 / 0,28 / 0 / 2,4 / 7,8.
  Un boli de ~8 mm quedaria sujeto hacia la muestra 8. De los 8 pares del
  escenario, uno es el propio contacto y 7 aparecen solo despues: artefacto
  de la simulacion (la mano real se detiene al tocar).

Lo que esto NO valida, y sigue pendiente: la palma principal (excluida del
ensayo), la holgura continua entre las 13 posturas muestreadas, la
resistencia, los agarres de objetos (vaso, pelota), el mecanismo de tendones
(que aun no existe en el diseno) y si la pinza toca por la yema o por el
canto. Es el primer resultado limpio de la mano, NO una mano funcional
validada ni lista para fabricar.

## v8: el indice con su propio recorrido — 2026-09-26, preparada

Unico problema de la v7: el indice, al cerrar del todo con el pulgar en
reposo, tocaba su falange 1 (5,2 mm3, solo en la muestra 12).

Cambio: el indice recorre el 90% que los demas dedos, en sus cuatro
articulaciones por igual: 54/54/45/36 grados en vez de 60/60/50/40
(`INDEX_FLEXION_LIMITS_DEG` y `finger_flexion_limits()` en `toreto_hand.py`).
Se aplica a la cinematica y a la posicion de los topes fisicos de las
bisagras. Corazon, anular, menique y pulgar sin cambios.

Por que uniforme: con la misma escala en las cuatro articulaciones, el nuevo
recorrido del indice es exactamente el tramo 0-90% del de la v7, que se
midio limpio hasta el 91,7% (muestra 11). Lo comprueba una prueba unitaria,
y otra impide subir la escala por encima de lo medido limpio.

Se repiten los cinco escenarios: los topes son geometria presente en toda
postura, y moverlos podria crear contacto con el dedo vecino. Se espera que
la pinza siga lograndose, algo mas tarde en el cierre (el indice avanza mas
despacio en proporcion al pulgar).

Verificado fuera de Fusion: 19/19 pruebas unitarias y el flujo completo en
el Fusion simulado. Informe: `prueba_mano_4_motores_v8.json`.

## v7: RESULTADO en Fusion — 2026-09-26 18:42

`prueba_mano_4_motores_v7.json`. 0 errores del nucleo, 50 apoyos verificados.

- Mano abierta: limpia. La correccion del taladro funciona: desaparece el
  unico choque con mano abierta de la v6 (casquillo/pasador del nudillo 1).
- Rotacion del pulgar sola, flexion del pulgar sola, y corazon+anular+menique
  (postura de senalar): limpios.
- Pinza del boli: LOGRADA. Primer contacto en la muestra 8 (66,7% del
  cierre) entre 07_DEDO_1_FALANGE_4 y 09_PULGAR_FALANGE_3, punta con punta,
  sin ningun otro choque antes. Hueco entre puntas (mm) por muestra:
  77,7 / 68,3 / 58,4 / 48,2 / 38,3 / 29,0 / 18,3 / 7,6 / 0 / 0 / 0 / 5,4 / 11,3.
  measureMinimumDistance funciona con cuerpos temporales. Los 19 pares que
  aparecen despues del contacto son artefacto de la simulacion (la mano real
  se detiene al tocar). No se sabe si el contacto es por la yema o por el
  canto: requiere una vista 3D.
- Indice solo: UN choque, 5,184 mm3, solo en la muestra 12 (cierre total)
  entre 07_DEDO_1_FALANGE_4 y 09_PULGAR_FALANGE_1 en reposo. Limpio hasta
  la muestra 11 (92%). Es el dedo mas cercano al pulgar.

Frente a la v6 (58 pares), queda un unico par real. Sigue sin validar: la
palma principal, holgura continua, resistencia, agarre de objetos y el
mecanismo de tendones. No es una mano funcional validada.

## v7: mano de 4 motores — 2026-09-26, preparada y SIN ejecutar

Estado de partida: la sesion anterior se corto tras la v6 (58 pares, 50
apoyos) con la correccion del taladro escrita pero sin ejecutar, y el script
ya apuntando a un `v7.json` de base compacta. Esa v7 no llego a correr.

Analisis de la v6 por momento del cierre: 55 de 58 pares tienen su peor
choque en las muestras 9-12 (32 en el cierre total); con la mano abierta
solo 1 (0,57 mm3, casquillo central/pasador del nudillo 1 del pulgar, que es
lo que corrige el taladro). El 87% del volumen es pulgar contra falanges
distales de indice y corazon: el ensayo cerraba los cinco dedos a la vez
hasta el final, lo que ninguna mano con pulgar oponible hace sin que el
pulgar entre en los dedos. Recortar material no podia resolverlo.

Decision del usuario: mano adaptativa de CUATRO motores (indice /
corazon+anular+menique / flexion pulgar / rotacion pulgar). La v7 se
redefine: mano abierta; cada motor solo con criterio de cero choques; y la
pinza del boli (pulgar girado enfrente del indice, ambos cierran a la vez).
Detalle en `README.md` y `toreto_motor_validation.py`.

Verificado fuera de Fusion: 14/14 pruebas unitarias; y el flujo completo
ejecutado contra un Fusion simulado con choques inventados (deteccion del
choque del cardan, contacto de pinza al 75%, clasificacion de choques
previos, JSON y resumen). Eso NO valida geometria: solo que el codigo no
fallara por errores de programacion. Sin cambios en centros, ejes, limites,
umbrales ni en el robot original.

## Base compacta del pulgar: ensayos posteriores al commit 37c07de

Se mantienen centros y ejes. Bisagras 1 y 2 del pulgar: radio exterior
3.2 mm, longitud 10 mm, pasador R1.4 mm, holgura radial 0.35 mm,
saliente de pasador 0.25 mm. Pared nominal 1.45 mm, sin validacion de carga.
El enlace intermedio se sustituye por una horquilla de capsulas laterales.
Se comprueba tambien su paso de pasador y sus tres apoyos de casquillos.

v4: rechazada por apoyo insuficiente en casquillo A del nudillo 2.
v5: mismo rechazo; contacto antes/despues 7.805 mm3, umbral 10 mm3.
v6: brazos prolongados hasta 10.2 mm desde la raiz para abarcar mayor
superficie del casquillo. Resultado en `prueba_base_compacta_pulgar_v6.json`.
Los umbrales de continuidad, volumen y apoyo no se han reducido.
Cinco pruebas unitarias de parametros pasan; no validan el funcionamiento.

## 2026-09-26: respaldo y alojamientos del pulgar

Respaldo previo `work/Toreto_respaldo_2026-09-26_dedos_corregidos.zip`:
42 archivos verificados por SHA-256 contra la copia de trabajo.
No es un F3D; contiene fuentes, datos y resultados para reproducir ensayos.

Se extendieron alojamientos a las tres falanges del pulgar sin cambiar
centros ni ejes. `prueba_alojamientos_pulgar_v3.json`: 13 posturas completas,
65 pares con penetracion, 0 errores del nucleo y 47 apoyos verificados.
La base del pulgar y el cierre siguen pendientes. No publicar como funcional.
Original intacto; no se guardo un ensamblaje Fusion porque no fue publicado.

## 2026-09-25: ejes del pulgar, cambio autorizado en variante aislada

Se compararon 52/128 (original), 30/106, 15/91, 0/76 y -15/61 grados de
orientación de ejes, conservando centros y recorridos. La mejor suma de máximos
de intrusión por cuerpo fue 0/76. Se dejó esa constante SOLO en toreto_hand.py
de esta carpeta. No se modificó el generador instalado original ni el robot.

Revisión real en Fusion de 121 posturas por cada uno de 17 cuerpos móviles:
- Falanges 2 y 3: 0 mm³ de intrusión en la palma en las posturas evaluadas.
- Falange 1: máximo 93.571 mm³, ya presente en postura abierta.
- Casquillo A del nudillo 2: máximo 112.522 mm³.
- Otros contactos locales: casquillo central 2 (0.829), casquillo B 2 (64.721),
  pasador 2 (20.144) y casquillo B 3 (4.166 mm³).

La suma de máximos individuales baja de 6549.395 a 295.952 mm³; NO es un volumen
simultáneo ni una medida de resistencia. No están comprobados los pares entre
piezas del pulgar, el contacto con otros dedos, la oposición útil o la holgura
continua entre muestras. No llamar funcional a esta candidata.

Informe: comparacion_ejes_pulgar.json. El ejecutable sigue en modo comparación
y no publica componentes. Pendiente liberar alojamiento proximal conservando
los apoyos, después verificar todos los pares móviles y generar vista de prueba.

## 2026-09-25: diagnóstico con sólidos reales

El barrido acumulado exacto falló por ASM_BAD_CONTAINMENT en falange 1,
muestra 119. Para separar errores acumulativos de interferencias reales se
ejecutaron 121 posturas independientes por cada uno de los 17 cuerpos móviles
del pulgar, siempre contra una copia nueva de la palma original.

La prueba independiente terminó. Máximas intrusiones por falange:
1: 353.578 mm³; 2: 1480.151 mm³; 3: 2484.109 mm³, todas al cierre total.
El casquillo B del nudillo 4 produjo separación de material en muestra 50.
No se han medido tamaños de los fragmentos ni resistencia estructural.
Esto NO prueba viabilidad de un alojamiento acumulado ni holgura continua.

Informe completo: diagnostico_pulgar_exacto.json en esta carpeta.
El ejecutable permanece en modo diagnóstico con retorno obligatorio antes
de crear componentes; no publica una mano no validada. No se guardó Fusion.
Siguiente decisión: autorizar o no cambios de trayectoria/ejes del pulgar
únicamente en la variante aislada, preservando la postura abierta y el robot.

## Tercera iteración: cortes transaccionales y tolerancia acotada

Cada operación de diferencia se ejecuta ahora en una copia temporal de la
palma. Solo se conserva el resultado si Fusion devuelve éxito. Para cajas,
ante error se prueban incrementos de 0.01, 0.025 y 0.05 mm por lado, conservando
la envolvente original y sin omitir muestras. Los controles siguen activos.

Resultado real: superó la primera falange del pulgar, pero se rechazó por
`CORTE RECHAZADO: palma dividida por 09_PULGAR_FALANGE_2 en muestra 19`.
No alcanzó los controles finales de volumen y apoyos ni creó componentes.
Documento de prueba verificado vacío después de cerrar el aviso. No se guardó
Fusion ni se modificó el brazo existente. Las dos pruebas unitarias pasan.

Esta evidencia rechaza la variante actual; no demuestra que una envolvente
más fiel a la falange sea inviable. No aumentar recortes ni ignorar fragmentos.
Próximo paso: evaluar el barrido de la geometría real de las falanges del
pulgar y la continuidad del alojamiento; si exige cambiar ejes o ubicación,
pedir autorización específica antes de modificar el diseño.

## Segunda iteración: envolventes cilíndricas

Se sustituyeron las cajas de los casquillos centrales por dos cilindros
expandidos: cuerpo y tope. Se omite únicamente la repetición del cilindro
coaxial de base, cuyo volumen es invariante bajo su propia rotación.
Se mantuvieron todas las comprobaciones de continuidad, volumen y apoyos.
Dos pruebas unitarias de parámetros pasan; no validan el BRep.

La ejecución alcanzó `09_PULGAR_FALANGE_1`, muestra 35 de 120, donde Fusion
arrojó `ASM_BAD_CONTAINMENT`. Los recortes anteriores, incluidos los cuatro
dedos, pasaron el control de sólido único en cada corte. NO se alcanzó la
validación final de volumen y soportes. NO se generó el componente de salida.
No se guardó Fusion ni se modificaron otros documentos.

Pendiente: resolver la operación de barrido de la primera falange del pulgar
sin omitir muestras fallidas ni reducir los controles; después comprobar
apoyos, todas las interferencias y movimiento real. No transferir al robot.

## Resultado del alojamiento con ejes 0/76 (26-09-2026)

El informe `prueba_alojamiento_0_76.json` confirma 4513 cortes temporales,
94.67406208180364 % de volumen conservado y controles de continuidad y
apoyo superados. Hubo dos reintentos conservadores de +0.01 mm.
Esto no valida resistencia, fabricación ni colisiones internas de la mano.
No se crearon componentes ni se guardó Fusion. El original no se modificó.

Se añadió `toreto_pair_validation.py` para comprobar sólidos de grupos
cinemáticos distintos en 13 posturas de cierre sincronizado. Excluye el
cuerpo principal de palma y solapes dentro del mismo grupo rígido. Los
errores del núcleo geométrico se registran como no resueltos, nunca como
ausencia de colisión. Esta prueba no cubre movimiento independiente de
dedos ni garantiza holgura continua. Compilación y tres pruebas unitarias OK.

## Colisiones internas: variante rechazada (26-09-2026)

Completadas 13 posturas sincronizadas, cero errores del núcleo y 235 pares
de cuerpos de grupos rígidos distintos con penetración superior a 0.01 mm3
en al menos una postura. No son 235 fallos independientes de articulación.
Mayor solape: dedo 1 falange 4 / pulgar falange 2, 1697.014 mm3 en muestra
11/12. También hay invasiones entre casquillos y falanges con la mano abierta
y entre bisagras de dedos vecinos. El ajuste de palma NO resuelve estos fallos.
Informe: `prueba_colisiones_internas.json`.

No publicar ni transferir esta variante. Corregir dimensiones/alojamientos de
bisagras y revisar el cierre del pulgar exige ampliar la reparación geométrica;
no basta con activar juntas. El documento de Fusion sigue vacío y sin guardar.

## Correccion autorizada de bisagras y alojamientos (26-09-2026)

Usuario autoriza corregir dimensiones y alojamientos en la copia de prueba,
conservando la posicion de la mano. Se mantienen centros, ejes y limites de
los cuatro dedos; original e instalacion principal intactos, Fusion sin guardar.

Primera correccion: longitud de bisagras principales 13.5 mm, saliente del
pasador 0.25 mm por extremo; alojamientos cilindricos de holgura 0.35 mm
para casquillos del grupo opuesto. Controles de falange solida unica,
volumen conservado >=65% y apoyo propio >=max(10 mm3,10% inicial).
Informe `prueba_colisiones_alojamientos.json`: 87 pares con penetracion
frente a 235 iniciales, en las mismas 13 posturas, sin errores de nucleo.
40 apoyos de casquillos verificados. Persisten choques del pulgar, puntas
vecinas y contactos falange-falange al final del cierre.

Segunda correccion: separacion longitudinal de extremos principales pasa
de 3.0 a 4.2 mm (punta distal conserva 0.3 mm). El loft de las puntas se
intersecta con su envolvente de ancho/profundidad nominal para impedir
abombamientos laterales excesivos. No se mueve ningun centro de articulacion.
Resultado en `prueba_colisiones_alojamientos_v2.json`.
Prueba terminada: 13 posturas, cero errores del nucleo, 40 apoyos verificados.
74 pares con penetracion; TODOS involucran al pulgar. Ningun par entre los
cuatro dedos principales supera 0.01 mm3 en estas muestras. Esto no prueba
holgura continua, movimientos independientes ni ausencia de choque con palma
(la palma principal se excluye de esta prueba). Pulgar pendiente de correccion.
Los cuatro tests de parametros y la compilacion pasan; no sustituyen CAD.
La validacion anterior de palma con 94.7% NO se puede trasladar a estas
dimensiones sin repetirla. Sigue prohibida la publicacion de la mano como
funcional hasta resolver el pulgar y validar conjunto, movimiento y apoyos.

## Primera iteración: cajas

Estado: RECHAZADA, no funcional ni apta para transferir al robot.

Se ejecutó desde la interfaz de Fusion en un documento nuevo, vacío,
convertido a diseño híbrido. No se guardó ningún documento de Fusion.
No se modificaron los otros documentos abiertos.

Resultado observado:

`RuntimeError: CORTE RECHAZADO: palma dividida por
08_DEDO_1_NUDILLO_1_CASQUILLO_CENTRAL en muestra 17`

El error se produjo en `toreto_clearance.py`, durante el cálculo temporal,
antes de crear el componente de salida. Tras cerrar el aviso se verificó
visualmente que el navegador del documento nuevo continuaba sin componentes.

La envolvente rectangular conservadora elimina demasiado material en esta
prueba. Este resultado no demuestra que una envolvente más ajustada sea viable.
No reducir ni desactivar las comprobaciones de continuidad y soporte para
forzar una salida. Se necesita replantear la holgura y comprobar las conexiones
estructurales, además de validar todo el movimiento antes de cualquier traslado.
