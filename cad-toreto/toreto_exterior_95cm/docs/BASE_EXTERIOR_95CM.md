# Módulo 1 — base exterior Toreto 95 cm

## Intención visual

La base reproduce el lenguaje del recorte de referencia:

- plataforma circular blanca de perfil bajo;
- aro negro continuo entre el labio y la cubierta superior;
- tambor frontal negro con dos paneles de sensores ciegos;
- cuatro huecos perimetrales con carenados blancos;
- pequeña carcasa de sensor sobre la corona superior;
- separación de colores blanco, negro y detalle cian.

Las ruedas no se modelan. Los huecos quedan vacíos deliberadamente para no
inventar dimensiones ni interfaces mecánicas.

## Cotas de envolvente

| Parámetro | Valor |
| --- | ---: |
| Diámetro nominal de la base | 400 mm |
| Altura de la carcasa principal | 225 mm |
| Espesor conceptual de piel | 3,2 mm |
| Hueco central para el futuro tronco | Ø232 mm |
| Número de huecos de rueda | 4 |

Estas cotas pertenecen a la maqueta estética de un robot de 950 mm. No son
cotas de fabricación mecánica ni fijan el tamaño de motores o ruedas.

## Despiece exterior

| Archivo STL | Cantidad | Color visual | Función estética |
| --- | ---: | --- | --- |
| `core_fascia_quadrant.stl` | 4 | negro | Tambor exterior y fachada |
| `outer_side_panel.stl` | 3 | blanco | Paños laterales y trasero |
| `top_deck_quadrant.stl` | 4 | blanco | Cubierta superior |
| `trim_ring_quadrant.stl` | 4 | negro | Aro de contraste |
| `wheel_arch_shell.stl` | 4 | blanco | Marco exterior del hueco de rueda |
| `sensor_panel_bezel.stl` | 2 | negro | Marco de panel frontal |
| `sensor_panel_insert.stl` | 2 | negro/cian | Inserto decorativo ciego |
| `top_sensor_plinth.stl` | 1 | blanco | Zócalo del sensor superior |
| `top_sensor_cover.stl` | 1 | negro | Cubierta exterior vacía |

Total: 25 copias impresas a partir de 9 STL únicos.

## Compatibilidad de impresión

La base de Ø400 mm se divide en cuadrantes. Cada STL único se mantiene dentro
del volumen de 256 × 256 × 256 mm de la Bambu Lab P1S en su orientación de
diseño. La orientación definitiva, soportes y tolerancias se decidirán después
de aprobar la forma y antes de fabricar.

## Exclusiones explícitas

- No hay ruedas ni rodillos mecanum.
- No hay alojamientos de motor, reductora, encoder o batería.
- No hay eje, rodamiento, tornillería, insertos ni clips.
- No hay suelo estructural ni esqueleto interno.
- Las lentes y el sensor superior son volúmenes exteriores ciegos.
- El hueco central no contiene unión mecánica con el tronco.

El siguiente módulo es el tronco y solo se diseña después de aprobar visualmente
esta base.

