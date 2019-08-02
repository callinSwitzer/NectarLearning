// servo

module servo(){
cube([12, 24, 24]);

translate([0, -4.15, 16])
    cube([12, 32.3, 2.4]);
    

translate([6, 6, 0])
    cylinder(32, 3, 3);
    

translate([3, 3, 30])
    cube([14, 6, 2]);
}



/*
translate([16, 0, 34])
rotate([270,0,90]) 
    servo();
*/


// servoHolder;

// cup
/*{translate([0, 50, 0])
difference(){
cylinder(71, d1 = 55, d2 = 93); 
cylinder(72, d1 = 53, d2 = 91); 
}*/


module servoStand(){
union(){
    // servo stand
     {cube([16,12, 5+4]);}

    // baseplate
    union(){
    translate([0, 40, 0])
        difference(){
        cylinder(3, d1 = 93, d2 = 93); 
        cylinder(5, d1 = 70, d2 = 70);}

    translate([32/2, -3, 0])
        rotate([0,0,90])
        cube([86, 32, 3]);
        
    }}}
// servoStand();
    

// cover
/*
translate([0, 40, 0])
difference(){
    // outer diameter
    cylinder(40, d1 = 93, d2 = 93); 
    // inner dia.
    cylinder(55, d1 = 91, d2 = 91);
}
*/
    
// IR photogate -- glue to bottom of cup lid


// cut out 3mm rad circles
module photogateHolder(){
    union(){
difference(){
translate([0, 0, 50]){
    difference(){
        difference(){
            
    cylinder(7.5, d1 = 30, d2 = 30);
    translate([0,0,-1]) cylinder(10, d1 = 15, d2 = 15);
    }
    
    translate([8, 0, 3.5])
    rotate([0, 90,0])
    cylinder(7, d1 = 5.5, d2 = 6, $fn=20);
    
    translate([-15, 0, 3.5])
    rotate([0, 90,0])
    cylinder(7, d1 = 6, d2 = 5.5, $fn=20);
    
    
translate([-30, -3, 0.5])
    cube([50, 6, 2]);
    
    translate([-15, -3, 0.5])
    cube([7, 6, 3]);

    translate([8, -3, 0.5])
    cube([7, 6, 3]);


}






};  

translate([-3.5, -16,52.5])
    cube([7,20,10]);

translate([-20,-18, 49])  
cube([60, 10, 20]);

translate([-20,8, 49])  
cube([60, 10, 20]);

}

translate([0,0, 52])
difference(){
            
   cylinder(0.5, d1 = 16, d2 = 16);
    translate([0,0,-1]) cylinder(5, d1 = 5, d2 = 5, $fn=20);
    }
    
translate([0,0, 50])
difference(){
            
   cylinder(0.5, d1 = 16, d2 = 16);
    translate([0,0,-1]) cylinder(5, d1 = 8, d2 = 8, $fn=20);
    } 
 
translate([-10,3, 50])  
cube([20, 5, 2]);
    
translate([-10,-8, 50])  
cube([20, 5, 2]);
}



}


translate([0, -25, 56])
rotate([0, 180, 0])
 photogateHolder();


// optionally remove the top
difference(){
    

union(){translate([0, 25, 56]){
    rotate([0, 180, 0])
     photogateHolder();}}
   
union(){translate([0,25,5.5])
        cylinder(10, d1 = 50, d2 = 50);}
}





// led blocker

module photogateBlocker(){
translate([0, -65, -0]){
difference(){
    
union(){
difference(){
    cylinder(7.5, d1 = 13, d2 = 13);
    cylinder(9, d1 = 10, d2 = 10);
    }
difference(){
    cylinder(3, d1 = 18, d2 = 18);
    cylinder(9, d1 = 10, d2 = 10);
    }
    
difference(){
    cylinder(2, d1 = 24, d2 = 24);
    cylinder(9, d1 = 10, d2 = 10);
    }
}
 
    
translate([-3.5, -14,0])
    cube([7,12,8]);
}
    

}
}

//photogateBlocker();



























