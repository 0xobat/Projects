#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "hardware/uart.h"

// GPS UART configuration
#define GPS_UART_ID uart0
#define GPS_TX_PIN 0  // GP0 (Pin 1)
#define GPS_RX_PIN 1  // GP1 (Pin 2)

// Try multiple baud rates that Neo-6M might be using
static const uint32_t test_baud_rates[] = {9600, 38400, 57600, 115200, 4800};
static const int num_baud_rates = sizeof(test_baud_rates) / sizeof(test_baud_rates[0]);

void gps_init_uart(uint32_t baud_rate) {
    uart_deinit(GPS_UART_ID);
    uart_init(GPS_UART_ID, baud_rate);

    gpio_set_function(GPS_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(GPS_RX_PIN, GPIO_FUNC_UART);

    uart_set_hw_flow(GPS_UART_ID, false, false);
    uart_set_format(GPS_UART_ID, 8, 1, UART_PARITY_NONE);
    uart_set_fifo_enabled(GPS_UART_ID, false);

    printf("Testing baud rate: %d\n", baud_rate);
}

void send_ubx_command(const uint8_t* command, size_t length) {
    for (size_t i = 0; i < length; i++) {
        uart_putc_raw(GPS_UART_ID, command[i]);
    }
    printf("Sent UBX command (%d bytes)\n", length);
}

void send_nmea_command(const char* command) {
    // Calculate NMEA checksum
    uint8_t checksum = 0;
    for (int i = 1; command[i] != '*' && command[i] != '\0'; i++) {
        checksum ^= command[i];
    }

    printf("Sending: %s%02X\r\n", command, checksum);
    uart_puts(GPS_UART_ID, command);
    uart_putc(GPS_UART_ID, (checksum >> 4) + (((checksum >> 4) > 9) ? 'A' - 10 : '0'));
    uart_putc(GPS_UART_ID, (checksum & 0xF) + (((checksum & 0xF) > 9) ? 'A' - 10 : '0'));
    uart_puts(GPS_UART_ID, "\r\n");
}

void listen_raw_data(uint32_t timeout_ms) {
    uint32_t start_time = to_ms_since_boot(get_absolute_time());
    int byte_count = 0;

    printf("=== LISTENING FOR RAW DATA ===\n");
    printf("Displaying everything received for %d ms...\n", timeout_ms);
    printf("RAW: ");

    while (to_ms_since_boot(get_absolute_time()) - start_time < timeout_ms) {
        if (uart_is_readable(GPS_UART_ID)) {
            char c = uart_getc(GPS_UART_ID);
            byte_count++;

            // Show both character and hex value
            if (c >= 32 && c <= 126) {
                printf("%c", c);
            } else if (c == '\r') {
                printf("\\r");
            } else if (c == '\n') {
                printf("\\n\n");
            } else {
                printf("[0x%02X]", (unsigned char)c);
            }
        }
        sleep_ms(1);
    }

    printf("\n=== END RAW DATA ===\n");
    printf("Total bytes: %d\n\n", byte_count);
}

bool test_gps_response(uint32_t timeout_ms) {
    uint32_t start_time = to_ms_since_boot(get_absolute_time());
    char buffer[256];
    int buf_pos = 0;
    bool data_received = false;
    bool nmea_detected = false;
    int byte_count = 0;
    int line_count = 0;

    printf("Listening for response...\n");
    printf("RAW DATA: ");

    while (to_ms_since_boot(get_absolute_time()) - start_time < timeout_ms) {
        if (uart_is_readable(GPS_UART_ID)) {
            char c = uart_getc(GPS_UART_ID);
            data_received = true;
            byte_count++;

            // Display both printable characters and hex values for non-printable
            if (c >= 32 && c <= 126) {
                printf("%c", c);  // Printable characters
            } else {
                printf("[0x%02X]", (unsigned char)c);  // Non-printable in hex
            }

            if (buf_pos < sizeof(buffer) - 1) {
                buffer[buf_pos++] = c;

                if (c == '\n' || c == '\r') {
                    buffer[buf_pos-1] = '\0';  // Replace newline with null terminator

                    if (strlen(buffer) > 0) {
                        line_count++;
                        printf("\nLINE %d: '%s' (length: %d)\n", line_count, buffer, strlen(buffer));

                        // Check for NMEA sentence
                        if (buffer[0] == '$') {
                            printf("  -> NMEA sentence detected!\n");
                            if (strstr(buffer, "GP") || strstr(buffer, "GN") || strstr(buffer, "PUBX")) {
                                nmea_detected = true;
                                printf("  -> Valid GPS NMEA sentence!\n");
                            }
                        } else if (buffer[0] == 0xB5 || strstr(buffer, "UBX")) {
                            printf("  -> UBX binary message detected!\n");
                        }
                        printf("RAW DATA: ");
                    }
                    buf_pos = 0;
                }
            } else {
                printf("\n[BUFFER OVERFLOW - resetting]\nRAW DATA: ");
                buf_pos = 0;
            }
        }
        sleep_ms(10);
    }

    printf("\n");
    printf("=== RECEPTION SUMMARY ===\n");
    printf("Total bytes received: %d\n", byte_count);
    printf("Total lines received: %d\n", line_count);

    if (!data_received) {
        printf("No data received\n");
        return false;
    } else if (!nmea_detected) {
        printf("Data received but no valid NMEA sentences\n");
        if (byte_count > 0) {
            printf("This could be:\n");
            printf("  - UBX binary protocol\n");
            printf("  - Wrong baud rate (garbled data)\n");
            printf("  - Module not configured for NMEA output\n");
        }
        return false;
    } else {
        printf("NMEA sentences detected!\n");
        return true;
    }
}

void configure_gps_nmea() {
    printf("\n=== Configuring GPS for NMEA output ===\n");

    // UBX command to set NMEA protocol on UART1 (CFG-PRT)
    // This configures UART1 to output NMEA at 9600 baud
    const uint8_t ubx_cfg_prt[] = {
        0xB5, 0x62,  // UBX header
        0x06, 0x00,  // CFG-PRT
        0x14, 0x00,  // Length: 20 bytes
        0x01,        // Port ID: UART1
        0x00,        // Reserved
        0x00, 0x00,  // TX Ready
        0xD0, 0x08, 0x00, 0x00,  // UART mode: 8N1
        0x80, 0x25, 0x00, 0x00,  // Baud rate: 9600
        0x01, 0x00,  // Input protocols: UBX only
        0x01, 0x00,  // Output protocols: NMEA only
        0x00, 0x00,  // Flags
        0x00, 0x00,  // Reserved
        0xA0, 0xA9   // Checksum
    };

    // UBX command to enable specific NMEA messages (CFG-MSG)
    const uint8_t ubx_enable_gga[] = {
        0xB5, 0x62,  // UBX header
        0x06, 0x01,  // CFG-MSG
        0x08, 0x00,  // Length: 8 bytes
        0xF0, 0x00,  // NMEA GGA
        0x00, 0x01, 0x01, 0x01, 0x01, 0x01,  // Enable on all ports
        0x02, 0x39   // Checksum
    };

    const uint8_t ubx_enable_rmc[] = {
        0xB5, 0x62,  // UBX header
        0x06, 0x01,  // CFG-MSG
        0x08, 0x00,  // Length: 8 bytes
        0xF0, 0x04,  // NMEA RMC
        0x00, 0x01, 0x01, 0x01, 0x01, 0x01,  // Enable on all ports
        0x06, 0x41   // Checksum
    };

    printf("Sending UBX configuration commands...\n");
    send_ubx_command(ubx_cfg_prt, sizeof(ubx_cfg_prt));
    sleep_ms(500);

    send_ubx_command(ubx_enable_gga, sizeof(ubx_enable_gga));
    sleep_ms(500);

    send_ubx_command(ubx_enable_rmc, sizeof(ubx_enable_rmc));
    sleep_ms(500);

    // Also try NMEA configuration commands
    printf("Sending NMEA configuration commands...\n");
    send_nmea_command("$PUBX,41,1,0007,0001,9600,0*");  // Set NMEA protocol
    sleep_ms(500);
}

int main() {
    stdio_init_all();

    printf("GPS Configuration Utility - Neo-6M\n");
    printf("===================================\n\n");

    // Continuously test baud rates in a loop
    while (true) {
        bool gps_found = false;
        uint32_t working_baud = 0;

        // Test different baud rates to find current GPS setting
        for (int i = 0; i < num_baud_rates && !gps_found; i++) {
            printf("\n--- Testing baud rate: %d ---\n", test_baud_rates[i]);
            gps_init_uart(test_baud_rates[i]);

            // First, just listen for any data without sending commands
            printf("Listening for spontaneous data...\n");
            listen_raw_data(2000);

            // Send a simple query command
            printf("Sending version query...\n");
            send_nmea_command("$PUBX,04*");

            if (test_gps_response(3000)) {
                gps_found = true;
                working_baud = test_baud_rates[i];
                printf("GPS found at %d baud!\n", working_baud);
            }
        }

        if (!gps_found) {
            printf("\n❌ GPS not responding at any tested baud rate\n");
            printf("Check connections and power supply\n");
        } else {
            printf("\n✅ GPS responding at %d baud\n", working_baud);

            // Now configure for NMEA output
            configure_gps_nmea();

            // Switch to 9600 baud and test NMEA output
            printf("\n--- Testing NMEA output at 9600 baud ---\n");
            gps_init_uart(9600);
            sleep_ms(1000);

            if (test_gps_response(10000)) {
                printf("\n✅ GPS successfully configured for NMEA output!\n");
                printf("You can now use gps_reader or gps_heartbeat\n");
            } else {
                printf("\n⚠️  Configuration may need more time\n");
                printf("Try running gps_heartbeat again in 1-2 minutes\n");
            }
        }

        // Wait 5 seconds before testing again
        printf("\n\n=== Waiting 5 seconds before next test cycle ===\n\n");
        sleep_ms(5000);
    }

    return 0;
}