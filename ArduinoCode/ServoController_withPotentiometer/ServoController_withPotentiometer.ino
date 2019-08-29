

#include <Servo.h>

Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int pos = 0;    // variable to store the servo position
int servoDigitalPin = 10; // pin that controls servo

int potpin = A1;

int topDegrees = 40; 
int bottomDegrees = 110; 

void setup() {
  myservo.attach(servoDigitalPin);  // attaches the servo on pin XX to the servo object
  Serial.begin(9600);
}

void loop() {

  topDegrees = analogRead(potpin); 
  Serial.print(topDegrees);
  Serial.print(" ");
  
  topDegrees = map(topDegrees, 0, 1023, 0, 90);
  Serial.println(topDegrees);
  
  
  for (pos = topDegrees; pos <= bottomDegrees; pos += 1) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    myservo.write(pos);              // tell servo to go to position in variable 'pos'
   delay(5);                       // waits 15ms for the servo to reach the position
  }
  myservo.detach();
  
  myservo.attach(10);
  for (pos = bottomDegrees
  ; pos >= topDegrees; pos -= 1) { // goes from 180 degrees to 0 degrees
    myservo.write(pos);              // tell servo to go to position in variable 'pos'
    delay(5);                       // waits 15ms for the servo to reach the position
  }
delay(2000);

}
