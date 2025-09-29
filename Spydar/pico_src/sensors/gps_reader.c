#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "pico/stdlib.h"
#include "hardware/uart.h"
#include "hardware/gpio.h"

// GPS UART configuration
#define GPS_UART_ID uart0
#define GPS_BAUD_RATE 9600
#define GPS_TX_PIN 0  // GP0 (Pin 1)
#define GPS_RX_PIN 1  // GP1 (Pin 2)

// LED configuration
#define LED_PIN PICO_DEFAULT_LED_PIN  // Built-in LED (GP25)

// GPS data buffer
#define GPS_BUFFER_SIZE 256
static char gps_buffer[GPS_BUFFER_SIZE];
static uint gps_buffer_pos = 0;

// GPS coordinate structure
typedef struct {
    float latitude;
    float longitude;
    char lat_dir;  // N/S
    char lon_dir;  // E/W
    int fix_quality;
    int satellites;
    bool valid_fix;
} gps_data_t;

// LED blinking state
typedef struct {
    bool is_blinking;
    uint32_t blink_start_time;
    uint32_t last_toggle_time;
    bool led_state;
} led_blink_t;

static gps_data_t current_gps = {0};
static led_blink_t led_blink = {false, 0, 0, false};
static bool fix_found_before = false;

void led_init() {
    // Initialize built-in LED
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    gpio_put(LED_PIN, 0);  // Start with LED off
    printf("LED initialized on GP%d\n", LED_PIN);
}

void led_start_blink() {
    led_blink.is_blinking = true;
    led_blink.blink_start_time = to_ms_since_boot(get_absolute_time());
    led_blink.last_toggle_time = led_blink.blink_start_time;
    led_blink.led_state = true;
    gpio_put(LED_PIN, 1);  // Turn on LED
    printf("🔆 GPS FIX FOUND! LED blinking for 5 seconds...\n");
}

void led_update() {
    if (!led_blink.is_blinking) return;

    uint32_t current_time = to_ms_since_boot(get_absolute_time());

    // Check if 5 seconds have passed
    if (current_time - led_blink.blink_start_time >= 5000) {
        led_blink.is_blinking = false;
        gpio_put(LED_PIN, 0);  // Turn off LED
        printf("LED blinking stopped\n");
        return;
    }

    // Toggle LED every 100ms
    if (current_time - led_blink.last_toggle_time >= 100) {
        led_blink.led_state = !led_blink.led_state;
        gpio_put(LED_PIN, led_blink.led_state);
        led_blink.last_toggle_time = current_time;
    }
}

void gps_init() {
    // Initialize UART0 for GPS communication
    uart_init(GPS_UART_ID, GPS_BAUD_RATE);

    // Configure GPIO pins for UART
    gpio_set_function(GPS_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(GPS_RX_PIN, GPIO_FUNC_UART);

    // Configure UART settings
    uart_set_hw_flow(GPS_UART_ID, false, false);
    uart_set_format(GPS_UART_ID, 8, 1, UART_PARITY_NONE);
    uart_set_fifo_enabled(GPS_UART_ID, false);

    printf("GPS UART initialized on GP%d (TX) and GP%d (RX)\n", GPS_TX_PIN, GPS_RX_PIN);
}

float parse_coordinate(const char* coord_str, const char* dir_str) {
    if (!coord_str || !dir_str) return 0.0;

    float coord = atof(coord_str);
    if (coord == 0.0) return 0.0;

    // Convert DDMM.MMMM to decimal degrees
    int degrees = (int)(coord / 100);
    float minutes = coord - (degrees * 100);
    float decimal_degrees = degrees + (minutes / 60.0);

    // Apply direction (negative for S/W)
    if (dir_str[0] == 'S' || dir_str[0] == 'W') {
        decimal_degrees = -decimal_degrees;
    }

    return decimal_degrees;
}

bool parse_gga_sentence(const char* sentence) {
    // Parse $GPGGA sentence: $GPGGA,time,lat,lat_dir,lon,lon_dir,quality,satellites,hdop,altitude,M,height,M,dgps_time,dgps_id*checksum
    char *tokens[15];
    char sentence_copy[GPS_BUFFER_SIZE];
    strncpy(sentence_copy, sentence, GPS_BUFFER_SIZE - 1);
    sentence_copy[GPS_BUFFER_SIZE - 1] = '\0';

    // Tokenize the sentence
    char *token = strtok(sentence_copy, ",");
    int token_count = 0;

    while (token != NULL && token_count < 15) {
        tokens[token_count++] = token;
        token = strtok(NULL, ",");
    }

    if (token_count < 7) return false;

    // Check if it's a GGA sentence
    if (strncmp(tokens[0], "$GPGGA", 6) != 0 && strncmp(tokens[0], "$GNGGA", 6) != 0) {
        return false;
    }

    // Parse fix quality (0 = no fix, 1 = GPS fix, 2 = DGPS fix)
    current_gps.fix_quality = atoi(tokens[6]);
    current_gps.valid_fix = (current_gps.fix_quality > 0);

    if (current_gps.valid_fix) {
        // Parse coordinates
        current_gps.latitude = parse_coordinate(tokens[2], tokens[3]);
        current_gps.longitude = parse_coordinate(tokens[4], tokens[5]);
        current_gps.lat_dir = tokens[3][0];
        current_gps.lon_dir = tokens[5][0];
        current_gps.satellites = atoi(tokens[7]);

        return true;
    }

    return false;
}

void gps_read_data() {
    // Check if data is available
    while (uart_is_readable(GPS_UART_ID)) {
        char c = uart_getc(GPS_UART_ID);

        // Store in buffer for processing
        if (gps_buffer_pos < GPS_BUFFER_SIZE - 1) {
            gps_buffer[gps_buffer_pos++] = c;

            // Check for end of NMEA sentence
            if (c == '\n') {
                gps_buffer[gps_buffer_pos] = '\0';

                // Try to parse GGA sentence for coordinates
                if (parse_gga_sentence(gps_buffer)) {
                    printf("GPS Fix: %.6f%c, %.6f%c (Quality: %d, Satellites: %d)\n",
                           current_gps.latitude, current_gps.lat_dir,
                           current_gps.longitude, current_gps.lon_dir,
                           current_gps.fix_quality, current_gps.satellites);

                    // Start LED blinking if this is the first fix found
                    if (!fix_found_before) {
                        led_start_blink();
                        fix_found_before = true;
                    }
                }

                gps_buffer_pos = 0;  // Reset buffer position
            }
        } else {
            // Buffer overflow protection
            gps_buffer_pos = 0;
        }
    }
}

gps_data_t gps_get_current_location() {
    return current_gps;
}

int main() {
    stdio_init_all();

    printf("GPS Reader - Pico C SDK\n");
    printf("Waiting for GPS fix...\n");
    printf("LED will blink for 5 seconds when first fix is found!\n");

    led_init();
    gps_init();

    while (true) {
        gps_read_data();
        led_update();  // Update LED blinking state

        // Display status every 5 seconds
        static uint32_t last_status = 0;
        uint32_t now = to_ms_since_boot(get_absolute_time());
        if (now - last_status > 5000) {
            if (current_gps.valid_fix) {
                printf("Current Location: %.6f, %.6f\n",
                       current_gps.latitude, current_gps.longitude);
            } else {
                printf("No GPS fix yet...\n");
            }
            last_status = now;
        }

        sleep_ms(100);
    }

    return 0;
}