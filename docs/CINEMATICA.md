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
    w1((wheel_fl)):::actuador
    w2((wheel_fr)):::actuador
    w3((wheel_rl)):::actuador
    w4((wheel_rr)):::actuador
    lidar([lidar_link]):::sensor

    base -->|"continuous · TBD"| w1
    base -->|"continuous · TBD"| w2
    base -->|"continuous · TBD"| w3
    base -->|"continuous · TBD"| w4
    base -->|fixed| lidar

    trunk[trunk_link<br/>tronco]:::estructura
    hip[hip_link<br/>cintura inferior]:::actuador
    waist[waist_link<br/>cintura superior]:::actuador
    torso[torso_link<br/>pecho + Ally]:::estructura
    base -->|fixed| trunk
    trunk -->|"revolute cadera · 0/+30° adelante · actuador lineal 24 V"| hip
    hip -->|"revolute giro cintura · ±150° · TBD"| waist
    waist -->|fixed| torso

    neck_pan[neck_pan_link]:::actuador
    head[head_link]:::estructura
    phone[iphone_link]:::actuador
    camera([camera_link]):::sensor
    torso -->|"revolute pan · ±90° · TBD actuador"| neck_pan
    neck_pan -->|"revolute tilt · +30/-45° · TBD actuador"| head
    head -->|"revolute volteo iPhone · 0/180° · servo"| phone
    phone -->|fixed| camera

    sh_l[shoulder_pitch_L]:::actuador
    shr_l[shoulder_roll_L]:::actuador
    el_l[elbow_L]:::actuador
    wr_l[wrist_1_L]:::actuador
    wr2_l[wrist_2_L]:::actuador
    gr_l[hand_L]:::actuador
    torso -->|"revolute hombro subir/bajar · -30/+130° · ≥15 N·m · TBD"| sh_l
    sh_l -->|"revolute rotación del brazo · ±90° · ≥7 N·m · TBD"| shr_l
    shr_l -->|"revolute codo · 0/135° · ≥7 N·m · TBD"| el_l
    el_l -->|"revolute muñeca 1 (girar) · ±90° · ≥2 N·m · TBD"| wr_l
    wr_l -->|"revolute muñeca 2 (doblar) · ±60° · ≥2 N·m · TBD"| wr2_l
    wr2_l -->|"mano adaptativa 4 motores · TBD"| gr_l

    sh_r[shoulder_pitch_R]:::actuador
    shr_r[shoulder_roll_R]:::actuador
    el_r[elbow_R]:::actuador
    wr_r[wrist_1_R]:::actuador
    wr2_r[wrist_2_R]:::actuador
    gr_r[hand_R]:::actuador
    torso -->|"revolute hombro subir/bajar · -30/+130° · ≥15 N·m · TBD"| sh_r
    sh_r -->|"revolute rotación del brazo · ±90° · ≥7 N·m · TBD"| shr_r
    shr_r -->|"revolute codo · 0/135° · ≥7 N·m · TBD"| el_r
    el_r -->|"revolute muñeca 1 (girar) · ±90° · ≥2 N·m · TBD"| wr_r
    wr_r -->|"revolute muñeca 2 (doblar) · ±60° · ≥2 N·m · TBD"| wr2_r
    wr2_r -->|"mano adaptativa 4 motores · TBD"| gr_r
```

## Notas

- La base no es una cadena serie clásica: al ser holonómica de 4 ruedas
  mecanum (`fl`/`fr`/`rl`/`rr` — delantera/trasera, izquierda/derecha, en
  disposición rectangular, no en triángulo), el `base_link` es el marco
  flotante de todo el árbol, no un eslabón fijo al suelo. Las 4 ruedas son
  `continuous` porque giran sin límite; los rodillos angulados de cada rueda
  mecanum son detalle de geometría/fricción, no un joint adicional en el URDF.
  (Cambiado de 3 ruedas omni a 4 mecanum el 23 de agosto de 2026 — ver
  `DECISIONES.md`.)
- Brazo (30 sept 2026): hombro 2 + codo 1 + muñeca 2 y mano de 4 motores,
  para poder juntar las manos delante del pecho; pares mínimos para 1 kg por
  mano con margen ×2 (ver `DECISIONES.md`).
- Giros (2 oct 2026): son los DESEADOS (requisitos), no límites medidos;
  0° = postura de la lámina. Los límites reales se miden con el pecho
  (327 mm) y la cabeza (175 mm) definitivos. Ver `DECISIONES.md`.
- `TBD` en cualquier joint significa: sin servo/motor elegido todavía. No
  fijar el ángulo límite hasta tener la hoja de datos del actuador real —
  poner un número ahora sería inventarlo.
- Cuando exista URDF real (fase 3), [`URDF-Visualizer`](https://github.com/UNLINEARITY/URDF-Visualizer)
  (WebGL/Three.js) es candidato para un visor interactivo del robot en el
  navegador — anotado en `ROADMAP.md`, no construido todavía porque no hay
  URDF que visualizar.
