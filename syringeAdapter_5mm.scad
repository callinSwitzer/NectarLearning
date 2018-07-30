module sadapt(){
    
    intersection(){ translate([0, 1, -4]) cylinder(h = 50, d = 11, $fn = 20);
difference(){
    translate([-4, -4, -2]) cube([8, 10, 12]);
    cylinder(h = 5.8, d = 4.5, $fn = 20);
    {translate([-4, 0, 6]) cylinder(h = 20, d = 3, $fn = 20); 
    translate([4, 0, 6]) cylinder(h = 20, d = 3, $fn = 20); 

    translate([-10, 0, 6]) rotate([0, 90, 0]) cylinder(h = 20, d = 3, $fn = 20); 
        }
    //translate([0, 0, -4]) cylinder(h = 5.8, d = 5, $fn = 20);
        translate([0,0, -2]) cylinder(r1 = 5.2/2, r2 = 4.5/2, h = 6, $fn = 20);
        //translate([0, 2.5, -3]) cylinder(h = 20, d = 1.5, $fn = 30);
        translate([0, 7, 0])
rotate([0, 90, 0])
rotate_extrude(convexity = 20)
translate([5, 0, 0])
circle(r = 1, $fn = 50);
        
        translate([0, 9, -6])
rotate([0, 90, 0])
rotate_extrude(convexity = 20)
translate([5, 0, 0])
circle(r = 1, $fn = 50);
    }
}

}
sadapt(); 



