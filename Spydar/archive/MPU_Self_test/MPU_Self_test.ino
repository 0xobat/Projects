/*
PROGRAM NAME: MPU-6050 Self-Test
DESCRIPTION: This code performs a self-test on the MPU-6050 sensor to ensure its operational stability.
The self-test evaluates the sensor's internal components and verifies their functionality.
The test result is considered acceptable if the measured values fall within the range of
-14% to 14% deviation from the expected values. 
AUTHOR: 0xObat
DATE: 15-05-2023
*/


#include<Wire.h>

// Registers used to configure the gyroscope and accelerometer
#define MPU_addr 0x68
#define sample_rate 0x19
#define configure 0x1A
#define gyro_config 0x1B
#define accl_config 0x1C
#define accl_data 0x3B
#define gyro_data 0x43
#define user_control 0x6A
#define pwr_mngt 0x6B

// Self Test Registers to obtain Factory trim
#define SELF_TEST_X 0x0D

// Variables to store data collected
byte XA_test, XG_test, YA_test, YG_test, ZA_test, ZG_test;
int FT_xa, FT_xg, FT_ya, FT_yg, FT_za, FT_zg;
uint8_t w_reg[4];

int16_t AcX, AcY, AcZ, GyX, GyY, GyZ; //variables to read sensor output
int16_t AcX_t, AcY_t, AcZ_t, GyX_t, GyY_t, GyZ_t; //variables to read sensor output with self test

// Result variables
int STR_xa, STR_ya, STR_za, STR_xg, STR_yg, STR_zg; // variables to store Self-Test Response
int dSTR_xa, dSTR_ya, dSTR_za, dSTR_xg, dSTR_yg, dSTR_zg; // variables to store Change from FT of Self-Test Response


void setup() {
  Wire.begin(); // Initialize I2C communication
  Serial.begin(9600); // Initialize serial communication

  // Start I2C transmission
  Wire.beginTransmission(MPU_addr);
  
  Wire.write(pwr_mngt);
  Wire.write(0);   //wakes device up from sleep mode
  Wire.write(configure);
  Wire.write(1);         //gyro ouput= 1kHz, accl output= 1kHz, approx. 2ms delay
  Wire.write(sample_rate);
  Wire.write(0);   //sample rate = 1kHz
  Wire.write(gyro_config);
  Wire.write(0);  //full scale range= 250 degrees/s; Self-Test disabled
  Wire.write(accl_config);
  Wire.write(16);   //full scale range= 8g; Self-Test disabled
  
  // End I2C transmission
  Wire.endTransmission(true);

  delay(500);
  
  // Obtain Factory Trims
  Wire.beginTransmission(MPU_addr);
  Wire.write(SELF_TEST_X);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_addr, 4, true);

  for (int i = 0; i < 4; i++) {
    w_reg[i] = Wire.read();
  }
  
  XG_test = w_reg[0] & 0b00011111;
  YG_test = w_reg[1] & 0b00011111;
  ZG_test = w_reg[2] & 0b00011111;
  
  XA_test = (w_reg[0] >> 3) | ((w_reg[3] & 0b00110000) >> 4);
  YA_test = (w_reg[1] >> 3) | ((w_reg[3] & 0b00001100) >> 2);
  ZA_test = (w_reg[3] >> 3) | (w_reg[3] & 0b00000011);
  
  // Gyroscope
  FT_xg = (XG_test == 0) ? 0 : 25 * 131 * pow(1.046, (XG_test - 1));
  FT_yg = (YG_test == 0) ? 0 : -25 * 131 * pow(1.046, (YG_test - 1));
  FT_zg = (ZG_test == 0) ? 0 : 25 * 131 * pow(1.046, (ZG_test - 1));
  
  // Accelerometer
  FT_xa = (XA_test == 0) ? 0 : 4096 * 0.92 * pow(1.046, (XA_test - 1));
  FT_ya = (YA_test == 0) ? 0 : 4096 * 0.92 * pow(1.046, (YA_test - 1));
  FT_za = (ZA_test == 0) ? 0 : 4096 * 0.92 * pow(1.046, (ZA_test - 1));

}

void loop() {
  // Perform Self-Test
  
  // Sensor output without self-test
  // Configure accelrometer without Self-Test
  Wire.beginTransmission(MPU_addr);
  Wire.write(gyro_config);
  Wire.write(0);  //full scale range= 250 degrees/s; Self-Test disabled
  Wire.write(accl_config);
  Wire.write(16);   //full scale range= 8g; Self-Test disabled
  Wire.endTransmission(true);
  delay(500);
  // Read gyroscope and accelerometer sensor output
  Wire.beginTransmission(MPU_addr);
  Wire.write(accl_data);
  Wire.endTransmission(false); 
  Wire.requestFrom(MPU_addr, 6, true); 
  AcX = Wire.read()<<8 | Wire.read(); // reading registers: 0x3B (ACCEL_XOUT_H) and 0x3C (ACCEL_XOUT_L)
  AcY = Wire.read()<<8 | Wire.read(); // reading registers: 0x3D (ACCEL_YOUT_H) and 0x3E (ACCEL_YOUT_L)
  AcZ = Wire.read()<<8 | Wire.read(); // reading registers: 0x3F (ACCEL_ZOUT_H) and 0x40 (ACCEL_ZOUT_L)
  Wire.beginTransmission(MPU_addr);
  Wire.write(gyro_data);
  Wire.endTransmission(false); 
  Wire.requestFrom(MPU_addr, 6, true); 
  GyX = Wire.read()<<8 | Wire.read(); // reading registers: 0x43 (GYRO_XOUT_H) and 0x44 (GYRO_XOUT_L)
  GyY = Wire.read()<<8 | Wire.read(); // reading registers: 0x45 (GYRO_YOUT_H) and 0x46 (GYRO_YOUT_L)
  GyZ = Wire.read()<<8 | Wire.read(); // reading registers: 0x47 (GYRO_ZOUT_H) and 0x48 (GYRO_ZOUT_L)
  
  delay(1000);


  // Sensor output with self-test
  // Configure accelerometer with Self-Test
  Wire.beginTransmission(MPU_addr);
  Wire.write(gyro_config);
  Wire.write(0);  //full scale range= 250 degrees/s; Self-Test disabled
  Wire.write(accl_config);
  Wire.write(240);   //full scale range= 8g; Self-Test enabled
  Wire.endTransmission(true);
  delay(500);
  // Read accelerometer sensor output
  Wire.beginTransmission(MPU_addr);
  Wire.write(accl_data);
  Wire.endTransmission(false); 
  Wire.requestFrom(MPU_addr, 6, true); 
  AcX_t = Wire.read()<<8 | Wire.read(); // reading registers: 0x3B (ACCEL_XOUT_H) and 0x3C (ACCEL_XOUT_L)
  AcY_t = Wire.read()<<8 | Wire.read(); // reading registers: 0x3D (ACCEL_YOUT_H) and 0x3E (ACCEL_YOUT_L)
  AcZ_t = Wire.read()<<8 | Wire.read(); // reading registers: 0x3F (ACCEL_ZOUT_H) and 0x40 (ACCEL_ZOUT_L)

  // Configure gyroscope with Self-Test
  Wire.beginTransmission(MPU_addr);
  Wire.write(gyro_config);
  Wire.write(224);  //full scale range= 250 degrees/s; Self-Test enabled
  Wire.write(accl_config);
  Wire.write(16);   //full scale range= 8g; Self-Test disabled
  Wire.endTransmission(true);
  delay(500);
  // Read gyroscope sensor output
  Wire.beginTransmission(MPU_addr);
  Wire.write(gyro_data);
  Wire.endTransmission(false); 
  Wire.requestFrom(MPU_addr, 6, true); 
  GyX_t = Wire.read()<<8 | Wire.read(); // reading registers: 0x43 (GYRO_XOUT_H) and 0x44 (GYRO_XOUT_L)
  GyY_t = Wire.read()<<8 | Wire.read(); // reading registers: 0x45 (GYRO_YOUT_H) and 0x46 (GYRO_YOUT_L)
  GyZ_t = Wire.read()<<8 | Wire.read(); // reading registers: 0x47 (GYRO_ZOUT_H) and 0x48 (GYRO_ZOUT_L)
  
  delay(100);

  
  // Print Self-Test Response
  // Self-Test Response(STR) = Sensor output with self-test enabled – Sensor output without self-test enabled
  STR_xa = AcX_t - AcX;
  STR_ya = AcY_t - AcY;
  STR_za = AcZ_t - AcZ;
  STR_xg = GyX_t - GyX;
  STR_yg = GyY_t - GyY;
  STR_zg = GyZ_t - GyZ;
  Serial.print("Accelerometer X-axis STR: "); Serial.println(STR_xa);
  Serial.print("Accelerometer Y-axis STR: "); Serial.println(STR_ya);
  Serial.print("Accelerometer Z-axis STR: "); Serial.println(STR_za);
  Serial.print("Gyroscope X-axis STR: "); Serial.println(STR_xg);
  Serial.print("Gyroscope Y-axis STR: "); Serial.println(STR_yg);
  Serial.print("Gyroscope Z-axis STR: "); Serial.println(STR_zg);
  delay(1000);
  
  // Print Change from Factory Trim of the Self-Test Response (%)
  dSTR_xa = (STR_xa - FT_xa) / FT_xa;
  dSTR_ya = (STR_ya - FT_ya) / FT_ya;
  dSTR_za = (STR_za - FT_za) / FT_za;
  dSTR_xg = (STR_xg - FT_xg) / FT_xg;
  dSTR_yg = (STR_yg - FT_yg) / FT_yg;
  dSTR_zg = (STR_zg - FT_zg) / FT_zg;
  Serial.print("Change from FT of Accelerometer X-axis: "); Serial.println(dSTR_xa);
  Serial.print("Change from FT of Accelerometer Y-axis: "); Serial.println(dSTR_ya);
  Serial.print("Change from FT of Accelerometer Z-axis: "); Serial.println(dSTR_za);
  Serial.print("Change from FT of Gyroscope X-axis: "); Serial.println(dSTR_xg);
  Serial.print("Change from FT of Gyroscope Y-axis: "); Serial.println(dSTR_yg);
  Serial.print("Change from FT of Gyroscope Z-axis: "); Serial.println(dSTR_zg);

  if (dSTR_xa >= -14 && dSTR_xa <= 14 &&
        dSTR_ya >= -14 && dSTR_ya <= 14 &&
        dSTR_za >= -14 && dSTR_za <= 14 &&
        dSTR_xg >= -14 && dSTR_xg <= 14 &&
        dSTR_yg >= -14 && dSTR_yg <= 14 &&
        dSTR_zg >= -14 && dSTR_zg <= 14) {
        Serial.println("Self-test PASSED");
    }
    else Serial.println("Self-Test FAILED -- Device faulty");
  
  delay(5000);
  
}
