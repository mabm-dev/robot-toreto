# Árbol cinemático (planificación)

Este diagrama **no es el URDF final** — es la jerarquía de enlaces y
articulaciones que se espera montar en Fusion en la fase 3 y exportar con el
plugin URDF Exporter. Los tipos de joint son los previstos; los ángulos límite
y el actuador de cada uno quedan como `TBD` hasta cerrar la fase 2
([`ROADMAP.md`](ROADMAP.md), milestone v0.2).

Las clases de color (`estructura`/`actuador`/`sensor`) y el estándar de
visualización técnica del proyecto (visores 3D, láminas Bento Grid, vistas
ortogonales normalizadas) los fijan las skills
[`toreto-cad-visual-identity`](../.claude/skills/toreto-cad-visual-identity/SKILL.md)
y [`toreto-mechanical-tokens`](../.claude/skills/toreto-mechanical-tokens/SKILL.md)
— no son arbitrarios, para que cualquier pieza nueva del proyecto use la misma
clave visual sin tener que redecidirla cada vez.

Sirve para razonar la estructura ahora, sin bloquear nada de CAD ni de
componentes — y como referencia directa cuando llegue el momento de nombrar
los links y joints reales en Fusion, para que coincidan con este árbol.

```mermaid
graph TD
    classDef estructura fill:#eef2f4,stroke:#5d7284,color:#152430
    classDef actuador fill:#0e86b8,stroke:#0e86b8,color:#ffffff
    classDef sensor fill:#1a7f5a,stroke:#1a7f5a,color:#ffffff

    base[["base_link<br/>base móvil"]]:::estructura
    w1((wheel_1)):::actuador
    w2((wheel_2)):::actuador
    w3((wheel_3)):::actuador
    lidar([lidar_link]):::sensor

    base -->|"continuous · TBD"| w1
    base -->|"continuous · TBD"| w2
    base -->|"continuous · TBD"| w3
    base -->|fixed| lidar

    waist[waist_link]:::estructura
    torso[torso_link]:::estructura
    base -->|fixed| waist
    waist -->|fixed| torso

    neck_pan[neck_pan_link]:::actuador
    head[head_link]:::estructura
    camera([camera_link]):::sensor
    torso -->|"revolute pan · ±90° · TBD actuador"| neck_pan
    neck_pan -->|"revolute tilt · +90/-45° · TBD actuador"| head
    head -->|fixed| camera

    sh_l[shoulder_L]:::actuador
    el_l[elbow_L]:::actuador
    wr_l[wrist_L]:::actuador
    gr_l[gripper_L]:::actuador
    torso -->|"revolute hombro · TBD"| sh_l
    sh_l -->|"revolute codo · TBD"| el_l
    el_l -->|"revolute muñeca · TBD"| wr_l
    wr_l -->|"prismatic pinza 3 dedos · TBD"| gr_l

    sh_r[shoulder_R]:::actuador
    el_r[elbow_R]:::actuador
    wr_r[wrist_R]:::actuador
    gr_r[gripper_R]:::actuador
    torso -->|"revolute hombro · TBD"| sh_r
    sh_r -->|"revolute codo · TBD"| el_r
    el_r -->|"revolute muñeca · TBD"| wr_r
    wr_r -->|"prismatic pinza 3 dedos · TBD"| gr_r
```

## Notas

- La base no es una cadena serie clásica: al ser holonómica de 3 ruedas omni,
  el `base_link` es el marco flotante de todo el árbol, no un eslabón fijo al
  suelo. Las 3 ruedas son `continuous` porque giran sin límite.
- `TBD` en cualquier joint significa: sin servo/motor elegido todavía. No
  fijar el ángulo límite hasta tener la hoja de datos del actuador real —
  poner un número ahora sería inventarlo.
- Cuando exista URDF real (fase 3), [`URDF-Visualizer`](https://github.com/UNLINEARITY/URDF-Visualizer)
  (WebGL/Three.js) es candidato para un visor interactivo del robot en el
  navegador — anotado en `ROADMAP.md`, no construido todavía porque no hay
  URDF que visualizar.
