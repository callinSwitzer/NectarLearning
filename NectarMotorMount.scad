

motorSize = [40, 40, 31]; 
shaftDim = [5, 100]; 
motorTop = [22, 2,2];

syringeDim = [8, 10, 20]; 
MinStickOut = 13; 
MaxStickOut = 70; 

module motor(motorSize, shaftDim, motorTop){
union(){
cube(motorSize);
translate([motorSize[0] / 2, motorSize[1] / 2, motorSize[2]]) cylinder(h = motorTop[1], d = motorTop[0]); 
translate([motorSize[0] / 2, motorSize[1] / 2, -55]) cylinder(h = shaftDim[1], d = shaftDim[0]); 
    
    }
}


//motor(motorSize, shaftDim, motorTop);





module syringe(syringeDim, MinStickOut, MaxStickOut){
    
    cylinder(h = 30, d = syringeDim[0]); 
    translate([-syringeDim[1]/2, -syringeDim[2]/2, 0]) cube([syringeDim[1], syringeDim[2], 2]); 
    translate([0, 0, -MaxStickOut]) cylinder(h = MaxStickOut, d = 9); 
    
}





//make actuall cutout a little bigger
motorSize = [42, 42, 33]; 
shaftDim = [9, 100]; 
motorTop = [24, 3,3];

syringeDim = [9, 12, 22]; 
MinStickOut = 13; 
MaxStickOut = 70; 

difference(){
translate([-25, -120, -5]) cube([50, 125, 50]); 


linear_extrude([40]) projection(cut = true) rotate([90,0,0])   translate([-motorSize[0] / 2, -motorSize[0] / 2, 0]) motor(motorSize, shaftDim, motorTop);
translate([0,0,15]) linear_extrude([40]) projection(cut = true) translate([0, -110, 0]) rotate([90, 90,0]) syringe(syringeDim, MinStickOut, MaxStickOut);

// remove extra material
translate([10, -105, 0]) cube([20, 60, 100]); 
translate([-30, -105, 0]) cube([20, 60, 100]); 
translate([15, -130, -10]) cube([20, 60, 100]); 
translate([-35, -130, -10]) cube([20, 60, 100]); 

translate([-35, -135, 30]) cube([100, 150, 150]); 

translate([15, -100, 0]) cube([20, 60, 100]); 
translate([-35, -100, 0]) cube([20, 60, 100]); 
    
    
//holes
translate([17, -58, -10]) cylinder(h = 20 , d = 7); 
translate([-17, -58, -10]) cylinder(h = 20 , d = 7); 
    
 
    }



  /*translate([0,0,21]) {
    color("red") rotate([90,0,0])   translate([-motorSize[0] / 2, -motorSize[0] / 2, 0]) motor(motorSize, shaftDim, motorTop);
    color("blue") translate([0, -110, 0]) rotate([90, 90,0]) syringe(syringeDim, MinStickOut, MaxStickOut);} */


module sadapt(){
difference(){
cylinder(h = 5.8, d = 10); 

cylinder(h = 5.8, d = 4.2);
    translate([4, -10, 0]) cube(20); 
translate([-4 - 20, -10, 0]) cube(20); 
    }}
    
/*translate([0, -130, 21]) rotate([90, 0,0]) sadapt(); */

