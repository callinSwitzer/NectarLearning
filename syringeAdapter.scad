module sadapt(){
difference(){
cylinder(h = 5.8*2, d = 10, $fn = 40); 

cylinder(h = 5.8, d = 4.4, $fn=20);
    translate([0,0,5.8]) cylinder(h = 5.8, d = 5, $fn = 20);
    translate([4, -10, 0]) cube(20); 
translate([-4 - 20, -10, 0]) cube(20); 
    
     translate([0, -10, 5.8]) cube([20, 20, 2]); 
    translate([0, -2.5, 5.8]) cube([5, 5, 20]); 
    translate([0, -2, -20+5.8]) cube([4, 4, 20]); 
    }
   
    }


sadapt(); 

