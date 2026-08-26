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

## IA local o en la nube — pendiente

Decisión abierta que bloquea la fase 2 (hay que cerrarla antes de comprar el
ordenador de a bordo):

- **Nube** (Gemini, vía Google AI Pro): basta una Raspberry Pi 5 — más barata
  y con menos consumo, pero exige internet y añade latencia de red.
- **Local**: hace falta un Jetson Orin Nano — más caro y con más consumo,
  pero funciona sin conexión y responde al instante.

Recomendación de partida: mixto — local lo crítico e inmediato (detección de
obstáculos, parada de emergencia), en la nube lo que tolera medio segundo
(conversación).

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
