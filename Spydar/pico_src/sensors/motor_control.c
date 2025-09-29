#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "pico/stdlib.h"
#include "hardware/pwm.h"
#include "hardware/gpio.h"
#include "hardware/clocks.h"

// ESC Pin Definitions (from README.md)
#define ESC0_PIN    6   // GP6/Pin 9 - Front Right
#define ESC1_PIN    7   // GP7/Pin 10 - Front Left
#define ESC2_PIN    8   // GP8/Pin 11 - Rear Left
#define ESC3_PIN    9   // GP9/Pin 12 - Rear Right

// LED for status indication
#define LED_PIN PICO_DEFAULT_LED_PIN

// ESC PWM Parameters (standard ESC values)
#define ESC_MIN_PULSE_US    1000    // Minimum pulse width (1ms)
#define ESC_MAX_PULSE_US    2000    // Maximum pulse width (2ms)
#define ESC_ARM_PULSE_US    1000    // Arming pulse width
#define ESC_PWM_FREQ_HZ     50      // Standard servo/ESC frequency (50Hz)

// Motor speed range for safety
#define MOTOR_MIN_SPEED     0       // 0% throttle
#define MOTOR_MAX_SPEED     100     // 100% throttle
#define MOTOR_ARM_SPEED     0       // Arming speed (0%)

// ESC structure for each motor
typedef struct {
    uint pin;
    uint slice;
    uint channel;
    uint16_t current_speed;
    bool armed;
    const char* name;
} esc_t;

// Motor array - Front Right, Front Left, Rear Left, Rear Right
static esc_t motors[4] = {
    {ESC0_PIN, 0, 0, 0, false, "Front-Right"},
    {ESC1_PIN, 0, 0, 0, false, "Front-Left"},
    {ESC2_PIN, 0, 0, 0, false, "Rear-Left"},
    {ESC3_PIN, 0, 0, 0, false, "Rear-Right"}
};

// Global motor control state
static bool motors_initialized = false;
static bool motors_armed = false;
static uint32_t pwm_wrap_value = 0;

// LED status functions
void led_init() {
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    gpio_put(LED_PIN, 0);
}

void led_blink(int count, int delay_ms) {
    for (int i = 0; i < count; i++) {
        gpio_put(LED_PIN, 1);
        sleep_ms(delay_ms);
        gpio_put(LED_PIN, 0);
        sleep_ms(delay_ms);
    }
}

// Calculate PWM level from microseconds
uint16_t us_to_pwm_level(uint16_t pulse_us) {
    if (pulse_us < ESC_MIN_PULSE_US) pulse_us = ESC_MIN_PULSE_US;
    if (pulse_us > ESC_MAX_PULSE_US) pulse_us = ESC_MAX_PULSE_US;

    // PWM level = (pulse_width_us * pwm_wrap_value) / (1000000 / pwm_freq)
    return (pulse_us * pwm_wrap_value) / 20000; // 20000us = 1/50Hz
}

// Calculate PWM level from percentage (0-100%)
uint16_t percent_to_pwm_level(uint8_t speed_percent) {
    if (speed_percent > 100) speed_percent = 100;

    // Map 0-100% to 1000-2000us
    uint16_t pulse_us = ESC_MIN_PULSE_US +
                       ((speed_percent * (ESC_MAX_PULSE_US - ESC_MIN_PULSE_US)) / 100);

    return us_to_pwm_level(pulse_us);
}

// Initialize PWM for all ESCs
bool motors_init() {
    printf("Initializing motor control system...\n");

    led_init();

    // Calculate PWM parameters
    uint32_t clock_freq = clock_get_hz(clk_sys);
    pwm_wrap_value = (clock_freq / (ESC_PWM_FREQ_HZ * 1000)) - 1; // Divider of 1000

    printf("System clock: %u Hz\n", clock_freq);
    printf("PWM wrap value: %u\n", pwm_wrap_value);

    // Initialize each motor's PWM
    for (int i = 0; i < 4; i++) {
        // Set GPIO function to PWM
        gpio_set_function(motors[i].pin, GPIO_FUNC_PWM);

        // Get PWM slice and channel
        motors[i].slice = pwm_gpio_to_slice_num(motors[i].pin);
        motors[i].channel = pwm_gpio_to_channel(motors[i].pin);

        // Configure PWM
        pwm_config config = pwm_get_default_config();
        pwm_config_set_clkdiv(&config, 1000.0f); // Divide clock by 1000
        pwm_config_set_wrap(&config, pwm_wrap_value);

        pwm_init(motors[i].slice, &config, true);

        // Set initial safe value (1000us - ESC arm position)
        uint16_t arm_level = us_to_pwm_level(ESC_ARM_PULSE_US);
        pwm_set_chan_level(motors[i].slice, motors[i].channel, arm_level);

        motors[i].current_speed = 0;
        motors[i].armed = false;

        printf("Motor %d (%s): Pin GP%d, Slice %d, Channel %d\n",
               i, motors[i].name, motors[i].pin, motors[i].slice, motors[i].channel);
    }

    motors_initialized = true;
    printf("Motor control system initialized successfully!\n");
    return true;
}

// Set individual motor speed (0-100%)
bool motor_set_speed(uint8_t motor_id, uint8_t speed_percent) {
    if (!motors_initialized) {
        printf("ERROR: Motors not initialized!\n");
        return false;
    }

    if (motor_id >= 4) {
        printf("ERROR: Invalid motor ID %d (0-3 valid)\n", motor_id);
        return false;
    }

    if (!motors_armed) {
        printf("WARNING: Motors not armed! Call motors_arm() first.\n");
        return false;
    }

    if (speed_percent > 100) {
        printf("WARNING: Speed clamped to 100%%\n");
        speed_percent = 100;
    }

    uint16_t pwm_level = percent_to_pwm_level(speed_percent);
    pwm_set_chan_level(motors[motor_id].slice, motors[motor_id].channel, pwm_level);

    motors[motor_id].current_speed = speed_percent;

    return true;
}

// Set all motor speeds at once
bool motors_set_all(uint8_t speed0, uint8_t speed1, uint8_t speed2, uint8_t speed3) {
    bool success = true;
    success &= motor_set_speed(0, speed0);
    success &= motor_set_speed(1, speed1);
    success &= motor_set_speed(2, speed2);
    success &= motor_set_speed(3, speed3);
    return success;
}

// Arm all ESCs (must be called before setting motor speeds)
bool motors_arm() {
    if (!motors_initialized) {
        printf("ERROR: Motors not initialized!\n");
        return false;
    }

    printf("🔧 Arming ESCs...\n");
    gpio_put(LED_PIN, 1); // LED on during arming

    // Send arming pulse (1000us) to all ESCs
    for (int i = 0; i < 4; i++) {
        uint16_t arm_level = us_to_pwm_level(ESC_ARM_PULSE_US);
        pwm_set_chan_level(motors[i].slice, motors[i].channel, arm_level);
        motors[i].armed = true;
        motors[i].current_speed = 0;
    }

    // Wait for ESC arming sequence
    printf("Waiting for ESC arming sequence (3 seconds)...\n");
    sleep_ms(3000);

    motors_armed = true;
    gpio_put(LED_PIN, 0); // LED off after arming

    printf("✅ ESCs armed successfully!\n");
    return true;
}

// Emergency stop - immediately set all motors to 0
void motors_emergency_stop() {
    printf("🚨 EMERGENCY STOP! All motors stopped!\n");

    for (int i = 0; i < 4; i++) {
        uint16_t stop_level = us_to_pwm_level(ESC_MIN_PULSE_US);
        pwm_set_chan_level(motors[i].slice, motors[i].channel, stop_level);
        motors[i].current_speed = 0;
    }

    // Blink LED rapidly to indicate emergency stop
    led_blink(10, 100);
}

// Disarm all ESCs
void motors_disarm() {
    printf("Disarming ESCs...\n");

    // Gradually reduce to zero
    for (int speed = 10; speed >= 0; speed--) {
        motors_set_all(speed, speed, speed, speed);
        sleep_ms(100);
    }

    motors_armed = false;

    for (int i = 0; i < 4; i++) {
        motors[i].armed = false;
        motors[i].current_speed = 0;
    }

    printf("ESCs disarmed\n");
}

// Motor mixing for quadcopter control
// roll: -100 to +100 (left/right)
// pitch: -100 to +100 (forward/backward)
// yaw: -100 to +100 (counter-clockwise/clockwise)
// throttle: 0 to 100 (up/down)
bool motors_mix_control(int8_t throttle, int8_t roll, int8_t pitch, int8_t yaw) {
    if (!motors_armed) {
        printf("WARNING: Motors not armed!\n");
        return false;
    }

    // Clamp inputs
    if (throttle < 0) throttle = 0;
    if (throttle > 100) throttle = 100;
    if (roll < -100) roll = -100;
    if (roll > 100) roll = 100;
    if (pitch < -100) pitch = -100;
    if (pitch > 100) pitch = 100;
    if (yaw < -100) yaw = -100;
    if (yaw > 100) yaw = 100;

    // Motor mixing (standard quadcopter X configuration)
    // Scale control inputs to throttle percentage
    int8_t roll_effect = (roll * throttle) / 400;    // Max 25% of throttle
    int8_t pitch_effect = (pitch * throttle) / 400;  // Max 25% of throttle
    int8_t yaw_effect = (yaw * throttle) / 800;      // Max 12.5% of throttle

    int16_t motor0 = throttle - roll_effect - pitch_effect - yaw_effect; // Front Right
    int16_t motor1 = throttle + roll_effect - pitch_effect + yaw_effect; // Front Left
    int16_t motor2 = throttle + roll_effect + pitch_effect - yaw_effect; // Rear Left
    int16_t motor3 = throttle - roll_effect + pitch_effect + yaw_effect; // Rear Right

    // Clamp motor values to valid range
    if (motor0 < 0) motor0 = 0; if (motor0 > 100) motor0 = 100;
    if (motor1 < 0) motor1 = 0; if (motor1 > 100) motor1 = 100;
    if (motor2 < 0) motor2 = 0; if (motor2 > 100) motor2 = 100;
    if (motor3 < 0) motor3 = 0; if (motor3 > 100) motor3 = 100;

    return motors_set_all(motor0, motor1, motor2, motor3);
}

// Print current motor status
void motors_print_status() {
    printf("\n=== Motor Status ===\n");
    printf("Initialized: %s\n", motors_initialized ? "Yes" : "No");
    printf("Armed: %s\n", motors_armed ? "Yes" : "No");

    for (int i = 0; i < 4; i++) {
        printf("Motor %d (%s): %d%% (%s)\n",
               i, motors[i].name, motors[i].current_speed,
               motors[i].armed ? "Armed" : "Disarmed");
    }
    printf("==================\n");
}

// ESC Calibration routine (run once for new ESCs)
void motors_calibrate() {
    if (!motors_initialized) {
        printf("ERROR: Motors not initialized!\n");
        return;
    }

    printf("\n🔧 ESC CALIBRATION PROCEDURE\n");
    printf("=============================\n");
    printf("⚠️  WARNING: Remove propellers before calibration!\n");
    printf("⚠️  Make sure ESCs are disconnected from power!\n");
    printf("Press any key when ready...\n");
    getchar();

    // Set maximum throttle
    printf("Setting maximum throttle (2000us)...\n");
    led_blink(3, 200);
    gpio_put(LED_PIN, 1); // LED on during calibration

    for (int i = 0; i < 4; i++) {
        uint16_t max_level = us_to_pwm_level(ESC_MAX_PULSE_US);
        pwm_set_chan_level(motors[i].slice, motors[i].channel, max_level);
    }

    printf("🔌 NOW CONNECT ESC POWER! You have 5 seconds...\n");
    sleep_ms(5000);

    // Set minimum throttle
    printf("Setting minimum throttle (1000us)...\n");
    for (int i = 0; i < 4; i++) {
        uint16_t min_level = us_to_pwm_level(ESC_MIN_PULSE_US);
        pwm_set_chan_level(motors[i].slice, motors[i].channel, min_level);
    }

    sleep_ms(2000);
    gpio_put(LED_PIN, 0); // LED off

    printf("✅ Calibration complete!\n");
    printf("ESCs should now be calibrated for 1000-2000us range\n");
}

// Test sequence for motors
void motors_test_sequence() {
    if (!motors_armed) {
        printf("ERROR: Motors must be armed first!\n");
        return;
    }

    printf("🧪 Running motor test sequence...\n");
    printf("⚠️  ENSURE PROPELLERS ARE REMOVED!\n");

    // Test each motor individually
    for (int motor = 0; motor < 4; motor++) {
        printf("Testing Motor %d (%s)...\n", motor, motors[motor].name);

        // Gradual spin up
        for (int speed = 0; speed <= 20; speed += 5) {
            motor_set_speed(motor, speed);
            sleep_ms(500);
        }

        // Hold for 2 seconds
        sleep_ms(2000);

        // Gradual spin down
        for (int speed = 20; speed >= 0; speed -= 5) {
            motor_set_speed(motor, speed);
            sleep_ms(300);
        }

        sleep_ms(1000);
    }

    printf("✅ Motor test sequence complete!\n");
}

int main() {
    stdio_init_all();

    printf("\n=== Motor Control System - Spydar Quadcopter ===\n");
    printf("Hardware: Raspberry Pi Pico\n");
    printf("ESCs: 4x Brushless Motor Controllers\n");
    printf("⚠️  SAFETY: Remove propellers during testing!\n\n");

    // Initialize motor control system
    if (!motors_init()) {
        printf("❌ Failed to initialize motors!\n");
        return 1;
    }

    // Print menu
    printf("\nMotor Control Menu:\n");
    printf("1. Calibrate ESCs (run once for new ESCs)\n");
    printf("2. Arm motors\n");
    printf("3. Test sequence (low speed)\n");
    printf("4. Manual control demo\n");
    printf("5. Emergency stop\n");
    printf("6. Disarm motors\n");
    printf("s. Show status\n");
    printf("q. Quit\n\n");

    char input;
    bool running = true;

    while (running) {
        printf("Enter command: ");
        input = getchar();
        getchar(); // consume newline

        switch (input) {
            case '1':
                motors_calibrate();
                break;

            case '2':
                motors_arm();
                break;

            case '3':
                motors_test_sequence();
                break;

            case '4':
                if (motors_armed) {
                    printf("Running manual control demo (10 seconds)...\n");
                    for (int i = 0; i < 100; i++) {
                        // Gentle movement demo
                        int8_t throttle = 15;
                        int8_t roll = (i % 20) - 10;
                        int8_t pitch = ((i/2) % 20) - 10;
                        int8_t yaw = ((i/4) % 10) - 5;

                        motors_mix_control(throttle, roll, pitch, yaw);
                        sleep_ms(100);
                    }
                    motors_set_all(0, 0, 0, 0);
                    printf("Demo complete\n");
                } else {
                    printf("Motors must be armed first!\n");
                }
                break;

            case '5':
                motors_emergency_stop();
                break;

            case '6':
                motors_disarm();
                break;

            case 's':
                motors_print_status();
                break;

            case 'q':
                printf("Shutting down...\n");
                if (motors_armed) {
                    motors_disarm();
                }
                running = false;
                break;

            default:
                printf("Invalid command. Try again.\n");
                break;
        }
    }

    return 0;
}