// Robot Toreto 95 cm - módulo 4: cabeza y cuello exteriores
// Basado en el cuarto recorte de referencia del usuario.
// SOLO carcasas visibles: sin cámara, pantalla, actuadores ni soporte interno.
// Unidades: milímetros.

$fn = 56;
part = "assembly";

head_w = 320;
head_d = 190;
head_h = 225;
neck_h = 70;
wall = 3.2;

white = [0.92,0.94,0.95];
black = [0.020,0.028,0.036];
dark  = [0.045,0.057,0.068];
cyan  = [0.00,0.72,0.96];
ice   = [0.72,0.92,1.00];

echo("HEAD_WIDTH_MM",head_w);
echo("HEAD_HEIGHT_MM",head_h);
echo("NECK_HEIGHT_MM",neck_h);
echo("HEAD_NECK_TOTAL_MM",head_h+neck_h);
echo("SCOPE","external_only_no_mechanics");

module rr2d(size=[20,20],r=3) {
    w=size[0]; d=size[1];
    hull()
        for (x=[-1,1],y=[-1,1])
            translate([x*(w/2-r),y*(d/2-r)]) circle(r=r);
}

module rounded_prism(size=[20,20,20],r=3,center=true) {
    translate([0,0,center ? -size[2]/2 : 0])
        linear_extrude(height=size[2]) rr2d([size[0],size[1]],r);
}

// Caja redondeada en la silueta frontal X/Z y extruida en profundidad Y.
module face_box(size=[100,60,80],r=20) {
    rotate([90,0,0]) rounded_prism([size[0],size[2],size[1]],r,true);
}

// Placa redondeada en la silueta lateral Y/Z y extruida en X.
module side_plate(size=[6,50,70],r=12) {
    rotate([0,90,0]) rounded_prism([size[2],size[1],size[0]],r,true);
}

module clip_x(side=1,span=430) {
    intersection() {
        children();
        translate([side*span/4,0,0]) cube([span/2,span,span],center=true);
    }
}

module clip_y(side=1,span=430) {
    intersection() {
        children();
        translate([0,side*span/4,0]) cube([span,span/2,span],center=true);
    }
}

module head_shell_full() {
    difference() {
        face_box([head_w,head_d,head_h],46);
        face_box([head_w-2*wall,head_d-2*wall,head_h-2*wall],46-wall);
        // Gran ventana facial frontal.
        translate([0,-96,0]) face_box([286,34,170],34);
        // Rejillas posteriores exteriores.
        for (z=[-48,-16,16,48])
            translate([0,96,z]) face_box([122,30,12],5);
    }
}

module head_tile(front=true,side=1) {
    clip_x(side) clip_y(front ? -1 : 1) head_shell_full();
}

module face_bezel_full() {
    difference() {
        face_box([290,10,178],36);
        face_box([278,13,166],30);
    }
}

module face_bezel_half(side=1) { clip_x(side) face_bezel_full(); }

module face_panel_full() { face_box([278,7,166],30); }
module face_panel_half(side=1) { clip_x(side) face_panel_full(); }

module face_glass_full() { face_box([266,3,154],27); }
module face_glass_half(side=1) { clip_x(side) face_glass_full(); }

module eye_ring() {
    rotate([90,0,0])
        difference() {
            cylinder(h=4,d=52,center=true);
            cylinder(h=6,d=38,center=true);
        }
}

module eye_pupil() {
    rotate([90,0,0]) cylinder(h=4,d=13,center=true);
}

module face_camera_dot() {
    rotate([90,0,0])
        difference() {
            cylinder(h=3,d=10,center=true);
            cylinder(h=5,d=4,center=true);
        }
}

module side_pod_shell() {
    difference() {
        face_box([38,82,114],16);
        face_box([31.6,75.6,107.6],12.8);
        translate([-22,0,0]) cube([44,110,140],center=true);
    }
}

module side_pod_insert() { side_plate([7,58,74],14); }

module neck_lower_ring() {
    difference() {
        cylinder(h=16,d=124,center=true);
        cylinder(h=19,d=108,center=true);
    }
}

module neck_column_shell() {
    difference() {
        cylinder(h=46,d=108,center=true);
        cylinder(h=49,d=101.6,center=true);
    }
}

module neck_upper_ring() {
    difference() {
        cylinder(h=14,d=116,center=true);
        cylinder(h=17,d=100,center=true);
    }
}

module neck_bridge_cover() {
    difference() {
        face_box([118,90,26],13);
        face_box([111.6,83.6,27],9.8);
    }
}

module assembly() {
    // Cuello negro escalonado: solo cubiertas exteriores.
    color(black) translate([0,0,8]) neck_lower_ring();
    color(dark)  translate([0,0,33]) neck_column_shell();
    color(black) translate([0,0,56]) neck_upper_ring();
    color(black) translate([0,0,64]) neck_bridge_cover();

    zc=neck_h+head_h/2;
    color(white) translate([0,0,zc]) {
        head_tile(true,-1); head_tile(true,1);
        head_tile(false,-1); head_tile(false,1);
    }

    color(black) translate([0,-99,zc]) {
        face_bezel_half(-1); face_bezel_half(1);
    }
    color(black) translate([0,-105,zc]) {
        face_panel_half(-1); face_panel_half(1);
    }
    color(dark) translate([0,-110,zc]) {
        face_glass_half(-1); face_glass_half(1);
    }

    for (x=[-66,66]) {
        color(cyan) translate([x,-113,zc]) eye_ring();
        color(ice)  translate([x,-116,zc]) eye_pupil();
    }
    color(black) translate([0,-115,zc-66]) face_camera_dot();

    color(white) translate([-166,0,zc]) side_pod_shell();
    color(white) mirror([1,0,0]) translate([-166,0,zc]) side_pod_shell();
    color(black) translate([-182,-2,zc]) side_pod_insert();
    color(black) translate([ 182,-2,zc]) side_pod_insert();
}

if (part == "assembly") assembly();
else if (part == "head_front_left") head_tile(true,-1);
else if (part == "head_front_right") head_tile(true,1);
else if (part == "head_back_left") head_tile(false,-1);
else if (part == "head_back_right") head_tile(false,1);
else if (part == "face_bezel_left") face_bezel_half(-1);
else if (part == "face_bezel_right") face_bezel_half(1);
else if (part == "face_panel_left") face_panel_half(-1);
else if (part == "face_panel_right") face_panel_half(1);
else if (part == "face_glass_left") face_glass_half(-1);
else if (part == "face_glass_right") face_glass_half(1);
else if (part == "eye_ring") eye_ring();
else if (part == "eye_pupil") eye_pupil();
else if (part == "face_camera_dot") face_camera_dot();
else if (part == "side_pod_shell") side_pod_shell();
else if (part == "side_pod_insert") side_pod_insert();
else if (part == "neck_lower_ring") neck_lower_ring();
else if (part == "neck_column_shell") neck_column_shell();
else if (part == "neck_upper_ring") neck_upper_ring();
else if (part == "neck_bridge_cover") neck_bridge_cover();
else assert(false,str("Pieza desconocida: ",part));
