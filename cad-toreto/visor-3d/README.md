# Visor 3D interactivo (proxy)

`index.html` es el código fuente completo (Three.js + OrbitControls
embebidos, sin CDN) de la lámina publicada como artefacto:
https://claude.ai/code/artifact/395e9f86-c36f-4226-be99-07e2d0115f3f

Geometría **proxy**, no el CAD final de Fusion — ver
[`docs/DECISIONES.md`](../../docs/DECISIONES.md). Sigue el estándar de las
skills `toreto-cad-visual-identity` y `toreto-mechanical-tokens`.

Para verlo: abrir `index.html` directamente en cualquier navegador, no hace
falta servidor.

Para seguir editándolo: es un único archivo grande porque lleva Three.js
r128 completo inline (los artifacts no pueden cargar scripts externos). Los
valores en cm parten de las cotas conocidas del proyecto (altura 95, base
⌀40); todo lo demás son proporciones estimadas, ajustadas a ojo contra la
imagen de referencia.
