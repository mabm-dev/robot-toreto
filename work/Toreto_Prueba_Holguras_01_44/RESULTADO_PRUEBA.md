# Prueba en Fusion — 2026-09-24

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
