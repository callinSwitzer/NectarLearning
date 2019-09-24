


translate([-63, -63, 14])
color("red")
import("D:/Dropbox/AcademiaDropbox/UW/3dPrints/tjunct.stl");


// vertical tube


// t junction
difference(){
union(){
difference() {
        
cylinder(r = 10.5, h = 28, $fn = 60);
//cylinder(r = 8.5, h = 33, $fn = 60);
};



// horizontal tube
translate([0,0,14])
rotate([0,90, 0])
difference() {
        
cylinder(r = 10.5, h = 15, $fn = 60);
//cylinder(r = 8.5, h = 33, $fn = 60);
};}


cylinder(r = 8.5, h = 33, $fn = 60);
translate([0,0,14])
rotate([0,90, 0])
// cone-shaped
cylinder(r2 = 9.2, r1 = 5.8, h = 15.1, $fn = 60);
};



