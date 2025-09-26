/*
Program Name: Spydar
Description: Semi-autonomous flight for quadcopter using geolocation and a pilot system, with an RC controller. 
Author: 0xObat
Date: 
*/

// Import libraries
#include <ESP32Servo.h> // ESP32Servo library installed by Library Manager
#include "ESC.h" // RC_ESP library installed by Library Manager
#include <HardwareSerial.h> //Provides access to the hardware serial ports
#include <TinyGPS++.h>
#include<Wire.h>

// Define Pins
#define ESC_PIN0 32 // connected to ESC 0 control wire
#define ESC_PIN1 33 // connected to ESC 1 control wire
#define ESC_PIN2 25 // connected to ESC 2 control wire
#define ESC_PIN3 26 // connected to ESC 3 control wire
#define RXPin 16  // Connected to GPS
#define TXPin 17  // Connected to GPS
#define GPSBaud 9600
#define ROLL 27     //Connected to RC
#define PITCH 14    //Connected to RC
#define THROTTLE 12 //Connected to RC
#define YAW 13      //Connected to RC

// Define constants
// Note: the following speeds may need to be modified for your particular hardware.
#define MIN_SPEED 1040 // speed just slow enough to turn motor off
#define MAX_SPEED 1240 // speed where my motor drew 3.6 amps at 12v.

// Registers used to configure the gyro and accel
#define sensor_add 0x68

// Define variable and objects
// ESC_Name (PIN, Minimum Value, Maximum Value, Arm Value)
ESC myESC0 (ESC_PIN0, 1000, 2000, 500);
ESC myESC1 (ESC_PIN1, 1000, 2000, 500);
ESC myESC2 (ESC_PIN2, 1000, 2000, 500);
ESC myESC3 (ESC_PIN3, 1000, 2000, 500);

HardwareSerial gpsSerial(1);
TinyGPSPlus gps;


void setup() {
  Serial.begin(115200);
  delay(5000);
  
  // Initialize MPU6050 configurations
  Wire.begin();
  Wire.beginTransmission(sensor_add);
  Wire.write(0x6B);
  Wire.write(0);   //wakes device up from sleep mode
  Wire.write(0x1A);
  Wire.write(1);         //gyro ouput= 1kHz, accl output= 1kHz, approx. 2ms delay
  Wire.write(0x19);
  Wire.write(9);   //sample rate = 100Hz
  Wire.write(0x1B);
  Wire.write(0);  //full scale range= 250 degrees/s
  Wire.write(0x1C);
  Wire.write(16);   //full scale range= 8g
  Wire.endTransmission(true);

  // Initialize the gps communication
  gpsSerial.begin(GPSBaud, SERIAL_8N1, RXPin, TXPin);

  // Initialize and Arm the ESC and motors
  pinMode(ESC_PIN0, OUTPUT);
  pinMode(ESC_PIN1, OUTPUT);
  pinMode(ESC_PIN2, OUTPUT);
  pinMode(ESC_PIN3, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  //Arm the ESC
  digitalWrite(LED_BUILTIN, HIGH); // set led to on to indicate arming
  myESC0.arm(); // Send the Arm command to ESC 0
  myESC1.arm(); // Send the Arm command to ESC 1
  myESC2.arm(); // Send the Arm command to ESC 2
  myESC3.arm(); // Send the Arm command to ESC 3
  delay(1000); // Wait a while
  digitalWrite(LED_BUILTIN, LOW); // led off to indicate arming completed

  // Initialize the RC controls
  pinMode(ROLL, INPUT);
  pinMode(PITCH, INPUT);
  pinMode(THROTTLE, INPUT);
  pinMode(YAW, INPUT);
} 



void loop() {
  // Read GPS data
  if (gpsSerial.available() > 0) {
    if (gps.encode(gpsSerial.read())) {
        double latitude, longitude;
        unsigned long age;
        latitude = gps.location.lat();
        longitude = gps.location.lng();
        age = gps.location.age();
    }
  }

  // Read RC Values
  roll_val = pulseIn(ROLL, HIGH);
  pitch_val = pulseIn(PITCH, HIGH);
  throttle_val = pulseIn(THROTTLE, HIGH);
  yaw_val = pulseIn(YAW, HIGH);

  
}
