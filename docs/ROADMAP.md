# Roadmap

Versión por hito, no por fecha — cada versión se cierra cuando su checklist
está completo, sin importar cuánto tarde. El orden **no se salta**: ver
[`DECISIONES.md`](DECISIONES.md#orden-de-trabajo-diseño--componentes--cad).

`v0.x` es todo lo previo a imprimir nada físico. `v1.x` es la primera maqueta
en plástico. `v2.x` es el robot mecánicamente funcional. `v3.x` es el robot
con IA integrada — el objetivo final.

## v0.1 — Diseño cerrado · fase 1 🟡 en curso

- [x] Lámina de diseño redibujada contra la imagen de referencia
- [ ] Visto bueno del usuario sobre la forma (brazos, cabeza, proporción base/torso)
- [ ] Proporciones finales documentadas en `cad-toreto/lista_piezas_v2.md`

## v0.2 — Componentes elegidos · fase 2 ⬜

- [ ] IA local o en la nube (Raspberry Pi 5 vs. Jetson Orin Nano) — bloquea el resto
- [ ] Servos de hombro y codo (los que más carga soportan — definen tamaño de carcasas)
- [ ] Resto de servos del brazo y la cabeza
- [ ] Motores + encoders de la base móvil
- [ ] Batería y arquitectura de alimentación
- [ ] LIDAR y cámara RGB-D
- [ ] Lista de compra con precios reales (sustituye a las estimaciones de la infografía)

## v0.3 — CAD funcional en Fusion · fase 3 ⬜

- [ ] Migrar de OpenSCAD a Autodesk Fusion (no AutoCAD — ver `DECISIONES.md`)
- [ ] Ensamblaje con articulaciones reales y topes de recorrido, siguiendo
      la jerarquía de [`CINEMATICA.md`](CINEMATICA.md)
- [ ] Exportar a URDF (plugin URDF Exporter)
- [ ] Medidas definitivas pieza a pieza, con los componentes físicos ya en la mano
- [ ] Verificar que cada pieza cabe en el volumen de la Bambu P1S (256×256×256 mm)
- [ ] Candidato a evaluar una vez exista URDF real: visor interactivo
      [URDF-Visualizer](https://github.com/UNLINEARITY/URDF-Visualizer) (WebGL)

## v1.0 — Maqueta física impresa ⬜

- [ ] Imprimir carcasas sin electrónica (validación de escala y encajes)
- [ ] Ajustar tolerancias reales de impresión sobre el CAD

## v1.1 — Banco de prueba del brazo (un eje) ⬜

- [ ] Montar un servo de hombro sobre eje y rodamiento reales
- [ ] Probar con carga progresiva: sin carga → 250 g → 500 g
- [ ] Confirmar holguras antes de fijar el hombro definitivo

## v1.2 — Base móvil funcional ⬜

- [ ] Motores + encoders + driver montados
- [ ] Control de movimiento básico (avanzar, girar)
- [ ] Parada de emergencia física

## v2.0 — Brazo completo funcional ⬜

- [ ] 6 DOF con servos reales en ambos brazos
- [ ] Pinza de 3 dedos con carga real (300-500 g)

## v2.1 — Integración electrónica ⬜

- [ ] Torso: pantalla táctil + caja electrónica
- [ ] Cabeza: cámara RGB-D + pantalla/ojos expresivos + 2 DOF
- [ ] Cableado definitivo y gestión de energía

## v3.0 — IA integrada ⬜

- [ ] Simulación en Gazebo con el URDF antes de mover el robot real
- [ ] Voz e interacción natural
- [ ] Navegación autónoma (LIDAR + cámara)
- [ ] Decidir qué corre local y qué en la nube, según [[decisión IA]](DECISIONES.md#ia-local-o-en-la-nube--pendiente)

---

Cada entrada que se cierre o decisión que se tome, anotarla también en
[`CUADERNO.md`](CUADERNO.md) el mismo día — el roadmap dice *qué* falta, el
cuaderno cuenta *cómo* se llegó ahí.
