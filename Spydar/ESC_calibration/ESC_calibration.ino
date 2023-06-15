/*
  ESC_Calibration
    It's important to calibrate the ESC with the values (uS / microseconds) he will expect to be for Min and Max speed.
    This one require a little procedure:  
      1 - Load the sketch to your Arduino board
      2 - Connect your ESC to the Arduino board
      3 - Power your Arduino board
      4 - Once the LED (LED_PIN) is HIGH/ON connect the power to your ESC, you have 5sec to do so
      5 - Once the LED is LOW/OFF the calibration should be done
      6 - Should now be calibrated between 1000us and 2000us
    
  27 April 2017
  by Eric Nantel
  
  Servo & Knob links
  http://www.arduino.cc/en/Tutorial/Knob
  http://people.interaction-ivrea.it/m.rinott
 */
#include "ESC.h"

// Define Pins
#define ESC_PIN0 32  // connected to ESC 0 control wire
#define ESC_PIN1 33 // connected to ESC 1 control wire
#define ESC_PIN2 25 // connected to ESC 2 control wire
#define ESC_PIN3 26 // connected to ESC 3 control wire

ESC myESC (ESC_PIN0, 1000, 2000, 500);

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);       // LED Visual Output (can be removed)
  digitalWrite(LED_BUILTIN, HIGH);    // LED High while signal is High (can be removed)
  myESC.calib();                  // Calibration of the Max and Min value the ESC is expecting
  myESC.stop();                   // Stop the ESC to avoid damage or injuries
  digitalWrite(LED_BUILTIN, LOW);     // LED Low when the calibration is done (can be removed)
}

void loop() {

}
