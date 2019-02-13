#include <Wire.h>
#include <Adafruit_MotorShield.h>

// Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 


// Connect a stepper motor with 200 steps per revolution (1.8 degree)
// to motor port #2 (M3 and M4)
Adafruit_StepperMotor *myMotor = AFMS.getStepper(200, 2);

// define variable we'll read from python
int val = 0;

void setup() {
  Serial.begin(9600);           // set up Serial library at 9600 bps
  AFMS.begin();  // create with the default frequency 1.6KHz
  myMotor->setSpeed(100);  //  rpm   
  Serial.println("Setup complete"); 
}

void loop() {

  // read serial port
  val = Serial.read();

  // 102 = f  
   if (val == 98){
    Serial.println(val);
    myMotor->step(40, FORWARD, SINGLE);    
    // release motor so it doesn't get too hot!
    myMotor->release(); 
  }

  // 98 = b
  else if (val == 102) {Serial.println(val);
    myMotor->step(40, BACKWARD, SINGLE);    
    // release motor so it doesn't get too hot!
    myMotor->release();  
    }

  
  //Serial.println("Single coil steps");
  //myMotor->step(500, FORWARD, SINGLE); 
  //myMotor->step(500, BACKWARD, SINGLE); 
  //myMotor-> release(); 
//  delay(3000); 
//
//  Serial.println("running!"); 
//
//  //Serial.println("Double coil steps");
//  myMotor->step(200, FORWARD, DOUBLE); 
//  myMotor->step(200, BACKWARD, DOUBLE);
//  
//  // release so motor doesn't get too hot
//  myMotor->release();
  
  //Serial.println("Interleave coil steps");
  //myMotor->step(100, FORWARD, INTERLEAVE); 
  //myMotor->step(100, BACKWARD, INTERLEAVE); 
  
  //Serial.println("Microstep steps");
  //myMotor->step(500, FORWARD, MICROSTEP); 
  //myMotor->step(500, BACKWARD, MICROSTEP);
}
