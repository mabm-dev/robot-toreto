# Lista de piezas - Toreto V0

## Piezas imprimibles

| Pieza | Cantidad | Material | Comentario |
| --- | ---: | --- | --- |
| Base cuadrante | 4 | PETG | Forma el anillo exterior de 400 mm |
| Placa central base | 1 | PETG-CF | Union de base, columna y electronica |
| Caja electronica | 1 | PETG | Para reguladores, hubs y controladores |
| Tapa/sensor frontal | 1 | PETG | Huecos para sensores o camara frontal |
| Cubierta rueda | 3 | PETG | Estetica/proteccion, no rueda funcional |
| Torso frontal | 1 | PETG | Hueco de pantalla tactil |
| Torso trasero | 1 | PETG | Acceso a electronica y cableado |
| Montura hombro izquierda | 1 | PETG-CF | Debe reforzarse con eje metalico |
| Montura hombro derecha | 1 | PETG-CF | Debe reforzarse con eje metalico |
| Columna cuello | 1 | PETG-CF | Paso de cables interior |
| Cabeza frontal | 1 | PETG | Hueco de pantalla/cara y camaras |
| Cabeza trasera | 1 | PETG | Cierre de cabeza |
| Orejas/laterales cabeza | 2 | PETG | Soportes laterales |
| Brazo superior | 2 | PETG-CF | Carcasa, no estructura final unica |
| Antebrazo | 2 | PETG-CF | Carcasa, no estructura final unica |
| Muneca/pinza conceptual | 2 | PETG-CF | Concepto de pinza ligera |

## Componentes no imprimibles

| Componente | Cantidad orientativa | Nota |
| --- | ---: | --- |
| Motores con encoder para base | 3 | Mejor comprar con reductora |
| Ruedas omni/mecanum | 3 | No recomiendo imprimirlas como pieza funcional |
| Driver motores | 1-3 | Segun motor elegido |
| Bateria 24 V | 1 | Li-ion/LiFePO4 con BMS |
| Reguladores DC-DC | 2-3 | 24 V a 12 V, 5 V y/o 19 V |
| Raspberry Pi 5 / Jetson / mini PC | 1 | Control local y puente con agentes |
| ESP32 / Arduino / STM32 | 1-2 | Control en tiempo real de motores/servos |
| Camara | 1-2 | Cara/cabeza o vision frontal |
| Microfonos | 1 | Preferible array USB |
| Altavoz + amplificador | 1 | Voz de Toreto |
| Pantalla cabeza | 1 | Cara expresiva |
| Pantalla torso | 1 | Opcional |
| IMU | 1 | Estabilidad y orientacion |
| Sensor distancia / LiDAR | 1 | Navegacion y seguridad |
| Boton parada emergencia | 1 | Muy recomendado |
| Rodamientos/ejes/tornilleria | varios | M3, M4, M5 e insertos termicos |

## Fases

### Fase 1 - Maqueta

Imprimir cabeza, torso y base sin motores para revisar escala, acceso a tornillos, paso de cables y presencia fisica.

### Fase 2 - Base movil

Montar la base con motores, encoders, bateria, control local y parada de emergencia.

### Fase 3 - IA fisica

Anadir cabeza con pantalla, camara, microfonos y comunicacion con tu sistema de agentes.

### Fase 4 - Brazo

Empezar con una pinza ligera y pocos grados de libertad antes de pasar a 6 DOF.
