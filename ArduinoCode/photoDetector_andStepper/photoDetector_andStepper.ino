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
  Serial.println(" Setup complete"); 
}

void loop() {

  // read serial port
  val = Serial.read();

  // put your main code here, to run repeatedly:
  stepIn = digitalRead(7); 
  stepIn_bottom = digitalRead(6); 
  ar1 = analogRead(A2);
  ar2 = analogRead(A0); 
  ar3 = analogRead(A1); 
  

   // 98 = b
   if (val == 98){
    //Serial.println(val);
      moveBackward();
    }

 
  // 102 = f  
  else if (val == 102) {
    //Serial.println(val);
    moveForward();
    }

  // refref: only write a line if prompted by python
  // 114 = r
  else if (val == 114) {
    Serial.print(ar1);
    Serial.print(",");
    Serial.print(ar2);
    Serial.print(",");
    Serial.print(ar3);
    Serial.print(",");
    Serial.print(stepIn);
    Serial.print(",");
    Serial.println(stepIn_bottom);
    }


  // move stepper all the way back, and then forward a little bit
  // c = 99
  else if (val == 99 && stepIn < 1){
    centerup();
  }

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
   myMotor->step(5, BACKWARD, SINGLE);    
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
   myMotor->step(5, FORWARD, SINGLE);    
    // release motor so it doesn't get too hot!
   myMotor->release();
  }
}
