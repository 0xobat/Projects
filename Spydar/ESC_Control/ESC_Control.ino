// Import libraries
#include <ESP32PWM.h> // ESP32Servo library installed by Library Manager
#include "ESC.h" // RC_ESP library installed by Library Manager

// Define Pins
#define ESC_PIN0 32 // connected to ESC 0 control wire
#define ESC_PIN1 33 // connected to ESC 1 control wire
#define ESC_PIN2 25 // connected to ESC 2 control wire
#define ESC_PIN3 26 // connected to ESC 3 control wire

// Define constants
#define MIN_SPEED 1074
#define MAX_SPEED 1240 // test value for initial testing 1240

// Define variable and objects
ESC myESC0 (ESC_PIN0, 1000, 2000, 500);
ESC myESC1 (ESC_PIN1, 1000, 2000, 500);
ESC myESC2 (ESC_PIN2, 1000, 2000, 500);
ESC myESC3 (ESC_PIN3, 1000, 2000, 500);

int ThrottleVal = 0;

void setup() {
  Serial.begin(9600);
  delay(1000);
  // Initialize the ESC and LED
  pinMode(ESC_PIN0, OUTPUT);
  pinMode(ESC_PIN1, OUTPUT);
  pinMode(ESC_PIN2, OUTPUT);
  pinMode(ESC_PIN3, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);

  // Arm the ESCs
  digitalWrite(LED_BUILTIN, HIGH); // set led to on to indicate arming
  Serial.println("Arming ESC");
  myESC0.arm(); // Send the Arm command to ESC 0
  myESC1.arm(); // Send the Arm command to ESC 1
  myESC2.arm(); // Send the Arm command to ESC 2
  myESC3.arm(); // Send the Arm command to ESC 3
  delay(2000); // Wait a while
  Serial.println("Arming Complete");
  digitalWrite(LED_BUILTIN, LOW); // led off to indicate arming completed
}

void loop() {
  ThrottleVal = 1000; //value between 999 and 2000
  ThrottleVal = map(ThrottleVal, 999, 2000, MIN_SPEED, MAX_SPEED); // scale throttle reading to valid speed range
  myESC0.speed(ThrottleVal); // sets the ESC speed
  delay(100);
}
