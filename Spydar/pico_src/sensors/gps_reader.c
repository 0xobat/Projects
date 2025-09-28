#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/uart.h"

// GPS UART configuration
#define GPS_UART_ID uart0
#define GPS_BAUD_RATE 9600
#define GPS_TX_PIN 0  // GP0 (Pin 1)
#define GPS_RX_PIN 1  // GP1 (Pin 2)

// GPS data buffer
#define GPS_BUFFER_SIZE 256
static char gps_buffer[GPS_BUFFER_SIZE];
static uint gps_buffer_pos = 0;

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

void gps_read_data() {
    // Check if data is available
    while (uart_is_readable(GPS_UART_ID)) {
        char c = uart_getc(GPS_UART_ID);

        // Echo GPS data to serial console
        printf("%c", c);

        // Store in buffer for processing
        if (gps_buffer_pos < GPS_BUFFER_SIZE - 1) {
            gps_buffer[gps_buffer_pos++] = c;

            // Check for end of NMEA sentence
            if (c == '\n') {
                gps_buffer[gps_buffer_pos] = '\0';
                gps_buffer_pos = 0;  // Reset buffer position
            }
        } else {
            // Buffer overflow protection
            gps_buffer_pos = 0;
        }
    }
}

int main() {
    stdio_init_all();

    printf("GPS Reader - Pico C SDK\n");
    printf("Reading GPS data...\n");

    gps_init();

    while (true) {
        gps_read_data();
        sleep_ms(100);
    }

    return 0;
}