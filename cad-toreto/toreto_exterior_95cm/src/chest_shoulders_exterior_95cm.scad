// Robot Toreto 95 cm - módulo 3: hombros y pecho exteriores
// Basado en el tercer recorte de referencia del usuario.
// SOLO carcasas visibles: sin servos, ejes, estructura ni pantalla real.
// Unidades: milímetros.

$fn = 48;
part = "assembly";

chest_h = 228;
wall = 3.2;

white = [0.92,0.94,0.95];
black = [0.025,0.032,0.040];
dark  = [0.055,0.067,0.078];
cyan  = [0.00,0.72,0.96];

echo("CHEST_HEIGHT_MM",chest_h);
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

module lofted_solid(h=100,bottom=[100,80],top=[110,90],r=15) {
    hull() {
        translate([0,0,-h/2+1]) rounded_prism([bottom[0],bottom[1],2],r,true);
        translate([0,0, h/2-1]) rounded_prism([top[0],top[1],2],r,true);
    }
}

module lofted_shell(h=100,bottom=[100,80],top=[110,90],r=15,t=wall) {
    difference() {
        lofted_solid(h,bottom,top,r);
        lofted_solid(
            h+2,
            [bottom[0]-2*t,bottom[1]-2*t],
            [top[0]-2*t,top[1]-2*t],
            max(1,r-t)
        );
    }
}

module clip_x(side=1,span=420) {
    intersection() {
        children();
        translate([side*span/4,0,0]) cube([span/2,span,span],center=true);
    }
}

module clip_y(side=1,span=420) {
    intersection() {
        children();
        translate([0,side*span/4,0]) cube([span,span/2,span],center=true);
    }
}

// Carcasa principal con hueco exterior de pantalla y ventilación posterior.
module chest_shell_full() {
    difference() {
        lofted_shell(chest_h,[288,202],[340,216],30,wall);
        translate([0,-108,-5])
            rotate([90,0,0]) rounded_prism([252,166,30],24,true);
        for (x=[-72,-36,0,36,72])
            translate([x,108,-62])
                rotate([90,0,0]) rounded_prism([18,58,28],6,true);
    }
}

module chest_tile(front=true,side=1) {
    clip_x(side) clip_y(front ? -1 : 1) chest_shell_full();
}

module chest_top_panel_full() {
    difference() {
        rounded_prism([340,216,4],30,true);
        rounded_prism([172,130,7],24,true);
    }
}

module chest_top_panel_half(side=1) {
    clip_x(side) chest_top_panel_full();
}

// Marco y superficie ciega de la pantalla central.
module display_bezel() {
    difference() {
        rotate([90,0,0]) rounded_prism([252,166,10],24,true);
        translate([0,-1,0]) rotate([90,0,0]) rounded_prism([226,140,12],18,true);
    }
}

module display_panel() {
    rotate([90,0,0]) rounded_prism([226,140,5],18,true);
}

module waveform_inlay() {
    heights=[10,18,30,46,26,16,8,22,42,66,38,20,12,26,48,30,18,10];
    union() {
        rotate([90,0,0]) rounded_prism([164,5,2],1.5,true);
        for (i=[0:len(heights)-1])
            translate([-76+i*9,0,0])
                rotate([90,0,0]) rounded_prism([4,heights[i],2],1.5,true);
    }
}

// Inserto negro superior que recibirá visualmente el futuro cuello.
module neck_deck_insert() {
    rounded_prism([166,124,7],24,true);
}

module neck_deck_accent() {
    difference() {
        rounded_prism([112,82,3],20,true);
        rounded_prism([94,64,5],15,true);
    }
}

// Hombro exterior circular. La tapa central incorpora únicamente el paso
// para el eje pasivo M4 del anclaje exterior del brazo.
module shoulder_ring_shell() {
    rotate([0,90,0])
        difference() {
            cylinder(h=52,d=126,center=true);
            cylinder(h=56,d=98,center=true);
        }
}

module shoulder_socket_disc() {
    rotate([0,90,0])
        difference() {
            cylinder(h=12,d=98,center=true);
            cylinder(h=14,d=34,center=true);
        }
}

module shoulder_center_cap() {
    rotate([0,90,0])
        difference() {
            cylinder(h=5,d=72,center=true);
            cylinder(h=7,d=4.4,center=true);
        }
}

// Apliques negros de las esquinas bajas del pecho.
module lower_corner_insert() {
    rotate([90,0,0]) rounded_prism([78,38,5],11,true);
}

module lower_front_slot() {
    rotate([90,0,0]) rounded_prism([52,8,4],3,true);
}

module assembly() {
    color(white) {
        chest_tile(true,-1); chest_tile(true,1);
        chest_tile(false,-1); chest_tile(false,1);
        translate([0,0,chest_h/2]) {
            chest_top_panel_half(-1); chest_top_panel_half(1);
        }
    }

    color(black) translate([0,-112,-5]) display_bezel();
    color(dark)  translate([0,-118,-5]) display_panel();
    color(cyan)  translate([0,-122,-5]) waveform_inlay();

    color(black) translate([0,0,chest_h/2+3]) neck_deck_insert();
    color(dark)  translate([0,-8,chest_h/2+7]) neck_deck_accent();

    for (side=[-1,1]) {
        color(white) translate([side*184,0,52]) shoulder_ring_shell();
        color(black) translate([side*214,0,52]) shoulder_socket_disc();
        color(dark)  translate([side*221,0,52]) shoulder_center_cap();
        color(black) translate([side*106,-103,-84]) lower_corner_insert();
    }

    color(black) translate([0,-106,-101]) lower_front_slot();
}

if (part == "assembly") assembly();
else if (part == "chest_front_left") chest_tile(true,-1);
else if (part == "chest_front_right") chest_tile(true,1);
else if (part == "chest_back_left") chest_tile(false,-1);
else if (part == "chest_back_right") chest_tile(false,1);
else if (part == "chest_top_left") chest_top_panel_half(-1);
else if (part == "chest_top_right") chest_top_panel_half(1);
else if (part == "display_bezel") display_bezel();
else if (part == "display_panel") display_panel();
else if (part == "waveform_inlay") waveform_inlay();
else if (part == "neck_deck_insert") neck_deck_insert();
else if (part == "neck_deck_accent") neck_deck_accent();
else if (part == "shoulder_ring_shell") shoulder_ring_shell();
else if (part == "shoulder_socket_disc") shoulder_socket_disc();
else if (part == "shoulder_center_cap") shoulder_center_cap();
else if (part == "lower_corner_insert") lower_corner_insert();
else if (part == "lower_front_slot") lower_front_slot();
else assert(false,str("Pieza desconocida: ",part));
