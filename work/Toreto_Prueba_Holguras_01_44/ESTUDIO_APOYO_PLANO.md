# Criba del apoyo plano del pulgar — 27-09-2026 (corregida)

Estudio **fuera de Fusion**. No cambia `toreto_hand.py`, las relaciones ni el
documento CAD. Se reproduce con `study_thumb_pad.py`, que usa
`hand_local_sections.json`, los ejes de `joint_specs()` y el mismo orden de
rotaciones que el ensayo v8. Se examinan las cuatro parejas de caras
longitudinales de las dos falanges finales. **Cada cara se clasifica por la
dirección en la que dobla su última articulación**: palmar hacia dentro de
la curva, dorsal hacia fuera; las dos perpendiculares son laterales. El índice
conserva su geometría y reparto de flexión; solo se varía su fracción de
cierre para encontrar el momento de contacto.

La v9 estaba al 75% del cierre del índice, con pulgar 30/30/26,25/15 grados
(cardán / juntas 2–4). El par de caras planas más cercano en esta aproximación
queda a 2,44 mm, con 43,6 grados de desalineación y el punto del pulgar en un
borde lateral. Esa cara del pulgar es **dorsal**, por lo que el dato no sirve
para decidir el agarre pedido. La observación visual fue contacto por la
punta. Esta aproximación **no reproduce el hueco exacto de 0,28 mm** medido
entre sólidos: son superficies y métricas diferentes.

La criba usa una malla de 5 grados para cada junta del pulgar dentro de los
topes actuales y exige: distancia de puntos <=2 mm, normales opuestas dentro
de 45,6 grados, puntos dentro de la zona longitudinal plana y fuera de los
bordes laterales. A 65% y 75% del índice no hay candidatos; a 80% hay tres
parejas de caras que pasan la criba, a 83% diez. La criba inicial no filtraba
la identidad de la cara; estos recuentos **no son pinzas válidas ni validadas**.

| Caso | Índice | Pulgar 1/2/3/4 | Caras que se acercan | Distancia aprox. | Desalineación | Dictamen |
|---|---:|---|---|---:|---:|---|
| A | 83% | 30/10/5/5° | palmar / lateral | 0,38 mm | 22,7° | Única de las tres que usa la cara de agarre del pulgar; puede ser una pinza tipo boli contra el costado del índice. |
| B | 83% | 25/40/15/5° | dorsal / lateral | 0,46 mm | 35,4° | Descartada: apoya el dorso del pulgar. |
| C | 80% | 25/20/35/20° | dorsal / palmar | 0,75 mm | 41,5° | Descartada: apoya el dorso del pulgar. |

**A no exige cambiar relaciones.** Con el cardán a 30° y el motor de flexión
del pulgar al 25%, las proporciones actuales producen 30/10/8,75/5°. Al 83%
del índice, la aproximación da 0,44 mm y 21,7° entre cara palmar del pulgar y
lateral del índice. Esta postura no supera el criterio de *punto interior* de
la criba: el par más cercano cae al 64% de la longitud plana del pulgar y al
18% de la del índice, cerca de sus extremos respectivos. En una búsqueda fina
con las mismas relaciones, 84% del índice y 21% de flexión da un par interior
a unos 0,31 mm y 22,8°, pero sigue siendo solo una predicción geométrica.

Para dos caras **palmares**, un barrido angular sin prueba de distancia da una
desalineación mínima de 69,1° con el índice al 75%, 73,9° al 80% y 79,0° al
85%. Así, en la región de la pinza actual, los ejes no ofrecen buen apoyo
palmar-palmar. Matiz importante: con el índice *abierto* sí aparece una
orientación de 39,7°, pero las piezas están lejos; por tanto el cálculo no
demuestra imposibilidad geométrica absoluta en toda postura, sino falta de
una pinza palmar-palmar cercana con la configuración estudiada.

Las distancias son entre puntos muestreados de caras idealizadas, **no**
holguras medidas por el núcleo geométrico. El loft real tiene esquinas
redondeadas y punta curvada. No se han comprobado intersecciones de sólidos,
recorrido continuo, palma, nudillos, apoyo sobre un boli, resistencia ni
agarre de vaso/pelota. Tampoco se ha demostrado un área de apoyo suficiente:
incluso A conserva unos 22° de desalineación. La variante A con relaciones
actuales no cambia topes ni acoplamientos; B y C se descartan antes de
considerar cambios mecánicos.

Siguiente paso, **solo tras aprobación**: ensayar con sólidos únicamente A
con las relaciones actuales (índice 83%, cardán 30°, flexión del pulgar 25%),
medir hueco/contacto real y choques antes del contacto, forzar recálculo de
la pose y dejar una foto fija. Luego decidir si vale el apoyo palmar del
pulgar contra el lateral del índice para un boli; si se exige palmar-palmar,
estudiar el rediseño del mecanismo del pulgar. No tocar el índice ni publicar
sobre el diseño original; detenerse ante cualquier desplazamiento inesperado.
