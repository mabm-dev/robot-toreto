# Brazo Toreto — prueba de marcos locales 1.0.35

La 1.0.35 conserva exactamente la implantacion y el giro hacia dentro del
pulgar de la 1.0.34. Invierte el sentido de flexion de los cuatro dedos
principales para que cierren desde la cara opuesta de la palma.

Las dieciseis juntas principales usan ahora los intervalos -60..0, -60..0,
-50..0 y -40..0 grados. Los topes fisicos se trasladan al mismo lado angular,
incluida la compensacion por contacto de los nervios. Las relaciones mantienen
las magnitudes progresivas 60/60/50/40. El pulgar conserva sus intervalos
0..30, 0..40, 0..35 y 0..20 grados, sus ejes, su posicion y su geometria.

Para validar en Fusion, anima las relaciones de `JUNTA_DEDO_1_1` y despues
`JUNTA_PULGAR_1`: deben cerrar hacia caras opuestas y encontrarse sobre la
palma sin cambiar la posicion abierta.

La 1.0.34 conserva la forma de giro validada visualmente en la 1.0.33, pero
refleja toda la implantacion del pulgar al lado opuesto del cierre de los dedos
principales. El anclaje, el cardan, las tres falanges y sus cuatro ejes se
transforman como un único mecanismo respecto al plano medio Y=48,4595 mm.

El pulgar abierto queda en la cara Y positiva, con la raiz en Y=68,0641 mm y
el anclaje en la misma cara exterior, Y=58,4595 mm. Al cerrar, las falanges
proximales permanecen fuera de la cubierta y la yema gira hacia dentro hasta
Y=47,32 mm. La horquilla abierta de 10 mm evita que el cardan nazca dentro de
la base maciza.

Se conservan los recorridos 30/40/35/20, la separacion de 76 grados entre los
ejes de base, las 20 juntas, las 15 relaciones y todas las fijaciones.

La 1.0.33 corrige el signo de profundidad de la 1.0.32. Los dedos principales
cierran hacia la cara Y positiva, por lo que el pulgar debe partir en la cara
opuesta. La cadena se desplaza 16 mm hacia Y negativa y los dos ejes del cardan
se recalculan con una separacion aproximada de 76 grados.

La abertura del soporte aumenta de 7,2 a 10 mm y atraviesa el extremo de la
base reforzada, formando una horquilla real alrededor del cardan. Durante el
cierre calculado, los tres puntos proximales se mantienen fuera de la palma en
Y=28,9, 25,7 y 28,2 mm. Despues la cadena cruza bajo el borde: la siguiente
articulacion alcanza Y=38,9 mm y la yema Y=49,6 mm para oponerse a los dedos.

Se conservan los recorridos 30/40/35/20, las 20 juntas, las 15 relaciones y
las fijaciones completas del brazo, de la mano y de la palma.

La 1.0.32 corrige la penetracion fisica visible en las vistas lateral y oblicua
de la 1.0.31. La base reforzada terminaba en un volumen macizo alrededor del
primer pivote, por lo que el cardan y la primera falange atravesaban la propia
palma al cerrar.

Ahora la base incorpora una cuna abierta de 7,2 mm de radio entre los dos ejes
del cardan. La cadena completa del pulgar se adelanta 14 mm hacia la cara
palmar y sus ejes cruzados se recalculan con una separacion aproximada de 88
grados. En la postura cerrada calculada, los tres puntos proximales quedan a
58,9, 61,9 y 63,9 mm de profundidad, delante de la cubierta, mientras la yema
regresa a 54,4 mm para oponerse a los dedos.

Se conservan los recorridos 30/40/35/20, las 20 juntas, las 15 relaciones y
las fijaciones completas del brazo, de la mano y de la palma.

La 1.0.31 afina la trayectoria observada en las dos animaciones de la 1.0.30.
Reduce el barrido lateral de la primera junta del pulgar de 40 a 30 grados,
aumenta la oposicion de la segunda de 30 a 40 grados, mantiene 35 grados en la
tercera y reduce la terminal de 25 a 20 grados. El objetivo es eliminar la
forma de Z, redondear el cierre y orientar mejor la yema hacia los dedos.

Se conserva sin cambios el cardan de ejes cruzados, los 21 componentes, las 20
juntas, las 15 relaciones de movimiento, los cuatro dedos principales y todas
las fijaciones del brazo y de la mano.

La 1.0.30 incorpora un pequeño cardan entre la palma y la primera falange del
pulgar. Sus dos ejes de base se cruzan aproximadamente 78 grados: el primero
produce un barrido lateral de 40 grados y el segundo añade 30 grados de
oposicion hacia los tres dedos derechos. Las dos bisagras distales, paralelas
al eje de oposicion, aportan 35 y 25 grados para completar el cierre natural.

La cadena del pulgar pasa a tener cuatro juntas y tres relaciones de cierre.
La mano contiene 21 componentes, 20 juntas revolutas y 15 relaciones de
movimiento. Se mantienen los limites 60/60/50/40 de los cuatro dedos
principales y la fijacion del brazo, del conjunto de mano y de la palma.

La 1.0.29 sustituye el barrido plano del pulgar de la 1.0.28 por una flexion
oblicua. El eje se calcula a partir del rayo abierto del pulgar y del centro de
las raices de los tres dedos situados a su derecha. Las tres bisagras quedan
paralelas en ese plano y usan 50/25/15 grados; esta combinacion lleva la punta
hacia dicho centro con una curva continua y evita plegarla sobre si misma.

Tambien fija a la raiz el componente superior completo. La mano y la palma ya
estaban fijadas internamente, pero Fusion podia escoger el brazo como lado
movil al animar relaciones desde `JUNTA_DEDO_n_2`, `_3` o `_4`. Esta fijacion
mantiene inmovil todo el brazo independientemente de la junta conducida.

La 1.0.28 corrige la trayectoria del pulgar observada en la animacion de la
1.0.27. Su primera bisagra deja de usar el mismo eje transversal que las otras
dos: ahora gira alrededor de la normal negativa de la palma. En la postura
frontal aprobada, este eje desplaza el pulgar hacia los tres dedos situados a
su derecha y crea el movimiento de oposicion.

Las juntas segunda y tercera mantienen sus ejes transversales para curvar la
punta durante la oposicion. Se conservan los recorridos 60/55/45 grados, las
dos relaciones de movimiento del pulgar y todos los valores de los cuatro
dedos principales.

La 1.0.27 aumenta el cierre de los dedos principales con un reparto progresivo
de 60/60/50/40 grados. Las dos primeras juntas acercan toda la cadena a la
palma; las dos ultimas orientan la punta sin plegarla en exceso sobre si misma.

El pulgar queda adaptado a 60/55/45 grados y recibe dos relaciones de
movimiento. En total se crean catorce relaciones: doce para los cuatro dedos
principales y dos para el pulgar. Los valores de cada relacion reproducen la
proporcion de los limites y los topes fisicos correspondientes.

La 1.0.26 limita a 45 grados cada una de las cuatro juntas de los dedos
principales. Los topes fisicos se regeneran con el mismo recorrido. El cierre
acumulado puede alcanzar 180 grados, pero se reparte entre las cuatro falanges
en vez de concentrar 90 grados o mas en cada nudillo.

Tambien crea doce relaciones de movimiento: la primera junta de cada dedo
controla las otras tres con relacion 1:1. Para comprobar el cierre conjunto en
Fusion debe usarse `Animar relaciones de unión` sobre `JUNTA_DEDO_n_1`.
`Editar límites de movimiento` sigue previsualizando una junta aislada.

La 1.0.25 corrige el sentido estructural observado al animar
`JUNTA_DEDO_1_1` en la 1.0.24. Fusion mueve el primer componente indicado al
crear una junta respecto al segundo. La versión anterior entregaba primero la
palma o la falange proximal, de modo que la animación desplazaba la mano
completa alrededor del dedo seleccionado.

Ahora cada junta entrega primero la falange distal y después la palma o
falange proximal. También fija temporalmente `06_MANO_ARTICULABLE` a su
componente padre, además de mantener fijada la palma dentro del subconjunto.
Al animar una junta debe permanecer inmóvil el brazo y girar únicamente la
falange seleccionada. `Animar relaciones de unión` permitirá comprobar después
el movimiento de toda la cadena distal.

La 1.0.24 utiliza la jerarquía validada en la 1.0.23 para crear 19 juntas
revolutas reales: cuatro por cada dedo principal y tres para el pulgar. La
palma queda fijada al componente `06_MANO_ARTICULABLE`; cada falange mantiene
un único grado de libertad alrededor del pasador transversal correspondiente.

El eje de cada junta se obtiene directamente de un borde circular del pasador.
El script verifica que su radio sea 2 mm y que su normal coincida con el eje
transversal calculado. Si la orientación del borde está invertida, invierte
también el intervalo angular para conservar el cierre hacia la palma.

Las juntas principales usan límites 0–90°, 0–100°, 0–85° y 0–65°. Las juntas
del pulgar usan 0–70°, 0–90° y 0–75°. Fusion puede conducir cada junta dentro
de esos intervalos sin recolocar la postura abierta durante su creación.

La 1.0.23 conserva exactamente la geometría y los topes validados en la
1.0.22, pero reorganiza la mano como un conjunto mecánico. Bajo el componente
`06_MANO_ARTICULABLE` crea 20 componentes hijos: la palma, las 16 falanges de
los cuatro dedos principales y las tres falanges del pulgar.

En cada articulación, los dos casquillos exteriores y el pasador desmontable
pertenecen al componente proximal. El casquillo central pertenece al componente
distal junto con su falange. Esta distribución hace que cada pareja comparta
el mismo eje físico y deja preparada la jerarquía necesaria para crear juntas
revolutas con límites angulares en la siguiente etapa.

Los sólidos conservan sus coordenadas globales y las ocurrencias nuevas usan
transformación identidad. Por ello la postura, la alineación con la muñeca y
la silueta no deben cambiar respecto a la 1.0.22. El recuento sigue siendo de
96 cuerpos para la mano y 101 para el conjunto completo.

La 1.0.22 conserva la mano, la palma y los 96 cuerpos validados en la 1.0.21.
Cada nudillo incorpora ahora un tope móvil unido al casquillo central y dos
topes fijos unidos a los casquillos exteriores. Son nervios cilíndricos de
1,25 mm de radio que se integran mediante unión booleana, de modo que no crean
piezas sueltas ni interfieren con el taladro o con la extracción del pasador.

Los recorridos nominales de los cuatro nudillos de cada dedo son 90°, 100°,
85° y 65° desde la palma hacia la punta. Los tres recorridos del pulgar son
70°, 90° y 75°. La posición angular incluye el radio de contacto de ambos
topes para que el contacto ocurra al alcanzar el límite y no antes.

Esta versión comprueba en Fusion la creación de las uniones booleanas y que
los topes permanezcan fuera del taladro. Los canales de accionamiento y la
conversión de falanges a componentes móviles quedan para la etapa siguiente.

La 1.0.21 conserva la geometría exterior aprobada en la 1.0.20 y sustituye los
19 cilindros visuales de los dedos por articulaciones mecánicas. Cada nudillo
contiene dos casquillos exteriores, un casquillo central y un pasador coaxial
independiente.

El pasador tiene 4 mm de diámetro y sobresale 1 mm por cada lado. Los casquillos
usan un taladro de 4,70 mm, equivalente a 0,35 mm de holgura radial, y dejan
0,40 mm de separación axial a cada lado del casquillo central. Los cuatro
cuerpos permiten comprobar visualmente el montaje y mantienen accesible el
pasador para desmontaje.

Esta etapa valida primero los casquillos, taladros y pasadores en Fusion. Los
límites nominales previstos son 90° / 100° / 85° / 65°. Los topes físicos y los
canales de accionamiento se incorporarán después de confirmar que los 19
conjuntos se generan sin errores y mantienen la silueta aprobada.

La 1.0.20 elimina la forma de campana visible en la vista inferior. La
profundidad de la palma negra baja de 44 a 20 mm en el nacimiento de los dedos,
frente a falanges de 14–15 mm. Aumenta gradualmente a 21, 22, 24 y 26 mm al
acercarse al conector de muñeca, cuyo diámetro de 26 mm queda completamente
recibido.

El desplazamiento del centro en profundidad se reduce de 8 a 2,5 mm para que
la palma se lea como una placa humanoide. Los cuatro dedos se trasladan 5,5 mm
con la nueva superficie de nudillos; sus longitudes, alineación, ejes, arco
cubital, cunas separadas y terminales abombadas permanecen intactos.

La 1.0.19 conserva exactamente la alineación de palma, nudillos y dedos de la
1.0.18. Sustituye las esferas terminales por falanges blancas de cuatro
secciones: mantienen su anchura durante el 68 % de la longitud y se reducen
progresivamente hasta un extremo abombado. La terminal recibe ahora el 27 % de
la longitud total de cada dedo.

Las cunas de los nudillos reducen su radio a 7 mm y penetran 6 mm en la palma.
Así permanecen separadas por material visible en vez de formar un borde recto
continuo. El arco transversal se reparte en 1,5 / 0 / 2,5 / 5 mm desde el índice
hasta el meñique, aumentando la capacidad de ahuecar la palma hacia el lado
cubital. El pulgar utiliza la misma terminal abombada sin esfera.

La 1.0.18 usa el conector negro de muñeca como eje maestro de toda la mano.
La palma rota 13,40 grados respecto a la postura heredada, sus centros locales
se alinean sobre una recta y la fila de nudillos se construye perpendicular a
ese eje. Los cuatro dedos salen paralelos al conector, sin abanico ni torsión.

La palma mide ahora 60 mm de longitud y conserva 76 × 44 mm en los nudillos.
Cuatro cunas redondeadas se integran en su borde para recibir las articulaciones
proximales. Los dos dedos centrales avanzan 2 mm en profundidad para crear un
arco palmar suave. Las falanges terminales blancas son más largas y anchas.

El pulgar rota junto con la palma, aumenta hasta 18 × 16 mm en su base y su
tercera falange se convierte en una terminal blanca alargada y redondeada.

La 1.0.17 gira los ejes de los nudillos 90 grados respecto a la prueba anterior.
Cada eje se calcula como el transversal del rayo local de su dedo: atraviesa el
ancho de la falange y permite que el movimiento ocurra en profundidad, hacia la
palma. En frontal debe leerse como una banda y en lateral como un círculo.

La palma crece moderadamente hasta 76 × 44 mm en el borde de nudillos. Las
raíces se separan 16,5 mm, las carcasas aumentan aproximadamente un 10 %, las
longitudes crecen un 3 % y la falange blanca terminal recibe más longitud y
volumen. El pulgar conserva la oposición neutra y usa su propio eje transversal
oblicuo, calculado desde su dirección.

La 1.0.16 convierte el esqueleto cinemático de la 1.0.15 en una mano modular
más próxima a las referencias. Las falanges principales aumentan hasta
14 × 13 mm en la base y 13 × 12,5 mm en la punta. Entre ellas aparecen nudillos
cilíndricos transversales independientes, incluido el nudillo de la palma.

Los cuatro dedos conservan sus longitudes diferentes, separan sus raíces a
15 mm y forman un abanico neutro total de 6 grados. La cuarta falange es blanca,
alargada y redondeada. El borde de la palma crece hasta 68 × 40 mm para rodear
las bases. El pulgar queda recto en oposición neutra y recibe tres nudillos
independientes. Las futuras posturas curvas se obtendrán girando estos cuerpos.

La 1.0.15 corrige la cinemática visual de los cuatro dedos principales usando
las nuevas referencias `manos robot.png` y `Copy_arm_design_from_image_202608242013.jpeg`.
Cada dedo nace en la posición ya aprobada y queda recto en reposo. Su eje tiene
una ligera convergencia hacia el centro de agarre, pero ninguna falange contiene
una curvatura permanente.

Cada dedo se divide ahora en cuatro cuerpos articulables: tres falanges negras
y una falange terminal blanca con punta redondeada. La longitud total de cada
dedo se conserva y se reparte en proporciones 29/27/24/20. La futura postura de
agarre se obtendrá girando las uniones transversales entre cuerpos.

La 1.0.13 colocó la rótula en el centro del perfil terminal, pero ese perfil
incluye la antigua protuberancia lateral de la horquilla. Por eso la muñeca
apareció desplazada aunque su salida siguiera la dirección del antebrazo.

La 1.0.14 conserva la altura longitudinal del extremo y toma el centro
transversal del primer perfil estable del núcleo. La corrección es de
0,08 mm en X, -23,49 mm en Y y 0,02 mm en Z. La envolvente, la rótula, el
conector y la mano completa se trasladan juntos, de modo que el esfuerzo entra
por el centro resistente del antebrazo y todas las uniones permanecen alineadas.

Las capturas de la 1.0.12 validaron la nueva mano y el pulgar reforzado. También
mostraron que la protección blanca de muñeca seguía abierta como una horquilla,
dejando demasiado vástago negro visible y concentrando el esfuerzo en la salida.

La 1.0.13 sustituye ese alojamiento por una envolvente esférica blanca R31,80 mm
unida al antebrazo. En su interior deja una cavidad para la rótula negra R13,36
mm y abre un único conducto inferior alineado con el eje del antebrazo. El
conector negro aumenta de R11 a R13 mm y nace exactamente en el centro de la
rótula. La protección queda cerrada delante, detrás y en ambos laterales; solo
queda abierta la salida necesaria hacia la palma.

Las vistas frontal y lateral derecha de la 1.0.11 confirmaron la nueva palma,
pero mostraron que el pulgar seguía comportándose como una pinza en voladizo:
su raíz estaba demasiado alejada en profundidad y dependía de un enlace fino.

La 1.0.12 adopta la arquitectura de `concepto_mano_5_dedos.png` y del módulo
`arms_exterior_95cm.scad` del repositorio. El pulgar nace de una base lateral
R12 mm integrada en la palma, permanece cerca de su plano de trabajo y utiliza
tres falanges robustas de 16 × 14, 14 × 12 y 12 × 10 mm. Los centros de sus
tramos quedan separados aproximadamente 28,6, 20,0 y 15,3 mm. Los cuatro dedos
principales, la palma 1.0.11 y todas las articulaciones del brazo se conservan.

Fusion creó correctamente la 1.0.10 y confirmó las nuevas falanges rectangulares
redondeadas. La revisión visual mostró que la palma negra era demasiado corta
y profunda, con una apertura que recordaba a una campana. La 1.0.11 conserva
la articulación de muñeca, el metacarpiano del pulgar y las cinco trayectorias,
pero rehace la silueta de la palma con cinco perfiles.

La palma mide 51 mm entre el frente de nudillos y la muñeca. Su ancho disminuye
de 60 a 38 mm y su profundidad de 36 a 26 mm. Así queda más larga, delgada y
claramente separada de la articulación circular de la muñeca.

Las capturas de la 1.0.9 validaron la unión del pulgar, la posición de la mano
y las proporciones de sus cinco trayectorias. La 1.0.10 conserva exactamente
los puntos medidos y el recorte de 0,6 mm en cada extremo de falange. Sustituye
solo los cilindros provisionales por carcasas macizas de sección rectangular
redondeada, con una reducción del 6 % hacia la punta. Cada dedo decrece de
11 × 10 a 9 × 8 mm; el pulgar decrece de 14 × 12 a 12 × 10 mm.

Esta versión sigue usando cuerpos independientes para cada falange. La prueba
comprueba el acabado exterior; los pasadores, las holguras de giro y el espesor
de pared se definirán después de aprobar la silueta.

La 1.0.8 corrigió el volumen de la palma y la posición de los cuatro dedos.
Las capturas mostraron que la primera falange del pulgar quedaba separada en
el espacio. La 1.0.9 añade un metacarpiano negro R8 mm desde el centro interior
del extremo proximal de la palma hasta la raíz medida del pulgar. Se une a la
palma, solapa con la primera falange y conserva la trayectoria del pulgar.

La 1.0.7 confirmó la colocación de la mano, pero la palma quedó sobredimensionada
porque la envolvente incluía también la rama del pulgar. La 1.0.8 rastrea el
intervalo principal de la palma por separado: el ancho pasa de 53,80 a 56,74
mm y la profundidad central se reduce progresivamente de 80 a 62 mm. Los
cuatro dedos se desplazan sobre ese intervalo principal para que sus bases
queden dentro de la palma. El pulgar conserva su trayectoria independiente.

Las vistas de Fusion validaron el hombro y la muñeca de la 1.0.6. La 1.0.7
añade una primera reconstrucción completa de la mano. La palma utiliza cuatro
secciones locales estables del contorno medido; un enlace negro R11 mm la une
al eje de muñeca. Los cuatro dedos tienen tres falanges independientes y el
pulgar dos. Las trayectorias X/Z proceden de las guías frontales y la posición
Y de las guías laterales transformadas al marco propio de la mano. Las puntas
son cuerpos blancos separados.

Esta etapa valida postura y proporciones exteriores. Las falanges aún son
cilíndricas y no incluyen pasadores ni límites de giro; se mantienen separadas
para reemplazarlas por carcasas detalladas después de validar el conjunto.

Las vistas frontal y lateral validaron el codo de la 1.0.5. La 1.0.6 conserva
sin cambios esa geometría y utiliza los dos perfiles terminales que no podían
interpolarse como articulaciones independientes. El extremo del brazo define
un alojamiento lateral de hombro de 110,63 mm de diámetro y 17,86 mm de
longitud. El extremo del antebrazo define una brida de muñeca de 63,60 mm de
diámetro y 10,32 mm de longitud. Ambos reciben ejes negros separados con 0,8
mm de holgura radial.

El loft del brazo termina ahora antes del perfil de hombro y el del antebrazo
antes del perfil de muñeca. Así se elimina la extensión provisional de perfil
constante y cada cambio abrupto corresponde a una pieza real del conjunto.

La vista lateral de la 1.0.4 validó el aro y el eje. La frontal mostró que un
cilindro blanco continuo cerraba el hueco central. La 1.0.5 divide el
alojamiento en dos mejillas laterales de 8,89 mm y deja entre ellas la abertura
de 47,57 mm medida en el contorno frontal. El eje y el enlace negros quedan
visibles en el centro, mientras la vista lateral conserva el aro blanco.

La comparación de la 1.0.3 con el lateral de referencia mostró que el eje era
correcto, pero todavía faltaban dos volúmenes visibles: el alojamiento circular
blanco solidario al antebrazo y el enlace negro entre el extremo del brazo y
el pivote. La 1.0.4 los añade alrededor del mismo centro ya validado.

El alojamiento exterior usa R27,78 mm y el taladro mantiene 0,8 mm de holgura
respecto al eje. El brazo se recorta alrededor del alojamiento completo para
evitar solapes. El eje y su enlace forman un cuerpo negro independiente del
antebrazo, conservando la separación necesaria para una articulación futura.

Las capturas de la 1.0.2 confirman que el eje se ve como puente rectangular
en frontal y como círculo en lateral. La 1.0.3 corta en las dos carcasas sendos
alojamientos coaxiales con el mismo eje y 0,8 mm de holgura radial. El cortador
penetra 2,3 mm desde cada plano terminal para eliminar el contacto plano sin
debilitar el núcleo. El eje continúa siendo un cuerpo independiente.

Las capturas de Fusion de la 1.0.1 validaron los dos núcleos: superficies
continuas, silueta frontal estable y profundidad sin pliegues. La 1.0.2
prolonga el perfil estable más próximo hasta cada plano terminal medido. De
esta forma completa la longitud sin interpolar los radios extremos que
autointersectaban el loft. Los collares solapan 0,5 mm con el núcleo antes de
unirse.

El hueco entre los planos opuestos del brazo y antebrazo determina ahora un
eje transversal de codo independiente. Su centro y radio proceden de esos dos
planos, y su dirección es la normal frontal media de los enlaces. Sigue siendo
una validación volumétrica: aún no define tolerancias, rodamientos ni espesor.

Fusion rechazó el loft completo 1.0.0 por autointersección. El diagnóstico
numérico localizó el pliegue en los cambios extremos: el último salto del brazo
y el primero y los dos últimos del antebrazo cambian de centro/radio más rápido
que su separación longitudinal. La 1.0.1 selecciona automáticamente el tramo
continuo más largo con razón de cambio local máxima 1.5. Conserva las 17
secciones medidas en el JSON; únicamente aplaza los perfiles terminales para
que esta ejecución valide primero los dos volúmenes principales.

Las vistas frontal y lateral muestran posturas distintas. Sus guías confirman
que no representan el mismo eje global: brazo 161.20/120.81 mm y antebrazo
90.25/131.53 mm en frontal/lateral. Cruzarlas mediante planos horizontales Z,
como en las pruebas 1.0.2–1.0.10, mezcla regiones longitudinales distintas.

Esta prueba no reinicia los trazados. Convierte cada contorno existente a un
marco propio definido por `upper_shell_axis` o `forearm_shell_axis`. En cada
vista mide la envolvente perpendicular a ese eje y empareja ancho/profundidad
por posición longitudinal normalizada. Luego orienta el sólido con el eje
frontal, que sigue siendo la postura maestra. El lateral aporta profundidad,
sin imponer su postura global.

Se usa Y=45 mm como plano neutro compartido para colocar ambos enlaces en la
postura frontal. Es una colocación visual de prueba, no una cota mecánica. La
geometría conserva desplazamientos locales respecto a las guías, por lo que
las secciones no quedan forzadas a centros simétricos.

Los extremos se limitan a un intervalo continuo con ancho y profundidad de al
menos 10 mm. Hay 17 secciones por pieza, más densas cerca de los extremos.
Cuando un rebaje crea varios intervalos se usa la envolvente exterior; por eso
esta primera prueba local no contiene aberturas. Tampoco incluye articulaciones,
mano, espesor o mecanismo.

Ejecutar `Toreto_Brazo_Marcos_Locales_95cm`. Crea
`94_BRAZO_MARCOS_LOCALES_PRUEBA_01` sin modificar las pruebas 90–92 ni los
lienzos. Ocultar manualmente los demás brazos para comparar superficies y la
silueta frontal. No se espera superposición con el lienzo lateral mientras el
modelo esté en la postura frontal.

La sintaxis y los cálculos numéricos se comprueban localmente. La ejecución del
loft y la calidad de sus superficies requieren Fusion. El usuario guarda el
documento de Fusion.
