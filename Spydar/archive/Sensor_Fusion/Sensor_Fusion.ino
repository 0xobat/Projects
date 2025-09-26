// Sensor fusion using Kalman Filter

#include <Wire.h>
#include <Kalman.h>

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

// Variables to store Sensor Output
int16_t AcX, AcY, AcZ; // variables to read accelerometer sensor output
int16_t GyX, GyY, GyZ; // variables to read gyroscope sensor output

void setup() {
  // Configure MPU
  Serial.begin(9600); // Initialize serial communication
  Wire.begin(); // Initialize I2C communication

  // Start I2C transmission
  Wire.beginTransmission(MPU_addr);
  
  Wire.write(pwr_mngt);
  Wire.write(11);   //wakes device up, disable Temperature sens, PLL Z-axis gyro clock source
  Wire.write(configure);
  Wire.write(1);         //gyro ouput= 1kHz, accl output= 1kHz, approx. 2ms delay
  Wire.write(sample_rate);
  Wire.write(0);   //sample rate = 1kHz
  Wire.write(gyro_config);
  Wire.write(0);  //full scale range = 250 degrees/s
  Wire.write(accl_config);
  Wire.write(0);   //full scale range = 2 g

  // End I2C transmission
  Wire.endTransmission(true);
}

void loop() {
  
  
}
