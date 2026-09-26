# Continuidad del proyecto Toreto — 26 de septiembre de 2026

> **Documento de relevo. Leerlo entero antes de tocar nada.**
> Sustituye a la versión del 13 de septiembre, que mandaba trabajar sobre el
> documento abierto en Fusion y reparar la mano con parches sucesivos. Ese
> método se abandonó: produjo unas 38 versiones sin converger.

## 1. Dónde estamos

- **La mano funciona en el ensayo de colisiones por primera vez.** Mano
  adaptativa de cuatro motores; la v8 salió *todo limpio y pinza del boli
  lograda*. Guardada en GitHub (commit `4eab5e7`).
- **No es una mano validada.** Faltan palma, holgura continua, resistencia,
  agarre de objetos, tendones, y comprobar si la pinza toca por la yema.
- **Lo siguiente que pidió el usuario: ver la pinza en 3D** (sección 5.1).
- La fase 2 (componentes) sigue casi toda abierta: sección 6.

## 2. Cómo trabajamos — el método que ha funcionado

Esto es lo más importante del documento. La v7 y la v8 salieron bien a la
primera en Fusion tras un mes de intentos fallidos, y fue por el método.

1. **Plan antes de actuar.** Explicar qué se va a hacer, en qué archivo y
   por qué, y esperar el "sí" del usuario. Lo pidió literalmente: *"antes
   de hacer nada dime qué harías"*.
2. **Diagnosticar en los datos antes de parchear.** Si algo no converge,
   parar y analizar el resultado (qué pares chocan, en qué muestra, cuánto),
   no proponer otro parche. Así se vio que el ensayo antiguo exigía algo
   imposible (sección 3).
3. **Validar fuera de Fusion antes de pedir una ejecución.** Pruebas
   unitarias y, si el flujo es nuevo o cambia, `simular_sin_fusion.py`, que
   recorre el ensayo entero con un Fusion falso. Cada ejecución en Fusion es
   tiempo real del usuario; una que falla por un error de programación es
   una ejecución tirada.
4. **Cambios pequeños, justificados con datos ya medidos, uno por
   ejecución.** Ejemplo: el índice al 90% de recorrido, porque ese tramo ya
   lo había medido limpio la v7.
5. **Aislamiento total.** El ensayo solo corre en un documento de Fusion
   vacío (se niega si hay cuerpos), trabaja con sólidos temporales, no
   publica nada y no toca el robot original.
6. **Decir lo que no se ha comprobado.** Un error del núcleo geométrico
   nunca cuenta como "sin choque". No llamar "funcional" a nada que no se
   haya validado. Cada informe lista lo que queda fuera.
7. **El usuario ejecuta en Fusion; Claude lee el JSON.** No controlar la
   interfaz de Fusion. Sí se puede capturar su ventana en modo solo lectura
   si el usuario pide revisar su estado.
8. **Documentar cada resultado el mismo día:** `RESULTADO_PRUEBA.md`
   (cronología), README de la prueba, `docs/DECISIONES.md` y
   `docs/ROADMAP.md` para decisiones, `docs/CUADERNO.md` (privado) para la
   trastienda.
9. **Git:** commits sin línea de co-autor (regla general del usuario);
   `git add` con rutas explícitas; push solo cuando el usuario lo pide.
10. **Componentes antes que mecánica** (regla del proyecto, `DECISIONES.md`).
    La mano no convergía en parte por diseñar bisagras y holguras sin saber
    qué iba a mover los dedos.

## 3. La mano: decisión, resultado y por qué ahora sí

**Decisión (26 sept, en `docs/DECISIONES.md`):** mano adaptativa de cuatro
motores, con tendones y muelles de retorno, motores en el antebrazo. El
usuario quiere agarres humanos: boli con pulgar e índice, pelota pequeña,
vaso, cualquier objeto dentro de 300-500 g.

| Motor | Articulaciones |
|---|---|
| Índice | `JUNTA_DEDO_1_1..4` (`DEDO_1` es el índice: base a 55 mm del pulgar) |
| Corazón + anular + meñique | `JUNTA_DEDO_2..4_1..4` |
| Flexión del pulgar | `JUNTA_PULGAR_2..4` |
| Rotación del pulgar | `JUNTA_PULGAR_1` (el cardán) |

**Por qué no convergía antes:** el ensayo cerraba los cinco dedos a la vez
hasta el final. En la v6, 55 de 58 choques estaban en el tramo final y el
87% del volumen era pulgar contra puntas. Ninguna mano con pulgar oponible
cierra así sin que el pulgar entre en los dedos; recortar material no podía
resolverlo.

**Ensayo actual (desde la v7):** mano abierta; cada motor solo, con criterio
de cero choques; y la pinza del boli.

| | v6 | v7 | v8 |
|---|---|---|---|
| Pares en colisión | 58 | 1 | **0** |
| Pinza del boli | — | al 67% | **al 83%, punta con punta** |

La v7 incluyó la corrección del taladro que dejó sin probar la sesión
anterior (limpió la mano abierta). La v8 bajó el recorrido del índice al
90% (54/54/45/36° en vez de 60/60/50/40), en cinemática y en topes físicos.

## 4. Archivos y cómo ejecutar

Todo en `work/Toreto_Prueba_Holguras_01_44/` (versionada en git):

- `toreto_hand.py` — generador de la mano. Límites: `MAIN_FLEXION_LIMITS_DEG`,
  `INDEX_FLEXION_LIMITS_DEG`, `THUMB_FLEXION_LIMITS_DEG`, `finger_flexion_limits()`.
- `toreto_motor_groups.py` — reparto de motores y escenarios. Sin Fusion.
- `toreto_motor_validation.py` — el ensayo.
- `Toreto_Prueba_Holguras_01_44.py` — script de Fusion. Hoy escribe
  `prueba_mano_4_motores_v8.json`: **cambiar a v9 en la próxima ejecución**.
- `test_clearance.py`, `test_motor_groups.py` — 19 pruebas.
- `simular_sin_fusion.py` — el ensayo con un Fusion falso.
- `RESULTADO_PRUEBA.md` — cronología de todos los ensayos, con rechazos.

**Ejecutar en Fusion:** en un documento **vacío**, Utilidades > Complementos >
`Toreto_Prueba_Holguras_01_44` > Ejecutar. Este script está registrado
apuntando a esa carpeta del repo: los cambios se ven sin copiar nada.

**Pruebas:** desde esa carpeta, `python -m unittest discover -s . -p "test_*.py" -v`
**Simulación:** `python simular_sin_fusion.py`

## 5. Pendiente de la mano, en orden

1. **Ver la pinza en 3D (lo siguiente).** Hay que publicar la mano en el
   documento de prueba. Antes, dos correcciones en el código de publicación
   (el tramo tras el `return` del script principal):
   - `create_digit_motion_links()` enlaza el cardán (`JUNTA_PULGAR_1`) con la
     flexión del pulgar. Eso era la mano de un motor. Con cuatro, el cardán
     va suelto y la flexión tiene como maestra `JUNTA_PULGAR_2`. Si se
     quiere, enlazar también los dedos 3 y 4 al 2 (un solo motor). El
     control de "15 relaciones" cambia.
   - Ese tramo llama a `clearance.repair()`, el recorte de la palma que
     falló repetidamente en septiembre y no está validado con las medidas
     actuales. Para visualizar, publicar sin él y marcarlo como no validado.
   - Mantener: solo documento vacío, nunca el robot original.
   Objetivo: ver si pulgar e índice se tocan por la yema o por el canto.
2. **Prueba de la palma** (`06_PALMA_Y_CONECTOR`, hoy excluida). Primero
   medir, como diagnóstico, cuánto invade cada motor la palma; recortar solo
   después, y con los controles de siempre.
3. **Agarres con objeto simulado:** vaso y pelota, deteniendo cada dedo al
   tocar el objeto (es lo que hace una mano adaptativa).
4. **Canales de tendón, anclajes y muelles de retorno.** El diseño no los
   tiene todavía.
5. **Holgura continua** entre posturas y **resistencia.** Pasadores y
   paredes: ¿el pasador de 2,8 mm será impreso o metálico? Impreso es frágil.
6. **Trasladar la mano al robot real** (`00_Toreto_Ensamblaje_95cm`), solo
   cuando esté validada.

## 6. Pendiente del resto del proyecto

**Plan general del usuario:** (1) la forma igual que los lienzos en Fusion;
(2) decidir qué mecanismos llevan y dónde; (3) agrandar o reducir según las
piezas, manteniendo la forma.

**Fase 2 — componentes** (`docs/ROADMAP.md`, v0.2):
- Los **4 motores concretos de la mano** — con su peso se dimensionan
  hombro y codo.
- Servos de hombro y codo; resto de servos del brazo; cuello de 2 DOF.
- Motores y encoders de la base (4 ruedas mecanum).
- Batería y alimentación. Requisito duro: **65 W por USB-C PD** para la Ally.
- **Microcontrolador de seguridad**: casi obligatorio, porque el ordenador
  principal (la Ally) es extraíble.
- Lista de compra con precios reales.

**Ya decidido:** todo local sin nube; ordenador de a bordo ROG Ally X Z2
(ya en propiedad) en bahía extraíble; RPLIDAR C1; cámara con IA integrada
tipo OAK-D; mano de 4 motores.

**Acordado en conversación, sin documentar todavía:**
- **Cara con el iPhone 12 Pro Max** del usuario (tiene el cable), con una
  **app iOS** que se conecta a la Ally y dibuja la cara. Un iPhone no acepta
  vídeo de entrada: hace falta la app. Su LiDAR no sustituye a la cámara.
- **Dónde va la Ally: reabierto.** `DECISIONES.md` dice base. El usuario
  prefirió el pecho, pero la lámina mide la carcasa del pecho en ~252 mm y
  la bahía necesita ~300 mm: no cabe sin cambiar la silueta. Se decide en el
  paso 2 del plan general.

## 7. Por rectificar (inconsistencias conocidas)

1. `docs/CINEMATICA.md` describe una "pinza de 3 dedos" prismática. Debe ser
   la mano de 5 dedos: 16 articulaciones de dedo + 4 de pulgar, 4 motores.
2. `docs/DECISIONES.md`:
   - documentar la cara con iPhone y la app iOS;
   - marcar como reabierta la ubicación de la Ally;
   - la entrada "La tabla de cotas Z no se fija todavía" choca con que los
     parámetros de Fusion ya se ajustaron a la lámina el 29 ago
     (`218b933`): aclarar que la forma exterior ya sigue la lámina y que lo
     pendiente son los ajustes por componentes.
3. `docs/ROADMAP.md` v0.3 no refleja el trabajo de septiembre (brazos,
   manos, cabeza, base y ruedas alineados con los lienzos: unos 22 commits).
4. **7 carpetas de scripts fallidos sin commitear** en
   `cad-toreto/toreto_fusion_95cm/fusion_scripts/`: `Toreto_*_01_38` a
   `01_43` y `Toreto_Reparar_Mano_95cm`. Decidir si se archivan en git como
   historial o se borran. En total hay 22 add-ins; conviene ordenarlos.
5. Los **5 módulos OpenSCAD** de `toreto_exterior_95cm` no se alinearon con
   la lámina (solo Fusion). Según `DECISIONES.md` Fusion sustituye a
   OpenSCAD: decidir si se actualizan o se marcan como históricos.
6. **Add-ins duplicados** entre el repo y
   `%APPDATA%\Autodesk\Autodesk Fusion 360\API\Scripts\`, sincronizados a
   mano. Solución: registrarlos en Fusion apuntando a la carpeta del repo,
   como ya pasa con `Toreto_Prueba_Holguras_01_44`.
7. La **captura de "forma aprobada"** del 13 sept vivía en `%TEMP%` y se
   perdió. Buscar otra copia.

## 8. Trampas conocidas

- **La carpeta buena es `C:\Users\tarif\Desktop\Robot-Toreto\cad-toreto`.**
  Hay dos hermanas que NO son el proyecto: `cad-toreto-gpt` (rama de 65 cm
  descartada) y `C:\Users\tarif\Desktop\cad-toreto` (taller de Codex del 5
  sept; sus lienzos son idénticos, pero no manda).
- **No guardar nada importante en `%TEMP%`**: ya se perdieron así la lámina
  (recuperada) y la captura de forma aprobada.
- `.gitignore` ignora `work/*` salvo `work/Toreto_Prueba_Holguras_01_44/`.
  Si se crea otra carpeta de trabajo que haya que versionar, añadir su
  excepción: si no, sus archivos nuevos serán invisibles para git.
- En este proyecto trabaja en paralelo **otra IA (Codex)**, con commits en
  inglés a nombre del usuario. Antes de empezar, revisar `git log` y
  `git status`: puede haber cambios nuevos o archivos modificados en disco.
- El documento de Fusion de pruebas se llama `Sin título` y debe estar
  **vacío**. No se guarda.

## 9. Lo subido a GitHub en este periodo

- **26 ago:** lámina calibrada; herramienta de medición de cotas Z; fix del
  add-in de referencias; README al día; STL de 26 MB a Git LFS (reescribió
  el historial); IA todo local; RPLIDAR C1 + cámara tipo OAK-D;
  transformación de lienzos por plano.
- **29 ago:** Ally X Z2 en bahía extraíble, con cotas confirmadas;
  `measure_silhouette.py`; parámetros de Fusion ajustados a la lámina;
  perfiles exactos (`extract_profiles.py` y add-in `Toreto_Perfiles_95cm`).
- **30 ago – 7 sept (Codex):** parámetros maestros sincronizados; pecho;
  palma y manos; brazos, cabeza, base y ruedas alineados con los lienzos.
- **26 sept:** `37c07de`, punto de control de la reparación de la mano
  (Codex); `4eab5e7`, mano de 4 motores v7/v8, decisión documentada y
  `.gitignore`; y este documento con `simular_sin_fusion.py`.
