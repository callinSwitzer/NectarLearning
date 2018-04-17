#include <Wire.h>
#include <Adafruit_MotorShield.h>

// Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 


// Connect a stepper motor with 200 steps per revolution (1.8 degree)
// to motor port #2 (M3 and M4)
Adafruit_StepperMotor *myMotor = AFMS.getStepper(200, 2);

// define variable we'll read from python
int val = 0;
int lightPin = A0;  //define a pin for Photo resistor
int lightPin1 = A3;  //define a pin for Photo resistor
int lightPin2 = A5;  //define a pin for Photo resistor
int stepIn; 
int ar1; 
int ar2; 
int ar3; 

void setup() {
  Serial.begin(9600);           // set up Serial library at 9600 bps
  AFMS.begin();  // create with the default frequency 1.6KHz
  myMotor->setSpeed(100);  //  rpm   
  Serial.println("Setup complete"); 
}

void loop() {

  // read serial port
  val = Serial.read();

  // put your main code here, to run repeatedly:
  stepIn = digitalRead(7); 
  Serial.print(stepIn *200 + 500); 
  Serial.print(","); 

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

//  ar1 = analogRead(A2);
//  Serial.print(ar1);
//  Serial.print(",");
//  //delay(10); 
  ar2 = analogRead(A0); 
  //delay(50); 
  ar3 = analogRead(A1); 
//  Serial.print(ar1); 
//  Serial.print(",");
  Serial.print(ar2);
  Serial.print(",");
  Serial.println(ar3); 

}
