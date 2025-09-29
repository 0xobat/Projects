#include <stdio.h>
#include <math.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"

// MPU-6050 I2C configuration
#define MPU_PORT i2c0
#define MPU_SDA 4  // GP4 (Pin 6)
#define MPU_SCL 5  // GP5 (Pin 7)
#define MPU_FREQ 400000

// MPU-6050 registers
#define MPU_ADDR 0x68
#define SAMPLE_RATE 0x19
#define CONFIGURE 0x1A
#define GYRO_CONFIG 0x1B
#define ACCL_CONFIG 0x1C
#define ACCL_DATA 0x3B
#define GYRO_DATA 0x43
#define USER_CONTROL 0x6A
#define PWR_MNGT 0x6B
#define SELF_TEST_X 0x0D

// Variables for self-test
uint8_t XA_test, XG_test, YA_test, YG_test, ZA_test, ZG_test;
int FT_xa, FT_xg, FT_ya, FT_yg, FT_za, FT_zg;
int16_t AcX, AcY, AcZ, GyX, GyY, GyZ;
int16_t AcX_t, AcY_t, AcZ_t, GyX_t, GyY_t, GyZ_t;

void mpu_init() {
    i2c_init(MPU_PORT, MPU_FREQ);
    gpio_set_function(MPU_SDA, GPIO_FUNC_I2C);
    gpio_set_function(MPU_SCL, GPIO_FUNC_I2C);
    gpio_pull_up(MPU_SDA);
    gpio_pull_up(MPU_SCL);

    printf("MPU-6050 I2C initialized\n");
}

void mpu_write(uint8_t reg, uint8_t data) {
    uint8_t buffer[2] = {reg, data};
    i2c_write_blocking(MPU_PORT, MPU_ADDR, buffer, 2, false);
}

void mpu_read(uint8_t reg, uint8_t *data, size_t len) {
    i2c_write_blocking(MPU_PORT, MPU_ADDR, &reg, 1, true);
    i2c_read_blocking(MPU_PORT, MPU_ADDR, data, len, false);
}

void mpu_setup() {
    // Wake device and configure
    mpu_write(PWR_MNGT, 0);
    mpu_write(CONFIGURE, 1);      // 1kHz output, ~2ms delay
    mpu_write(SAMPLE_RATE, 0);    // 1kHz sample rate
    mpu_write(GYRO_CONFIG, 0);    // 250°/s range, self-test disabled
    mpu_write(ACCL_CONFIG, 16);   // 8g range, self-test disabled

    sleep_ms(500);

    // Obtain Factory Trims
    uint8_t w_reg[4];
    mpu_read(SELF_TEST_X, w_reg, 4);

    XG_test = w_reg[0] & 0b00011111;
    YG_test = w_reg[1] & 0b00011111;
    ZG_test = w_reg[2] & 0b00011111;

    XA_test = (w_reg[0] >> 3) | ((w_reg[3] & 0b00110000) >> 4);
    YA_test = (w_reg[1] >> 3) | ((w_reg[3] & 0b00001100) >> 2);
    ZA_test = (w_reg[2] >> 3) | (w_reg[3] & 0b00000011);

    // Calculate Factory Trim values
    // Gyroscope
    FT_xg = (XG_test == 0) ? 0 : 25 * 131 * pow(1.046, (XG_test - 1));
    FT_yg = (YG_test == 0) ? 0 : -25 * 131 * pow(1.046, (YG_test - 1));
    FT_zg = (ZG_test == 0) ? 0 : 25 * 131 * pow(1.046, (ZG_test - 1));

    // Accelerometer
    FT_xa = (XA_test == 0) ? 0 : 4096 * 0.34 * pow(0.92/0.34, (XA_test-1)/30.0);
    FT_ya = (YA_test == 0) ? 0 : 4096 * 0.34 * pow(0.92/0.34, (YA_test-1)/30.0);
    FT_za = (ZA_test == 0) ? 0 : 4096 * 0.34 * pow(0.92/0.34, (ZA_test-1)/30.0);
}

void read_sensor_data(bool self_test_enabled) {
    uint8_t raw_data[6];

    if (self_test_enabled) {
        // Enable self-test for accelerometer
        mpu_write(GYRO_CONFIG, 0);    // Gyro self-test disabled
        sleep_ms(50);
        mpu_write(ACCL_CONFIG, 240);  // Accel self-test enabled
        sleep_ms(500);

        // Read accelerometer
        mpu_read(ACCL_DATA, raw_data, 6);
        AcX_t = (raw_data[0] << 8) | raw_data[1];
        AcY_t = (raw_data[2] << 8) | raw_data[3];
        AcZ_t = (raw_data[4] << 8) | raw_data[5];

        // Enable self-test for gyroscope
        mpu_write(GYRO_CONFIG, 224);  // Gyro self-test enabled
        sleep_ms(50);
        mpu_write(ACCL_CONFIG, 16);   // Accel self-test disabled (8g range)
        sleep_ms(500);

        // Read gyroscope
        mpu_read(GYRO_DATA, raw_data, 6);
        GyX_t = (raw_data[0] << 8) | raw_data[1];
        GyY_t = (raw_data[2] << 8) | raw_data[3];
        GyZ_t = (raw_data[4] << 8) | raw_data[5];
    } else {
        // Disable self-test
        mpu_write(GYRO_CONFIG, 0);    // Gyro self-test disabled
        sleep_ms(50);
        mpu_write(ACCL_CONFIG, 16);   // Accel self-test disabled (8g range)
        sleep_ms(500);

        // Read accelerometer
        mpu_read(ACCL_DATA, raw_data, 6);
        AcX = (raw_data[0] << 8) | raw_data[1];
        AcY = (raw_data[2] << 8) | raw_data[3];
        AcZ = (raw_data[4] << 8) | raw_data[5];

        // Read gyroscope
        mpu_read(GYRO_DATA, raw_data, 6);
        GyX = (raw_data[0] << 8) | raw_data[1];
        GyY = (raw_data[2] << 8) | raw_data[3];
        GyZ = (raw_data[4] << 8) | raw_data[5];
    }
}

bool perform_self_test() {
    // Read sensor output without self-test
    read_sensor_data(false);
    sleep_ms(1000);

    // Read sensor output with self-test
    read_sensor_data(true);
    sleep_ms(100);

    // Calculate Self-Test Response (STR)
    int STR_xa = AcX_t - AcX;
    int STR_ya = AcY_t - AcY;
    int STR_za = AcZ_t - AcZ;
    int STR_xg = GyX_t - GyX;
    int STR_yg = GyY_t - GyY;
    int STR_zg = GyZ_t - GyZ;

    printf("Self-Test Response:\n");
    printf("Accelerometer X-axis STR: %d\n", STR_xa);
    printf("Accelerometer Y-axis STR: %d\n", STR_ya);
    printf("Accelerometer Z-axis STR: %d\n", STR_za);
    printf("Gyroscope X-axis STR: %d\n", STR_xg);
    printf("Gyroscope Y-axis STR: %d\n", STR_yg);
    printf("Gyroscope Z-axis STR: %d\n", STR_zg);

    // Calculate Change from Factory Trim (%)
    int dSTR_xa = (FT_xa != 0) ? ((STR_xa - FT_xa) * 100) / FT_xa : 0;
    int dSTR_ya = (FT_ya != 0) ? ((STR_ya - FT_ya) * 100) / FT_ya : 0;
    int dSTR_za = (FT_za != 0) ? ((STR_za - FT_za) * 100) / FT_za : 0;
    int dSTR_xg = (FT_xg != 0) ? ((STR_xg - FT_xg) * 100) / FT_xg : 0;
    int dSTR_yg = (FT_yg != 0) ? ((STR_yg - FT_yg) * 100) / FT_yg : 0;
    int dSTR_zg = (FT_zg != 0) ? ((STR_zg - FT_zg) * 100) / FT_zg : 0;

    printf("\nChange from Factory Trim (%%): \n");
    printf("Accelerometer X-axis: %d%%\n", dSTR_xa);
    printf("Accelerometer Y-axis: %d%%\n", dSTR_ya);
    printf("Accelerometer Z-axis: %d%%\n", dSTR_za);
    printf("Gyroscope X-axis: %d%%\n", dSTR_xg);
    printf("Gyroscope Y-axis: %d%%\n", dSTR_yg);
    printf("Gyroscope Z-axis: %d%%\n", dSTR_zg);

    // Check if within ±14% tolerance
    bool test_passed = (dSTR_xa >= -14 && dSTR_xa <= 14 &&
                        dSTR_ya >= -14 && dSTR_ya <= 14 &&
                        dSTR_za >= -14 && dSTR_za <= 14 &&
                        dSTR_xg >= -14 && dSTR_xg <= 14 &&
                        dSTR_yg >= -14 && dSTR_yg <= 14 &&
                        dSTR_zg >= -14 && dSTR_zg <= 14);

    return test_passed;
}

int main() {
    stdio_init_all();

    printf("MPU-6050 Self-Test - Pico C SDK\n");
    printf("Author: 0xObat\n");
    printf("Description: Self-test validation with factory trim checking\n\n");

    mpu_init();
    mpu_setup();

    while (true) {
        printf("=== Starting Self-Test ===\n");

        if (perform_self_test()) {
            printf("\n*** Self-test PASSED ***\n");
        } else {
            printf("\n*** Self-Test FAILED -- Device faulty ***\n");
        }

        printf("\nWaiting 5 seconds before next test...\n\n");
        sleep_ms(5000);
    }

    return 0;
}