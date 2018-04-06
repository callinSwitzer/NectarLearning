

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
translate([motorSize[0] / 2, motorSize[1] / 2, -5]) cylinder(h = shaftDim[1], d = shaftDim[0]); 
    
    }
}

//motor(motorSize, shaftDim, motorTop);





module syringe(syringeDim, MinStickOut, MaxStickOut){
    
    cylinder(h = 30, d = syringeDim[0]); 
    translate([-syringeDim[1]/2, -syringeDim[2]/2, 0]) cube([syringeDim[1], syringeDim[2], 2]); 
    translate([0, 0, -MaxStickOut]) cylinder(h = MaxStickOut, d = 7); 
    
}




difference(){
translate([-25, -120, -5]) cube([50, 125, 50]); 


linear_extrude([40]) projection(cut = true) rotate([90,0,0])   translate([-motorSize[0] / 2, -motorSize[0] / 2, 0]) motor(motorSize, shaftDim, motorTop);
translate([0,0,11]) linear_extrude([40]) projection(cut = true) translate([0, -110, 0]) rotate([90, 90,0]) syringe(syringeDim, MinStickOut, MaxStickOut);}