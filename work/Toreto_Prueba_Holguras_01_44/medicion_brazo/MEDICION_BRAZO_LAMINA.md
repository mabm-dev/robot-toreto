# Brazo: medición sobre la lámina frente al brazo de prueba — 27-09-2026

Fuente maestra: los lienzos calibrados de `cad-toreto/toreto_fusion_95cm/
reference/lienzos_95cm/` (0,5 mm/px, Z=0 en el suelo). Brazo derecho del
robot. Y en el lienzo lateral derecho: negativo = hacia delante.

**Método.** Se amplió el brazo con una rejilla de 10 mm (imágenes de esta
carpeta) y se leyeron a ojo los centros: en el lateral los pivotes de hombro
y codo se ven como círculos (sus ejes van de lado a lado, eje X); la X de
cada punto se leyó en el frontal, en el eje de la carcasa a esa altura.
Precisión estimada: unos ±3 mm por punto. Las guías de Codex
(`fusion_traces.json`) se comprobaron dibujándolas sobre el lienzo lateral
(`guias_brazo.jpg`): siguen el brazo.

| Punto (lámina) | X | Y | Z |
|---|---:|---:|---:|
| Centro del hombro | 196 | 16 | 690 |
| Pivote inferior del brazo superior | 228 | 47 | 575,5 |
| Pivote superior del antebrazo | 239,5 | 58,6 | 509,5 |
| Fin de la carcasa del antebrazo | 265 | -27,5 | 402,5 |
| Muñeca | 268 | -34 | 389 |

**Codo:** los dos círculos pequeños (68 mm entre sí) son las fijaciones de
la pieza negra de enlace a cada carcasa; **el giro es un solo eje, en el
centro de esa pieza** (aclarado por el usuario el 27-09-2026). Por eso se
compara el codo del brazo de prueba con el punto medio entre ambos círculos.

| Tramo | Lámina | Brazo de prueba |
|---|---:|---:|
| Hombro → centro del codo | 156,6 mm | 211,3 mm |
| Centro del codo → muñeca | 179,6 mm | 124,3 mm |
| Total | 336,3 mm | 335,7 mm |
| Inclinación hacia delante: brazo / antebrazo | -15° / +37,5° | 0° / 0° |

Diferencias del brazo de prueba respecto a la lámina:

- **Hombro 67 mm desplazado**: 52 mm más alto y 39 mm hacia atrás. Su eje
  está en lo alto de la carcasa (Z 742), no en el pivote dibujado (Z 690).
- **Codo bien**: a 4,8 mm del punto medio entre los dos pivotes.
- **Muñeca 93 mm desplazada**: 88 mm hacia atrás y 29 mm más alta, porque
  el antebrazo está recto en el plano frontal en vez de inclinado ~38°.
- El largo total coincide, pero está mal repartido: el brazo superior sobra
  ~55 mm y al antebrazo le faltan ~55 mm.

Causa: el generador (`Toreto_Brazo_Marcos_Locales_95cm`) toma la postura y
las longitudes de la vista frontal, donde el antebrazo inclinado se ve
acortado, y usa la lateral solo para el grosor.

Incertidumbre: los dos lienzos laterales no coinciden del todo (el antebrazo
sale a 38° en el derecho y a 46° en el izquierdo según las guías). Es un
dibujo, no un plano: tomar estas cotas con ±5-10 mm.

Brazo del montaje (`Toreto_Brazos_95cm` 3.9.0), por lectura del código, sin
comprobar en Fusion: modela la inclinación (brazo ~14° atrás, antebrazo ~35°
adelante) con un solo eje de codo; parámetros `largo_brazo` 178 mm y
`largo_antebrazo` 186 mm. Su antebrazo parece más largo que el de la lámina
(~190-200 mm del eje del codo al final de la carcasa frente a ~164 mm);
pendiente de medirlo en Fusion.
