// Configure and Read Sensor output

#include<Wire.h>

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
  // Read Acceleration from registers
  Wire.beginTransmission(MPU_addr);
  Wire.write(accl_data);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_addr,6,true);
  AcX = Wire.read() << 8 | Wire.read();
  AcY = Wire.read() << 8 | Wire.read();
  AcZ = Wire.read() << 8 | Wire.read();

  // Read angular velocity from registers
  Wire.beginTransmission(MPU_addr);
  Wire.write(gyro_data);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_addr,6,true);
  GyX = Wire.read() << 8 | Wire.read();
  GyY = Wire.read() << 8 | Wire.read();
  GyZ = Wire.read() << 8 | Wire.read(); 

  // Print Sensor outputs
  Serial.print("AcX = "); Serial.print(AcX);
  Serial.print(" | AcY = "); Serial.print(AcY);
  Serial.print(" | AcZ = "); Serial.println(AcZ);
  Serial.print("GyX = "); Serial.print(GyX);
  Serial.print(" | GyY = "); Serial.print(GyY);
  Serial.print(" | GyZ = "); Serial.println(GyZ);
  delay(1000);
}
