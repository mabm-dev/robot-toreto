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

Las referencias no son piezas fabricables. El script es repetible: actualiza
los lienzos existentes sin duplicarlos y no duplica la malla existente.
