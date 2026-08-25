# Robot Toreto Fusion 95 cm

Integración de Autodesk Fusion 360 y referencias dimensionales del diseño
exterior vigente. Esta carpeta no contiene la antigua rama funcional de 65 cm.

## Alcance

- Altura exterior exacta: **950 mm**.
- Base compacta: **Ø400 × 225 mm**.
- Cuatro ruedas mecanum mostradas únicamente como volumen visual.
- Tronco, cintura, pecho, cuello y cabeza en módulos desmontables.
- Pantalla frontal horizontal.
- Brazos de **170 mm + 150 mm**.
- Mano antropomórfica: cuatro dedos de tres falanges y pulgar de dos falanges.
- Solo carcasas y piezas exteriores.

No incluye motores, esqueleto, rodamientos, ejes, cableado, electrónica ni
anclajes definitivos. Los alojamientos funcionales se diseñarán después de
seleccionar y medir los componentes reales.

## Distribución vertical

| Módulo | Altura | Cota superior |
|---|---:|---:|
| Base | 225 mm | 225 mm |
| Tronco blanco | 185 mm | 410 mm |
| Cintura negra | 100 mm | 510 mm |
| Pecho | 190 mm | 700 mm |
| Cuello | 55 mm | 755 mm |
| Cabeza | 195 mm | 950 mm |

## Archivos conservados

- `fusion_scripts/`: versiones vigentes de los complementos de Fusion 360.
- `reference/lienzos_95cm/`: frontal, posterior y dos laterales calibrados
  entre `Z=0` y `Z=950 mm`.
- `reference/toreto_fusion_95cm_assembly.stl`: referencia volumétrica, no pieza
  fabricable.
- `reference/`: imágenes conceptuales aprobadas.
- `src/`: fuente paramétrica usada para regenerar la referencia volumétrica.
- `tools/prepare_fusion_canvases.py`: preparación reproducible de los lienzos.

Las piezas exteriores exportables vigentes están en la carpeta hermana
`toreto_exterior_95cm`; se retiraron de aquí los STL preliminares duplicados.

## Estado

Es una maqueta CAD exterior y paramétrica para cerrar apariencia, partición y
volúmenes. Los complementos construyen geometría de revisión, no mecánica
definitiva. Antes de imprimir el conjunto completo hay que:

1. confirmar motores, ruedas, servos, sensores y batería;
2. introducir sus envolventes reales en Fusion 360;
3. definir tornillería, insertos, tolerancias y nervios;
4. comprobar alcance y par de brazos;
5. laminar prototipos parciales en Bambu Studio u OrcaSlicer.
