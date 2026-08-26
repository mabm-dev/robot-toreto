# Robot Toreto

Robot asistente de 95 cm impreso en 3D: base holonómica de 4 ruedas mecanum
con LIDAR, brazo de 6 grados de libertad por lado, cabeza de 2 grados de
libertad con cámara RGB-D, torso con pantalla táctil. Peso objetivo ~15 kg.

## Estado del proyecto

El proyecto avanza en tres fases fijas, en este orden — ver el porqué en
[`docs/DECISIONES.md`](docs/DECISIONES.md):

| Fase | Qué decide | Estado |
| --- | --- | --- |
| 1. Diseño | Forma, proporciones y módulos | 🟡 en curso — forma aprobada, proporciones finales pendientes |
| 2. Componentes | Batería, servos, motores, LIDAR, cámara, procesador | ⬜ no empezada — bloquea el resto |
| 3. CAD y materiales | Medidas definitivas y material pieza a pieza (Fusion) | 🟡 exterior avanzando — solo carcasas, sin mecánica ni cotas fijas (adelanto permitido, ver `DECISIONES.md`) |

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
├── visor-3d/                    # visor 3D interactivo (Three.js) — con este
│                                 # se aprobó la forma en v0.1
├── toreto_fusion_95cm/          # integración Autodesk Fusion 360 (fase 3, exterior)
│   ├── fusion_scripts/          #   10 add-ins de Fusion vigentes
│   ├── reference/lienzos_95cm/  #   4 vistas calibradas a 950mm + herramientas
│   │                             #   de medición (tools/measure_z_boundaries.py)
│   └── src/                     #   fuente paramétrica de la referencia volumétrica
├── toreto_exterior_95cm/        # piezas exteriores en OpenSCAD (fase 3, exterior)
│   ├── src/                     #   5 módulos .scad (base/tronco/pecho-hombros/
│   │                             #   cabeza-cuello/brazos)
│   ├── exports/                 #   STL por pieza
│   └── docs/                    #   una nota por módulo
├── toreto_v2.scad, toreto_reference_v1.scad, toreto_concept_v0.scad
│                                 # maquetas OpenSCAD anteriores (fase 1) — superadas
│                                 # por el trabajo de 95cm de arriba, se conservan
│                                 # como historial
└── exports/, exports_v1/, exports_v2/   # STL y renders de esas maquetas anteriores

docs/
├── ROADMAP.md               # versiones y checklist de cada una
├── DECISIONES.md            # por qué se tomó cada decisión importante
└── CINEMATICA.md            # árbol de links/joints previsto (planificación)
```

`toreto_fusion_95cm` y `toreto_exterior_95cm` describen el **mismo** exterior
de 95cm desde dos herramientas distintas (Fusion 360 y OpenSCAD) — hoy no
reparten los 950mm verticales de la misma forma entre sí; ver
`docs/DECISIONES.md` para el porqué no se ha fijado todavía una tabla única.

Hay también un cuaderno de aprendizaje (`docs/CUADERNO.md` en local) que es
deliberadamente privado y no está en este repositorio.

## Piezas y materiales

El trabajo exterior vigente (solo carcasas, sin mecánica) vive en
[`cad-toreto/toreto_fusion_95cm/`](cad-toreto/toreto_fusion_95cm/README.md)
(Fusion 360) y [`cad-toreto/toreto_exterior_95cm/`](cad-toreto/toreto_exterior_95cm/)
(OpenSCAD) — ver sus propios README. Ninguna pieza lleva todavía mecanismo
interno funcional (servos, reductoras, rodamientos reales): eso llega en la
fase 3 con los componentes ya elegidos, y las particiones verticales entre
módulos siguen sin fijarse por el mismo motivo (ver `docs/DECISIONES.md`).

`toreto_v2.scad` (y `lista_piezas_v2.md`, `guia_impresion_p1s.md`) es la
maqueta visual anterior — validó forma, proporción y que cada pieza entra en
el volumen de impresión de la Bambu Lab P1S (256 × 256 × 256 mm), pero está
superada por el trabajo de 95cm de arriba. Se conserva como historial, no
como referencia vigente.

Impresión: más perímetros antes que más relleno — 4-5 paredes con giroide al
25-30 %. Detalle en [`cad-toreto/guia_impresion_p1s.md`](cad-toreto/guia_impresion_p1s.md)
(de la maqueta anterior; sigue aplicando como criterio general de slicing).

## Herramientas

Fusion 360 (CAD final, fase 3), Bambu Studio (slicing), OpenSCAD (maquetas de
fase 1), KiCad / AutoCAD Electrical (electrónica), ROS 2 + Gazebo (control y
simulación, fase 3), NotebookLM (documentación).

## Licencia

Sin licencia definida todavía — todos los derechos reservados por defecto.
