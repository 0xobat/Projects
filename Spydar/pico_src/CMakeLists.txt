# == DO NOT EDIT THE FOLLOWING LINES for the Raspberry Pi Pico VS Code Extension to work ==
if(WIN32)
    set(USERHOME $ENV{USERPROFILE})
else()
    set(USERHOME $ENV{HOME})
endif()
set(sdkVersion 2.2.0)
set(toolchainVersion 14_2_Rel1)
set(picotoolVersion 2.2.0)
set(picoVscode ${USERHOME}/.pico-sdk/cmake/pico-vscode.cmake)
if (EXISTS ${picoVscode})
    include(${picoVscode})
endif()
# ====================================================================================
set(PICO_BOARD pico CACHE STRING "Board type")

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

# GPS Heartbeat Test executable
add_executable(gps_heartbeat
    sensors/gps_heartbeat.c
)

target_link_libraries(gps_heartbeat
    pico_stdlib
    hardware_uart
    hardware_gpio
)

pico_add_extra_outputs(gps_heartbeat)
pico_enable_stdio_usb(gps_heartbeat 1)
pico_enable_stdio_uart(gps_heartbeat 0)

# GPS Configuration utility
add_executable(gps_configure
    sensors/gps_configure.c
)

target_link_libraries(gps_configure
    pico_stdlib
    hardware_uart
    hardware_gpio
)

pico_add_extra_outputs(gps_configure)
pico_enable_stdio_usb(gps_configure 1)
pico_enable_stdio_uart(gps_configure 0)

# RC Control Test executable
add_executable(rc_control
    sensors/rc_control.c
)

target_link_libraries(rc_control
    pico_stdlib
    hardware_gpio
    hardware_timer
)

pico_add_extra_outputs(rc_control)
pico_enable_stdio_usb(rc_control 1)
pico_enable_stdio_uart(rc_control 0)

# Motor Control Test executable
add_executable(motor_control
    sensors/motor_control.c
)

target_link_libraries(motor_control
    pico_stdlib
    hardware_pwm
    hardware_gpio
    hardware_clocks
)

pico_add_extra_outputs(motor_control)
pico_enable_stdio_usb(motor_control 1)
pico_enable_stdio_uart(motor_control 0)