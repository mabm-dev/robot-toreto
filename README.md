# Robot Toreto

Robot asistente de 95 cm impreso en 3D: base holonómica de 3 ruedas omni con
LIDAR, brazo de 6 grados de libertad por lado, cabeza de 2 grados de libertad
con cámara RGB-D, torso con pantalla táctil. Peso objetivo ~15 kg.

## Estado del proyecto

El proyecto avanza en tres fases fijas, en este orden — ver el porqué en
[`docs/DECISIONES.md`](docs/DECISIONES.md):

| Fase | Qué decide | Estado |
| --- | --- | --- |
| 1. Diseño | Forma, proporciones y módulos | 🟡 en curso |
| 2. Componentes | Batería, servos, motores, LIDAR, cámara, procesador | ⬜ no empezada |
| 3. CAD y materiales | Medidas definitivas y material pieza a pieza (Fusion) | ⬜ no empezada |

Seguimiento del avance, en este repo:

- [`docs/ROADMAP.md`](docs/ROADMAP.md) — versiones y checklist de cada una
- [`docs/DECISIONES.md`](docs/DECISIONES.md) — por qué se tomó cada decisión
- [`docs/CINEMATICA.md`](docs/CINEMATICA.md) — árbol de links/joints previsto (planificación, no URDF final)

Documentos vivos (consulta desde cualquier dispositivo, se actualizan sobre la
misma URL):

- [Índice del proyecto](https://claude.ai/code/artifact/3c1e9e5f-cfa8-4d47-8dd7-55fb1f6f150b)
- [Lámina de diseño](https://claude.ai/code/artifact/774ba526-7714-4aee-aeff-1aad35ca3a55)
- [Stack de herramientas](https://claude.ai/code/artifact/6abfaa55-f3db-4c18-a0bd-476af38d9d59)

## Estructura del repositorio

```
cad-toreto/
├── toreto_v2.scad          # modelo paramétrico vigente (OpenSCAD)
├── toreto_reference_v1.scad, toreto_concept_v0.scad   # versiones anteriores
├── lista_piezas_v2.md      # mapeo pieza ↔ material ↔ archivo STL
├── guia_impresion_p1s.md   # perfiles, orientación y soportes para la Bambu P1S
├── README_V2.md            # notas de la versión vigente
└── exports/, exports_v1/, exports_v2/   # STL y renders exportados

docs/
├── ROADMAP.md               # versiones y checklist de cada una
├── DECISIONES.md            # por qué se tomó cada decisión importante
└── CINEMATICA.md            # árbol de links/joints previsto (planificación)
```

Hay también un cuaderno de aprendizaje (`docs/CUADERNO.md` en local) que es
deliberadamente privado y no está en este repositorio.

## Piezas y materiales

`toreto_v2.scad` es una **maqueta visual**: valida forma y proporción, y que
cada pieza entra en el volumen de impresión de la Bambu Lab P1S
(256 × 256 × 256 mm). Todavía no lleva mecanismo interno funcional (servos,
reductoras, rodamientos reales) — eso llega en la fase 3, con los componentes
ya elegidos.

El desglose completo (15 piezas, material sugerido por pieza, notas de
montaje) está en [`cad-toreto/lista_piezas_v2.md`](cad-toreto/lista_piezas_v2.md).

Impresión: más perímetros antes que más relleno — 4-5 paredes con giroide al
25-30 %. Detalle completo en
[`cad-toreto/guia_impresion_p1s.md`](cad-toreto/guia_impresion_p1s.md).

## Herramientas

Fusion 360 (CAD final, fase 3), Bambu Studio (slicing), OpenSCAD (maquetas de
fase 1), KiCad / AutoCAD Electrical (electrónica), ROS 2 + Gazebo (control y
simulación, fase 3), NotebookLM (documentación).

## Licencia

Sin licencia definida todavía — todos los derechos reservados por defecto.
