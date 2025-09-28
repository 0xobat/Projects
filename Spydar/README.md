# Project Spydar - Self Balancing Quadcopter

A comprehensive quadcopter design featuring autonomous flight capabilities with remote control, hover mode, and GPS navigation.

## Project Overview

This quadcopter project implements:

- **Self-balancing flight** using sensor fusion and PID control
- **Remote control operation** via RC transmitter
- **Hover mode** for stable positioning
- **GPS waypoint navigation** capabilities

## System Architecture

### Control System

- **Flight Control Unit:** Raspberry Pi Pico microcontroller
- **Control Algorithms:**
  - PID controllers for attitude stabilization (roll, pitch, yaw)
  - Fuzzy logic for enhanced control
  - Sensor fusion combining gyroscope and accelerometer data
- **Flight Modes:** Manual RC control and GPS-assisted autonomous flight

### Hardware Components

#### Sensors

- **MPU-6050:** 6-axis gyroscope and accelerometer for attitude sensing
- **NEO-6M GPS:** Global positioning for navigation and waypoint following
- **RC Receiver:** 4+ channel receiver for manual control input

#### Propulsion System

- **4x Brushless Motors:** ESC (electronic speed controllers)
- **4x Propellers:** Counter-rotating configuration
- **Power Distribution:** Parallel motor connection with voltage regulation

#### Electronics

- **Microcontroller:** Raspberry Pi Pico (pins configured for SPI, I2C, UART communication)
- **Power System:** Rechargeable LiPo battery with voltage regulation
- **Communication:** UART protocol for GPS, I2C for MPU-6050, PWM for ESCs

## Pin Configuration

### Raspberry Pi Pico Connections

#### Communication Interfaces

- **GPS Module:** UART0 TX (GP0/Pin 1), UART0 RX (GP1/Pin 2)
- **MPU-6050:** I2C0 SCL (GP5/Pin 7), I2C0 SDA (GP4/Pin 6)

#### Motor Control (PWM)

- **ESC 0:** PWM - GP6/Pin 9
- **ESC 1:** PWM - GP7/Pin 10
- **ESC 2:** PWM - GP8/Pin 11
- **ESC 3:** PWM - GP9/Pin 12

#### Remote Control Inputs (GPIO)

- **Roll:** GPIO - GP21/Pin 27
- **Pitch:** GPIO - GP20/Pin 26
- **Throttle:** GPIO - GP19/Pin 25
- **Yaw:** GPIO - GP18/Pin 24

## Control Algorithm Features

### PID Control System

- **Attitude Control:** Separate PID loops for roll, pitch, and yaw axes
- **Position Control:** GPS-based positioning with configurable waypoints
- **Motor Mixing:** Converts control commands to individual motor speeds

### Sensor Processing

- **High-frequency sensor reading** for real-time response
- **Digital filtering** for noise reduction
- **Sensor calibration** routines for optimal performance

## Software Architecture

The code is developed using the **Raspberry Pi Pico C/C++ SDK** and organized into modular functions:

- **Setup:** Initialize sensors, calibrate systems, configure communication
- **Main Loop:** Read sensors, calculate control outputs, update motors
- **ISR:** Handle RC input and real-time control tasks

## Test Code Included

- **MPU-6050 self-test:** Sensor validation and calibration
- **ESC PWM calibration:** Motor controller setup and testing
- **GPS communication:** UART protocol testing and data parsing

## Flight Characteristics

- **Programmable flight parameters** via RC control ranges
- **Configurable PID gains** for different flight characteristics
- **Safety features** including failsafe modes
- **Real-time telemetry** for flight monitoring

## Documentation

Complete hardware schematics and wiring diagrams are included showing:

- Power distribution system
- Sensor connections and pin assignments
- ESC wiring configuration
- RC receiver integration
