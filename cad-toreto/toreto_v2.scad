// Robot Toreto - V2
// Rediseno desde cero para parecerse al robot de la infografia
// "Robot Asistente Inteligente": formas redondeadas, cabeza pildora con
// pantalla negra completa, torso que se estrecha hacia la cintura,
// brazos delgados con juntas esfericas negras y manos con dedos,
// base blanca tipo tambor con 3 ruedas omni asomando.
//
// Altura 95 cm, base 40 cm. Unidades: mm.
// Maqueta visual: sin mecanica funcional todavia.
// Toda pieza imprimible se disena para caber en Bambu P1S (256x256x256).

$fn = 96;

part = "assembly";
exploded = false;
show_height_marker = false;

// Pose de los brazos [j1, j2, j3, j4, j5, j6] — ver arm_assembly().
// Cambia estos valores y previsualiza para probar el rango de movimiento.
pose_left = [0, 4, 16, 0, 0, 0.25];
pose_right = [0, 4, 16, 0, 0, 0.25];

target_height = 950;
base_d = 400;

wall = 3.2;

// Alturas de cada zona (suma ~930 mm).
chassis_h = 70;      // chasis negro inferior + ruedas
drum_h = 170;        // tambor blanco de la base
taper_h = 110;       // segundo nivel de la base (mas estrecho)
waist_h = 120;       // columna central negra
torso_h = 270;       // torso blanco
neck_h = 45;         // cuello negro
head_h = 145;        // cabeza

z_drum = chassis_h;
z_taper = z_drum + drum_h;
z_waist = z_taper + taper_h;
z_torso = z_waist + waist_h;
z_neck = z_torso + torso_h;
z_head = z_neck + neck_h;

head_w = 212;
head_d = 138;

torso_top_w = 242;
torso_top_d = 165;
torso_bot_w = 198;
torso_bot_d = 148;

white = [0.92, 0.91, 0.88];
black = [0.045, 0.048, 0.05];
dark = [0.10, 0.105, 0.11];
blue = [0.05, 0.62, 0.95];
glass = [0.01, 0.015, 0.02];

// ----------------- Utilidades -----------------

module rounded_rect_2d(size=[20, 20], r=4) {
    hull() {
        translate([r, r]) circle(r=r);
        translate([size[0]-r, r]) circle(r=r);
        translate([r, size[1]-r]) circle(r=r);
        translate([size[0]-r, size[1]-r]) circle(r=r);
    }
}

module rounded_box(size=[20, 20, 20], r=4, center=true) {
    translate(center ? [-size[0]/2, -size[1]/2, -size[2]/2] : [0, 0, 0])
        linear_extrude(height=size[2])
            rounded_rect_2d([size[0], size[1]], min(r, min(size[0], size[1]) / 2 - 0.1));
}

// Caja tipo pildora: redondeada en las 3 dimensiones (hull de 8 esferas).
module soft_box(size=[40, 40, 40], r=12) {
    hx = size[0]/2 - r; hy = size[1]/2 - r; hz = size[2]/2 - r;
    hull() {
        for (x=[-hx, hx], y=[-hy, hy], z=[-hz, hz])
            translate([x, y, z]) sphere(r=r);
    }
}

// Capsula entre dos puntos (para segmentos de brazo).
module capsule(p1=[0,0,0], p2=[0,0,-100], d=50) {
    hull() {
        translate(p1) sphere(d=d);
        translate(p2) sphere(d=d);
    }
}

module mirror_x(enabled=false) {
    if (enabled) mirror([1, 0, 0]) children();
    else children();
}

module front_half(size=[1000, 1000, 1000]) {
    translate([0, -size[1]/4, 0]) cube([size[0], size[1]/2, size[2]], center=true);
}

module back_half(size=[1000, 1000, 1000]) {
    translate([0, size[1]/4, 0]) cube([size[0], size[1]/2, size[2]], center=true);
}

module m3_hole(h=20) { cylinder(h=h, d=3.25, center=true); }
module m4_hole(h=24) { cylinder(h=h, d=4.35, center=true); }

module screw_boss(h=14, od=9, id=3.25) {
    difference() {
        cylinder(h=h, d=od, center=true);
        cylinder(h=h+0.6, d=id, center=true);
    }
}

// ----------------- Base movil (piezas 11/12) -----------------

// Perfil de revolucion del cuerpo blanco de la base: tambor inferior ancho
// con borde superior redondeado + segundo nivel mas estrecho, como en la
// referencia. shrink > 0 genera el solido interior para vaciar la carcasa.
module base_white_solid(shrink=0) {
    s = shrink;
    r1 = base_d/2;    // tambor inferior
    r2 = 128;         // segundo nivel
    rotate_extrude($fn=128)
        polygon([
            [0, s],
            [r1 - 12 - s, s],
            [r1 - 3 - s, 10],
            [r1 - s, 26],
            [r1 - s, drum_h - 34],
            [r1 - 4 - s, drum_h - 16],
            [r1 - 16 - s, drum_h - 6],
            [r1 - 32 - s, drum_h - s],
            // plataforma superior del tambor
            [r2 + 12, drum_h - s],
            // segundo nivel con borde redondeado
            [r2 - s, drum_h + 14],
            [r2 - s, drum_h + taper_h - 28],
            [r2 - 5 - s, drum_h + taper_h - 12],
            [r2 - 18 - s, drum_h + taper_h - s],
            [0, drum_h + taper_h - s]
        ]);
}

// Chasis negro inferior con huecos para las 3 ruedas omni.
module chassis_black() {
    difference() {
        union() {
            translate([0, 0, chassis_h/2 + 8])
                cylinder(h=chassis_h - 16, d=base_d - 24, center=true);
            // falda inferior
            translate([0, 0, 14]) cylinder(h=28, d=base_d - 44, center=true);
        }
        for (a=[90, 210, 330]) {
            rotate([0, 0, a])
                translate([0, -(base_d/2 - 62), 52])
                    cube([150, 100, 130], center=true);
        }
    }
}

// Rueda omnidireccional decorativa (item 13, pieza comprada).
module omni_wheel_dummy() {
    rotate([0, 90, 0]) {
        color(black) cylinder(h=56, d=118, center=true);
        color(dark) cylinder(h=60, d=62, center=true);
        // rodillos perimetrales
        for (a=[0:30:330])
            rotate([0, 0, a])
                translate([52, 0, 0])
                    rotate([90, 0, 0])
                        color([0.14, 0.14, 0.15])
                            scale([1, 1, 0.55]) sphere(d=34);
    }
}

// Banda frontal de sensores.
module sensor_band() {
    difference() {
        rotate([0, 0, 0])
            intersection() {
                translate([0, 0, 0]) cylinder(h=34, d=base_d + 4, center=true);
                translate([0, -base_d/2 + 20, 0]) cube([200, 60, 36], center=true);
            }
        translate([0, 0, 0]) cylinder(h=38, d=base_d - 26, center=true);
        for (x=[-52, 0, 52])
            translate([x, -base_d/2 - 2, 2])
                rotate([90, 0, 0]) cylinder(h=24, d=17, center=true);
    }
}

// Puck LIDAR decorativo (item 14, pieza comprada).
module lidar_dummy() {
    color(black) cylinder(h=34, d=72, center=true);
    color(dark) translate([0, 0, 12]) cylinder(h=14, d=62, center=true);
    color(blue) translate([0, 0, 2]) cylinder(h=6, d=74, center=true);
}

// Cuadrante del tambor de la base para imprimir (4 uds). Hueco interior.
module base_drum_quadrant() {
    difference() {
        intersection() {
            base_white_solid(0);
            translate([base_d/4 + 60, base_d/4 + 60, (drum_h + taper_h)/2])
                cube([base_d/2 + 120, base_d/2 + 120, drum_h + taper_h + 4], center=true);
        }
        base_white_solid(wall);
        // taladros de union entre cuadrantes
        for (z=[30, drum_h - 30, drum_h + 40]) {
            rr = z > drum_h ? base_d/2 - 70 : base_d/2 - 11;
            translate([rr - 8, 12, z]) rotate([90, 0, 0]) m4_hole(30);
            translate([12, rr - 8, z]) rotate([0, 90, 0]) m4_hole(30);
        }
    }
}

module base_assembly() {
    color(black) chassis_black();
    for (a=[90, 210, 330])
        rotate([0, 0, a])
            translate([0, -(base_d/2 - 62), 59])
                rotate([0, 0, 90]) omni_wheel_dummy();
    color(white)
        difference() {
            translate([0, 0, z_drum]) base_white_solid(0);
            // ranura negra decorativa a media altura del tambor
            translate([0, 0, z_drum + drum_h*0.42])
                difference() {
                    cylinder(h=10, d=base_d + 2, center=true);
                    cylinder(h=12, d=base_d - 14, center=true);
                }
        }
    color(black) translate([0, 0, z_drum + drum_h*0.42])
        difference() {
            cylinder(h=9, d=base_d - 2, center=true);
            cylinder(h=11, d=base_d - 16, center=true);
        }
    color(black) translate([0, 0, z_drum + 42]) sensor_band();
    translate([0, -108, z_taper + taper_h - 4]) lidar_dummy();
}

// ----------------- Columna central (pieza 9) -----------------

module waist_column() {
    difference() {
        union() {
            cylinder(h=waist_h, d=104);
            translate([0, 0, 0]) cylinder(h=18, d=142);
            translate([0, 0, waist_h - 18]) cylinder(h=18, d=132);
            // una sola vertebra central
            translate([0, 0, waist_h*0.52]) cylinder(h=14, d=120, center=true);
        }
        cylinder(h=waist_h*3, d=44, center=true);
        for (a=[0:90:270]) {
            rotate([0, 0, a]) translate([52, 0, 9]) m4_hole(20);
            rotate([0, 0, a]) translate([48, 0, waist_h - 9]) m4_hole(20);
        }
    }
}

// Caja electronica trasera (pieza 10), pegada a la columna central.
module electronics_box() {
    difference() {
        soft_box([140, 76, 104], r=14);
        soft_box([140 - 2*wall, 76 - 2*wall, 104 - 2*wall], r=11);
        translate([0, -38, 0]) rounded_box([84, 14, 56], r=8, center=true);
    }
}

// ----------------- Torso (piezas 4/5) -----------------

// Solido del torso: ancho en hombros, estrecho en cintura.
module torso_solid(shrink=0) {
    s = shrink;
    hull() {
        // cintura
        translate([0, 0, 42])
            soft_box([torso_bot_w - 2*s, torso_bot_d - 2*s, 74], r=33);
        // pecho / hombros
        translate([0, 0, torso_h - 70])
            soft_box([torso_top_w - 2*s, torso_top_d - 2*s, 124], r=54);
    }
}

module torso_shell(side="front") {
    difference() {
        intersection() {
            difference() {
                torso_solid(0);
                torso_solid(wall);
            }
            translate([0, 0, torso_h/2])
                if (side == "front") front_half([360, 300, torso_h + 20]);
                else back_half([360, 300, torso_h + 20]);
        }
        // hueco pantalla tactil del pecho
        if (side == "front")
            translate([0, -torso_top_d/2 - 6, torso_h - 118])
                rounded_box([132, 40, 96], r=16, center=true);
        // puerto de servicio trasero
        if (side == "back")
            translate([0, torso_top_d/2 - 26, 60])
                rounded_box([100, 40, 46], r=10, center=true);
    }
    // torretas de tornillo para unir mitades
    for (x=[-72, 72], z=[70, torso_h - 80])
        translate([x, side == "front" ? -20 : 20, z])
            rotate([90, 0, 0]) screw_boss(h=22, od=10, id=3.25);
}

// Pantalla del pecho (insercion negra con onda azul).
module torso_screen() {
    color(glass) rounded_box([128, 8, 92], r=14, center=true);
    color(blue)
        for (x=[-44:8:44]) {
            h = 8 + 26 * abs(sin(x * 11) * cos(x * 3));
            translate([x, -3, 0]) cube([2.6, 3, h], center=true);
        }
}

module torso_assembly() {
    color(white) torso_shell("front");
    color(white) torso_shell("back");
    translate([0, -torso_top_d/2 + 10, torso_h - 118]) torso_screen();
}

// ----------------- Cuello (pieza 3) -----------------

module neck_column() {
    difference() {
        union() {
            cylinder(h=neck_h, d=58);
            cylinder(h=12, d=86);
            translate([0, 0, neck_h - 12]) cylinder(h=12, d=78);
        }
        cylinder(h=neck_h*3, d=30, center=true);
        for (a=[0:120:240]) {
            rotate([0, 0, a]) translate([32, 0, 6]) m3_hole(16);
            rotate([0, 0, a]) translate([28, 0, neck_h - 6]) m3_hole(16);
        }
    }
}

// ----------------- Cabeza (piezas 1/2) -----------------

module head_solid(shrink=0) {
    soft_box([head_w - 2*shrink, head_d - 2*shrink, head_h - 2*shrink], r=56 - shrink*0.5);
}

module head_shell(side="front") {
    difference() {
        intersection() {
            difference() {
                head_solid(0);
                head_solid(wall);
            }
            if (side == "front") front_half([320, 240, 220]);
            else back_half([320, 240, 220]);
        }
        // hueco de la pantalla-cara (casi toda la cara frontal)
        if (side == "front")
            translate([0, -head_d/2 + 4, 2])
                rounded_box([180, 30, 106], r=44, center=true);
        // acceso trasero
        if (side == "back")
            translate([0, head_d/2 - 22, -14])
                rounded_box([110, 30, 52], r=12, center=true);
    }
    for (x=[-78, 78], z=[-38, 38])
        translate([x, side == "front" ? -18 : 18, z])
            rotate([90, 0, 0]) screw_boss(h=18, od=9, id=3.25);
}

// Pantalla-cara negra brillante con ojos azules.
module face_screen() {
    color(glass)
        translate([0, 0, 2])
            rounded_box([182, 10, 108], r=44, center=true);
    for (x=[-46, 46]) {
        translate([x, -6.5, 10]) {
            color(blue) rotate([90, 0, 0])
                difference() {
                    cylinder(h=3, d=34, center=true);
                    cylinder(h=5, d=24, center=true);
                }
            color(blue) rotate([90, 0, 0]) cylinder(h=3, d=9, center=true);
        }
    }
}

// Oreja / pod lateral con camara (pieza 2 se ancla detras).
module ear_pod() {
    difference() {
        scale([0.45, 1, 1]) sphere(d=100);
        translate([16, 0, 0]) rotate([0, 90, 0]) cylinder(h=22, d=34, center=true);
    }
}

// Soporte de camara RGB-D interior (pieza 2).
module camera_mount() {
    difference() {
        union() {
            rounded_box([70, 26, 30], r=6, center=true);
            translate([0, -16, 0]) rounded_box([44, 10, 20], r=4, center=true);
        }
        translate([0, -18, 0]) rotate([90, 0, 0]) cylinder(h=16, d=17, center=true);
        for (x=[-24, 24]) translate([x, 4, 0]) m3_hole(24);
    }
}

module head_assembly() {
    color(white) head_shell("front");
    color(white) head_shell("back");
    translate([0, -head_d/2 + 10, 0]) face_screen();
    color(dark) {
        translate([head_w/2 + 6, 0, 0]) ear_pod();
        translate([-head_w/2 - 6, 0, 0]) mirror([1, 0, 0]) ear_pod();
    }
    color(dark) translate([0, -head_d/2 + 42, 8]) camera_mount();
}

// ----------------- Brazo 6 DOF (piezas 6/7/8) -----------------
// El brazo se modela apuntando hacia -Z desde el hombro.

arm_upper_len = 180;
arm_fore_len = 170;

module shoulder_joint() { sphere(d=80); }

// Los segmentos empiezan desplazados del centro de la junta para dejar
// la bola negra expuesta (ahi va el eje real de giro).
module upper_arm_shell(shrink=0) {
    difference() {
        capsule([0, 0, -20], [0, 0, -arm_upper_len], 54 - 2*shrink);
        if (shrink == 0) {
            capsule([0, 0, -20], [0, 0, -arm_upper_len], 54 - 2*wall);
            translate([0, 0, -20]) m4_hole(80);
            translate([0, 0, -arm_upper_len]) rotate([90, 0, 0]) m4_hole(80);
        }
    }
}

module forearm_shell(shrink=0) {
    difference() {
        capsule([0, 0, -18], [0, 0, -arm_fore_len], 46 - 2*shrink);
        if (shrink == 0) {
            capsule([0, 0, -18], [0, 0, -arm_fore_len], 46 - 2*wall);
            translate([0, 0, -18]) rotate([90, 0, 0]) m4_hole(70);
            translate([0, 0, -arm_fore_len]) m4_hole(70);
        }
    }
}

// Dedo articulado de dos falanges, ligeramente curvado.
module finger() {
    color(black) {
        hull() {
            sphere(d=15);
            translate([0, -6, -30]) sphere(d=13);
        }
        translate([0, -6, -30])
            hull() {
                sphere(d=13);
                translate([0, -8, -24]) sphere(d=10);
            }
    }
}

// Mano-pinza con 3 dedos (pieza 8). open: 0 cerrada .. 1 abierta (DOF 6).
module gripper_hand(open=0.25) {
    ang = 34 * open;
    color(black) {
        sphere(d=42);                      // muneca
        translate([0, 0, -30]) soft_box([46, 34, 42], r=12);  // palma
    }
    // dos dedos delante, uno detras (pulgar)
    translate([-13, -10, -48]) rotate([12 + ang, 0, 0]) finger();
    translate([13, -10, -48]) rotate([12 + ang, 0, 0]) finger();
    translate([0, 12, -48]) rotate([-14 - ang, 0, 180]) finger();
}

// Soporte de brazo al torso (pieza 6).
module arm_shoulder_support() {
    difference() {
        union() {
            rotate([0, 90, 0]) cylinder(h=26, d=72, center=true);
            translate([-18, 0, 0]) soft_box([26, 60, 70], r=10);
        }
        rotate([0, 90, 0]) m4_hole(90);
    }
}

// Pod blanco de hombro del que cuelga el brazo.
module shoulder_pod() {
    scale([0.85, 0.95, 1]) sphere(d=96);
}

// Brazo articulado con los 6 DOF de la infografia.
// pose = [j1, j2, j3, j4, j5, j6]:
//   j1  rotacion base del hombro (gira el brazo sobre el eje vertical)
//   j2  elevacion del hombro (adelante/atras, 0 = colgando)
//   j3  flexion del codo (0 = estirado, positivo = doblar)
//   j4  muneca pitch
//   j5  muneca yaw (giro de la pinza)
//   j6  apertura de pinza (0 cerrada .. 1 abierta)
module arm_assembly(left=true, pose=[0, 4, 16, 0, 0, 0.25]) {
    mirror_x(!left) {
        color(white) shoulder_pod();
        translate([6, 0, -42]) {
            color(black) sphere(d=58);          // junta hombro (j1+j2)
            rotate([0, 0, pose[0]])              // j1 rotacion base
            rotate([pose[1], -7, 0]) {           // j2 elevacion
                color(white) upper_arm_shell();
                translate([0, 0, -arm_upper_len]) {
                    color(black) sphere(d=52);   // codo (j3)
                    rotate([-pose[2], 3, 0]) {   // j3 flexion codo
                        color(white) forearm_shell();
                        translate([0, 0, -arm_fore_len])
                            rotate([pose[3], 0, pose[4]])   // j4 + j5 muneca
                                gripper_hand(open=pose[5]); // j6 pinza
                    }
                }
            }
        }
    }
}

// ----------------- Ensamblaje completo -----------------

module full_assembly() {
    base_assembly();
    color(black) translate([0, 0, z_waist]) waist_column();
    color(dark) translate([0, 64, z_waist + 55]) electronics_box();
    translate([0, 0, z_torso]) torso_assembly();
    color(black) translate([0, 0, z_neck]) neck_column();
    translate([0, 0, z_head + head_h/2]) head_assembly();
    // hombros a la altura del pecho
    translate([torso_top_w/2 + 30, 0, z_torso + torso_h - 70])
        arm_assembly(true, pose_left);
    translate([-torso_top_w/2 - 30, 0, z_torso + torso_h - 70])
        arm_assembly(false, pose_right);

    if (show_height_marker)
        color([0.0, 0.55, 0.9, 0.22])
            translate([-280, 0, target_height/2])
                cube([5, 5, target_height], center=true);
}

module exploded_assembly() {
    base_assembly();
    color(black) translate([0, 0, z_waist + 120]) waist_column();
    color(dark) translate([200, 78, z_waist + 190]) electronics_box();
    translate([0, 0, z_torso + 240]) torso_assembly();
    color(black) translate([0, 0, z_neck + 360]) neck_column();
    translate([0, 0, z_head + head_h/2 + 480]) head_assembly();
    translate([torso_top_w/2 + 180, 0, z_torso + torso_h + 178]) arm_assembly(true);
    translate([-torso_top_w/2 - 180, 0, z_torso + torso_h + 178]) arm_assembly(false);
}

// ----------------- Selector de piezas -----------------
// Numero de pieza de la infografia entre parentesis.

if (part == "assembly") {
    if (exploded) exploded_assembly(); else full_assembly();
} else if (part == "head_front_shell") {           // (1)
    head_shell("front");
} else if (part == "head_back_shell") {            // (1)
    head_shell("back");
} else if (part == "ear_pod") {                    // (1) x2
    ear_pod();
} else if (part == "face_screen") {                // (1) insercion
    face_screen();
} else if (part == "camera_mount") {               // (2)
    camera_mount();
} else if (part == "neck_column") {                // (3)
    neck_column();
} else if (part == "torso_front_shell") {          // (4)
    torso_shell("front");
} else if (part == "torso_back_shell") {           // (5)
    torso_shell("back");
} else if (part == "torso_screen") {               // (4) insercion
    torso_screen();
} else if (part == "arm_shoulder_support") {       // (6) x2
    arm_shoulder_support();
} else if (part == "upper_arm_shell") {            // (7) x2
    upper_arm_shell();
} else if (part == "forearm_shell") {              // (7) x2
    forearm_shell();
} else if (part == "shoulder_joint") {             // (7) x2
    shoulder_joint();
} else if (part == "shoulder_pod") {               // (6) x2
    shoulder_pod();
} else if (part == "gripper_hand") {               // (8) x2
    gripper_hand();
} else if (part == "finger") {                     // (8) x6
    finger();
} else if (part == "waist_column") {               // (9)
    waist_column();
} else if (part == "electronics_box") {            // (10)
    electronics_box();
} else if (part == "base_drum_quadrant") {         // (11/12) x4
    base_drum_quadrant();
} else if (part == "chassis_black") {              // (12)
    chassis_black();
} else if (part == "sensor_band") {                // (15 aprox)
    sensor_band();
} else if (part == "omni_wheel_dummy") {           // (13) referencia
    omni_wheel_dummy();
} else if (part == "lidar_dummy") {                // (14) referencia
    lidar_dummy();
} else {
    full_assembly();
}
