tubeDia = 7.5; 

ledDia = 5.6; 

photoResistDia = 5.5;


module tube(){
   difference(){
    
    //cylinder(h = 30, d = tubeDia + 4);  
   translate([-(tubeDia + 4) ,-(tubeDia + 4) / 2, 0])  
       cube([tubeDia + 24, tubeDia + 4, 30]);
    translate([5,0,0]) cylinder(h = 30, d = tubeDia, $fn = 40);  
   }
}


module LEDHolder(){
    {
        
        rotate([90, 0, 0])
        rotate([0, 90, 0]){
            difference(){
                cube([ledDia + 4, ledDia + 10, ledDia + 4]);
                translate([2, 2, 0])
                cube([ledDia, ledDia + 6, 20]);
            }
        }
    }
}


module slices(){
    cube([60, 5, 1.5]); 
    
}


module photoResist(){
    intersection(){
    cylinder(h = 3, d = 5.5, $fn = 30); 
    translate([-4.5/2, -5,0]) cube([4.5, 10, 4.3]); }
    
}


module fullSetup(){
difference(){
    union(){
        tube(); 
        //translate([2.5, -4.6,14.7]) LEDHolder();
        }
    
        
    translate([0,0, 1]) {translate([-20, -2.5, 25.5]) slices();
    translate([-14, 0,26]) rotate([0, 90, 0]) cylinder(d= ledDia, h = 10, $fn = 40); 
        
    translate([-20, -2.5, 25.5 - 6]) slices();
    translate([-14, 0,26-6]) rotate([0, 90, 0]) cylinder(d= ledDia, h = 10, $fn = 40); 
    
    translate([-20, -2.5, 25.5 - 12]) slices();
    translate([-14, 0,26-12]) rotate([0, 90, 0]) cylinder(d= ledDia, h = 10, $fn = 40); 
        }
    //led's
     translate([12, 0, 27]) rotate([0, 90, 0]) cylinder(d= ledDia, h = 10, $fn = 40);  
    
     translate([12, 0, 27 - 6]) rotate([0, 90, 0]) cylinder(d= ledDia, h = 10, $fn = 40); 
    
     translate([12, 0, 27 - 12]) rotate([0, 90, 0]) cylinder(d= ledDia, h = 10, $fn = 40); 
    //translate([12, -2, 17]) cube([20, 4, 10]); 
     translate([-15, -25, -30]) cube(40);  

    //translate([0, -ledDia / 2, 16.7]) rotate([90, 0, 90]) cube([ledDia, ledDia + 6, 20]);
        //cylinder(h = 30, d = tubeDia, $fn = 40); 
    }
}



translate([15, 0, 0]) difference(){
translate([5, 0, - 10]) fullSetup(); 
    
translate([-15,0,0]) cube(50); } 



translate([5, 0,0])
rotate([0,0,180]) translate([15, 0, 0])  {
    difference(){
    translate([10, 0, -10]) fullSetup(); 
        translate([-5, -50,0]) cube(50);
        } 
}


 
    