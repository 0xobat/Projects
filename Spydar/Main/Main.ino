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
#define ROLL 27     //Connected to RC
#define PITCH 14    //Connected to RC
#define THROTTLE 12 //Connected to RC
#define YAW 13      //Connected to RC

// Registers used to configure the gyro and accel
#define MPU_addr 0x68
#define sample_rate 0x19
#define configure 0x1A
#define gyro_config 0x1B
#define accl_config 0x1C
#define accl_data 0x3B
#define gyro_data 0x43
#define user_control 0x6A
#define pwr_mngt 0x6B

// Define constants
#define GPSBaud 9600
#define MIN_SPEED 1074 // speed just slow enough to turn motor off
#define MAX_SPEED 1240 // speed where my motor drew 3.6 amps at 12v.

// Define variables


// Define objects


void setup(){

}

void loop(){

}
  
i2c_Read(){

}