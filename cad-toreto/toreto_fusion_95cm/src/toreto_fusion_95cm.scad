// Robot Toreto 95 cm - version fusionada aprobada por imagen
// Solo forma exterior y piezas imprimibles de referencia.
// Sin motores, esqueleto, ejes, rodamientos, cableado ni electronica.
// Unidades: milimetros.

$fn = 44;

part = "assembly";
hand_pose = "open"; // open | closed

TARGET_HEIGHT = 950;
WALL = 3.2;

BASE_D = 400;
BASE_H = 225;
TRUNK_H = 185;
WAIST_H = 100;
CHEST_H = 190;
NECK_H = 55;
HEAD_H = 195;

CHEST_W = 310;
CHEST_D = 198;
HEAD_W = 285;
HEAD_D = 175;
UPPER_ARM_L = 170;
FOREARM_L = 150;

Z_TRUNK = BASE_H;
Z_WAIST = Z_TRUNK + TRUNK_H;
Z_CHEST = Z_WAIST + WAIST_H;
Z_NECK = Z_CHEST + CHEST_H;
Z_HEAD = Z_NECK + NECK_H;

WHITE = [0.92,0.94,0.95];
WHITE_EDGE = [0.74,0.78,0.81];
BLACK = [0.018,0.024,0.031];
DARK = [0.055,0.066,0.078];
MID = [0.16,0.18,0.20];
CYAN = [0.00,0.72,0.96];
ICE = [0.78,0.94,1.00];

echo("TARGET_HEIGHT_MM", TARGET_HEIGHT);
echo("ACTUAL_HEIGHT_MM", Z_HEAD + HEAD_H);
echo("BASE_DIAMETER_MM", BASE_D);
echo("UPPER_ARM_LENGTH_MM", UPPER_ARM_L);
echo("FOREARM_LENGTH_MM", FOREARM_L);
echo("SCOPE", "EXTERIOR_ONLY_NO_MECHANICS");
assert(Z_HEAD + HEAD_H == TARGET_HEIGHT,
       str("Altura incorrecta: ", Z_HEAD + HEAD_H));

// --------------------------------------------------------------------------
// Utilidades geometricas
// --------------------------------------------------------------------------

module rr2d(size=[20,20], r=3) {
    w=size[0]; d=size[1];
    hull()
        for (x=[-1,1], y=[-1,1])
            translate([x*(w/2-r), y*(d/2-r)]) circle(r=r);
}

module rounded_prism(size=[20,20,20], r=3, center=true) {
    translate([0,0,center ? -size[2]/2 : 0])
        linear_extrude(height=size[2]) rr2d([size[0],size[1]],r);
}

module face_box(size=[100,60,80], r=20) {
    rotate([90,0,0]) rounded_prism([size[0],size[2],size[1]],r,true);
}

module soft_box(size=[20,20,20], r=4) {
    sx=size[0]; sy=size[1]; sz=size[2];
    hull()
        for (x=[-1,1], y=[-1,1], z=[-1,1])
            translate([x*(sx/2-r),y*(sy/2-r),z*(sz/2-r)]) sphere(r=r);
}

module lofted_solid(h=100, bottom=[100,80], top=[90,70], r=15) {
    hull() {
        translate([0,0,-h/2+1]) rounded_prism([bottom[0],bottom[1],2],r,true);
        translate([0,0, h/2-1]) rounded_prism([top[0],top[1],2],r,true);
    }
}

module lofted_shell(h=100, bottom=[100,80], top=[90,70], r=15, t=WALL) {
    difference() {
        lofted_solid(h,bottom,top,r);
        lofted_solid(h+2,
            [bottom[0]-2*t,bottom[1]-2*t],
            [top[0]-2*t,top[1]-2*t], max(1,r-t));
    }
}

module rounded_shell(size=[100,80,100], r=15, t=WALL) {
    difference() {
        rounded_prism(size,r,true);
        rounded_prism([size[0]-2*t,size[1]-2*t,size[2]+2],max(1,r-t),true);
    }
}

module clip_x(side=1, span=500) {
    intersection() {
        children();
        translate([side*span/4,0,0]) cube([span/2,span,span],center=true);
    }
}

module clip_y(side=1, span=500) {
    intersection() {
        children();
        translate([0,side*span/4,0]) cube([span,span/2,span],center=true);
    }
}

module positive_quadrant(span=440) {
    intersection() {
        children();
        cube([span/2,span/2,BASE_H+30],center=false);
    }
}

// --------------------------------------------------------------------------
// Base compacta: cuatro sectores, cuatro mecanum y banda de sensores
// --------------------------------------------------------------------------

module base_outer_full() {
    difference() {
        union() {
            translate([0,0,22]) cylinder(h=118,d=390);
            translate([0,0,140]) cylinder(h=31,d=400);
            hull() {
                translate([0,0,171]) cylinder(h=3,d=396);
                translate([0,0,220]) cylinder(h=3,d=350);
            }
            translate([0,0,217]) cylinder(h=8,d=252);
        }
        translate([0,0,18]) cylinder(h=210,d=382);
        translate([0,0,164]) cylinder(h=66,d=342);
        for (a=[45,135,225,315])
            rotate([0,0,a]) translate([0,-188,76])
                rounded_prism([118,96,144],25,true);
    }
}

module base_quadrant() { positive_quadrant() base_outer_full(); }

module base_sensor_band() {
    difference() {
        translate([0,0,34]) cylinder(h=104,d=382);
        translate([0,0,30]) cylinder(h=112,d=373);
        for (a=[45,135,225,315])
            rotate([0,0,a]) translate([0,-188,76])
                rounded_prism([122,100,148],26,true);
    }
}

module trim_ring() {
    difference() {
        translate([0,0,166]) cylinder(h=7,d=392);
        translate([0,0,164]) cylinder(h=11,d=352);
    }
}

module base_top_cap() {
    // Tapa superior continua: evita ver el hueco interior desde arriba.
    difference() {
        translate([0,0,216]) cylinder(h=6,d=350);
        translate([0,0,214]) cylinder(h=10,d=238);
    }
}

module wheel_arch() {
    difference() {
        rounded_prism([126,80,150],27,true);
        rounded_prism([112,86,138],22,true);
        translate([0,-46,0]) cube([150,88,180],center=true);
        translate([0,0,-76]) cube([150,110,35],center=true);
    }
}

module wheel_well_back() {
    // Fondo visual negro del paso de rueda; no es soporte ni chasis.
    rounded_prism([112,18,132],22,true);
}

module mecanum_wheel() {
    // Volumen visual, no rueda mecanica funcional.
    color(BLACK) rotate([90,0,0]) cylinder(h=42,d=92,center=true);
    color(DARK)
        for (a=[0:30:330])
            rotate([0,a,0]) translate([0,0,45])
                rotate([45,0,0]) capsule(28,11);
    color(BLACK) rotate([90,0,0]) cylinder(h=46,d=46,center=true);
    color(CYAN) rotate([90,0,0]) cylinder(h=48,d=7,center=true);
}

module capsule(len=20,d=8) {
    hull() {
        translate([0,0,-len/2]) sphere(d=d);
        translate([0,0, len/2]) sphere(d=d);
    }
}

module sensor_bezel(w=140,h=30) {
    difference() {
        face_box([w,8,h],8);
        translate([0,-1,0]) face_box([w-14,10,h-12],5);
    }
}

module sensor_insert(w=126,h=18) {
    union() {
        face_box([w,4,h],5);
        for (x=[-44,0,44]) translate([x,-3,0])
            rotate([90,0,0]) cylinder(h=3,d=x==0?7:12,center=true);
    }
}

module top_sensor() {
    color(WHITE) difference() {
        cylinder(h=14,d=88,center=true);
        cylinder(h=17,d=68,center=true);
    }
    color(BLACK) translate([0,0,20]) difference() {
        cylinder(h=34,d=64,center=true);
        translate([0,0,-2]) cylinder(h=35,d=57,center=true);
    }
    color(CYAN) translate([0,-32,20]) cube([5,2,5],center=true);
}

module base_assembly(show_wheels=true) {
    for (a=[0:90:270]) color(WHITE) rotate([0,0,a]) base_quadrant();
    color(BLACK) base_sensor_band();
    color(BLACK) trim_ring();
    color(WHITE) base_top_cap();

    for (a=[45,135,225,315]) {
        color(BLACK) rotate([0,0,a]) translate([0,-177,76]) wheel_well_back();
        color(WHITE) rotate([0,0,a]) translate([0,-192,78]) wheel_arch();
        if (show_wheels)
            rotate([0,0,a]) translate([0,-198,72]) mecanum_wheel();
    }

    for (z=[67,111]) {
        color(BLACK) translate([0,-191,z]) sensor_bezel();
        color(DARK) translate([0,-196,z]) sensor_insert();
    }
    translate([88,-108,226]) top_sensor();
}

// --------------------------------------------------------------------------
// Tronco blanco y cintura negra, ambos desmontables
// --------------------------------------------------------------------------

module trunk_shell_full() {
    lofted_shell(TRUNK_H,[252,214],[214,174],30,WALL);
}

module trunk_front() { clip_y(-1) trunk_shell_full(); }
module trunk_back() { clip_y(1) trunk_shell_full(); }

module trunk_lip() {
    difference() {
        lofted_solid(18,[225,184],[216,176],24);
        lofted_solid(20,[205,164],[196,156],18);
    }
}

module service_hatch(w=104,h=64) {
    difference() {
        face_box([w,3,h],10);
        translate([0,-1,0]) face_box([w-8,5,h-8],8);
    }
}

module trunk_assembly() {
    color(WHITE) {
        trunk_front(); trunk_back();
        translate([0,0,TRUNK_H/2-8]) trunk_lip();
    }
    color(BLACK) translate([0,-108,20]) service_hatch(104,64);
    color(BLACK) translate([0,-109,93]) sensor_bezel(96,28);
    color(DARK) translate([0,-113,93]) sensor_insert(82,16);
}

module waist_shell() {
    rounded_shell([190,150,WAIST_H],20,WALL);
}

module waist_assembly() {
    color(BLACK) waist_shell();
    color(DARK) translate([0,-76,8]) service_hatch(120,48);
    color(BLACK) translate([0,0,-WAIST_H/2+7])
        difference() { cylinder(h=14,d=212,center=true); cylinder(h=16,d=192,center=true); }
    color(BLACK) translate([0,0,WAIST_H/2-7])
        difference() { cylinder(h=14,d=204,center=true); cylinder(h=16,d=184,center=true); }
}

// --------------------------------------------------------------------------
// Pecho compacto, pantalla horizontal y hombros protegidos
// --------------------------------------------------------------------------

module chest_shell_full() {
    difference() {
        lofted_shell(CHEST_H,[270,184],[CHEST_W,CHEST_D],28,WALL);
        translate([0,-CHEST_D/2-8,-2]) face_box([224,34,132],22);
        for (x=[-62,-31,0,31,62])
            translate([x,CHEST_D/2+5,-45]) face_box([16,24,48],5);
    }
}

module chest_tile(front=true, side=1) {
    clip_x(side) clip_y(front?-1:1) chest_shell_full();
}

module chest_top_half(side=1) {
    clip_x(side)
        difference() {
            rounded_prism([CHEST_W,CHEST_D,5],28,true);
            rounded_prism([126,96,8],20,true);
        }
}

module display_bezel() {
    difference() {
        face_box([232,11,140],23);
        translate([0,-1,0]) face_box([208,14,116],17);
    }
}

module display_panel() { face_box([208,5,116],17); }

module waveform() {
    heights=[8,16,28,44,26,15,9,22,39,58,36,20,12,25,43,28,17,9];
    union() {
        face_box([166,2,4],1.2);
        for (i=[0:len(heights)-1])
            translate([-76+i*9,0,0]) face_box([4,2,heights[i]],1.3);
    }
}

module shoulder_ring() {
    rotate([0,90,0]) difference() {
        cylinder(h=34,d=105,center=true);
        cylinder(h=38,d=78,center=true);
    }
}

module shoulder_disc() {
    rotate([0,90,0]) difference() {
        cylinder(h=12,d=78,center=true);
        cylinder(h=15,d=32,center=true);
    }
}

module chest_assembly() {
    color(WHITE) {
        chest_tile(true,-1); chest_tile(true,1);
        chest_tile(false,-1); chest_tile(false,1);
        translate([0,0,CHEST_H/2]) { chest_top_half(-1); chest_top_half(1); }
    }
    color(BLACK) translate([0,-CHEST_D/2-8,-2]) display_bezel();
    color(DARK) translate([0,-CHEST_D/2-15,-2]) display_panel();
    color(CYAN) translate([0,-CHEST_D/2-18,-2]) waveform();
    color(BLACK) translate([0,0,CHEST_H/2+4]) rounded_prism([126,96,8],20,true);
    for (side=[-1,1]) {
        color(WHITE) translate([side*(CHEST_W/2+26),0,24]) shoulder_ring();
        color(BLACK) translate([side*(CHEST_W/2+45),0,24]) shoulder_disc();
    }
}

// --------------------------------------------------------------------------
// Cabeza proporcionada y cuello cosmetico pan/tilt
// --------------------------------------------------------------------------

module neck_assembly() {
    color(BLACK) translate([0,0,7]) difference() {
        cylinder(h=14,d=112,center=true); cylinder(h=17,d=96,center=true);
    }
    color(DARK) translate([0,0,NECK_H/2]) difference() {
        cylinder(h=NECK_H-18,d=96,center=true); cylinder(h=NECK_H-15,d=89.6,center=true);
    }
    color(BLACK) translate([0,0,NECK_H-7]) difference() {
        cylinder(h=14,d=106,center=true); cylinder(h=17,d=90,center=true);
    }
}

module head_shell_full() {
    difference() {
        face_box([HEAD_W,HEAD_D,HEAD_H],40);
        face_box([HEAD_W-2*WALL,HEAD_D-2*WALL,HEAD_H-2*WALL],40-WALL);
        translate([0,-HEAD_D/2-8,0]) face_box([258,32,148],31);
        for (z=[-42,-14,14,42]) translate([0,HEAD_D/2+5,z]) face_box([110,24,10],4);
    }
}

module head_tile(front=true, side=1) {
    clip_x(side) clip_y(front?-1:1) head_shell_full();
}

module face_bezel() {
    difference() {
        face_box([264,11,154],33);
        face_box([252,14,142],28);
    }
}

module face_panel() { face_box([252,6,142],28); }

module eye_ring() {
    rotate([90,0,0]) difference() {
        cylinder(h=4,d=43,center=true); cylinder(h=6,d=31,center=true);
    }
}

module side_pod() {
    difference() {
        face_box([34,72,103],15);
        face_box([27.6,65.6,96.6],11.8);
        translate([-20,0,0]) cube([40,100,130],center=true);
    }
}

module head_assembly() {
    color(WHITE) {
        head_tile(true,-1); head_tile(true,1);
        head_tile(false,-1); head_tile(false,1);
    }
    color(BLACK) translate([0,-HEAD_D/2-10,0]) face_bezel();
    color(DARK) translate([0,-HEAD_D/2-16,0]) face_panel();
    for (x=[-57,57]) {
        color(CYAN) translate([x,-HEAD_D/2-20,5]) eye_ring();
        color(ICE) translate([x,-HEAD_D/2-23,5]) rotate([90,0,0]) cylinder(h=3,d=10,center=true);
    }
    color(WHITE) translate([-HEAD_W/2-12,0,0]) side_pod();
    color(WHITE) mirror([1,0,0]) translate([-HEAD_W/2-12,0,0]) side_pod();
    color(BLACK) for (side=[-1,1]) translate([side*(HEAD_W/2+28),0,0])
        rotate([0,90,0]) rounded_prism([66,52,5],13,true);
}

// --------------------------------------------------------------------------
// Brazos exteriores y mano antropomorfica corregida
// --------------------------------------------------------------------------

module arm_shell(len=170, lower=[58,48], upper=[80,64], r=20) {
    lofted_shell(len,lower,upper,r,WALL);
}

module elbow_cover() { rounded_shell([58,50,38],13,WALL); }

module wrist_cuff() {
    difference() {
        lofted_solid(28,[48,40],[54,46],14);
        lofted_solid(30,[41.6,33.6],[47.6,39.6],10.8);
    }
}

module knuckle(axis="x", d=10, depth=10, pin=2.2) {
    difference() {
        if (axis=="x") rotate([0,90,0]) cylinder(h=depth,d=d,center=true);
        else rotate([90,0,0]) cylinder(h=depth,d=d,center=true);
        if (axis=="x") rotate([0,90,0]) cylinder(h=depth+3,d=pin,center=true);
        else rotate([90,0,0]) cylinder(h=depth+3,d=pin,center=true);
    }
}

module phalange(len=22,w=11,d=8,tip=false) {
    union() {
      color(MID)
        difference() {
            union() {
                translate([0,0,len/2]) lofted_solid(len,[w,d],[w*0.86,d*0.86],max(2,w/3));
                knuckle("x",w+2,d+2,2.2);
                // Puentes solapados: una sola malla entre cuerpo y nudillos.
                translate([0,0,1.5]) rounded_prism([w,d,5],max(1.5,w/4),true);
                if (!tip) translate([0,0,len]) knuckle("x",w+1,d+1,2.2);
                if (!tip) translate([0,0,len-1.5])
                    rounded_prism([w*0.86,d*0.86,5],max(1.4,w/4),true);
            }
            translate([0,-d/4,len/2]) cylinder(h=len+10,d=1.4,center=true);
        }
      // La tapa pisa 4 mm el cuerpo para que el STL sea un único sólido.
      if (tip) color(WHITE) translate([0,0,len+1]) soft_box([w+1,d+1,10],3);
    }
}

module finger_three(lengths=[24,20,17], widths=[11,10,9], curl=[0,0,0]) {
    rotate([curl[0],0,0]) {
        phalange(lengths[0],widths[0],8,false);
        translate([0,0,lengths[0]]) rotate([curl[1],0,0]) {
            phalange(lengths[1],widths[1],7.5,false);
            translate([0,0,lengths[1]]) rotate([curl[2],0,0])
                phalange(lengths[2],widths[2],7,true);
        }
    }
}

module thumb_two(curl=[8,10]) {
    rotate([curl[0],0,0]) {
        phalange(22,12,9,false);
        translate([0,0,22]) rotate([curl[1],0,0])
            phalange(18,10,8,true);
    }
}

module palm_shell() {
    difference() {
        soft_box([54,22,58],8);
        soft_box([47.6,15.6,51.6],5);
        translate([0,0,-30]) cube([38,30,16],center=true);
    }
}

module hand_assembly(pose="open", side=1) {
    // Una unica arquitectura: cuatro dedos de 3 falanges y pulgar de 2.
    curl = pose=="closed" ? [52,66,74] : [4,7,9];
    thumbcurl = pose=="closed" ? [58,72] : [8,12];
    roots=[-18,-6,6,18];
    lengths=[[22,18,15],[25,21,17],[25,21,17],[22,18,15]];
    // Convergencia ligera: mantiene la lectura de cuatro dedos separados.
    inward=[3,1,-1,-3];

    color(WHITE) palm_shell();
    color(BLACK) translate([0,0,-35]) wrist_cuff();

    for (i=[0:3])
        translate([roots[i],-5,27]) rotate([0,inward[i],0])
            finger_three(lengths[i],[11,10,9],curl);

    // Pulgar lateral, raiz a 90 grados respecto a las bisagras de dedos.
    translate([-29,-2,-2]) rotate([0,-56,0]) rotate([0,0,90])
        thumb_two(thumbcurl);
}

module arm_assembly(side=1, hand="open") {
    shoulder_z = 24;
    sx=side;

    color(BLACK) translate([sx*(CHEST_W/2+52),0,shoulder_z])
        rotate([0,90,0]) cylinder(h=18,d=70,center=true);
    color(WHITE) translate([sx*(CHEST_W/2+63),0,shoulder_z-74])
        rotate([0,-sx*4,0]) arm_shell(UPPER_ARM_L,[56,46],[78,62],20);

    elbow_z=shoulder_z-UPPER_ARM_L;
    color(BLACK) translate([sx*(CHEST_W/2+75),0,elbow_z]) elbow_cover();
    color(WHITE) translate([sx*(CHEST_W/2+78),0,elbow_z-FOREARM_L/2-6])
        rotate([0,-sx*2,0]) arm_shell(FOREARM_L,[48,40],[62,50],17);

    wrist_z=elbow_z-FOREARM_L-8;
    color(BLACK) translate([sx*(CHEST_W/2+83),0,wrist_z]) wrist_cuff();
    translate([sx*(CHEST_W/2+83),0,wrist_z-70])
        scale([sx,1,1]) rotate([180,0,0]) hand_assembly(hand,side);
}

module arms_assembly(hand="open") {
    arm_assembly(-1,hand);
    arm_assembly(1,hand);
}

// --------------------------------------------------------------------------
// Vistas maestras
// --------------------------------------------------------------------------

module full_assembly() {
    base_assembly(true);
    translate([0,0,Z_TRUNK+TRUNK_H/2]) trunk_assembly();
    translate([0,0,Z_WAIST+WAIST_H/2]) waist_assembly();
    translate([0,0,Z_CHEST+CHEST_H/2]) {
        chest_assembly();
        arms_assembly(hand_pose);
    }
    translate([0,0,Z_NECK]) neck_assembly();
    translate([0,0,Z_HEAD+HEAD_H/2]) head_assembly();
}

module exploded_view() {
    // Mismos modulos, separados para revisar pieles y accesos.
    base_assembly(true);

    translate([0,-32,Z_TRUNK+TRUNK_H/2+55]) color(WHITE) trunk_front();
    translate([0, 32,Z_TRUNK+TRUNK_H/2+55]) color(WHITE) trunk_back();
    translate([0,0,Z_WAIST+WAIST_H/2+110]) waist_assembly();

    translate([0,0,Z_CHEST+CHEST_H/2+165]) {
        for (side=[-1,1]) {
            color(WHITE) translate([side*12,-35,0]) chest_tile(true,side);
            color(WHITE) translate([side*12, 35,0]) chest_tile(false,side);
        }
        color(BLACK) translate([0,-145,-2]) display_bezel();
        translate([0,0,0]) arms_assembly("open");
    }

    translate([0,0,Z_NECK+235]) neck_assembly();
    translate([0,0,Z_HEAD+HEAD_H/2+280]) {
        for (side=[-1,1]) {
            color(WHITE) translate([side*9,-34,0]) head_tile(true,side);
            color(WHITE) translate([side*9, 34,0]) head_tile(false,side);
        }
        color(BLACK) translate([0,-132,0]) face_bezel();
        color(DARK) translate([0,-143,0]) face_panel();
    }
}

module hand_comparison() {
    translate([-70,0,0]) hand_assembly("open",1);
    translate([ 70,0,0]) hand_assembly("closed",1);
}

if (part=="assembly") full_assembly();
else if (part=="exploded") exploded_view();
else if (part=="hand_compare") hand_comparison();
else if (part=="hand_open") hand_assembly("open",1);
else if (part=="hand_closed") hand_assembly("closed",1);
else if (part=="base_quadrant") base_quadrant();
else if (part=="wheel_arch") wheel_arch();
else if (part=="trunk_front") trunk_front();
else if (part=="trunk_back") trunk_back();
else if (part=="waist_shell") waist_shell();
else if (part=="chest_front_left") chest_tile(true,-1);
else if (part=="chest_front_right") chest_tile(true,1);
else if (part=="chest_back_left") chest_tile(false,-1);
else if (part=="chest_back_right") chest_tile(false,1);
else if (part=="display_bezel") display_bezel();
else if (part=="head_front_left") head_tile(true,-1);
else if (part=="head_front_right") head_tile(true,1);
else if (part=="head_back_left") head_tile(false,-1);
else if (part=="head_back_right") head_tile(false,1);
else if (part=="face_bezel") face_bezel();
else if (part=="upper_arm_shell") arm_shell(UPPER_ARM_L,[56,46],[78,62],20);
else if (part=="forearm_shell") arm_shell(FOREARM_L,[48,40],[62,50],17);
else if (part=="palm_shell") palm_shell();
else if (part=="finger_proximal") phalange(25,11,8,false);
else if (part=="finger_middle") phalange(21,10,7.5,false);
else if (part=="finger_distal") phalange(17,9,7,true);
else if (part=="thumb_proximal") phalange(22,12,9,false);
else if (part=="thumb_distal") phalange(18,10,8,true);
else assert(false,str("Pieza desconocida: ",part));
