# Limpieza de pruebas de brazo por marcos locales

Este script elimina exclusivamente las ocurrencias superiores cuyo nombre
cumpla `94_BRAZO_MARCOS_LOCALES_PRUEBA_01_<numero>`, salvo la versión vigente
`94_BRAZO_MARCOS_LOCALES_PRUEBA_01_35`.

No modifica componentes con otros nombres, cuerpos del robot original ni
lienzos. Después de ejecutarlo, guarda y vuelve a abrir el documento para que
Fusion libere memoria y reconstruya únicamente los componentes conservados.
