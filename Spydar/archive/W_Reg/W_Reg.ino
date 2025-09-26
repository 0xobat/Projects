// Sensor Fusion 
// 1. Read sensor data
// 2. Calculate angles using Kalman filter algorithms
// 3. Output theta array (clean sensor data)

// Import libraries
#include<Wire.h>
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

// Define variables and objects
int16_t AcX, AcY, AcZ; // variables to read accelerometer sensor output
int16_t GyX, GyY, GyZ; // variables to read gyroscope sensor output

struct MPUData {
  int16_t Ac[3];
  int16_t Gy[3];
};

MPUData sensor_output;

// Kalman filter objects
#define RAD_TO_DEG 57.295779513082320876798154814105
Kalman kalmanX;
Kalman kalmanY;
Kalman kalmanZ;
float angleX, angleY, angleZ;
float angle[3]; // Variables to store angles

void setup(){
  Serial.begin(9600);
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

void loop(){
  read_MPU_data();
  calculate_angles(sensor_output);

  Serial.print("X-Axis angle: "); Serial.println(angle[0]);
  Serial.print("Y-Axis angle: "); Serial.println(angle[1]);
  Serial.print("Z-Axis angle: "); Serial.println(angle[2]);

  delay(5000);
}


// Function to data from accelerometer and gyroscope
MPUData read_MPU_data(){
  Wire.beginTransmission(MPU_addr);
  Wire.write(accl_data);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_addr,6,true);

  sensor_output.Ac[0] = Wire.read() << 8 | Wire.read();
  sensor_output.Ac[1] = Wire.read() << 8 | Wire.read();
  sensor_output.Ac[2] = Wire.read() << 8 | Wire.read();

  // Read angular velocity from registers
  Wire.beginTransmission(MPU_addr);
  Wire.write(gyro_data);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_addr,6,true);
  
  sensor_output.Gy[0] = Wire.read() << 8 | Wire.read();
  sensor_output.Gy[1] = Wire.read() << 8 | Wire.read();
  sensor_output.Gy[2] = Wire.read() << 8 | Wire.read(); 

  return  sensor_output;
}

float calculate_angles(MPUData data){
  AcX = data.Ac[0];
  AcY = data.Ac[1];
  AcZ = data.Ac[2];
  GyX = data.Gy[0];
  GyY = data.Gy[1];
  GyZ = data.Gy[2];

  angleX = atan2(AcY, AcZ) * RAD_TO_DEG;
  angleY = atan2(-AcX, sqrt(AcY * AcY + AcZ * AcZ)) * RAD_TO_DEG;
  angleZ += GyZ * 0.0000611;

  kalmanX.setAngle(angleX);
  kalmanY.setAngle(angleY);
  kalmanZ.setAngle(angleZ);
  angleX = kalmanX.getAngle();
  angleY = kalmanY.getAngle();
  angleZ = kalmanZ.getAngle();

  angle[0] = angleX;
  angle[1] = angleY;
  angle[2] = angleZ;

  return angle;
}
