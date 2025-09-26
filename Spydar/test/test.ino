#include "pico/stdlib.h"
#include "hardware/uart.h"

#define UART_ID uart0
#define TX_PIN 0
#define RX_PIN 1
#define BAUD_RATE 9600

// Define variables to store GPS data
float latitude = 0.0;
float longitude = 0.0;

void read_gps_data() {
    char gps_data[128];
    int data_index = 0;
    
    while (true) {
        if (uart_is_readable(UART_ID)) {
            char received_char = uart_getc(UART_ID);
            if (received_char == '\n') {
                gps_data[data_index] = '\0';
                if (strstr(gps_data, "$GPRMC") != NULL) {
                    char *token = strtok(gps_data, ",");
                    for (int i = 0; i < 3; i++) {
                        token = strtok(NULL, ",");
                    }
                    if (token) {
                        latitude = atof(token);
                    }
                    token = strtok(NULL, ",");
                    if (token) {
                        longitude = atof(token);
                    }
                }
                data_index = 0;
            } else {
                gps_data[data_index++] = received_char;
            }
        }
    }
}

int main() {
    stdio_init_all();

    uart_init(UART_ID, BAUD_RATE);
    uart_set_pin(UART_ID, TX_PIN, RX_PIN, UART_PIN_ENABLE_RX);
    
    read_gps_data();

    while (true) {
        printf("Latitude: %.6f, Longitude: %.6f\n", latitude, longitude);
        sleep_ms(1000);
    }
    
    return 0;
}
