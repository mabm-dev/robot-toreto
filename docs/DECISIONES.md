# Decisiones del proyecto

Registro de decisiones que no se deducen del código ni del CAD, para no depender
de memoria de chat. Se añade una entrada nueva cuando se cierra algo importante;
las anteriores no se editan, solo se marcan como superadas si cambia.

## Orden de trabajo: diseño → componentes → CAD

Tres fases, en este orden, sin saltárselo:

1. **Diseño** — cerrar forma, proporciones y módulos.
2. **Componentes** — elegir batería, servos, motores, LIDAR, cámara y procesador.
3. **CAD y materiales** — medidas definitivas y material pieza a pieza, con los
   componentes ya en la mano.

Ninguna cota es definitiva hasta tener los componentes físicos. Por eso el CAD
va al final, no al principio.

**Estado actual: fase 1 (diseño).**

## Diseñar contra la referencia, no contra el CAD anterior

La imagen de referencia (`docs/referencia_infografia.png` si se añade) es la
especificación, no un punto de partida aproximado. Al iterar el diseño no se
reutiliza geometría de versiones previas — se parte de cero y se compara
directamente contra la referencia.

## Fusion sustituye a OpenSCAD (a partir de fase 3)

OpenSCAD sirve para maquetas visuales rápidas (fase 1), pero el CAD final de
fase 3 se hace en **Autodesk Fusion**, por dos motivos concretos:

- Ensamblaje con **articulaciones reales y topes** — el brazo se arrastra con
  el ratón para validar alcance y colisiones, en vez de escribir ángulos a
  mano y renderizar cada vez.
- El plugin **URDF Exporter** convierte ese ensamblaje en el modelo cinemático
  que consumen ROS 2 y Gazebo.

Stack mínimo del proyecto: Fusion, Bambu Studio, NotebookLM, KiCad o AutoCAD
Electrical, ROS 2 + Gazebo, GitHub.

Impresión: más perímetros antes que más relleno — 4-5 paredes con giroide al
25-30 %, en una Bambu Lab P1S (volumen 256 × 256 × 256 mm).

## IA local o en la nube — cerrada: todo local, Jetson Orin Nano (26 ago 2026)

> **Parcialmente superada el 29 ago 2026** por la entrada
> "[Ordenador de a bordo: ROG Ally X Z2 en bahía extraíble](#ordenador-de-a-bordo-rog-ally-x-z2-en-bahía-extraíble-29-ago-2026)".
> Sigue vigente lo esencial —**todo local, sin nube**—; lo que cambia es
> *qué máquina* lo ejecuta.


Decisión que bloqueaba el resto de la fase 2. Se barajaron tres opciones
(nube con Raspberry Pi 5, mixto con Pi 5 + LIDAR local para el reflejo de
emergencia, y todo local con Jetson) y el usuario eligió **todo local**:

- **Ordenador de a bordo único: NVIDIA Jetson Orin Nano** (Super Developer
  Kit o equivalente — modelo exacto y precio real quedan para la lista de
  compra). No hace falta Raspberry Pi adicional: el Jetson hace de único
  computador de a bordo.
- Funciona sin conexión a internet y responde al instante, tanto para la
  conversación como para la detección de obstáculos/parada de emergencia.
  No se usa Gemini/Google AI Pro para la IA embarcada del robot (sigue
  disponible para todo lo demás del proyecto que ya lo usa).
- Coste más alto que la alternativa nube (~250 € frente a ~80 € de una
  Raspberry Pi, cifras aproximadas de agosto 2026 — verificar en la lista de
  compra real) y más consumo, asumido a cambio de funcionar sin red y sin
  depender de servicio externo.

**Pendiente para cuando se elijan motores/encoders de la base:** decidir si
el control de motores y la parada de emergencia por hardware corren
directamente en el Jetson (Linux, sin tiempo real garantizado) o si conviene
un microcontrolador aparte (Arduino/STM32/ESP32) dedicado a esa parte
crítica — no es lo mismo IA local que control en tiempo real, y el Jetson
resuelve la primera pero no necesariamente la segunda.

## Ordenador de a bordo: ROG Ally X Z2 en bahía extraíble (29 ago 2026)

> **Superada el 1 oct 2026** en cuanto a la ubicación: la Ally va en el
> pecho, a la vista (ver "Ally en el pecho, iPhone en la cabeza"). Sigue
> vigente que es el ordenador de a bordo y todo local.

El usuario **ya tiene** una ASUS ROG Ally X con Ryzen AI Z2 Extreme. Pasa a
ser el ordenador de a bordo, en lugar del Jetson Orin Nano de la entrada
anterior. Lo esencial de aquella decisión no cambia: **todo local, sin
nube**. Cambia la máquina.

**Por qué:** ya está pagada (frente a ~250 € del Jetson), y sus 24 GB de RAM
frente a los 8 GB del Orin Nano dan margen real para un LLM local de
conversación decente. Se pierde el ecosistema NVIDIA (CUDA, TensorRT, Isaac
ROS), que es el estándar de facto en robótica — pero la cámara elegida (tipo
OAK-D) hace su propia inferencia de visión a bordo, que es justo donde ese
ecosistema era imbatible.

**Dónde va: en la BASE, no en el pecho.** Medido contra la geometría real de
`base_exterior_95cm.scad` (no a ojo): alineada con el eje X caben hasta
**300 × 130 × 55 mm**, y sobran unos 80 mm de altura por encima. Los huecos
de rueda están a ±45°/135°/225°, así que los ejes X e Y apuntan a los
espacios *entre* ruedas, donde cabe bastante más que el cilindro central
libre (⌀260 mm). En el pecho solo entraba en una orientación, sin holgura y
ocupándolo entero — además de subir el centro de gravedad ~700 g, que con
base holonómica de mecanum se nota al acelerar.

**Formato: bahía extraíble**, no empotrada. Se desliza dentro de la base con
un único conector USB-C (alimentación + datos) y se saca cuando el usuario
quiera usarla como consola. Se descartó empotrarla permanentemente: es el
componente más caro del robot y perderla como portátil no compensa la
simplificación mecánica.

### Consecuencias abiertas, para no perderlas de vista

1. **La parada de emergencia ya no puede vivir en el ordenador principal.**
   Si el cerebro se puede extraer físicamente, un reflejo de seguridad que
   dependa de él desaparece al sacarlo. Esto convierte el microcontrolador
   dedicado (Arduino/STM32/ESP32) —que la entrada anterior dejaba como
   "quizá"— en prácticamente obligatorio, y con él la pregunta de qué debe
   seguir funcionando con la bahía vacía: ¿el robot queda inerte pero
   seguro, o mantiene movimiento básico?
2. **Térmica y ventilación**: está diseñada para disipar al aire libre, en
   las manos. Dentro de una carcasa cerrada necesita conducto propio, y
   **tiene que salir hacia arriba** (ver cotas confirmadas más abajo: por
   los lados solo quedan ~2 mm, por arriba sobran ~68 mm).
3. **Dos baterías**: la Ally lleva la suya (80 Wh). Puede ser una ventaja
   (dominio eléctrico independiente) o una complicación de gestión. Su
   cargador es de **65 W (20 V / 3,5 A)**, lo que fija un requisito duro
   para la arquitectura de alimentación, todavía sin cerrar: la base tiene
   que poder entregar 65 W por USB-C PD de forma sostenida.
4. **Duplicidades que conviene revisar antes de comprar nada.** La Ally trae
   pantalla táctil de 7" 1080p, altavoces estéreo, matriz de micrófonos con
   cancelación por IA e IMU de 6 ejes. Metida en la base:
   - la **IMU** queda justo donde debe estar la de un robot (`base_link`) —
     ganancia limpia, un componente menos que comprar;
   - la **pantalla, los altavoces y los micrófonos** quedan enterrados e
     inservibles, mientras el diseño de la cabeza prevé comprar *otra*
     pantalla de 7" (Waveshare) y el robot necesitará micro y altavoz en la
     cabeza de todas formas. La duplicidad de pantalla es la más llamativa:
     conviene decidir a conciencia, no por inercia.

### Cotas confirmadas (29 ago 2026)

Ficha oficial aportada por el usuario: **290 × 121 × 27,5–50,9 mm, 715 g**,
batería 80 Wh, cargador 65 W, **dos puertos USB-C** (uno USB4/Thunderbolt 4
con DP 2.1 y PD 3.0; otro USB-C 3.2 Gen2 con DP 2.1 y PD 3.0), Wi-Fi 6E y
Bluetooth 5.2.

Los dos USB-C resuelven el reparto limpiamente: uno para alimentación (PD
desde la batería del robot), otro para el hub de periféricos (LIDAR, cámara
y microcontrolador). No hace falta ningún adaptador extra.

Envolvente libre medida en `base_exterior_95cm.scad`, alineada con el eje X:

| Eje | Aparato | Bahía (+2 mm holgura, +3,2 mm pared) | Límite real | Margen |
|---|---:|---:|---:|---|
| Ancho (X) | 290 mm | 300,4 mm | >320 mm | holgado |
| Fondo (Y) | 121 mm | 131,4 mm | ~134 mm | **~2 mm — crítico** |
| Alto (Z) | 50,9 mm | 61,3 mm | ~130 mm | ~68 mm libres |

**Cabe montada, sin desmontar nada.** El fondo es la cota que manda; el
ancho y el alto sobran. De ahí que la ventilación tenga que ser vertical.

**Nota de método:** es el primer componente físico que existe de verdad en
el proyecto. Por la regla de [orden de trabajo](#orden-de-trabajo-diseño--componentes--cad),
es también la primera restricción interna real, y por tanto lo primero que
empieza a desbloquear la tabla de cotas Z que sigue congelada.

## LIDAR y cámara RGB-D — cerrada (26 ago 2026)

- **LIDAR: RPLIDAR C1** (Slamtec) — 12m de alcance, montado en la base,
  familia con soporte ROS2 oficial (`rplidar_ros`), estándar de facto en
  los tutoriales de Nav2. Se prefirió sobre el A1M8 (más barato, ~8m) por
  el margen de alcance.
- **Cámara: con IA integrada, categoría tipo OAK-D** (Luxonis) — la propia
  cámara procesa parte de la visión (detección, quizás profundidad) antes
  de mandar datos al Jetson, en vez de una RGB-D "tonta" que le pasa todo
  el cómputo crudo al Jetson. Modelo exacto pendiente de la lista de compra.
- Se comprobaron dos cámaras que el usuario ya tenía (Tapo C411, Tapo C230)
  y una Insta360 Ace Pro 2 — ninguna sirve: sin sensor de profundidad
  ninguna de las tres, y además la Tapo depende de wifi/nube propietaria y
  la Ace Pro 2 es una cámara de acción sin salida de vídeo en vivo de baja
  latencia. Hace falta comprar una cámara nueva.

## Mano: adaptativa de cuatro motores (26 sept 2026)

La mano tiene que coger como una humana: un boli con **pulgar e índice**, una
pelota pequeña, un vaso, y en general cualquier objeto dentro de su límite
de carga (300-500 g).

- **Un motor rígido para toda la mano no sirve**: solo tiene una postura
  cerrada, válida para un único tamaño de objeto.
- **Tres motores** (cuatro dedos juntos + flexión y rotación del pulgar)
  coge vaso y pelota, pero el boli lo tomaría con pulgar, índice y corazón a
  la vez: es la pinza de *escribir*, no la de *coger* un objeto pequeño.
- **Cuatro motores**, que es lo elegido:

  | Motor | Mueve |
  |---|---|
  | Índice | sus 4 articulaciones |
  | Corazón + anular + meñique | juntos |
  | Flexión del pulgar | sus 3 articulaciones de flexión |
  | Rotación del pulgar | el cardán de la base: lo pone enfrente o al lado del índice |

  El índice independiente permite además **señalar**, que en un robot
  asistente que conversa con personas es comunicación, no un extra.

**Adaptativa** quiere decir que cada motor tira de tendones que recorren los
dedos, con muelles de retorno: si un dedo toca el objeto se detiene y los
demás siguen cerrando hasta tocar también. Así un mismo motor se amolda a un
vaso o a una pelota sin programar cada agarre. Los motores irían en el
antebrazo, no en la palma, para que la mano pese poco (es la solución del
humanoide de código abierto InMoov, impreso en 3D).

**Qué queda sin decidir, a propósito:** los motores concretos (modelo, par,
peso) son componente de fase 2 y siguen pendientes. Con su peso se podrán
dimensionar por fin los servos de hombro y codo, que esperaban a saber
cuánto pesa la mano.

**Consecuencias en el CAD:**

- El modelo ya tenía las 20 articulaciones repartibles en esos cuatro grupos,
  incluida la rotación del pulgar (el cardán). No hacen falta articulaciones
  nuevas.
- Faltan piezas que el diseño no tiene todavía: canales de tendón dentro de
  las falanges, anclajes y muelles de retorno.
- **El ensayo de colisiones cambia.** Hasta la v6 se cerraban los cinco dedos
  a la vez hasta el final, y el análisis mostró que 55 de los 58 choques que
  quedaban estaban en ese tramo final, el 87% del volumen pulgar contra las
  puntas de índice y corazón. Ninguna mano con pulgar oponible puede cerrar
  así sin que el pulgar acabe dentro de los dedos: por eso recortar material
  no convergía, y cada intento acababa partiendo una pieza. La v7 prueba en su
  lugar cada motor por separado (criterio: cero choques) y la pinza del boli.
  Detalle en `work/Toreto_Prueba_Holguras_01_44/`.

**Cómo debe tocar la pinza del boli (26 sept 2026, tras verla en 3D):** el
**pulgar** debe apoyar con la **cara plana de su última falange**, no con la
punta curva: la curva deja poca superficie y el boli gira o resbala. Hoy
(v8) toca de punta, contra la cara interior de la última falange del
índice. **El índice está bien así** y no se cambia. Además, las caras de
agarre serán **rugosas o con textura** para mejorar la sujeción. Cambiar la
postura del pulgar exige un ensayo nuevo; no se ha tocado todavía.

**Pinza del boli aceptada (27 sept 2026): pinza lateral.** Ensayo v10b con
sólidos: cardán girado del todo, índice y flexión del pulgar cerrando 1:0,26,
sin tocar geometría ni relaciones. Primer contacto con el índice al 78% y el
pulgar al 20%, sin ningún choque antes. El pulgar apoya con su **cara plana
palmar** (centro de la falange); el índice pone la **esquina redondeada de
su punta** (costado/cara interior), y entre ambos queda una V de unos
20-30°. Vista en 3D y aceptada por el usuario tal cual. Las yemas blandas y
rugosas ayudarán a rellenar la V. Apoyo plano contra plano descartado por
ahora: con los ejes actuales del pulgar siempre queda desalineación.

## Brazo: codo de un solo eje con pieza de enlace (27 sept 2026)

El codo tiene **un único eje de giro**, en el centro de una pieza negra de
enlace. Esa pieza va fijada a la carcasa del brazo y a la del antebrazo (los
dos círculos pequeños de la lámina son sus fijaciones, no dos ejes) y las
separa para que no choquen al doblar. Lo aclaró el usuario sobre el render
de referencia.

Medición del brazo sobre la lámina frente al brazo de prueba (el de
`work/Toreto_Prueba_Holguras_01_44/`): el codo coincide (5 mm), pero el
hombro está 67 mm desplazado y la muñeca 93 mm, porque el generador toma
longitudes y postura de la vista frontal. Detalle y cotas en
`work/Toreto_Prueba_Holguras_01_44/medicion_brazo/MEDICION_BRAZO_LAMINA.md`.

## Identidad visual: CAD 3D interactivo (23 ago 2026)

Estándar de documentación técnica para todo el material visual del proyecto:

- Visores 3D interactivos en Three.js (materiales PBR, `OrbitControls`,
  iluminación de estudio de 3 puntos, sombras dinámicas) en vez de dibujos
  estáticos.
- Láminas en layout Bento Grid, modo oscuro.
- Vistas 2D solo como proyecciones ortogonales normalizadas (con cotas y
  líneas de centros) — no como icono decorativo.

Estándar fijado en las skills `toreto-cad-visual-identity` y
`toreto-mechanical-tokens` (`.claude/skills/`). Esta última es explícita en
no inventar datos: remite a `docs/CINEMATICA.md` y a este archivo como única
fuente de verdad, y dejar como `TBD` lo que dependa de componentes aún no
elegidos (fase 2).

La primera lámina 3D bajo este estándar es un **proxy geométrico** basado en
las cotas ya conocidas (altura 950 mm, base ⌀400 mm, torso_h 228 mm, waist_h
202 mm) — no es el modelo real de Fusion, que llega en fase 3.

## Base: 4 ruedas mecanum (23 ago 2026)

La base móvil usa **4 ruedas mecanum en disposición rectangular**, holonómica
(traslación en cualquier dirección y giro sobre su eje sin necesidad de
orientar las ruedas). Altura (95 cm) y el resto de medidas generales no
cambian.

Actualizado: `README.md`, `docs/CINEMATICA.md` (nodos `wheel_fl/fr/rl/rr`).

**Confirmado el 29 sept 2026:** el render 3D dibuja ruedas omnidireccionales
de doble fila, pero se mantienen **mecanum** (lo que dibuja el lienzo y lo
que da movimiento lateral con las cuatro ruedas paralelas), con el
**aspecto del render**: rodillos más gruesos y juntos, tapa negra con luz.

## Brazo: requisitos de movimiento y fuerza (30 sept 2026)

- **Juntar las manos delante del pecho.** Con un solo eje en el hombro y otro
  en el codo cada brazo se mueve en su propio plano vertical (separados unos
  400 mm) y las manos nunca se acercan. Por eso el brazo lleva **hombro 2
  (subir/bajar + rotación del brazo sobre su eje) + codo 1 + muñeca 2**; con
  el codo a 90° y el brazo girado, antebrazo (164 mm) y mano (~90) llegan al
  centro. Pendiente comprobar en el modelo que al plegarlos no chocan con el
  pecho.
- **Carga: 1 kg por mano, también con el brazo estirado** (el usuario
  descartó rebajarlo a 0,5 kg estirado: "es muy poco").
- **Coste:** los actuadores comerciales (2.000-4.000 € los dos brazos) son
  demasiado caros. Vía elegida: **reductoras impresas en la P1S** (cicloidal
  en hombro y rotación del brazo, NEMA17 + TMC2209), servos baratos en la
  muñeca y micromotores con tendones en la mano; objetivo ~300 € los dos
  brazos. Motores del hombro dentro del pecho y el del codo cerca del
  hombro para aligerar el brazo. Primero un prototipo del hombro que
  demuestre 15 N·m; si aguanta, se repite en el resto.
- **Par mínimo por articulación** (brazo estirado en horizontal con 1 kg,
  margen ×2). Masas SUPUESTAS hasta elegir piezas: brazo con motor de codo
  0,6 kg, antebrazo con motores de muñeca y mano 0,8 kg, mano 0,25 kg;
  largos del modelo: hombro-codo 157 mm, codo-fin del antebrazo 164 mm.

  | Articulación | Par estático | Mínimo con margen |
  |---|---|---|
  | Hombro subir/bajar | ~7,2 N·m | **~15 N·m** |
  | Hombro rotación del brazo (codo a 90°) | ~3,6 N·m | ~7 N·m |
  | Codo | ~3,6 N·m | ~7 N·m |
  | Muñeca | ~0,9 N·m | ~2 N·m |

  Recalcular con las masas reales en cuanto se elijan los motores. Aligerar
  el antebrazo (motores de la mano cerca del codo) es lo que más baja el par
  del hombro. La carga adelanta el centro de masas: comprobar el equilibrio
  con el brazo estirado y 1 kg.

## Ally en el pecho, iPhone en la cabeza (1 oct 2026)

**Decidido** tras revisarlo con la maqueta `Toreto_Maqueta_Ally_Pecho`
1.2.2 (todo cabe; los choques que quedan son de cómo se dibujaron las zonas
reservadas). **Sustituye** a "Ordenador de a bordo: … bahía extraíble en la
base": la Ally ya no va en la base. **Cabeza ~15 mm más alta** (160 → 175)
para que el giro del iPhone (156 mm) no asome por los cantos. El usuario
acepta que el robot pase de 950 a **~965 mm**; el cuello no se acorta.

- **ROG Xbox Ally X en el pecho, a la vista** (pantalla táctil y mandos
  usables desde fuera, aire retro). Pecho ensanchado de 252 a 321 mm hacia
  el hueco de los discos del hombro, con un aro negro fino; los brazos no
  se mueven. Ventilación de la Ally: toma aire por los lados y lo expulsa
  por arriba (análisis de MuyComputer, 15-10-2025).
- **iPhone 12 Pro Max en la cabeza con giro tipo libro** (eje en su borde
  largo, guías en semicírculo, servo pequeño): modo cara (pantalla al
  frente, cámara TrueDepth) y modo visión (3 cámaras + LiDAR al frente, sin
  recortes de visión). Las cámaras no se pueden separar ni alargar del
  iPhone (emparejamiento de piezas y calibración de fábrica).
- Ahorro seguro ~100-170 € (pantalla de cabeza, micrófonos, altavoz); la
  OAK-D sigue prevista hasta probar el iPhone en modo visión.
- Resuelto: la cabeza (160 mm) era justa para los 156 mm del giro y los
  cantos dejaban asomar el iPhone 2-5 mm; se hace ~15 mm más alta.
- Puertos de la Ally (2 × USB4, jack) y botón de encendido con huella:
  **borde superior, a la izquierda** vista de frente. Hueco de cables
  reservado ahí (fuera del bloque del cuello). Pecho a 327 mm para dejar
  10 mm de aire a cada lado de la Ally.
- **Encendido por software, sin pulsador mecánico** (podría pulsar o
  dañar el botón con las vibraciones). La Ally queda en reposo moderno y la
  despierta el microcontrolador de seguridad haciendo de teclado USB
  (activar "permitir que este dispositivo reactive el equipo" en el
  Administrador de dispositivos). **Wake-on-WLAN descartado:** el reposo
  moderno no responde al paquete de despertar por red. Desde apagada solo
  serviría cortar y devolver la corriente del USB-C si la Ally arranca sola
  al recibirla (pendiente de comprobar); si no, no apagarla nunca del todo.
  Configuración: en el dispositivo HID del microcontrolador y en los
  concentradores raíz USB, permitir reactivar el equipo y NO permitir
  apagarlos para ahorrar energía; suspensión selectiva de USB desactivada
  (con `powercfg` si está oculta). El microcontrolador se alimenta de la
  batería del robot, no del USB de la Ally, para poder despertarla aunque
  el puerto quede sin corriente.

## Batería: LiFePO4 24 V ~384 Wh en la base, 5 h de uso (1 oct 2026)

- **Requisito del usuario: 5 horas de uso continuo** sin cargar.
- Consumo estimado (a medir con los motores reales): ~60-70 W de media
  (Ally ~20 W, iPhone ~5 W, ruedas ~10 W, brazos ~10-20 W, cuello y
  cintura ~3 W, LIDAR + OAK-D + electrónica ~8 W, pérdidas ~10 %); picos de
  ~250-300 W. La Ally (80 Wh) y el iPhone (~14 Wh) llevan su propia batería
  y siguen vivos un rato si se agota la del robot.
- **Batería: LiFePO4 de 24 V, ~15 Ah (~384 Wh)**, ~4-5 kg, con BMS. Elegida
  frente a Li-ion por seguridad en casa (no arde) y vida útil (2.000-4.000
  ciclos). 24 V es la tensión de los motores y drivers.
- **Va en la base**, libre desde que la Ally pasó al pecho: el peso abajo
  compensa la Ally en el pecho y el kilo en la mano.
- Acompañan: fusible, interruptor general y seta de emergencia que corta
  los motores; convertidor 24 V → USB-C PD 65-100 W para la Ally;
  convertidor 24 V → 5 V para el microcontrolador y el iPhone; cargador
  LiFePO4 de 24 V.
- **Carga a mano** por ahora: conector de carga en la parte trasera de la
  base, junto al interruptor general (tipo aviación GX16 o XT60, para los
  ~5 A del cargador). Comprar la batería solo tras comprobar sus medidas
  contra el hueco del chasis (~246 × 410 × 69 mm; la altura es lo justo).
- **Sitio reservado para una base de carga automática futura:** dos
  contactos de muelle en la parte trasera e inferior de la base, a
  ~40-60 mm del suelo, con su cableado previsto hasta la batería. Se añaden
  sin rehacer la base cuando la navegación sepa volver a la estación.

## Cables y calor: requisitos (1 oct 2026)

- **Bus CAN** para todos los motores: cada brazo baja a 4 hilos (24 V, GND,
  CAN-H, CAN-L) que pasan **por dentro del eje del hombro, hueco (Ø10-12)**.
- **Canal central** de ~60 × 60 mm de arriba abajo del pecho, con la
  **columna de aluminio 2020** que sube desde la base y lleva el mazo de
  cables hacia la cintura y el cuello. Nada puede ocuparlo.
- **Aire:** entrada por rejillas en los costados del pecho (≥10 mm entre la
  Ally y la pared), salida por rejillas en el techo del pecho a los lados
  del cuello; rejilla trasera en la cabeza para el iPhone; el cuello no
  debe meter en la cabeza el aire caliente del pecho.
- Calor estimado en el pecho, peor caso: ~45-55 W (Ally 35 W + motores del
  hombro). Los drivers bajan la corriente con el brazo quieto.
- **Siguientes temas:** límites de giro de cada articulación y baterías
  (Ally + iPhone + motores; primera estimación 300-500 Wh).

## Hombro: unión pecho-brazo con discos apilados (29 sept 2026)

El lienzo dibuja la unión del hombro como **discos negros apilados** y el
render como un solo cilindro. Se sigue el **lienzo**: el usuario lo prefiere
porque varios discos grandes reparten mejor el peso del brazo. Lo que sí se
toma del render y de la vista lateral de la lámina: la parte alta del brazo
es una cápsula blanca redondeada con un **disco negro grande** en la cara
exterior (hoy es un bloque con un medio disco).

## Fuente maestra de cotas: lámina de 4 vistas calibrada (26 ago 2026)

`cad-toreto/toreto_fusion_95cm/reference/lamina_maestra_4vistas.jpg` es la
fuente única para dimensionar el exterior de 95 cm — frontal, lateral
derecho, posterior y lateral izquierdo, cada uno calibrado de forma
independiente contra la silueta real del robot en esa vista (no contra una
caja de recorte), a 0,5 mm/px exactos entre Z=0 (suelo) y Z=950 mm
(coronilla).

El generador (`tools/prepare_fusion_canvases.py`) valida su propia salida:
si alguna vista no cae dentro de Z=0–950 mm con menos de 3 px de margen, el
script falla en vez de escribir un lienzo mal calibrado.

Con esta fuente ya fiable, el siguiente paso es medir sobre el lienzo
frontal (maestro) las separaciones Z reales de cada módulo, y usar esa
tabla única para corregir los add-ins de Fusion y los módulos OpenSCAD de
`toreto_exterior_95cm`, que hoy no coinciden entre sí en cómo reparten los
950 mm.

## La tabla de cotas Z no se fija todavía (26 ago 2026)

La medición sobre el lienzo frontal ya está hecha —
`tools/measure_z_boundaries.py` genera la regla de píxeles reproducible,
lectura completa en `docs/CUADERNO.md`— pero el usuario decidió **no
fijarla como tabla única todavía**: dónde caen los cortes reales de
tronco/cintura/pecho depende de dónde queden la batería y los mecanismos
internos, y eso es fase 2 (componentes), no fase 1 (silueta exterior). Fijar
la tabla solo con la silueta de fuera sería inventar una cota que luego
puede no tener sitio por dentro — exactamente lo que la regla de
[orden de trabajo](#orden-de-trabajo-diseño--componentes--cad) quiere evitar.

Los 10 add-ins de Fusion y los 5 módulos OpenSCAD siguen, por tanto, con sus
valores por defecto actuales (no coincidentes entre sí) hasta que haya
componentes elegidos y la tabla se pueda fijar con conocimiento de qué va
dentro de cada módulo.

## Documentos vivos (fuera de este repo)

Se publican como artefactos porque se consultan desde la tablet. Al
actualizarlos, republicar sobre la misma URL, no crear uno nuevo:

- [Índice del proyecto](https://claude.ai/code/artifact/3c1e9e5f-cfa8-4d47-8dd7-55fb1f6f150b)
- [Lámina de diseño](https://claude.ai/code/artifact/774ba526-7714-4aee-aeff-1aad35ca3a55)
- [Stack de herramientas](https://claude.ai/code/artifact/6abfaa55-f3db-4c18-a0bd-476af38d9d59)
