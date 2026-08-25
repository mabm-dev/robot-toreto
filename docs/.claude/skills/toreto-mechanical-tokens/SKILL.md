---
name: toreto-mechanical-tokens
description: Registro maestro de parámetros cinemáticos, tolerancias y pipeline de software para Toreto. Define como únicas fuentes de verdad a docs/CINEMATICA.md y docs/DECISIONES.md.
---

# Toreto Mechanical & Architecture Tokens

## Parámetros Cinemáticos y Mecánicos (Fuente de verdad: docs/CINEMATICA.md)
* **Configuración:** Brazo articulado de 6 grados de libertad (6-DOF).
* **Payload nominal:** Consultar y respetar los cálculos de dinámica/estática en `docs/CINEMATICA.md`.
* **Alcance máximo y dimensiones:** Determinado por la geometría 3D en Autodesk Fusion / OpenSCAD.
* **Repetibilidad y holguras:** Definidas según las especificaciones de los reductores mecánicos seleccionados.
* **Actuadores:** Según la lista de materiales (BOM) oficial del repositorio (definir en fase mecánica).
* **Tolerancias de ensamble:** Especificadas en planos según ajustes requeridos por rodamientos de diseño.

## Pipeline de Software (Fuente de verdad: docs/DECISIONES.md)
* **CAD Mecánico:** Autodesk Fusion + OpenSCAD (BOSL2).
* **Simulación y Cinemática:** Plugin URDF Exporter -> ROS 2 / Gazebo Sim.
* **Esquemas de Control:** Documentación para esquemas en fase 2 (AutoCAD Electrical).
