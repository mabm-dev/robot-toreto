# Continuidad del proyecto Toreto — 29 de septiembre de 2026

## 0. AL RETOMAR (29 sept): lo primero

**EJECUTADO (29 sept): cuello–pecho como en el lienzo.** Pecho 25 cuerpos
(Z 540–737,8), cuello 3 cuerpos; modo `alturas` sin cambios (pecho→cuello
−7,86). Revisado: interior cerrado; el anillo de la cabeza no se ve.
Pecho 2.8.0 EJECUTADO: tapa negra que rellena el rebaje hasta Z 722 y disco
de 97 mm en 722-730 (forma del render 3D; el render vale para forma, no
para medidas).
**EJECUTADO: Pecho 2.9.0 + Cintura 2.0.0 + Tronco 1.4.0** (tronco 7
cuerpos, cintura 11, pecho 25 en Z 520–737,8; alturas: tronco→cintura
−36,04 y cintura→pecho −20,02, como se esperaba). Revisión visual: el
tronco hueco se veía por la silla (mismo fallo que el pecho).
**Cabeza 4.1.2 EJECUTADA y aceptada** (13 cuerpos; los ojos serán dibujo de
la pantalla, no importa que asomen 1,2 mm): el visor
plano sobresalía como una losa (el frente es curvo: a 107 mm del centro
está 17 mm atrás) y el hueco de la pantalla rompía las esquinas. Visor
214×128 R30 y pantalla 200×114 R24 enrasados (zona delantera de la propia
carcasa), ojos pegados a la cara, sin hueco interior (Waveshare en fase 2).
**Tronco 1.6.1 EJECUTADO y aceptado** (9 cuerpos): panel frontal sobre el LIDAR, piel
de 1,5 mm que sigue el cono, 82 mm de ancho, R9, Z 228-310 (lienzo).
Cabeza 4.1.0 EJECUTADA (14 cuerpos). **Cabeza 4.1.1 EJECUTADA** (13, dorso
liso): sin tapa posterior (con el dorso redondo solo asomaban
sus esquinas). Antes, 4.1.0: loft de 17 secciones con esquinas
redondeadas reales (frente 264×160 R40, frente del lateral R15, dorso R75)
en vez de las 9 que hacían un "tejado" con arista. Primer intento: la
carcasa salió bien pero el loft del bisel (sin tocar, de la 4.0.0 de Codex)
falló por autointersección; probablemente la 4.0.0 nunca llegó a ejecutarse
entera. Bisel y pantalla pasan a rectángulos redondeados (R35/R28).
**EN CURSO (1 oct): fase 2, maqueta `Toreto_Maqueta_Ally_Pecho` 1.2.0**
(complemento aparte, componente 90_MAQUETA_ALLY_PECHO; para verla ocultar
04_PECHO_HOMBROS y 06_CABEZA): pecho 321 mm con la Ally X a la vista,
reductoras Ø60 + NEMA17 del hombro, iPhone 12 Pro Max con giro tipo libro,
zonas reservadas de cables y aire. Choques en maqueta_ally_pecho.json.
Ver `docs/DECISIONES.md` (propuesta Ally/iPhone, cables y calor, requisitos
del brazo: 1 kg por mano, hombro 2 + codo 1 + muñeca 2, reductoras
impresas, prototipo del hombro con opción A NEMA17 + MKS SERVO42D).
Decidido el 1-2 oct (todo en DECISIONES.md y CINEMATICA.md): Ally en el
pecho (327 mm), iPhone volteable en la cabeza (+15 mm, robot ~965 mm),
batería LiFePO4 24 V ~384 Wh en la base (5 h, carga a mano con sitio para
contactos), giros deseados y cadera nueva (actuador lineal, mecánica 85°,
software 30°). **Pecho 3.0.0 EJECUTADO (2 oct):** 327 mm, Ally X a la
vista, rejillas, aro fino; 29 cuerpos; modo nuevo `comprobar` (alturas +
interferencias): pecho→cuello −0,03, 0 choques brazos-resto. La maqueta
90_MAQUETA ya no hace falta. **Cabeza 4.2.1 EJECUTADA (2 oct):** 175 mm
(Z 790-965), hueca 3 mm (segundo loft), marco + visor de acrílico como piel
de 3 mm, iPhone 12 Pro Max ~9 mm tras el visor (el frente se curva: más
adelante sus extremos se salían) en modo cara arriba con los ojos, guías en
semicírculo, servo MG90S detrás del barrido, rejilla trasera; 16 cuerpos;
comprobar: cuello→cabeza −0,04, 0 choques. Fallo conocido: Fusion no
conserva el nombre del visor (sale "Cuerpo…") ni la opacidad del script;
puesta a mano (30 %). Siguientes: la cabeza
(175 mm), diseñar la cadera, y el prototipo del hombro (opción A).
Aparcado: desmontar la Epson WF-2820 (negro atascado) para sensores ópticos
y goma de yemas; si no, comprar "optical endstop" y lámina antideslizante.

**HECHO (30 sept): brazo v14 en el montaje.** `Toreto_Brazo_Mano_v14`
reemplazó al v13c (derecho; el izquierdo por simetría), juntas_espejo: 20
juntas y 16 relaciones (peor pasador 0,001 mm); alturas iguales; modo nuevo
`interferencias` (solo lectura): 0 choques brazos-resto (212 × 144 cuerpos).
Con esto el exterior queda igualado al lienzo y al render. SIGUIENTE: fase 2
(qué piezas lleva y dónde). Detalle del brazo v14: (`MODE='ver_brazo'` en `Toreto_Prueba_Holguras_01_44`):
cápsula blanca del hombro R55 (antes R45), cara exterior recortada plana
(R60) para que el tramo inclinado no tape el disco, disco negro R45×3 +
escalón R20×2 unidos a la tapa del eje (que ahora acaba en la cara), y
`_appearance` crea los colores si faltan. Primera ejecución OK (tapa y
rótula a 0,0 mm; blanco/negro bien); el usuario pidió la parte alta como la
cápsula redonda del render: por encima del eje se quita todo lo que esté a
más de R55 del eje (tapa semicircular concéntrica al disco). Simuladores y 20 pruebas OK
(test_arm_pose actualizado a v14). Pasos: documento HÍBRIDO vacío → ejecutar
→ guardar como `Toreto_Brazo_Mano_v14` → en el montaje Reemplazar componente
(brazo derecho) → borrar juntas de la mano izquierda → `MODE='juntas_espejo'`
→ `MODE='alturas'`. Antes estaba aplazado (proceso largo: documento nuevo + Reemplazar +
juntas_espejo): disco negro Ø84 visible en el hombro con aro blanco, y
arreglar el color gris (el script solo aplica "TORETO Blanco satinado" si ya
existe en el documento; en uno nuevo no existe y queda acero por defecto).
Base 2.0.0 EJECUTADA (83 cuerpos; base→tronco −28,94). **Base 2.0.1
EJECUTADA y aceptada**: chasis recortado a R 218 (asomaba del disco), placas de
rueda R 57, pasadores en los rodillos, carcasa de motor redonda Ø44.
Base 2.0.0 (simulada: 83 cuerpos, Z 0-228,9, rodillos tocan Z 0). Planta REDONDA Ø450 (la lámina mide igual
de frente y de lado; antes elipse 450×356), disco blanco Z 160-200 con
chaflán y aro negro en la tapa, cuerpo negro Z 100-160 con arcos, chasis
246 mm Z 31-100, pilares blancos laterales, mecanum Ø148 × 66 con 10
rodillos Ø24 a 45° y dos placas, eje + soporte de motor visibles, LIDAR
adelantado a Y −150 con el pedestal recortado contra el tronco. Decisiones
(DECISIONES.md): mecanum con aspecto del render; hombro con discos del
lienzo. Pendiente después: hombro (cápsula blanca + disco negro exterior),
cabeza redondeada, panel sobre el LIDAR, brazos blancos.

**EJECUTADO y ACEPTADO (29 sept): Tronco 1.6.0 + Cintura 2.2.0**
(alturas: tronco→cintura −60,04, resto igual). Decisión del
usuario: el bloque inferior de la cintura va FIJO y ENTERO por dentro del
tronco (el giro está en la junta de anillos). La 1.5.0 (espiga, tronco
elíptico 0,8) se ejecutó y el bloque asomaba por las esquinas: una elipse
no puede envolver un bloque casi cuadrado. Ahora: cono 200-335 (246→228,
fondo 0,9 medido en la vista lateral) + collar blanco de planta cuadrada
redondeada 212×190 R85 (Z 335-390) cuyo hueco es exactamente el bloque
(182×146 R50, baja a Z 330), silla en U recortada en el collar (fondo 354)
y tapa interior Z 325-335. Alturas esperadas: tronco→cintura **−60**.
Antes: Tronco 1.4.1 (8 cuerpos) + Cintura 2.0.1 ejecutados; silla de radio 40 y
bloque inferior de radio 36 (fondo plano ±55 como el lienzo) y relleno
blanco 08_RELLENO_SILLA_BLANCO (Z 346-390) que cierra el interior. Ejecutar
Tronco → Cintura → alturas (debe seguir igual). **Lección:** al abrir una
carcasa hueca, cerrar siempre el interior con un relleno. Pecho con falda hasta Z 520;
cintura en 3 piezas (bloque superior 170×136 Z 470-540 con conector redondo
en cada costado; junta de anillos Ø128 Z 460-470; bloque inferior 182×146
Z 354-460 con franja y panel 74×70); tronco con borde en silla (Z 390 en
los costados, 350 delante y detrás) y sin collar negro. Ejecutar Tronco →
Cintura → Pecho → alturas. **Solapes nuevos a propósito:** tronco→cintura
−36 y cintura→pecho −20. Siguiente diferencia: cabeza redondeada (render). Pecho 2.7.0
(rebaje en U de 135 mm con fondo en Z 700, abierto por delante y cerrado a
30 mm de la trasera; asiento negro de 6 mm que tapa el interior; copa negra
de 97→73 mm en Z 700-730) y Cuello 2.0.0 (base 97→83 en 730-749, cuello de
72 en 749-763, collarín de 94 en 763-790; sin fuelle). Ya copiados a
`%APPDATA%` y comprobados con un Fusion simulado. Ejecutar Pecho → Cuello →
modo `alturas`. Diferencias con el lienzo que quedan (juego de diferencias
del 29 sept; las marcas naranjas del lienzo son las juntas 200/390/541/730/
791): anillo inferior de la cabeza (144 mm, más ancho que el collarín),
falda blanca del pecho que baja ~20 mm sobre la cintura, cintura en dos
bloques, cuna en U arriba del tronco, panel blanco sobre el LIDAR y pantalla
del pecho (el lienzo ~170×118; el Android real 160×90: se decide en fase 2).

**HECHO el 29 sept: montaje de alturas cerrado.** Tronco 200-390, cuello
730-790; `alturas_montaje_v14.json` da los seis módulos en su cota nominal
(0 / 200 / 390 / 540 / 730 / 790 / 950). Juntas tronco→cintura,
cintura→pecho y cuello→cabeza a -0.04 mm (tolerancia de la caja envolvente,
no hueco real). Solapes a propósito: base→tronco -28.9 (torreta LIDAR hasta
228.9) y pecho→cuello -7.9 (conectores de hombro hasta 737.8). Lo siguiente
es la fase 2 (sección 6).

Pasos que se ejecutaron (en `Toreto_hombro_encajado_sin_articulaciones_backup`):

1. Complemento **`Toreto_Tronco_95cm`** (1.3.1) → regenera el tronco con
   `alto_tronco` = 190. Hoy acaba en Z 385 (se hizo con 185) y deja 5 mm de
   hueco bajo la cintura.
2. Complemento **`Toreto_Cuello_95cm`** (1.2.1) → regenera el cuello con
   `alto_cuello` = 60. Hoy acaba en Z 785 (se hizo con 55) y deja 5 mm bajo
   la cabeza.
3. Comprobar con `Toreto_Prueba_Holguras_01_44` en **modo `alturas`** (v14,
   SOLO LECTURA; es el modo activo): tronco→cintura y cuello→cabeza deben dar
   0. Los solapes base→tronco (torreta del LIDAR) y pecho→cuello (discos del
   hombro e inserto del cuello) son a propósito.

Ambos complementos ya están copiados a `%APPDATA%\Autodesk\Autodesk Fusion
360\API\Scripts`. Causa de fondo: los generadores solo se regeneran si cambia
su VERSION; al cambiar parámetros de altura nadie los regeneró. Sigue siendo
un defecto: cualquier cambio de parámetros exige subir la versión.

**Base 1.10.0 y Cabeza 4.0.0 estaban solo en `%APPDATA%`** (cambiadas el 5
sept, probablemente por Codex, sin subir). Copiadas al repo el 29 sept.

**Estado del montaje (29 sept):** pecho 2.6.0 con la pieza de hombro de la
lámina; dos brazos v13c (`Toreto_Brazo_Mano_v13c`, el izquierdo por Crear >
Simetría) con el hombro coaxial con el conector del pecho; las dos manos de
4 motores articuladas (la izquierda con `MODE='juntas_espejo'`). Interferencia
brazo-pecho limpia y sin huecos en el hombro.

**Siguiente, por orden del usuario:** montar entero (HECHO 29 sept) → **qué piezas lleva y dónde** (fase 2: sección 6) → dimensiones
reales → límites de articulaciones. Propuesta pendiente de decidir: brazo con
hombro 2 + codo 1 + muñeca 2 movimientos, y los 4 motores de la mano.

**Pendientes conocidos del montaje:** rótula de la muñeca asignada al
antebrazo (debería ir con la mano); palma sin recortar contra las primeras
falanges; piezas del pecho embutidas entre sí (algunas a propósito).

**Lecciones de estos días:** una interferencia limpia no prueba que las
piezas estén unidas (mirar huecos); al cambiar el brazo derecho la simetría
se recalcula sola y hay que borrar las juntas de la mano izquierda y volver
a ejecutar `juntas_espejo`; medir alturas con el modo `alturas` en vez de a
mano; y antes de fiarse de un complemento, comparar la copia de `%APPDATA%`
con la del repo.

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
- **Pinza vista en 3D (v9, 26 sept noche):** el pulgar toca de punta. El
  usuario decidió que el índice está bien y que el **pulgar debe apoyar con
  la cara plana de su última falange** (sección 5.1).
- **Pinza del boli CERRADA (27 sept):** pinza lateral, ensayada con sólidos
  (v10/v10b) y vista en 3D: cara plana del pulgar contra la esquina
  redondeada de la punta del índice, V de 20-30°, sin choques antes del
  contacto. El usuario la aceptó (`docs/DECISIONES.md`).
- **Brazo v11** (`fccfe50`): medidas y postura de la lámina, verificado en
  Fusion. **Orden decidido por el usuario:** montar el robot entero →
  qué piezas lleva → dimensiones reales → y solo entonces límites.
- **El montaje BUENO es el documento de Fusion
  `Toreto_hombro_encajado_sin_articulaciones_backup`** (confirmado por el usuario
  el 27 sept; no `00_Toreto_Ensamblaje_95cm` ni el que no lleva `_backup`).
  Estado al 27 sept: dos brazos v13 con el hombro encajado y las dos manos
  articuladas (commit `5c7654d`). Antes, en el documento sin `_backup`:
  todos los módulos más UN brazo, el de prueba antiguo (`94_BRAZO_MARCOS_LOCALES…`).
  El conector de hombro del pecho (`07_CONECTOR_HOMBRO_DER`, complemento
  Pecho_Hombros 2.5.0) queda en X 166-196,5, Y 0, Z 690,8, radio 36,5 mm:
  a la altura del pivote del v11 (Z 690), con 16 mm de diferencia en Y.
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
- `toreto_motor_validation.py` — ensayo histórico de la v8.
- `toreto_lateral_validation.py`, `toreto_contact_faces.py` — ensayo aislado
  y clasificación del primer contacto de la v10.
- `Toreto_Prueba_Holguras_01_44.py` — script de Fusion. Modo activo:
  `ensayo_lateral`; si se ejecuta escribe `prueba_mano_4_motores_v10.json`.
- `test_clearance.py`, `test_motor_groups.py`, `test_lateral_pinch.py` —
  33 pruebas.
- `simular_lateral_sin_fusion.py` — v10 con Fusion falso; el simulador
  inventa choques, no valida la geometría.
- `RESULTADO_PRUEBA.md` — cronología de todos los ensayos, con rechazos.

**Ejecutar en Fusion:** en un documento **vacío de diseño híbrido** (uno de
pieza falla: solo admite un componente), Utilidades > Complementos >
`Toreto_Prueba_Holguras_01_44` > Ejecutar. Este script está registrado
apuntando a esa carpeta del repo: los cambios se ven sin copiar nada.

**Pruebas:** desde esa carpeta, `python -m unittest discover -s . -p "test_*.py" -v`
**Simulación v10:** `python simular_lateral_sin_fusion.py`

## 5. Pendiente de la mano, en orden

1. **Pinza del boli: hecha y aceptada** (v10b; ver `RESULTADO_PRUEBA.md` y
   `ESTUDIO_APOYO_PLANO.md`). Queda pendiente en el script forzar el
   recálculo tras la pose: Fusion guarda los valores de las juntas pero no
   mueve las piezas hasta que se acciona una junta a mano.
   **Agarre de vaso** (propuesto, sin empezar): cilindro simulado de 60-80
   mm, cada falange se detiene al tocarlo.
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
