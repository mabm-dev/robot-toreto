# cad-toreto — índice

Todo el CAD de Robot Toreto vive aquí, no en la raíz del repo (ver
`docs/DECISIONES.md` en la raíz para el porqué de cada decisión). Esta
carpeta acumula varias generaciones de trabajo — de más reciente/vigente a
más antigua/histórica:

## Vigente (fase 3, exterior — sin mecánica ni cotas fijas)

- **[`toreto_fusion_95cm/`](toreto_fusion_95cm/README.md)** — integración
  Autodesk Fusion 360: 10 add-ins, las 4 vistas de referencia calibradas a
  950mm (`reference/lienzos_95cm/`) y las herramientas que las generan y
  miden (`tools/`).
- **[`toreto_exterior_95cm/`](toreto_exterior_95cm/README.md)** — las mismas
  piezas exteriores en OpenSCAD: 5 módulos fuente, STL exportados y un
  render/doc por módulo.

Ambas carpetas describen el **mismo** exterior de 95cm desde herramientas
distintas y hoy no reparten los 950mm verticales de la misma forma entre sí
— la tabla única de cotas está deliberadamente sin fijar porque depende de
dónde queden batería y mecanismos internos (fase 2, todavía sin cerrar).

## Vigente (fase 1 — visor de forma)

- **[`visor-3d/`](visor-3d/README.md)** — visor 3D interactivo en Three.js;
  con él se aprobó la forma del robot (milestone v0.1 del roadmap).

## Histórico (maquetas anteriores, superadas)

- `toreto_v2.scad` (+ `lista_piezas_v2.md`, `README_V2.md`,
  `STL_EXPORTADOS_V2.md`, `exports_v2/`) — última maqueta OpenSCAD de fase 1
  antes de migrar a Fusion. Validó forma, proporción y que cada pieza cabe
  en el volumen de la Bambu P1S (256×256×256mm); no lleva mecanismo interno.
- `toreto_reference_v1.scad` (+ `README_V1_REFERENCIA.md`,
  `STL_EXPORTADOS_V1.md`, `exports_v1/`) y `toreto_concept_v0.scad`
  (+ `lista_piezas_concepto.md`) — generaciones anteriores a v2.
- `guia_impresion_p1s.md` — perfiles de slicing; el criterio general (más
  perímetros que relleno) sigue aplicando aunque las piezas cambien.
- `MIGRACION_95CM.md` — nota de la consolidación del 25 ago 2026 que separó
  lo que sí pasaba a 95cm de lo que se descartaba (rama de 65cm con servos
  ST-3215 ya elegidos — ver `toreto-gpt-descartado` en la memoria del
  proyecto, no forma parte de este repo).

No confundir con la carpeta hermana `cad-toreto-gpt/` (fuera de este repo,
en `.gitignore`) — es una rama paralela de 65cm descartada, no el proyecto
activo.
