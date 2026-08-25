// Robot Toreto 95 cm - módulo 2: tronco inferior exterior
// Basado en el segundo recorte de referencia del usuario.
// SOLO carcasas visibles: sin columna, estructura, actuadores ni fijaciones.
// Unidades: milímetros.

$fn = 48;
part = "assembly";

trunk_h = 202;
lower_h = 132;
tower_h = 86;
wall = 3.2;

white = [0.92,0.94,0.95];
black = [0.025,0.032,0.040];
dark  = [0.070,0.080,0.090];
cyan  = [0.00,0.72,0.96];

echo("TRUNK_HEIGHT_MM",trunk_h);
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

module lofted_solid(h=100,bottom=[100,80],top=[90,70],r=15) {
    hull() {
        translate([0,0,-h/2+1]) rounded_prism([bottom[0],bottom[1],2],r,true);
        translate([0,0, h/2-1]) rounded_prism([top[0],top[1],2],r,true);
    }
}

module lofted_shell(h=100,bottom=[100,80],top=[90,70],r=15,t=wall) {
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

module rounded_shell(size=[100,80,100],r=15,t=wall) {
    difference() {
        rounded_prism(size,r,true);
        rounded_prism([size[0]-2*t,size[1]-2*t,size[2]+2],max(1,r-t),true);
    }
}

module clip_y(side=1,span=360) {
    intersection() {
        children();
        translate([0,side*span/4,0]) cube([span,span/2,span],center=true);
    }
}

// Faldón blanco que enlaza visualmente con la base aprobada.
module lower_skirt_full() {
    lofted_shell(lower_h,[250,210],[210,170],28,wall);
}

module lower_skirt_front() { clip_y(-1) lower_skirt_full(); }
module lower_skirt_back()  { clip_y( 1) lower_skirt_full(); }

// Labio blanco elevado alrededor del bloque negro superior.
module skirt_top_lip_full() {
    difference() {
        lofted_solid(18,[220,180],[214,174],24);
        lofted_solid(20,[204,164],[198,158],17);
    }
}

module skirt_top_lip_half() { clip_y(-1) skirt_top_lip_full(); }

// Torre negra exterior: una carcasa hueca y sin ninguna interfaz interior.
module tower_shell() {
    rounded_shell([190,150,tower_h],20,wall);
}

module tower_collar() {
    difference() {
        rounded_prism([208,168,18],22,true);
        rounded_prism([192,152,20],15,true);
    }
}

// Relieve frontal puramente estético del bloque negro.
module tower_front_relief() {
    difference() {
        rotate([90,0,0]) rounded_prism([124,50,3],8,true);
        translate([0,-1,0]) rotate([90,0,0]) rounded_prism([108,34,5],6,true);
    }
}

module tower_detail_tab() {
    rotate([90,0,0]) rounded_prism([48,12,3],4,true);
}

// Conjunto de sensores frontales ciegos, sin electrónica.
module trunk_sensor_bezel() {
    difference() {
        rotate([90,0,0]) rounded_prism([100,30,7],8,true);
        translate([0,-1,0]) rotate([90,0,0]) rounded_prism([86,18,9],5,true);
    }
}

module trunk_sensor_insert() {
    union() {
        rotate([90,0,0]) rounded_prism([86,18,4],5,true);
        for (x=[-30,0,30])
            translate([x,-3,0]) rotate([90,0,0]) cylinder(h=2,d=x==0 ? 7 : 12,center=true);
    }
}

// Tapa de servicio exterior: solo un marco en relieve.
module service_panel_frame() {
    difference() {
        rotate([90,0,0]) rounded_prism([104,62,2.4],10,true);
        translate([0,-1,0]) rotate([90,0,0]) rounded_prism([98,56,4],8,true);
    }
}

module service_port_ring() {
    rotate([90,0,0])
        difference() {
            cylinder(h=3,d=12,center=true);
            cylinder(h=5,d=5,center=true);
        }
}

module service_marker() {
    rotate([90,0,0]) linear_extrude(height=2,center=true)
        polygon([[-6,-4],[6,-4],[0,6]]);
}

module assembly() {
    color(white) translate([0,0,lower_h/2]) {
        lower_skirt_front();
        lower_skirt_back();
    }

    color(white) translate([0,0,124]) {
        skirt_top_lip_half();
        rotate([0,0,180]) skirt_top_lip_half();
    }

    color(black) translate([0,0,125]) tower_collar();
    color(black) translate([0,0,trunk_h-tower_h/2]) tower_shell();

    // Relieves del bloque negro.
    color(dark) translate([0,-76,168]) tower_front_relief();
    color(dark) translate([0,-78,190]) tower_detail_tab();

    // Frente del faldón blanco, como en la referencia.
    color(black) translate([0,-91,91]) trunk_sensor_bezel();
    color(dark)  translate([0,-96,91]) trunk_sensor_insert();
    color(cyan)  translate([0,-99,91]) rotate([90,0,0]) cylinder(h=2,d=3.5,center=true);

    color(white) translate([0,-99,47]) service_panel_frame();
    color(black) translate([0,-102,38]) service_port_ring();
    color(white) translate([0,-102,68]) service_marker();
}

if (part == "assembly") assembly();
else if (part == "lower_skirt_front") lower_skirt_front();
else if (part == "lower_skirt_back") lower_skirt_back();
else if (part == "skirt_top_lip_half") skirt_top_lip_half();
else if (part == "tower_shell") tower_shell();
else if (part == "tower_collar") tower_collar();
else if (part == "tower_front_relief") tower_front_relief();
else if (part == "tower_detail_tab") tower_detail_tab();
else if (part == "trunk_sensor_bezel") trunk_sensor_bezel();
else if (part == "trunk_sensor_insert") trunk_sensor_insert();
else if (part == "service_panel_frame") service_panel_frame();
else if (part == "service_port_ring") service_port_ring();
else if (part == "service_marker") service_marker();
else assert(false,str("Pieza desconocida: ",part));

