// Reset Sensor registers and output paths

#include<Wire.h>

// Registers used to configure the gyro and accel
#define MPU_addr 0x68
#define user_control 0x6A
#define pwr_mngt 0x6B
#define sig_path_reset 0x68
#define who_am_i 0x75

byte who;

void setup() {
  Serial.begin(9600); // Initialize serial communication
  Wire.begin(); // Initialize I2C communication

  // Start I2C transmission
  Wire.beginTransmission(MPU_addr);
  
  Wire.write(pwr_mngt);
  Wire.write(128);   //Resets device
  delay(100);
  Wire.write(sig_path_reset);
  Wire.write(3);     //Reset temp, accel and gyro
  delay(100);
  Wire.write(user_control);
  Wire.write(1);   //Reset signal path
  
  // End I2C transmission
  Wire.endTransmission(true);
}

void loop() {
  // Start I2C transmission
  Wire.beginTransmission(MPU_addr);
  
  Wire.write(who_am_i);
  Wire.endTransmission(false);

  Wire.requestFrom(MPU_addr,1);
  who = Wire.read();

  // End I2C transmission
  Wire.endTransmission(true);

  Serial.print("Who Am I: 0x"); Serial.println(who, HEX);
  delay(5000);
}
