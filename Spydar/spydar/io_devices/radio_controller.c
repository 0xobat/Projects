/***********************************
 *  Reader for Radio controller (4 Channels)
 *  @author: 0xObat
 *  @date: 2025-
*/
#include <stdio.h>
#include <stdint.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/timer.h"

// RC receiver pin definitions (matching README.md configuration)
#define RC_ROLL_PIN      18  // GP18/Pin 24 / Ch1 (Roll)
#define RC_PITCH_PIN 19  // GP19/Pin 25 / Ch2 (Pitch)
#define RC_THROTTLE_PIN    20  // GP20/Pin 26 / Ch3 (Throttle)
#define RC_YAW_PIN     21  // GP21/Pin 27 / Ch4 (Yaw)

// RC pulse width values (in microseconds)
#define RC_MIN_PULSE    1000  // Minimum pulse width
#define RC_MAX_PULSE    2000  // Maximum pulse width
#define RC_CENTER_PULSE 1500  // Center/neutral pulse width
#define RC_TIMEOUT_US   25000 // 25ms timeout for pulse measurement

// RC channel structure
typedef struct {
    uint pin;
    volatile uint32_t pulse_start;
    volatile uint32_t pulse_width;
    volatile bool pulse_valid;
    const char* name;
} rc_channel_t;

// RC channel array (ordered by channel number)
static rc_channel_t rc_channels[4] = {
    {RC_YAW_PIN, 0, 0, false, "Ch1-Yaw"},
    {RC_THROTTLE_PIN, 0, 0, false, "Ch2-Throttle"},
    {RC_PITCH_PIN, 0, 0, false, "Ch3-Pitch"},
    {RC_ROLL_PIN, 0, 0, false, "Ch4-Roll"}
};

// GPIO interrupt handler for RC pulse measurement
void rc_gpio_callback(uint gpio, uint32_t events) {
    uint32_t current_time = time_us_32();

    // Find the channel that triggered the interrupt
    for (int i = 0; i < 4; i++) {
        if (rc_channels[i].pin == gpio) {
            if (events & GPIO_IRQ_EDGE_RISE) {
                // Rising edge - start of pulse
                rc_channels[i].pulse_start = current_time;
                rc_channels[i].pulse_valid = false;
            } else if (events & GPIO_IRQ_EDGE_FALL) {
                // Falling edge - end of pulse
                if (rc_channels[i].pulse_start != 0) {
                    uint32_t pulse_duration = current_time - rc_channels[i].pulse_start;

                    // Validate pulse width (should be between 1000-2000μs)
                    if (pulse_duration >= RC_MIN_PULSE && pulse_duration <= RC_MAX_PULSE) {
                        rc_channels[i].pulse_width = pulse_duration;
                        rc_channels[i].pulse_valid = true;
                    }
                }
            }
            break;
        }
    }
}

void rc_init() {
    printf("Initializing RC control system...\n");

    // Configure GPIO pins for RC inputs
    for (int i = 0; i < 4; i++) {
        gpio_init(rc_channels[i].pin);
        gpio_set_dir(rc_channels[i].pin, GPIO_IN);
        gpio_pull_down(rc_channels[i].pin);  // Pull down to ensure clean signals

        // Enable interrupts for both rising and falling edges
        gpio_set_irq_enabled_with_callback(rc_channels[i].pin,
                                         GPIO_IRQ_EDGE_RISE | GPIO_IRQ_EDGE_FALL,
                                         true, &rc_gpio_callback);

        printf("RC %s channel initialized on GP%d\n", rc_channels[i].name, rc_channels[i].pin);
    }

    printf("RC control system initialized successfully\n");
}

uint16_t rc_get_pulse_width(uint channel) {
    if (channel >= 4) return 0;

    if (rc_channels[channel].pulse_valid) {
        return rc_channels[channel].pulse_width;
    }

    return 0;  // Return 0 if no valid pulse received
}

bool rc_is_valid(uint channel) {
    if (channel >= 4) return false;
    return rc_channels[channel].pulse_valid;
}

int16_t rc_get_scaled_value(uint channel, int16_t min_val, int16_t max_val) {
    if (channel >= 4 || !rc_channels[channel].pulse_valid) {
        return 0;
    }

    uint16_t pulse = rc_channels[channel].pulse_width;

    // Map pulse width (1000-2000μs) to desired range (min_val to max_val)
    int32_t scaled = ((int32_t)(pulse - RC_MIN_PULSE) * (max_val - min_val)) /
                     (RC_MAX_PULSE - RC_MIN_PULSE) + min_val;

    // Clamp to range
    if (scaled < min_val) scaled = min_val;
    if (scaled > max_val) scaled = max_val;

    return (int16_t)scaled;
}

void rc_print_values() {
    printf("\n=== RC Channel Values ===\n");
    for (int i = 0; i < 4; i++) {
        if (rc_channels[i].pulse_valid) {
            int16_t scaled = rc_get_scaled_value(i, -100, 100);
            printf("%s: %4dus (scaled: %4d%%)\n",
                   rc_channels[i].name,
                   rc_channels[i].pulse_width,
                   scaled);
        } else {
            printf("%s: No signal\n", rc_channels[i].name);
        }
    }
    printf("=========================\n");
}

// Channel index definitions for easier access (ordered by channel number)
enum {
    RC_CH1_YAW = 0,
    RC_CH2_THROTTLE = 1,
    RC_CH3_PITCH = 2,
    RC_CH4_ROLL = 3
};

int main() {
    // Initialize stdio
    stdio_init_all();

    // Wait for USB connection (optional)
    sleep_ms(2000);

    printf("\n=== RC Control Test ===\n");
    printf("Reading RC receiver signals...\n");

    // Initialize RC system
    rc_init();

    // Main loop
    while (true) {
        // Print RC values every second
        rc_print_values();

        // Check for failsafe conditions
        bool all_valid = true;
        for (int i = 0; i < 4; i++) {
            if (!rc_is_valid(i)) {
                all_valid = false;
                break;
            }
        }

        if (!all_valid) {
            printf("WARNING: Not all RC channels are receiving valid signals!\n");
        }

        // Example of getting individual channel values
        if (rc_is_valid(RC_CH2_THROTTLE)) {
            uint16_t throttle_raw = rc_get_pulse_width(RC_CH2_THROTTLE);
            int16_t throttle_percent = rc_get_scaled_value(RC_CH2_THROTTLE, 0, 100);

            if (throttle_percent < 10) {
                printf("Channel 2 (Throttle) LOW - Safe to arm\n");
            } else if (throttle_percent > 90) {
                printf("Channel 2 (Throttle) HIGH - Maximum power\n");
            }
        }

        sleep_ms(1000);
    }

    return 0;
}