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
servoStand();
    

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
    cylinder(6, d1 = 29, d2 = 29);
    cylinder(7, d1 = 19, d2 = 19);
    }
    
    translate([9, 0, 2.5])
    rotate([0, 90,0])
    cylinder(7, d1 = 5.5, d2 = 6, $fn=20);
    
    translate([-16, 0, 2.5])
    rotate([0, 90,0])
    cylinder(7, d1 = 6, d2 = 5.5, $fn=20);
    

}

};  
translate([-3.5, -15,50])
    cube([7,8,8]);

}
}
}

translate([0, -25, 56])
rotate([0, 180, 0])
photogateHolder();


























