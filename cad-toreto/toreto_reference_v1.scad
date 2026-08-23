// Robot Toreto Reference V1
// Visual CAD concept closer to the original reference image.
// Units: millimeters.
//
// Open in OpenSCAD. Change "part" to export individual STL files.
// This is still a concept shell: final motor, bearing, screen and battery
// holes must be adapted to the real components you buy.

$fn = 96;

part = "assembly";
exploded = false;
show_height_marker = false;

target_height = 950;

// Main proportions inspired by the reference image.
base_d = 410;
base_h = 170;
base_lower_h = 62;
base_upper_h = 74;
waist_h = 165;

torso_w = 245;
torso_d = 178;
torso_h = 265;

neck_h = 108;

head_w = 232;
head_d = 132;
head_h = 136;

wall = 3.0;
clearance = 0.35;

white = [0.88, 0.86, 0.80];
black = [0.025, 0.027, 0.027];
dark = [0.08, 0.085, 0.085];
blue = [0.00, 0.55, 0.95];
glass = [0.005, 0.010, 0.016];

// ----------------- Utilities -----------------

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

module m3_hole(h=20) {
    cylinder(h=h, d=3.25, center=true);
}

module m4_hole(h=24) {
    cylinder(h=h, d=4.35, center=true);
}

module screw_boss(h=14, od=9, id=3.25) {
    difference() {
        cylinder(h=h, d=od, center=true);
        cylinder(h=h+0.6, d=id, center=true);
    }
}

module cable_slot(size=[40, 12, 24]) {
    rounded_box(size, r=4, center=true);
}

// ----------------- Base -----------------

module base_lower_full() {
    difference() {
        union() {
            cylinder(h=base_lower_h, d=base_d, center=true);
            translate([0, -base_d/2 + 18, 5])
                rounded_box([168, 36, 34], r=10, center=true);
        }
        cylinder(h=base_lower_h+2, d=255, center=true);
        translate([0, -base_d/2 + 3, 5])
            rounded_box([128, 22, 20], r=7, center=true);
    }
}

module base_upper_full() {
    difference() {
        union() {
            cylinder(h=base_upper_h, d=360, center=true);
            translate([0, 0, 24]) cylinder(h=28, d=286, center=true);
        }
        cylinder(h=base_upper_h+35, d=176, center=true);
        for (a=[0:45:315]) {
            rotate([0, 0, a]) translate([128, 0, 0]) m4_hole(base_upper_h + 40);
        }
    }
}

module base_quadrant(level="lower") {
    h = level == "lower" ? base_lower_h : base_upper_h;
    d = level == "lower" ? base_d : 360;
    inner = level == "lower" ? 255 : 176;

    difference() {
        intersection() {
            cylinder(h=h, d=d, center=true);
            translate([d/4, d/4, 0])
                cube([d/2 + 2, d/2 + 2, h + 2], center=true);
        }
        cylinder(h=h+3, d=inner, center=true);
        for (p=[[18, 118], [18, 176], [118, 18], [176, 18]]) {
            translate([p[0], p[1], 0]) m4_hole(h+6);
        }
        translate([125, 125, 0]) cylinder(h=h+3, d=76, center=true);
    }
}

module front_sensor_panel() {
    difference() {
        rounded_box([154, 24, 38], r=8, center=true);
        for (x=[-48, 0, 48]) {
            translate([x, -13, 4])
                rotate([90, 0, 0])
                    cylinder(h=18, d=18, center=true);
        }
        for (x=[-65, 65]) {
            translate([x, -13, -12])
                rotate([90, 0, 0])
                    cylinder(h=18, d=7, center=true);
        }
    }
}

module lidar_cap() {
    difference() {
        union() {
            cylinder(h=22, d=58, center=true);
            translate([0, 0, 13]) cylinder(h=18, d=42, center=true);
        }
        translate([0, 0, 23]) cylinder(h=8, d=30, center=true);
        for (a=[0:120:240]) rotate([0, 0, a]) translate([22, 0, 0]) m3_hole(28);
    }
}

module omni_wheel_dummy() {
    // Decorative placeholder, not a functional omni wheel.
    rotate([90, 0, 0]) {
        color(black) cylinder(h=52, d=88, center=true);
        color(dark) cylinder(h=56, d=56, center=true);
    }
    for (a=[0:45:315]) {
        rotate([0, 0, a])
            translate([34, 0, 0])
                rotate([90, 0, 0])
                    color([0.11, 0.11, 0.11]) cylinder(h=58, d=14, center=true);
    }
    color(blue)
        rotate([90, 0, 0])
            cylinder(h=58, d=18, center=true);
}

module wheel_pod_shell() {
    difference() {
        rounded_box([102, 56, 92], r=16, center=true);
        rotate([90, 0, 0]) cylinder(h=64, d=76, center=true);
        translate([0, -31, 0]) rotate([90, 0, 0]) cylinder(h=10, d=84, center=true);
    }
}

module base_assembly() {
    color(black) translate([0, 0, base_lower_h/2]) base_lower_full();
    color(white) translate([0, 0, base_lower_h + base_upper_h/2 - 2]) base_upper_full();
    color(black) translate([0, 0, base_h - 18]) cylinder(h=26, d=235, center=true);
    color(white) translate([0, 0, base_h + 4]) lidar_cap();
    color(black) translate([0, -base_d/2 + 15, base_lower_h/2 + 4]) front_sensor_panel();

    for (a=[0, 120, 240]) {
        rotate([0, 0, a]) {
            translate([0, -base_d/2 + 37, base_lower_h/2 - 10]) omni_wheel_dummy();
            color(white) translate([0, -base_d/2 + 37, base_lower_h/2 - 10]) wheel_pod_shell();
        }
    }
}

// ----------------- Waist and torso -----------------

module waist_stack() {
    color(black) {
        translate([0, 0, 0]) cylinder(h=waist_h, d=115, center=true);
        translate([0, 0, -waist_h/2 + 18]) cylinder(h=24, d=155, center=true);
        translate([0, 0, waist_h/2 - 18]) cylinder(h=24, d=150, center=true);
    }
    color(dark) {
        for (z=[-48, 0, 48]) translate([0, 0, z]) cylinder(h=10, d=142, center=true);
    }
}

module torso_outer() {
    rounded_box([torso_w, torso_d, torso_h], r=30, center=true);
}

module torso_inner() {
    rounded_box([torso_w - 2*wall, torso_d - 2*wall, torso_h - 2*wall], r=26, center=true);
}

module torso_shell(side="front") {
    difference() {
        intersection() {
            difference() {
                torso_outer();
                torso_inner();
            }
            if (side == "front") front_half([340, 280, 340]);
            else back_half([340, 280, 340]);
        }

        if (side == "front") {
            translate([0, -torso_d/2 - 0.3, 42])
                rounded_box([154, 15, 104], r=18, center=true);
            translate([0, -torso_d/2 - 0.3, -82])
                rounded_box([142, 15, 42], r=10, center=true);
            translate([0, -torso_d/2 - 0.3, -124])
                rounded_box([78, 15, 18], r=6, center=true);
        } else {
            translate([0, torso_d/2 + 0.3, -78])
                rounded_box([118, 15, 58], r=10, center=true);
        }

        if (side == "front") translate([0, 0.2, 0]) cube([300, clearance, 310], center=true);
        else translate([0, -0.2, 0]) cube([300, clearance, 310], center=true);
    }

    for (x=[-98, 98], z=[-104, -38, 80]) {
        translate([x, side == "front" ? -28 : 28, z])
            rotate([90, 0, 0])
                screw_boss(h=24, od=10, id=3.25);
    }
}

module torso_display_insert() {
    color(glass) {
        translate([0, 0, 42]) rounded_box([146, 7, 96], r=16, center=true);
        translate([0, 0, -82]) rounded_box([134, 7, 34], r=8, center=true);
    }
    color(blue) translate([0, -4, 42]) {
        for (x=[-48:12:48]) {
            h = 14 + 18 * abs(sin(x * 7));
            translate([x, 0, 0]) cube([3, 3, h], center=true);
        }
    }
}

module torso_front_bezel() {
    difference() {
        union() {
            rounded_box([212, 12, 178], r=24, center=true);
            translate([0, 0, -118]) rounded_box([160, 12, 52], r=12, center=true);
        }
        translate([0, 0, 42]) rounded_box([154, 16, 104], r=18, center=true);
        translate([0, 0, -82]) rounded_box([142, 16, 42], r=10, center=true);
        translate([0, 0, -124]) rounded_box([78, 16, 18], r=6, center=true);
    }
}

module shoulder_pod(left=true) {
    mirror_x(!left)
        difference() {
            union() {
                translate([torso_w/2 + 25, 0, 72])
                    rotate([90, 0, 0])
                        cylinder(h=76, d=92, center=true);
                translate([torso_w/2 + 1, 0, 72])
                    rounded_box([48, 82, 94], r=18, center=true);
            }
            translate([torso_w/2 + 25, 0, 72])
                rotate([90, 0, 0])
                    cylinder(h=82, d=52, center=true);
            translate([torso_w/2 + 25, 0, 72])
                rotate([90, 0, 0])
                    m4_hole(92);
        }
}

module shoulder_black_insert(left=true) {
    mirror_x(!left)
        translate([torso_w/2 + 25, -41, 72])
            rotate([90, 0, 0])
                cylinder(h=8, d=58, center=true);
}

module torso_assembly() {
    color(white) torso_shell("front");
    color(black) torso_shell("back");
    color(white) translate([0, -torso_d/2 - 7, 0]) torso_front_bezel();
    color(glass) translate([0, -torso_d/2 - 7, 0]) torso_display_insert();
    color(white) {
        shoulder_pod(true);
        shoulder_pod(false);
    }
    color(black) {
        shoulder_black_insert(true);
        shoulder_black_insert(false);
    }
}

// ----------------- Neck and head -----------------

module neck_stack() {
    difference() {
        union() {
            cylinder(h=neck_h, d=76, center=true);
            translate([0, 0, -neck_h/2 + 10]) cylinder(h=20, d=104, center=true);
            translate([0, 0, neck_h/2 - 10]) cylinder(h=20, d=96, center=true);
            for (z=[-24, 18]) translate([0, 0, z]) cylinder(h=14, d=84, center=true);
        }
        cylinder(h=neck_h + 3, d=40, center=true);
        for (a=[0:90:270]) {
            rotate([0, 0, a]) translate([36, 0, -neck_h/2 + 10]) m4_hole(24);
            rotate([0, 0, a]) translate([33, 0, neck_h/2 - 10]) m4_hole(24);
        }
    }
}

module head_outer() {
    rounded_box([head_w, head_d, head_h], r=30, center=true);
}

module head_inner() {
    rounded_box([head_w - 2*wall, head_d - 2*wall, head_h - 2*wall], r=26, center=true);
}

module head_shell(side="front") {
    difference() {
        intersection() {
            difference() {
                head_outer();
                head_inner();
            }
            if (side == "front") front_half([320, 230, 210]);
            else back_half([320, 230, 210]);
        }

        if (side == "front") {
            translate([0, -head_d/2 - 0.3, 8])
                rounded_box([178, 16, 78], r=17, center=true);
            for (x=[-84, 84]) {
                translate([x, -head_d/2 - 0.3, -36])
                    rotate([90, 0, 0])
                        cylinder(h=18, d=6, center=true);
            }
        } else {
            translate([0, head_d/2 + 0.3, -28])
                rounded_box([128, 15, 42], r=10, center=true);
        }

        if (side == "front") translate([0, 0.2, 0]) cube([280, clearance, 175], center=true);
        else translate([0, -0.2, 0]) cube([280, clearance, 175], center=true);
    }

    for (x=[-92, 92], z=[-44, 46]) {
        translate([x, side == "front" ? -22 : 22, z])
            rotate([90, 0, 0])
                screw_boss(h=20, od=9.5, id=3.25);
    }
}

module head_face_plate() {
    difference() {
        rounded_box([184, 7, 84], r=18, center=true);
        for (x=[-48, 48]) {
            translate([x, -4, 13])
                rotate([90, 0, 0])
                    cylinder(h=10, d=36, center=true);
        }
    }
}

module eye_pair() {
    for (x=[-48, 48]) {
        translate([x, 0, 13]) {
            color(blue) rotate([90, 0, 0]) cylinder(h=4, d=33, center=true);
            color(glass) rotate([90, 0, 0]) cylinder(h=5, d=23, center=true);
            color(blue) rotate([90, 0, 0]) cylinder(h=6, d=7, center=true);
        }
    }
}

module head_side_pod(left=true) {
    mirror_x(!left)
        difference() {
            union() {
                translate([head_w/2 + 14, 0, 0])
                    rounded_box([34, 70, 94], r=17, center=true);
                translate([head_w/2 + 20, 0, 0])
                    rotate([90, 0, 0])
                        cylinder(h=58, d=76, center=true);
            }
            translate([head_w/2 + 20, -30, 0])
                rotate([90, 0, 0])
                    cylinder(h=14, d=48, center=true);
            translate([head_w/2 + 20, 0, 0])
                rotate([90, 0, 0])
                    m4_hole(78);
        }
}

module head_assembly() {
    color(white) {
        head_shell("front");
        head_shell("back");
        head_side_pod(true);
        head_side_pod(false);
    }
    color(glass) translate([0, -head_d/2 - 6, 8]) head_face_plate();
    translate([0, -head_d/2 - 11, 8]) eye_pair();
    color(black) {
        translate([head_w/2 + 20, -34, 0]) rotate([90, 0, 0]) cylinder(h=8, d=48, center=true);
        translate([-head_w/2 - 20, -34, 0]) rotate([90, 0, 0]) cylinder(h=8, d=48, center=true);
    }
}

// ----------------- Arms -----------------

module arm_link(len=205, dia=58, depth=44) {
    difference() {
        hull() {
            translate([0, 0, -len/2 + dia/2])
                rotate([90, 0, 0]) cylinder(h=depth, d=dia, center=true);
            translate([0, 0, len/2 - dia/2])
                rotate([90, 0, 0]) cylinder(h=depth, d=dia, center=true);
        }
        hull() {
            translate([0, 0, -len/2 + dia/2])
                rotate([90, 0, 0]) cylinder(h=depth + 3, d=dia - 15, center=true);
            translate([0, 0, len/2 - dia/2])
                rotate([90, 0, 0]) cylinder(h=depth + 3, d=dia - 15, center=true);
        }
        translate([0, 0, -len/2 + dia/2]) rotate([90, 0, 0]) m4_hole(depth + 8);
        translate([0, 0, len/2 - dia/2]) rotate([90, 0, 0]) m4_hole(depth + 8);
    }
}

module upper_arm_shell() {
    arm_link(205, 64, 48);
}

module forearm_shell() {
    arm_link(190, 54, 42);
}

module joint_disc(d=52, depth=44) {
    difference() {
        rotate([90, 0, 0]) cylinder(h=depth, d=d, center=true);
        rotate([90, 0, 0]) m4_hole(depth + 8);
    }
}

module gripper_three_finger() {
    union() {
        difference() {
            cylinder(h=36, d=44, center=true);
            cylinder(h=38, d=18, center=true);
        }
        translate([0, 0, -38]) rounded_box([38, 34, 46], r=8, center=true);

        for (x=[-18, 18]) {
            translate([x, -7, -82])
                rotate([0, 0, x > 0 ? -12 : 12])
                    rounded_box([12, 18, 60], r=4, center=true);
        }
        translate([0, 12, -78])
            rounded_box([11, 16, 54], r=4, center=true);
    }
}

module arm_assembly(left=true) {
    mirror_x(!left) {
        color(black) translate([torso_w/2 + 52, -1, 72]) joint_disc(58, 60);
        color(white) translate([torso_w/2 + 72, 0, -34])
            rotate([0, 12, 0]) upper_arm_shell();
        color(black) translate([torso_w/2 + 92, 0, -136]) joint_disc(48, 48);
        color(white) translate([torso_w/2 + 103, 0, -244])
            rotate([0, -10, 0]) forearm_shell();
        color(black) translate([torso_w/2 + 118, 0, -338]) joint_disc(38, 40);
        color(black) translate([torso_w/2 + 122, 0, -390]) gripper_three_finger();
    }
}

// ----------------- Full assembly -----------------

module full_assembly() {
    base_z = 0;
    waist_z = base_h + waist_h/2 - 4;
    torso_z = base_h + waist_h + torso_h/2 - 32;
    neck_z = torso_z + torso_h/2 + neck_h/2 - 8;
    head_z = neck_z + neck_h/2 + head_h/2 + 8;

    translate([0, 0, base_z]) base_assembly();
    translate([0, 0, waist_z]) waist_stack();
    translate([0, 0, torso_z]) torso_assembly();
    translate([0, 0, neck_z]) color(black) neck_stack();
    translate([0, 0, head_z]) head_assembly();
    translate([0, 0, torso_z]) {
        arm_assembly(true);
        arm_assembly(false);
    }

    if (show_height_marker) {
        color([0.0, 0.55, 0.9, 0.22])
            translate([-275, 0, target_height/2])
                cube([5, 5, target_height], center=true);
    }
}

module exploded_assembly() {
    translate([0, 0, 0]) base_assembly();
    translate([0, 0, 255]) waist_stack();
    translate([0, 0, 520]) torso_assembly();
    translate([0, 0, 745]) color(black) neck_stack();
    translate([0, 0, 925]) head_assembly();
    translate([330, 0, 520]) arm_assembly(true);
    translate([-330, 0, 520]) arm_assembly(false);
}

// ----------------- Part selector -----------------

if (part == "assembly") {
    if (exploded) exploded_assembly(); else full_assembly();
} else if (part == "base_lower_quadrant") {
    base_quadrant("lower");
} else if (part == "base_upper_quadrant") {
    base_quadrant("upper");
} else if (part == "front_sensor_panel") {
    front_sensor_panel();
} else if (part == "lidar_cap") {
    lidar_cap();
} else if (part == "wheel_pod_shell") {
    wheel_pod_shell();
} else if (part == "omni_wheel_dummy") {
    omni_wheel_dummy();
} else if (part == "waist_stack") {
    waist_stack();
} else if (part == "torso_front_shell") {
    torso_shell("front");
} else if (part == "torso_back_shell") {
    torso_shell("back");
} else if (part == "torso_display_insert") {
    torso_display_insert();
} else if (part == "torso_front_bezel") {
    torso_front_bezel();
} else if (part == "shoulder_pod_left") {
    shoulder_pod(true);
} else if (part == "shoulder_pod_right") {
    shoulder_pod(false);
} else if (part == "neck_stack") {
    neck_stack();
} else if (part == "head_front_shell") {
    head_shell("front");
} else if (part == "head_back_shell") {
    head_shell("back");
} else if (part == "head_face_plate") {
    head_face_plate();
} else if (part == "eye_pair") {
    eye_pair();
} else if (part == "head_side_pod") {
    head_side_pod(true);
} else if (part == "upper_arm_shell") {
    upper_arm_shell();
} else if (part == "forearm_shell") {
    forearm_shell();
} else if (part == "joint_disc_shoulder") {
    joint_disc(58, 60);
} else if (part == "joint_disc_elbow") {
    joint_disc(48, 48);
} else if (part == "joint_disc_wrist") {
    joint_disc(38, 40);
} else if (part == "gripper_three_finger") {
    gripper_three_finger();
} else {
    full_assembly();
}
