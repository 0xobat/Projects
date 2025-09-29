#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "hardware/uart.h"

// GPS UART configuration
#define GPS_UART_ID uart0
#define GPS_BAUD_RATE 4800
#define GPS_TX_PIN 0  // GP0 (Pin 1)
#define GPS_RX_PIN 1  // GP1 (Pin 2)

// Test parameters
#define TEST_TIMEOUT_MS 30000  // 30 seconds
#define HEARTBEAT_INTERVAL_MS 2000  // 2 seconds

typedef struct {
    bool uart_responding;
    bool nmea_detected;
    bool valid_sentences;
    int total_sentences;
    int valid_sentence_count;
    uint32_t test_start_time;
} gps_test_t;

static gps_test_t test_status = {0};

void gps_test_init() {
    // Initialize UART0 for GPS communication
    uart_init(GPS_UART_ID, GPS_BAUD_RATE);

    // Configure GPIO pins for UART
    gpio_set_function(GPS_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(GPS_RX_PIN, GPIO_FUNC_UART);

    // Configure UART settings
    uart_set_hw_flow(GPS_UART_ID, false, false);
    uart_set_format(GPS_UART_ID, 8, 1, UART_PARITY_NONE);
    uart_set_fifo_enabled(GPS_UART_ID, false);

    test_status.test_start_time = to_ms_since_boot(get_absolute_time());

    printf("GPS Heartbeat Test - Pico C SDK\n");
    printf("Testing Neo-6M GPS module...\n");
    printf("UART: GP%d (TX), GP%d (RX) at %d baud\n\n",
           GPS_TX_PIN, GPS_RX_PIN, GPS_BAUD_RATE);
}

bool is_valid_nmea_sentence(const char* sentence) {
    // Check for NMEA sentence format: $GPXXX or $GNXXX
    if (strlen(sentence) < 6) return false;
    if (sentence[0] != '$') return false;
    if (strncmp(sentence + 1, "GP", 2) != 0 && strncmp(sentence + 1, "GN", 2) != 0) return false;

    // Look for comma-separated fields
    return strchr(sentence, ',') != NULL;
}

void process_gps_data() {
    static char buffer[256];
    static int buf_pos = 0;

    while (uart_is_readable(GPS_UART_ID)) {
        test_status.uart_responding = true;

        char c = uart_getc(GPS_UART_ID);

        if (buf_pos < sizeof(buffer) - 1) {
            buffer[buf_pos++] = c;

            if (c == '\n') {
                buffer[buf_pos] = '\0';
                test_status.total_sentences++;

                // Check if it's a valid NMEA sentence
                if (is_valid_nmea_sentence(buffer)) {
                    test_status.nmea_detected = true;
                    test_status.valid_sentence_count++;

                    // Check for specific sentence types that indicate GPS is working
                    if (strstr(buffer, "$GPGGA") || strstr(buffer, "$GNGGA") ||
                        strstr(buffer, "$GPRMC") || strstr(buffer, "$GNRMC")) {
                        test_status.valid_sentences = true;
                    }
                }

                buf_pos = 0;
            }
        } else {
            buf_pos = 0; // Buffer overflow protection
        }
    }
}

void print_test_status() {
    uint32_t elapsed = to_ms_since_boot(get_absolute_time()) - test_status.test_start_time;

    printf("\n=== GPS Heartbeat Status (%.1fs) ===\n", elapsed / 1000.0);
    printf("UART Communication:  %s\n", test_status.uart_responding ? "✓ OK" : "✗ FAIL");
    printf("NMEA Data Detected:  %s\n", test_status.nmea_detected ? "✓ OK" : "✗ FAIL");
    printf("Valid GPS Sentences: %s\n", test_status.valid_sentences ? "✓ OK" : "✗ FAIL");
    printf("Total Sentences:     %d\n", test_status.total_sentences);
    printf("Valid Sentences:     %d\n", test_status.valid_sentence_count);

    if (test_status.valid_sentence_count > 0) {
        printf("Data Quality:        %.1f%% valid\n",
               (float)test_status.valid_sentence_count / test_status.total_sentences * 100.0);
    }

    // Overall status
    bool gps_working = test_status.uart_responding &&
                       test_status.nmea_detected &&
                       test_status.valid_sentences;

    printf("\nGPS Module Status:   %s\n", gps_working ? "🟢 WORKING" : "🔴 NOT WORKING");

    if (!gps_working) {
        printf("\nTroubleshooting:\n");
        if (!test_status.uart_responding) {
            printf("- Check GPS module power supply\n");
            printf("- Verify UART wiring (TX/RX pins)\n");
            printf("- Ensure GPS module is powered on\n");
        } else if (!test_status.nmea_detected) {
            printf("- GPS may be in binary mode\n");
            printf("- Check baud rate settings\n");
            printf("- Verify GPS module configuration\n");
        } else if (!test_status.valid_sentences) {
            printf("- GPS may still be initializing\n");
            printf("- Check antenna connection\n");
            printf("- Ensure clear sky view for satellite signals\n");
        }
    }
    printf("=====================================\n\n");
}

int main() {
    stdio_init_all();

    gps_test_init();

    uint32_t last_heartbeat = 0;
    uint32_t test_end_time = test_status.test_start_time + TEST_TIMEOUT_MS;

    printf("Starting %d second GPS heartbeat test...\n", TEST_TIMEOUT_MS / 1000);
    printf("Listening for NMEA data...\n\n");

    while (true) {
        uint32_t current_time = to_ms_since_boot(get_absolute_time());

        // Process incoming GPS data
        process_gps_data();

        // Print heartbeat status
        if (current_time - last_heartbeat >= HEARTBEAT_INTERVAL_MS) {
            print_test_status();
            last_heartbeat = current_time;
        }

        // Check if test should end
        if (current_time >= test_end_time) {
            printf("Test completed after %d seconds.\n", TEST_TIMEOUT_MS / 1000);
            print_test_status();

            // Final recommendation
            bool gps_working = test_status.uart_responding &&
                              test_status.nmea_detected &&
                              test_status.valid_sentences;

            if (gps_working) {
                printf("✅ GPS module is functioning properly!\n");
                printf("   Ready for navigation applications.\n");
            } else {
                printf("❌ GPS module needs attention.\n");
                printf("   Please check connections and configuration.\n");
            }

            break;
        }

        sleep_ms(100);
    }

    return 0;
}