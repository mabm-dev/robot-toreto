# Toreto_Referencias_95cm

Secuencia de Autodesk Fusion para colocar dentro de `00_REFERENCIAS` cuatro
lienzos ortogonales del robot:

- `PATRON_01_FRONTAL_95CM` y `PATRON_02_POSTERIOR_95CM`, en el plano XZ;
- `PATRON_03_LATERAL_IZQUIERDO_95CM` y
  `PATRON_04_LATERAL_DERECHO_95CM`, en el plano YZ;
- la malla STL completa, si existe, como comprobación adicional.

Todos los lienzos comparten escala y origen: contacto con el suelo en `Z=0`
y parte superior de la cabeza en `Z=950 mm`. Solo el frontal queda visible al
terminar. En `00_REFERENCIAS > Lienzos`, apaga su bombilla y enciende la vista
que necesites para evitar superposiciones.

Desde la versión 2.1.0, las cuatro siluetas se calibran de forma independiente
contra sus límites auditados y ocupan exactamente 1900 intervalos a
`0,5 mm/píxel`; los márgenes originales de la lámina no afectan a la escala.

**2.2.0 (26 ago 2026): solo el FRONTAL está verificado dentro de Fusion.**
El posterior y los dos laterales usaban la misma fórmula de transformación
que el frontal, sin comprobar que el plano YZ de Fusion mapea sus ejes
igual que el XZ (no lo hace necesariamente) ni que ver la espalda del robot
necesita invertir el ancho de imagen (sí hace falta: el posterior ya lleva
ese espejo desde esta versión). Si al ejecutar el add-in alguno de los tres
sigue sin encajar, revisar `_canvas_transform()` en el `.py` — está separado
por plano exactamente para poder corregir uno sin tocar los demás.

Las referencias no son piezas fabricables. El script es repetible: actualiza
los lienzos existentes sin duplicarlos y no duplica la malla existente.
