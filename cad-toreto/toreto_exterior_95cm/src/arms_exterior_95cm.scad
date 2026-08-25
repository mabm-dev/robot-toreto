// Robot Toreto 95 cm - módulo 5: brazos exteriores
// Basado en el quinto recorte de referencia del usuario.
// Piezas exteriores y módulos de mano preparados para articulación subactuada:
// canales y alojamientos incluidos, sin servos ni esqueleto interno.
// Unidades: milímetros.

$fn = 44;
part = "assembly";
detail_view = (part == "hand_detail");

upper_len = 170;
forearm_len = 150;
wall = 3.2;
finger_pin_d = 2.2;       // holgura para pasador/tornillo M2
finger_cable_d = 1.4;     // canal para Dyneema/Kevlar de tracción
return_pocket_d = 3.2;    // alojamiento superficial para muelle/elastómero
finger_clearance = 0.4;   // holgura lateral por lado
main_prox_len = 22;
main_mid_len = 20;
main_dist_len = 17;
thumb_prox_len = 20;
thumb_mid_len = 17;
thumb_dist_len = 16;
shoulder_pin_d = 4.4;     // paso para eje/tornillo M4

white = [0.92,0.94,0.95];
black = [0.025,0.032,0.040];
dark  = [0.065,0.075,0.085];

echo("UPPER_ARM_LENGTH_MM",upper_len);
echo("FOREARM_LENGTH_MM",forearm_len);
echo("HAND_FUNCTION","four_three_link_fingers_plus_opposed_thumb_anthropomorphic");
echo("FINGER_PIN_CLEARANCE_MM",finger_pin_d);
echo("TENDON_CHANNEL_MM",finger_cable_d);
echo("RETURN_POCKET_MM",return_pocket_d);
echo("SHOULDER_PIN_CLEARANCE_MM",shoulder_pin_d);
echo("SCOPE","external_shells_with_passive_hand_joints_no_actuators");

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

module lofted_solid(h=100,bottom=[60,50],top=[80,65],r=18) {
    hull() {
        translate([0,0,-h/2+1]) rounded_prism([bottom[0],bottom[1],2],r,true);
        translate([0,0, h/2-1]) rounded_prism([top[0],top[1],2],r,true);
    }
}

module lofted_shell(h=100,bottom=[60,50],top=[80,65],r=18,t=wall) {
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

module rounded_shell(size=[70,55,45],r=14,t=wall) {
    difference() {
        rounded_prism(size,r,true);
        rounded_prism([size[0]-2*t,size[1]-2*t,size[2]+2],max(1,r-t),true);
    }
}

module upper_arm_shell() {
    lofted_shell(upper_len,[60,50],[88,70],23,wall);
}

module upper_arm_seam() {
    difference() {
        rotate([90,0,0]) rounded_prism([42,76,2.4],9,true);
        translate([0,-1,0]) rotate([90,0,0]) rounded_prism([38,72,4],7,true);
    }
}

module elbow_cover() {
    rounded_shell([64,54,42],14,wall);
}

module elbow_side_cap() {
    rotate([0,90,0])
        difference() {
            cylinder(h=5,d=42,center=true);
            cylinder(h=7,d=12,center=true);
        }
}

module forearm_shell() {
    lofted_shell(forearm_len,[54,46],[72,58],20,wall);
}

module forearm_seam() {
    difference() {
        rotate([90,0,0]) rounded_prism([38,62,2.4],8,true);
        translate([0,-1,0]) rotate([90,0,0]) rounded_prism([34,58,4],6,true);
    }
}

module wrist_cuff() {
    difference() {
        lofted_solid(34,[54,46],[60,52],17);
        lofted_solid(36,[47.6,39.6],[53.6,45.6],13.8);
    }
}

// Anclaje exterior del brazo al hombro. El disco apoya sobre la tapa de
// 72 mm del pecho y el paso M4 permite una rotación pasiva. La lengüeta
// inferior entra visualmente en la carcasa abierta del brazo superior.
module shoulder_anchor() {
    difference() {
        union() {
            rotate([0,90,0]) cylinder(h=21,d=72,center=true);
            hull() {
                translate([0,0,-22]) rounded_prism([24,38,24],8,true);
                translate([-5,0,-42]) rounded_prism([28,36,26],8,true);
            }
        }
        rotate([0,90,0]) cylinder(h=40,d=shoulder_pin_d,center=true);
    }
}

// Cubierta blanca gruesa que abraza el disco negro y se solapa con la boca
// del brazo superior, igual que el hombro mostrado en la referencia.
module shoulder_outer_hood() {
    rotate([0,90,0])
        difference() {
            cylinder(h=30,d=100,center=true);
            cylinder(h=34,d=74,center=true);
        }
}

// Oreja de la palma. Dos orejas forman una horquilla y dejan libre el
// alojamiento de la falange proximal.
module palm_knuckle_ear(x=0,y=0,z=-28,ear_t=3.4) {
    hull() {
        translate([x,y,z])
            rotate([90,0,0]) cylinder(h=ear_t,d=17,center=true);
        translate([x,y,-20]) rounded_prism([17,ear_t,14],4,true);
    }
}

// Variante con eje transversal X para que los dos dedos delanteros y el
// pulgar se cierren uno contra otro, como en la referencia.
module palm_knuckle_ear_x(x=0,y=0,z=-12,ear_t=3.2) {
    hull() {
        translate([x,y,z])
            rotate([0,90,0]) cylinder(h=ear_t,d=13,center=true);
        translate([x,y,-5]) rounded_prism([ear_t,13,10],1.4,true);
    }
}

module palm_wedge_solid(h=24,top=[30,25],bottom=[34,28],r=6) {
    hull() {
        translate([0,0,h/2-1]) rounded_prism([top[0],top[1],2],r,true);
        translate([0,0,-h/2+1]) rounded_prism([bottom[0],bottom[1],2],r-1,true);
    }
}

module palm_wedge_shell() {
    difference() {
        palm_wedge_solid(24,[46,30],[54,34],7);
        palm_wedge_solid(26,[39.6,23.6],[47.6,27.6],4.8);
    }
}

// Palma antropomórfica con cuatro horquillas delanteras y un pulgar lateral.
module hand_palm_shell() {
    inner_gap = 12 + 2*finger_clearance;
    ear_t = 3.2;
    ear_x = inner_gap/2 + ear_t/2;
    front_y = -6;
    thumb_y = 7;
    pivot_z = -10;

    difference() {
        union() {
            translate([0,0,7]) palm_wedge_shell();
            translate([0,0,18]) rounded_shell([46,30,8],7,2.6);

            // Cuatro dedos delanteros, como una mano humana.
            for (cx=[-18,-6,6,18], dx=[-ear_x,ear_x])
                palm_knuckle_ear_x(cx+dx,front_y,pivot_z,ear_t);

            // Pulgar lateral opuesto, fuera del bloque de cuatro dedos.
            for (dx=[-ear_x,ear_x])
                palm_knuckle_ear_x(28+dx,thumb_y,pivot_z+3,ear_t);
        }

        for (cx=[-18,-6,6,18])
            translate([cx,front_y,pivot_z])
                rotate([0,90,0]) cylinder(h=30,d=finger_pin_d,center=true);
        translate([28,thumb_y,pivot_z+3])
            rotate([0,90,0]) cylinder(h=30,d=finger_pin_d,center=true);
        // Guías de tendón alineadas con cada dedo.
        for (cx=[-18,-6,6,18])
            translate([cx,front_y,-2]) cylinder(h=32,d=finger_cable_d,center=true);
        translate([28,thumb_y,-1]) cylinder(h=30,d=finger_cable_d,center=true);
    }
}

// Falange modular visualmente limpia: cuerpo afilado, casquillos circulares
// y dos pasos M2 para que las tres piezas se reconozcan al primer vistazo.
module finger_link(
    len=main_prox_len,
    body_w=12,
    body_d=9,
    top_eye_depth=12,
    next_eye_depth=9
) {
    difference() {
        union() {
            translate([0,0,-len/2])
                lofted_solid(len,[body_w,body_d],[body_w*0.84,body_d*0.84],max(2,body_w/3));
            rotate([90,0,0]) cylinder(h=top_eye_depth,d=body_w+2,center=true);
            translate([0,0,-len])
                rotate([90,0,0])
                    cylinder(h=next_eye_depth,d=body_w+1,center=true);
        }
        // Canal longitudinal para el tendón de cierre.
        translate([0,-body_d/4,-len/2])
            cylinder(h=len+18,d=finger_cable_d,center=true);
        // Alojamiento dorsal superficial para muelle de torsión o elastómero.
        translate([0,body_d/2-0.9,-len+2])
            rotate([90,0,0]) cylinder(h=2.0,d=return_pocket_d,center=true);
        translate([0,0,0])
            rotate([90,0,0]) cylinder(h=30,d=finger_pin_d,center=true);
        translate([0,0,-len])
            rotate([90,0,0]) cylinder(h=30,d=finger_pin_d,center=true);
    }
}

// Falange distal universal con ojo central y punta redondeada.
module finger_distal(len=main_dist_len,body_w=10,body_d=8,eye_depth=8) {
    difference() {
        union() {
            translate([0,0,-len/2])
                lofted_solid(len,[body_w,body_d],[body_w*0.68,body_d*0.68],max(2,body_w/3));
            rotate([90,0,0]) cylinder(h=eye_depth,d=body_w+2,center=true);
            translate([0,1,-len]) sphere(d=body_w+1);
        }
        translate([0,-body_d/4,-len/2])
            cylinder(h=len+12,d=finger_cable_d,center=true);
        translate([0,body_d/2-0.8,-len+2])
            rotate([90,0,0]) cylinder(h=1.8,d=return_pocket_d,center=true);
        rotate([90,0,0]) cylinder(h=24,d=finger_pin_d,center=true);
    }
}

module articulated_main_finger(prox_angle=-12,mid_angle=-22,dist_angle=-20) {
    rotate([0,prox_angle,0]) {
        color(detail_view ? [0.26,0.28,0.30] : [0.09,0.105,0.12])
            finger_link(main_prox_len,10,7.5,10,8);
        translate([0,0,-main_prox_len]) rotate([0,mid_angle,0]) {
            color(detail_view ? [0.42,0.44,0.46] : [0.13,0.145,0.16])
                finger_link(main_mid_len,9,7,8,7);
            translate([0,0,-main_mid_len]) rotate([0,dist_angle,0])
                color(detail_view ? [0.60,0.62,0.64] : [0.19,0.20,0.21])
                    finger_distal(main_dist_len,8,6.8,7);
        }
    }
}

module articulated_thumb(prox_angle=20,mid_angle=28,dist_angle=30) {
    rotate([0,prox_angle,0]) {
        color(detail_view ? [0.30,0.32,0.34] : [0.11,0.125,0.14])
            finger_link(thumb_prox_len,10,7.5,10,7);
        translate([0,0,-thumb_prox_len]) rotate([0,mid_angle,0]) {
            color(detail_view ? [0.44,0.46,0.48] : [0.15,0.165,0.18])
                finger_link(thumb_mid_len,9,7,8,7);
            translate([0,0,-thumb_mid_len]) rotate([0,dist_angle,0])
                color(detail_view ? [0.56,0.58,0.60] : [0.19,0.20,0.21])
                    finger_distal(thumb_dist_len,8,6.8,7);
        }
    }
}

// Vista montada: cuatro dedos verticales y un pulgar lateral oponible.
module articulated_hand_assembly() {
    color(detail_view ? [0.20,0.22,0.25] : black) hand_palm_shell();

    // Los cuatro dedos se abren gradualmente desde el centro hacia los lados.
    // Se intercambian físicamente las posiciones de los dos dedos centrales.
    main_x=[-18,6,-6,18];
    // Corrección de 35° hacia dentro respecto a la postura abierta anterior.
    inward_correction=35;
    // Se intercambian las orientaciones de los dos dedos centrales.
    main_rz=[108-inward_correction,82+inward_correction,
             98-inward_correction,72+inward_correction];
    for (i=[0:3])
        translate([main_x[i],-6,-10]) rotate([0,0,main_rz[i]])
            articulated_main_finger(-10,-20,-18);

    // Pulgar más corto, lateral y orientado hacia la base de los dedos.
    translate([28,7,-7]) rotate([-90,0,0]) rotate([0,0,270])
        articulated_thumb(20,28,30);
}

// Vista auxiliar del acoplamiento con las dimensiones exactas del hombro
// aprobado: aro Ø126/98, disco Ø98/34 y tapa Ø72 con paso M4.
module shoulder_connection_preview() {
    color(white) translate([-50,0,0])
        rotate([0,90,0]) difference() {
            cylinder(h=52,d=126,center=true);
            cylinder(h=56,d=98,center=true);
        }
    color(black) translate([-20,0,0])
        rotate([0,90,0]) difference() {
            cylinder(h=12,d=98,center=true);
            cylinder(h=14,d=34,center=true);
        }
    color(dark) translate([-13,0,0])
        rotate([0,90,0]) difference() {
            cylinder(h=5,d=72,center=true);
            cylinder(h=7,d=4.4,center=true);
        }
    color(black) shoulder_anchor();
    color(white) translate([4,0,0]) shoulder_outer_hood();
    color(white) translate([-12,0,-92]) rotate([0,-5,0]) upper_arm_shell();
}

module arm_assembly(side=1) {
    sx=side;

    color(black)
        translate([sx*234,0,0]) scale([sx,1,1]) shoulder_anchor();
    color(white)
        translate([sx*238,0,0]) scale([sx,1,1]) shoulder_outer_hood();

    color(white)
        translate([sx*222,0,-92]) rotate([0,-sx*5,0]) upper_arm_shell();
    color([0.78,0.81,0.83])
        translate([sx*229,-36,-95]) rotate([0,-sx*5,0]) upper_arm_seam();

    color(black) translate([sx*236,0,-186]) elbow_cover();
    color(dark)  translate([sx*270,0,-186]) elbow_side_cap();

    color(white)
        translate([sx*240,0,-285]) rotate([0,-sx*3,0]) forearm_shell();
    color([0.78,0.81,0.83])
        translate([sx*245,-30,-286]) rotate([0,-sx*3,0]) forearm_seam();

    color(black) translate([sx*244,0,-374]) wrist_cuff();
    translate([sx*246,0,-416]) scale([sx,1,1]) articulated_hand_assembly();
}

module arms_assembly() {
    arm_assembly(-1);
    arm_assembly(1);
}

if (part == "assembly") arms_assembly();
else if (part == "hand_detail") articulated_hand_assembly();
else if (part == "shoulder_connection_preview") shoulder_connection_preview();
else if (part == "upper_arm_shell_left") upper_arm_shell();
else if (part == "upper_arm_shell_right") mirror([1,0,0]) upper_arm_shell();
else if (part == "upper_arm_seam") upper_arm_seam();
else if (part == "elbow_cover") elbow_cover();
else if (part == "elbow_side_cap") elbow_side_cap();
else if (part == "forearm_shell_left") forearm_shell();
else if (part == "forearm_shell_right") mirror([1,0,0]) forearm_shell();
else if (part == "forearm_seam") forearm_seam();
else if (part == "wrist_cuff") wrist_cuff();
else if (part == "shoulder_anchor") shoulder_anchor();
else if (part == "shoulder_outer_hood") shoulder_outer_hood();
else if (part == "hand_palm_left") hand_palm_shell();
else if (part == "hand_palm_right") mirror([1,0,0]) hand_palm_shell();
else if (part == "finger_proximal_main") finger_link(main_prox_len,10,7.5,10,8);
else if (part == "finger_middle_main") finger_link(main_mid_len,9,7,8,7);
else if (part == "finger_distal_main") finger_distal(main_dist_len,8,6.8,7);
else if (part == "thumb_proximal") finger_link(thumb_prox_len,10,7.5,10,7);
else if (part == "thumb_middle") finger_link(thumb_mid_len,9,7,8,7);
else if (part == "thumb_distal") finger_distal(thumb_dist_len,8,6.8,7);
else assert(false,str("Pieza desconocida: ",part));
