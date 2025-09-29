#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"

// MPU-6050 I2C configuration
#define MPU_I2C_ID i2c0
#define MPU_SDA_PIN 4  // GP4 (Pin 6)
#define MPU_SCL_PIN 5  // GP5 (Pin 7)
#define MPU_I2C_FREQ 400000

// MPU-6050 registers and address
#define MPU_ADDR 0x68
#define USER_CONTROL 0x6A
#define PWR_MGMT_1 0x6B
#define SIGNAL_PATH_RESET 0x68
#define WHO_AM_I 0x75

void mpu_i2c_init() {
    // Initialize I2C0 for MPU-6050
    i2c_init(MPU_I2C_ID, MPU_I2C_FREQ);

    // Configure GPIO pins for I2C
    gpio_set_function(MPU_SDA_PIN, GPIO_FUNC_I2C);
    gpio_set_function(MPU_SCL_PIN, GPIO_FUNC_I2C);

    // Enable pull-ups on I2C pins
    gpio_pull_up(MPU_SDA_PIN);
    gpio_pull_up(MPU_SCL_PIN);

    printf("MPU-6050 I2C initialized on GP%d (SDA) and GP%d (SCL)\n", MPU_SDA_PIN, MPU_SCL_PIN);
}

int mpu_write_register(uint8_t reg, uint8_t data) {
    uint8_t buffer[2] = {reg, data};
    int result = i2c_write_blocking(MPU_I2C_ID, MPU_ADDR, buffer, 2, false);
    return result;
}

int mpu_read_register(uint8_t reg, uint8_t *data) {
    // Write register address
    int result = i2c_write_blocking(MPU_I2C_ID, MPU_ADDR, &reg, 1, true);
    if (result != 1) return result;

    // Read data
    result = i2c_read_blocking(MPU_I2C_ID, MPU_ADDR, data, 1, false);
    return result;
}

void mpu_reset() {
    printf("Resetting MPU-6050...\n");

    // Step 1: Device reset (Register 107, bit 7)
    mpu_write_register(PWR_MGMT_1, 0x80);
    sleep_ms(100);

    // Step 2: Reset all signal paths (Register 104, bits 2:0)
    // Bit 2: GYRO_RESET, Bit 1: ACCEL_RESET, Bit 0: TEMP_RESET
    mpu_write_register(SIGNAL_PATH_RESET, 0x07);
    sleep_ms(100);

    printf("MPU-6050 reset complete\n");
}

uint8_t mpu_who_am_i() {
    uint8_t who_am_i_val = 0;

    if (mpu_read_register(WHO_AM_I, &who_am_i_val) == 1) {
        return who_am_i_val;
    }

    return 0;
}

int main() {
    stdio_init_all();

    printf("MPU-6050 Reset - Pico C SDK\n");

    mpu_i2c_init();

    // Perform reset
    mpu_reset();

    // Continuous WHO_AM_I reading
    while (true) {
        uint8_t who = mpu_who_am_i();
        printf("Who Am I: 0x%02X\n", who);

        if (who == 0x68) {
            printf("MPU-6050 detected successfully!\n");
        } else {
            printf("MPU-6050 communication error or device not found\n");
        }

        sleep_ms(5000);
    }

    return 0;
}