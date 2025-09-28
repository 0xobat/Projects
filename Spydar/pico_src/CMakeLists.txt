cmake_minimum_required(VERSION 3.13)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Pull in Raspberry Pi Pico SDK
include(pico_sdk_import.cmake)

project(spydar_pico C CXX ASM)

# Initialize the Raspberry Pi Pico SDK
pico_sdk_init()

# GPS Reader executable
add_executable(gps_reader
    sensors/gps_reader.c
)

target_link_libraries(gps_reader
    pico_stdlib
    hardware_uart
    hardware_gpio
)

pico_add_extra_outputs(gps_reader)
pico_enable_stdio_usb(gps_reader 1)
pico_enable_stdio_uart(gps_reader 0)

# MPU Reset executable
add_executable(mpu_reset
    sensors/mpu_reset.c
)

target_link_libraries(mpu_reset
    pico_stdlib
    hardware_i2c
    hardware_gpio
)

pico_add_extra_outputs(mpu_reset)
pico_enable_stdio_usb(mpu_reset 1)
pico_enable_stdio_uart(mpu_reset 0)

# MPU Self-test executable
add_executable(mpu_self_test
    sensors/mpu_self_test.c
)

target_link_libraries(mpu_self_test
    pico_stdlib
    hardware_i2c
    hardware_gpio
    pico_float
    pico_double
)

pico_add_extra_outputs(mpu_self_test)
pico_enable_stdio_usb(mpu_self_test 1)
pico_enable_stdio_uart(mpu_self_test 0)