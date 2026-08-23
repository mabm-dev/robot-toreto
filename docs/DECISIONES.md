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

## `cad-toreto-gpt` queda descartada (23 ago 2026)

Existió una rama paralela del proyecto, `cad-toreto-gpt/` (no versionada en
este repositorio), con un robot funcional de 65 cm y componentes ya elegidos
(servo FEETECH ST-3215-C018, controlador Waveshare ESP32, motores JGB37-520,
ruedas mecanum). Se llevó en otro hilo de trabajo, sin relación con este
repositorio.

El 23 de agosto de 2026 se decidió explícitamente que **no** es el proyecto
real. `cad-toreto/` (95 cm) es la línea activa. No se adoptan los componentes,
medidas ni arquitectura eléctrica de la rama descartada.

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

## Documentos vivos (fuera de este repo)

Se publican como artefactos porque se consultan desde la tablet. Al
actualizarlos, republicar sobre la misma URL, no crear uno nuevo:

- [Índice del proyecto](https://claude.ai/code/artifact/3c1e9e5f-cfa8-4d47-8dd7-55fb1f6f150b)
- [Lámina de diseño](https://claude.ai/code/artifact/774ba526-7714-4aee-aeff-1aad35ca3a55)
- [Stack de herramientas](https://claude.ai/code/artifact/6abfaa55-f3db-4c18-a0bd-476af38d9d59)
