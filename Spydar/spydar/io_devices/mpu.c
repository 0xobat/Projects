/***********************************
 * MPU-6050 Reader for accelerometer and gyroscope data.
 *  @author: 0xObat
  * @date: 2025-
  * Adapted from Arduino code to Raspberry Pi Pico C SDK 
*/

#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"

// I2C pins
#define MPU_PORT i2c0
#define MPU_SDA 4
#define MPU_SCL 5
#define MPU_FREQ 400000

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

// Software filtering
#define FILTER_SIZE 1
int32_t accel_filter[3][FILTER_SIZE] = {0}; // [x,y,z][samples]
int32_t gyro_filter[3][FILTER_SIZE] = {0};
uint8_t filter_index = 0;

void mpu_init() {
    i2c_init(MPU_PORT, MPU_FREQ);
    gpio_set_function(MPU_SDA, GPIO_FUNC_I2C);
    gpio_set_function(MPU_SCL, GPIO_FUNC_I2C);

    printf("MPU-6050 I2C initialized\n");
}

void mpu_write(uint8_t reg, uint8_t data) {
    uint8_t buffer[2] = {reg, data};
    i2c_write_blocking(MPU_PORT, MPU_addr, buffer, 2, false);
}

void mpu_read(uint8_t reg, uint8_t *data, size_t len) {
    i2c_write_blocking(MPU_PORT, MPU_addr, &reg, 1, true);
    i2c_read_blocking(MPU_PORT, MPU_addr, data, len, false);
}

void mpu_setup() {
    // Configure all registers in sequence like Arduino reference
    uint8_t config_sequence[] = {
        pwr_mngt, 11,        // wakes device up, disable Temperature sens, PLL Z-axis gyro clock source
        configure, 3,        // gyro ouput= 1kHz, accl output= 1kHz, approx. 2ms delay
        sample_rate, 0,      // sample rate = 1kHz
        gyro_config, 0,      // full scale range = 250 degrees/s
        accl_config, 0       // full scale range = 2 g
    };

    // Write all configuration at once
    for (int i = 0; i < sizeof(config_sequence); i += 2) {
        mpu_write(config_sequence[i], config_sequence[i + 1]);
    }

    sleep_ms(500);
}

void read_sensor_data() {
    uint8_t raw_data[6];
    int16_t raw_accel[3], raw_gyro[3];

    // Read Acceleration from registers
    mpu_read(accl_data, raw_data, 6);
    raw_accel[0] = (raw_data[0] << 8) | raw_data[1];
    raw_accel[1] = (raw_data[2] << 8) | raw_data[3];
    raw_accel[2] = (raw_data[4] << 8) | raw_data[5];

    // Read angular velocity from registers
    mpu_read(gyro_data, raw_data, 6);
    raw_gyro[0] = (raw_data[0] << 8) | raw_data[1];
    raw_gyro[1] = (raw_data[2] << 8) | raw_data[3];
    raw_gyro[2] = (raw_data[4] << 8) | raw_data[5];

    // Apply moving average filter
    for (int i = 0; i < 3; i++) {
        accel_filter[i][filter_index] = raw_accel[i];
        gyro_filter[i][filter_index] = raw_gyro[i];

        // Calculate average
        int32_t accel_sum = 0, gyro_sum = 0;
        for (int j = 0; j < FILTER_SIZE; j++) {
            accel_sum += accel_filter[i][j];
            gyro_sum += gyro_filter[i][j];
        }

        if (i == 0) {
            AcX = accel_sum / FILTER_SIZE;
            GyX = gyro_sum / FILTER_SIZE;
        } else if (i == 1) {
            AcY = accel_sum / FILTER_SIZE;
            GyY = gyro_sum / FILTER_SIZE;
        } else {
            AcZ = accel_sum / FILTER_SIZE;
            GyZ = gyro_sum / FILTER_SIZE;
        }
    }

    filter_index = (filter_index + 1) % FILTER_SIZE;
}

int main() {
    stdio_init_all();
    mpu_init();
    mpu_setup();

    while (1) {
        read_sensor_data();

        // Print Sensor outputs
        printf("AcX = %d | AcY = %d | AcZ = %d | GyX = %d | GyY = %d | GyZ = %d\n", AcX, AcY, AcZ, GyX, GyY, GyZ);
        sleep_ms(1000);
    }

    return 0;
}
