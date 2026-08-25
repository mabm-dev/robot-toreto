// Robot Toreto 95 cm - módulo 1: base exterior
// Diseñado contra el recorte de referencia facilitado por el usuario.
// SOLO superficies visibles: sin ruedas, motores, ejes, chasis ni anclajes.
// Unidades: milímetros.

$fn = 40;
part = "assembly";

base_d = 400;
base_h = 225;
wall = 3.2;

white = [0.92,0.94,0.95];
black = [0.025,0.032,0.040];
dark  = [0.055,0.067,0.078];
cyan  = [0.00,0.72,0.96];

echo("BASE_DIAMETER_MM",base_d);
echo("BASE_SHELL_HEIGHT_MM",base_h);
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

module soft_box(size=[20,20,20],r=4) {
    sx=size[0]; sy=size[1]; sz=size[2];
    hull()
        for (x=[-1,1],y=[-1,1],z=[-1,1])
            translate([x*(sx/2-r),y*(sy/2-r),z*(sz/2-r)]) sphere(r=r);
}

module positive_quadrant(span=430) {
    intersection() {
        children();
        cube([span/2,span/2,base_h+80],center=false);
    }
}

module wheel_bay_cutout() {
    translate([0,-190,82]) rounded_prism([116,102,150],24,true);
}

module all_wheel_bay_cutouts() {
    for (a=[-45,45,135,225]) rotate([0,0,a]) wheel_bay_cutout();
}

// Tambor negro visible entre los cuatro huecos de rueda.
module core_fascia_full() {
    difference() {
        translate([0,0,12]) cylinder(h=148,d=380);
        translate([0,0,8]) cylinder(h=156,d=372);
        all_wheel_bay_cutouts();
    }
}

module core_fascia_quadrant() { positive_quadrant() core_fascia_full(); }

// Paños blancos laterales entre los huecos delanteros y traseros.
// Son pieles curvas independientes, no pilares estructurales.
module outer_side_panel() {
    rotate([0,0,-24])
        rotate_extrude(angle=48,convexity=8)
            translate([191,24]) square([9,121]);
}

// Cubierta blanca superior: perfil escalonado y ligeramente troncocónico.
module top_deck_outer() {
    union() {
        // Labio exterior casi vertical, como el bumper blanco de la referencia.
        translate([0,0,145]) cylinder(h=28,d=400);
        // Corona superior de poca pendiente.
        hull() {
            translate([0,0,176]) cylinder(h=3,d=382);
            translate([0,0,222]) cylinder(h=3,d=350);
        }
        // Collar exterior donde empezará el módulo de tronco.
        translate([0,0,216]) cylinder(h=9,d=250);
    }
}

module top_deck_inner() {
    union() {
        translate([0,0,145+wall]) cylinder(h=24,d=392);
        hull() {
            translate([0,0,176+wall]) cylinder(h=3,d=374);
            translate([0,0,base_h-wall]) cylinder(h=3,d=342);
        }
    }
}

module top_deck_full() {
    difference() {
        top_deck_outer();
        top_deck_inner();
        translate([0,0,140]) cylinder(h=92,d=232);
    }
}

module top_deck_quadrant() { positive_quadrant() top_deck_full(); }

// Aro negro fino embutido en la cubierta blanca.
module trim_ring_full() {
    difference() {
        translate([0,0,170]) cylinder(h=7,d=390);
        translate([0,0,168]) cylinder(h=11,d=352);
    }
}

module trim_ring_quadrant() { positive_quadrant() trim_ring_full(); }

// Piel blanca lateral que enmarca cada hueco de rueda.
module wheel_arch_shell() {
    difference() {
        rounded_prism([126,82,158],28,true);
        rounded_prism([112,88,144],22,true);
        // Abierto hacia el exterior y hacia abajo.
        translate([0,-48,0]) cube([150,90,190],center=true);
        translate([0,0,-78]) cube([150,110,40],center=true);
    }
}

// Panel frontal de sensores: solo bezel y lentes ciegas decorativas.
module sensor_panel_bezel() {
    difference() {
        rotate([90,0,0]) rounded_prism([142,31,8],9,true);
        translate([0,-1,0]) rotate([90,0,0]) rounded_prism([128,19,10],6,true);
    }
}

module sensor_panel_insert() {
    union() {
        rotate([90,0,0]) rounded_prism([128,19,5],6,true);
        for (x=[-48,0,48])
            translate([x,-3,0]) rotate([90,0,0]) cylinder(h=2,d=x==0 ? 7 : 13,center=true);
    }
}

// Carcasa del pequeño sensor superior de la referencia; no contiene sensor.
module top_sensor_plinth() {
    difference() {
        cylinder(h=14,d=96,center=true);
        cylinder(h=17,d=76,center=true);
    }
}

module top_sensor_cover() {
    difference() {
        union() {
            cylinder(h=34,d=72,center=true);
            translate([0,0,17]) cylinder(h=5,d=64,center=true);
        }
        translate([0,0,-2]) cylinder(h=35,d=65,center=true);
        // Tres ventanas exteriores ciegas.
        for (a=[-38,0,38])
            rotate([0,0,a]) translate([0,-36,0])
                rotate([90,0,0]) rounded_prism([12,12,6],3,true);
    }
}

module assembly() {
    // Cuatro sectores imprimibles idénticos.
    for (a=[0:90:270]) {
        color(black) rotate([0,0,a]) core_fascia_quadrant();
        color(white) rotate([0,0,a]) top_deck_quadrant();
        color(black) rotate([0,0,a]) trim_ring_quadrant();
    }

    // Cuatro arcos de rueda exteriores, sin rueda ni soporte.
    for (a=[-45,45,135,225]) {
        color(white) rotate([0,0,a]) translate([0,-193,82]) wheel_arch_shell();
    }

    // Laterales blancos anchos; el frontal queda negro como en la referencia.
    for (a=[0,90,180]) color(white) rotate([0,0,a]) outer_side_panel();

    // Dos bandas de sensores ciegas como en el frontal de la imagen.
    for (z=[102,58]) {
        color(black) translate([0,-191,z]) sensor_panel_bezel();
        color(dark) translate([0,-196,z]) sensor_panel_insert();
        color(cyan) translate([0,-200,z]) rotate([90,0,0]) cylinder(h=2,d=4,center=true);
    }

    // Sensor superior desplazado hacia el frontal derecho.
    color(white) translate([92,-112,226]) top_sensor_plinth();
    color(black) translate([92,-112,250]) top_sensor_cover();
    color(cyan) translate([92,-149,250]) cube([5,2,5],center=true);
}

if (part == "assembly") assembly();
else if (part == "core_fascia_quadrant") core_fascia_quadrant();
else if (part == "outer_side_panel") outer_side_panel();
else if (part == "top_deck_quadrant") top_deck_quadrant();
else if (part == "trim_ring_quadrant") trim_ring_quadrant();
else if (part == "wheel_arch_shell") wheel_arch_shell();
else if (part == "sensor_panel_bezel") sensor_panel_bezel();
else if (part == "sensor_panel_insert") sensor_panel_insert();
else if (part == "top_sensor_plinth") top_sensor_plinth();
else if (part == "top_sensor_cover") top_sensor_cover();
else assert(false,str("Pieza desconocida: ",part));
