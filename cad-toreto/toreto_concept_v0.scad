// Toreto Concept V0
// Parametric CAD concept for a modular assistant robot.
// Units: millimeters.
//
// Open in OpenSCAD. Change "part" to export individual STL files.
// Suggested export parts:
// assembly, base_quadrant, base_center_plate, torso_front, torso_back,
// head_front, head_back, head_side_pod, upper_arm_shell, forearm_shell,
// wrist_gripper_concept, wheel_cover, sensor_panel.

$fn = 72;

part = "assembly";
show_exploded = true;

// Printer envelope for Bambu P1S reference.
printer_x = 256;
printer_y = 256;
printer_z = 256;

// Main robot reference dimensions.
target_height = 950;
base_diameter = 400;
base_height = 150;
torso_w = 230;
torso_d = 170;
torso_h = 220;
neck_h = 78;
head_w = 220;
head_d = 120;
head_h = 112;
wall = 3.0;
fit_clearance = 0.35;

// ---------- Utility geometry ----------

module rounded_rect_2d(size=[20, 20], r=3) {
    hull() {
        translate([r, r]) circle(r=r);
        translate([size[0]-r, r]) circle(r=r);
        translate([r, size[1]-r]) circle(r=r);
        translate([size[0]-r, size[1]-r]) circle(r=r);
    }
}

module rounded_box(size=[20, 20, 20], r=3, center=true) {
    translate(center ? [-size[0]/2, -size[1]/2, -size[2]/2] : [0, 0, 0])
        linear_extrude(height=size[2])
            rounded_rect_2d([size[0], size[1]], min(r, min(size[0], size[1]) / 2 - 0.1));
}

module half_space(side="front", size=[1000, 1000, 1000]) {
    // Front is negative Y. Back is positive Y.
    if (side == "front") {
        translate([0, -size[1]/4, 0]) cube([size[0], size[1]/2, size[2]], center=true);
    } else {
        translate([0, size[1]/4, 0]) cube([size[0], size[1]/2, size[2]], center=true);
    }
}

module screw_boss(h=12, od=9, id=3.1) {
    difference() {
        cylinder(h=h, d=od, center=true);
        cylinder(h=h+0.4, d=id, center=true);
    }
}

module m3_hole(h=20) {
    cylinder(h=h, d=3.2, center=true);
}

module m4_hole(h=20) {
    cylinder(h=h, d=4.3, center=true);
}

module mirror_x(enabled=false) {
    if (enabled) mirror([1, 0, 0]) children();
    else children();
}

module label_plate(size=[38, 12, 1.6]) {
    color([0.02, 0.02, 0.02])
        rounded_box(size, r=2, center=true);
}

// ---------- Head ----------

module head_outer() {
    rounded_box([head_w, head_d, head_h], r=20, center=true);
}

module head_inner() {
    rounded_box([head_w - 2*wall, head_d - 2*wall, head_h - 2*wall], r=17, center=true);
}

module head_shell(side="front") {
    difference() {
        intersection() {
            difference() {
                head_outer();
                head_inner();
            }
            half_space(side, [320, 240, 180]);
        }

        // Split seam clearance.
        if (side == "front") {
            translate([0, 0.25, 0]) cube([260, fit_clearance, 140], center=true);
        } else {
            translate([0, -0.25, 0]) cube([260, fit_clearance, 140], center=true);
        }

        // Face screen opening and camera/microphone holes.
        if (side == "front") {
            translate([0, -head_d/2 - 0.2, 8])
                rounded_box([166, 12, 64], r=10, center=true);

            for (x=[-48, 48]) {
                translate([x, -head_d/2 - 3, 18])
                    rotate([90, 0, 0])
                        cylinder(h=20, d=20, center=true);
            }

            for (x=[-76, 76]) {
                translate([x, -head_d/2 - 3, -25])
                    rotate([90, 0, 0])
                        cylinder(h=20, d=5, center=true);
            }
        }
    }

    // Internal screw bosses for joining both halves.
    for (x=[-88, 88], z=[-38, 42]) {
        translate([x, side == "front" ? -18 : 18, z])
            rotate([90, 0, 0])
                screw_boss(h=18, od=9, id=3.1);
    }
}

module head_side_pod(left=true) {
    mirror_x(!left)
        difference() {
            union() {
                translate([head_w/2 + 14, 0, 0])
                    rotate([90, 0, 0])
                        cylinder(h=46, d=72, center=true);
                translate([head_w/2 + 8, 0, 0])
                    rounded_box([28, 56, 76], r=12, center=true);
            }
            translate([head_w/2 + 14, 0, 0])
                rotate([90, 0, 0])
                    cylinder(h=50, d=45, center=true);
            translate([head_w/2 + 14, -24, 0])
                rotate([90, 0, 0])
                    m4_hole(20);
            translate([head_w/2 + 14, 24, 0])
                rotate([90, 0, 0])
                    m4_hole(20);
        }
}

module head_assembly() {
    color([0.88, 0.86, 0.82]) head_shell("front");
    color([0.78, 0.77, 0.73]) head_shell("back");
    color([0.88, 0.86, 0.82]) {
        head_side_pod(true);
        head_side_pod(false);
    }
    translate([0, -head_d/2 - 5, 8]) color([0.01, 0.02, 0.03])
        rounded_box([160, 5, 58], r=9, center=true);
}

// ---------- Neck ----------

module neck_column() {
    difference() {
        union() {
            cylinder(h=neck_h, d=72, center=true);
            translate([0, 0, -neck_h/2 + 7]) cylinder(h=14, d=96, center=true);
            translate([0, 0, neck_h/2 - 7]) cylinder(h=14, d=92, center=true);
        }
        cylinder(h=neck_h + 1, d=42, center=true);
        for (a=[0:90:270]) {
            rotate([0, 0, a]) translate([34, 0, -neck_h/2 + 7]) m4_hole(18);
            rotate([0, 0, a]) translate([32, 0, neck_h/2 - 7]) m4_hole(18);
        }
    }
}

// ---------- Torso ----------

module torso_outer() {
    rounded_box([torso_w, torso_d, torso_h], r=22, center=true);
}

module torso_inner() {
    rounded_box([torso_w - 2*wall, torso_d - 2*wall, torso_h - 2*wall], r=19, center=true);
}

module torso_shell(side="front") {
    difference() {
        intersection() {
            difference() {
                torso_outer();
                torso_inner();
            }
            half_space(side, [330, 260, 300]);
        }

        if (side == "front") {
            translate([0, -torso_d/2 - 0.2, 28])
                rounded_box([116, 12, 88], r=12, center=true);
            translate([0, -torso_d/2 - 0.2, -72])
                rounded_box([150, 12, 42], r=8, center=true);
        }

        // Cable exit and service ports.
        if (side == "back") {
            translate([0, torso_d/2 + 0.2, -70])
                rounded_box([92, 12, 40], r=8, center=true);
        }
    }

    for (x=[-92, 92], z=[-86, -22, 62]) {
        translate([x, side == "front" ? -24 : 24, z])
            rotate([90, 0, 0])
                screw_boss(h=22, od=10, id=3.1);
    }
}

module shoulder_mount(left=true) {
    mirror_x(!left)
        difference() {
            union() {
                translate([torso_w/2 + 18, 0, 60])
                    rotate([90, 0, 0])
                        cylinder(h=78, d=82, center=true);
                translate([torso_w/2 - 4, 0, 60])
                    rounded_box([42, 86, 90], r=14, center=true);
            }
            translate([torso_w/2 + 18, 0, 60])
                rotate([90, 0, 0])
                    cylinder(h=82, d=48, center=true);
            translate([torso_w/2 + 18, 0, 60])
                rotate([90, 0, 0])
                    m4_hole(90);
        }
}

module torso_assembly() {
    color([0.88, 0.86, 0.82]) torso_shell("front");
    color([0.12, 0.13, 0.13]) torso_shell("back");
    color([0.12, 0.13, 0.13]) {
        shoulder_mount(true);
        shoulder_mount(false);
    }
    translate([0, -torso_d/2 - 5, 28]) label_plate([108, 5, 80]);
}

// ---------- Base ----------

module base_shell_reference() {
    difference() {
        union() {
            cylinder(h=55, d=base_diameter, center=true);
            translate([0, 0, 45]) cylinder(h=70, d=330, center=true);
            translate([0, 0, 88]) cylinder(h=24, d=245, center=true);
        }
        translate([0, 0, 10]) cylinder(h=160, d=250, center=true);
        translate([0, -base_diameter/2 + 18, 20])
            rounded_box([145, 24, 38], r=8, center=true);
    }
}

module base_quadrant() {
    // One quarter of the 400 mm base ring. Print four units.
    difference() {
        intersection() {
            cylinder(h=42, d=base_diameter, center=true);
            translate([base_diameter/4, base_diameter/4, 0])
                cube([base_diameter/2 + 2, base_diameter/2 + 2, 44], center=true);
        }
        cylinder(h=46, d=274, center=true);

        // Seam fasteners.
        for (p=[[112, 8], [178, 8], [8, 112], [8, 178]]) {
            translate([p[0], p[1], 0]) m4_hole(50);
        }

        // Pocket to reduce print time and weight.
        translate([132, 132, 0]) cylinder(h=46, d=92, center=true);
    }
}

module base_center_plate() {
    difference() {
        cylinder(h=12, d=236, center=true);
        cylinder(h=14, d=82, center=true);
        for (a=[0:45:315]) {
            rotate([0, 0, a]) translate([94, 0, 0]) m4_hole(16);
        }
    }
}

module electronics_box() {
    difference() {
        rounded_box([190, 150, 68], r=10, center=true);
        translate([0, 0, 4]) rounded_box([176, 136, 64], r=8, center=true);
        translate([0, -76, 8]) rounded_box([118, 10, 28], r=5, center=true);
        for (x=[-76, 76], y=[-56, 56]) {
            translate([x, y, -26]) m3_hole(12);
        }
    }
}

module wheel_cover() {
    difference() {
        rounded_box([78, 44, 92], r=14, center=true);
        translate([0, 0, 0])
            rotate([90, 0, 0])
                cylinder(h=50, d=58, center=true);
        translate([0, -24, 0])
            rotate([90, 0, 0])
                cylinder(h=12, d=64, center=true);
    }
}

module sensor_panel() {
    difference() {
        rounded_box([150, 18, 42], r=7, center=true);
        for (x=[-46, 0, 46]) {
            translate([x, -10, 4])
                rotate([90, 0, 0])
                    cylinder(h=16, d=19, center=true);
        }
        for (x=[-65, 65]) {
            translate([x, -10, -13])
                rotate([90, 0, 0])
                    cylinder(h=16, d=6, center=true);
        }
    }
}

module wheel_placeholder() {
    color([0.03, 0.03, 0.035])
        rotate([90, 0, 0])
            cylinder(h=50, d=90, center=true);
    color([0.08, 0.13, 0.16])
        rotate([90, 0, 0])
            cylinder(h=54, d=54, center=true);
}

module base_assembly() {
    color([0.88, 0.86, 0.82]) base_shell_reference();
    translate([0, 0, 94]) color([0.1, 0.1, 0.1]) electronics_box();
    translate([0, -base_diameter/2 + 19, 20]) color([0.02, 0.02, 0.025]) sensor_panel();
    for (a=[0, 120, 240]) {
        rotate([0, 0, a]) {
            translate([0, -base_diameter/2 + 36, -5]) wheel_placeholder();
            translate([0, -base_diameter/2 + 36, -5]) color([0.88, 0.86, 0.82]) wheel_cover();
        }
    }
}

// ---------- Arm ----------

module arm_link_shell(len=185, w=56, d=42) {
    difference() {
        hull() {
            translate([0, 0, -len/2 + w/2])
                rotate([90, 0, 0])
                    cylinder(h=d, d=w, center=true);
            translate([0, 0, len/2 - w/2])
                rotate([90, 0, 0])
                    cylinder(h=d, d=w, center=true);
        }
        hull() {
            translate([0, 0, -len/2 + w/2])
                rotate([90, 0, 0])
                    cylinder(h=d+2, d=w-14, center=true);
            translate([0, 0, len/2 - w/2])
                rotate([90, 0, 0])
                    cylinder(h=d+2, d=w-14, center=true);
        }
        translate([0, 0, -len/2 + w/2])
            rotate([90, 0, 0]) m4_hole(d+6);
        translate([0, 0, len/2 - w/2])
            rotate([90, 0, 0]) m4_hole(d+6);
    }
}

module upper_arm_shell() {
    color([0.86, 0.84, 0.8]) arm_link_shell(190, 62, 46);
}

module forearm_shell() {
    color([0.86, 0.84, 0.8]) arm_link_shell(180, 52, 40);
}

module wrist_gripper_concept() {
    difference() {
        union() {
            cylinder(h=34, d=42, center=true);
            translate([0, 0, -38]) rounded_box([36, 32, 48], r=8, center=true);
            for (x=[-17, 17]) {
                translate([x, -8, -78])
                    rotate([0, 0, x > 0 ? -10 : 10])
                        rounded_box([12, 18, 58], r=4, center=true);
            }
        }
        cylinder(h=40, d=18, center=true);
    }
}

module arm_assembly(left=true) {
    mirror_x(!left) {
        translate([torso_w/2 + 38, 0, 40])
            rotate([0, 18, 0]) upper_arm_shell();
        translate([torso_w/2 + 78, 0, -128])
            rotate([0, -14, 0]) forearm_shell();
        translate([torso_w/2 + 94, 0, -236]) wrist_gripper_concept();
        color([0.05, 0.05, 0.055]) {
            translate([torso_w/2 + 26, 0, 62])
                rotate([90, 0, 0]) cylinder(h=64, d=56, center=true);
            translate([torso_w/2 + 66, 0, -52])
                rotate([90, 0, 0]) cylinder(h=48, d=48, center=true);
            translate([torso_w/2 + 88, 0, -198])
                rotate([90, 0, 0]) cylinder(h=42, d=36, center=true);
        }
    }
}

// ---------- Full assembly ----------

module assembly() {
    z_base = base_height / 2;
    z_torso = 285;
    z_neck = z_torso + torso_h/2 + neck_h/2 + 8;
    z_head = z_neck + neck_h/2 + head_h/2 + 8;

    translate([0, 0, z_base]) base_assembly();
    translate([0, 0, z_torso]) torso_assembly();
    translate([0, 0, z_neck]) color([0.08, 0.08, 0.08]) neck_column();
    translate([0, 0, z_head]) head_assembly();
    translate([0, 0, z_torso]) {
        arm_assembly(true);
        arm_assembly(false);
    }

    // Ground/reference height marker.
    color([0.15, 0.6, 0.8, 0.28])
        translate([-260, 0, target_height/2])
            cube([4, 4, target_height], center=true);
}

module exploded_assembly() {
    translate([0, 0, 80]) base_assembly();
    translate([0, 0, 360]) torso_assembly();
    translate([0, 0, 590]) color([0.08, 0.08, 0.08]) neck_column();
    translate([0, 0, 760]) head_assembly();
    translate([260, 0, 430]) arm_assembly(true);
    translate([-260, 0, 430]) arm_assembly(false);
}

// ---------- Part selector ----------

if (part == "assembly") {
    if (show_exploded) exploded_assembly(); else assembly();
} else if (part == "base_quadrant") {
    base_quadrant();
} else if (part == "base_center_plate") {
    base_center_plate();
} else if (part == "electronics_box") {
    electronics_box();
} else if (part == "wheel_cover") {
    wheel_cover();
} else if (part == "sensor_panel") {
    sensor_panel();
} else if (part == "torso_front") {
    torso_shell("front");
} else if (part == "torso_back") {
    torso_shell("back");
} else if (part == "shoulder_mount_left") {
    shoulder_mount(true);
} else if (part == "shoulder_mount_right") {
    shoulder_mount(false);
} else if (part == "neck_column") {
    neck_column();
} else if (part == "head_front") {
    head_shell("front");
} else if (part == "head_back") {
    head_shell("back");
} else if (part == "head_side_pod") {
    head_side_pod(true);
} else if (part == "upper_arm_shell") {
    upper_arm_shell();
} else if (part == "forearm_shell") {
    forearm_shell();
} else if (part == "wrist_gripper_concept") {
    wrist_gripper_concept();
} else {
    assembly();
}
