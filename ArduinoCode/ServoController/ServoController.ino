

#include <Servo.h>

Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int pos = 0;    // variable to store the servo position
int servoDigitalPin = 10; // pin that controls servo

int topDegrees = 40; 
int bottomDegrees = 110; 

int potpin = A1; // potentiometer pin
int ar0; // analog read from phototransistor
int val;
int servoPosition; 

void setup() {
  Serial.begin(19200);  
  myservo.attach(servoDigitalPin);  // attaches the servo on pin XX to the servo object
}

void loop() {

  topDegrees = analogRead(potpin); 
  topDegrees = map(topDegrees, 0, 1023, 0, 90);

  servoPosition = myservo.read();

  // read serial port
  val = Serial.read();
  ar0 = analogRead(A0); 
  

   // 100 = d
   if (val == 100){
    //Serial.println(val);
      moveDown();
    }

 
  // 117 = u 
  else if (val == 117) {
    //Serial.println(val);
    moveUp();
    }

  // refref: only write a line if prompted by python
  // 114 = r
  else if (val == 114) {
    Serial.println(ar0);
    }



}
  
  


void moveDown()
{
  myservo.attach(servoDigitalPin);
  for (pos = servoPosition; pos <= bottomDegrees; pos += 1) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    myservo.write(pos);              // tell servo to go to position in variable 'pos'
   delay(5);                       // waits 15ms for the servo to reach the position
  }
  myservo.detach();
}

void moveUp()
{
  myservo.attach(servoDigitalPin);
  for (pos = servoPosition; pos >= topDegrees; pos -= 1) { // goes from 180 degrees to 0 degrees
    myservo.write(pos);              // tell servo to go to position in variable 'pos'
    delay(5);                       // waits 15ms for the servo to reach the position
  }
  myservo.detach();
}
