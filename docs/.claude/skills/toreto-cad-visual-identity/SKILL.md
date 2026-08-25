---
name: toreto-cad-visual-identity
description: Motor de visualización técnica, infografías Bento Grid y visores 3D interactivos en Three.js para el robot Toreto (6-DOF). Se activa al generar láminas técnicas, diagramas cinemáticos y visores 3D, prohibiendo el uso de SVGs planos tipo caricatura.
---

# Toreto CAD & Visual Identity Skill

Esta skill define el estándar gráfico, interactivo y de documentación técnica para el proyecto Toreto.

## Directivas Visuales Obligatorias

1. **Prohibición de SVGs 2D planos/caricatura:** No generar dibujos esquemáticos infantiles ni iconos vectoriales planos decorativos.
2. **Visores 3D Interactivos (Artifacts / WebGL):**
   - Usar Three.js con `OrbitControls`.
   - Materiales PBR (`MeshStandardMaterial` con `metalness: 0.8`, `roughness: 0.2`) simulando aluminio mecanizado y fibra de carbono.
   - Entorno con iluminación de estudio (Key + Fill + Rim light), sombras dinámicas y `GridHelper` técnico.
   - Controles interactivos (sliders) para mover cada articulación según los rangos definidos en `docs/CINEMATICA.md`.
3. **Láminas Técnicas e Infografías (HTML + Tailwind CSS):**
   - Layout *Bento Grid* industrial en modo oscuro (`bg-slate-950`, `border-slate-800`).
   - Bloques obligatorios: Tabla de parámetros mecánicos calculados, diagrama de arquitectura de control y visor 3D/esquema técnico normalizado.
4. **Vistas 2D Técnicas:**
   - Si se requieren diagramas vectoriales, deben ser proyecciones ortogonales normalizadas (alzado, planta, perfil) con cotas reales y líneas de centros.
