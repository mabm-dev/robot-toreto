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

La versión 2.4.0 consolida las correcciones comprobadas en Fusion:

- usa una matriz distinta para XZ y YZ, manteniendo Z vertical;
- ancla cada vista por el eje central de la base, no por el centro del PNG;
- conserva el espejo horizontal necesario en la vista posterior;
- elimina de `00_REFERENCIAS > Lienzos` cualquier lienzo antiguo y conserva
  exclusivamente los cuatro patrones calibrados de 95 cm.

Las referencias no son piezas fabricables. El script es repetible: actualiza
los lienzos existentes sin duplicarlos y no duplica la malla existente.
