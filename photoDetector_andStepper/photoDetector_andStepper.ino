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
int stepIn_bottom; 
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
  Serial.print(stepIn *10 + 30); // limit switch
  Serial.print(","); 
  stepIn_bottom = digitalRead(6); 
  Serial.print(stepIn_bottom *10 + 30); // limit switch
  Serial.print(","); 
  
  

   // 98 = b
   if (val == 98){
    Serial.println(val);
      moveBackward();
  }

 
  // 102 = f  
  else if (val == 102) {
    Serial.println(val);
    moveForward();
    }

  // 99 = c
  else if (val == 99 && stepIn < 1) {
    centerup();
    }
 // refref: only write a line if prompted by python
  ar1 = analogRead(A2);
  Serial.print(ar1);
  Serial.print(",");
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


// This moves the punger all the way to the back, and then forward a little bit
void centerup()
{
  stepIn = digitalRead(7); 
 
  while(stepIn < 1){
 
   myMotor->step(10, FORWARD, SINGLE);    
    // release motor so it doesn't get too hot!
   myMotor->release();
  stepIn = digitalRead(7); 
  }

  delay(100); 
  //move forward a little bit
  for (int i=0; i <= 10; i++){
      moveForward();
   }
  
}



// This function moves forward
void moveForward()
{
  stepIn_bottom = digitalRead(6); 
  //move forward a little bit
  if (stepIn_bottom < 1){
   myMotor->step(20, BACKWARD, SINGLE);    
    // release motor so it doesn't get too hot!
   myMotor->release();
  }
}


// This function moves backward
void moveBackward()
{
  stepIn = digitalRead(7); 
  //move forward a little bit
  if (stepIn < 1){
   myMotor->step(20, FORWARD, SINGLE);    
    // release motor so it doesn't get too hot!
   myMotor->release();
  }
}

