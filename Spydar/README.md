# Project Spydar - FPV Quadcopter

A 5-inch FPV quadcopter build featuring digital FPV system, GPS navigation, and autonomous flight capabilities.

## Project Overview

This quadcopter project implements:

- **FPV freestyle flight** with DJI O4 digital video transmission
- **Remote control operation** via Remote Controller
- **Stabilized flight modes** using Betaflight flight controller
- **GPS navigation** capabilities for position hold and waypoint missions

## System Architecture

### Control System

- **Flight Controller:** SpeedyBee F7 V3 BL32 Flight Controller (30x30mm stack)
- **ESC:** Integrated 50A BLHeli_32 4-in-1 ESC
- **Flight Firmware:** Betaflight
- **Control Algorithms:**
  - PID controllers for attitude stabilization (roll, pitch, yaw)
  - GPS rescue and position hold modes
  - Multiple flight modes: Acro, Angle, Horizon
- **Remote Control:** DJI FPV Remote Controller 3 with S.Bus protocol

### Hardware Components

#### Frame

- **SpeedyBee Master 5 V2:** 5-inch freestyle frame with quick-release arms
- **Weight:** ~140g frame kit
- **Mounting:** 30.5x30.5mm and 20x20mm FC patterns

#### FPV System

- **Goggles:** DJI Goggles N3 with O4 video transmission
- **Air Unit:** DJI O4 Air Unit for digital HD video
- **Remote:** DJI FPV Remote Controller 3

#### Sensors

- **IMU:** Built-in gyroscope and accelerometer on F7 flight controller
- **GPS Module:** Ublox NEO-6M for navigation and position hold
- **Barometer:** Built-in on F7 flight controller

#### Propulsion System

- **Motors:** 4x Axisflying 2207 1960KV brushless motors
- **Propellers:** HQProp Ethix S5 5x4x3 tri-blade props (16 props: 8 CW, 8 CCW)
- **Power Distribution:** Integrated on ESC stack

#### Power System

- **Battery:** SUNPADOW 6S LiPo 22.2V 1400mAh
- **Charger:** LiPo balance charger
- **Connector:** XT60

## Configuration

### Flight Controller Setup

- **Firmware:** Betaflight (latest stable)
- **Receiver Protocol:** S.Bus from DJI FPV Remote Controller 3
- **GPS:** UART connection to NEO-6M module
- **ESC Protocol:** DShot600 or DShot300
- **Blackbox Logging:** Enabled via micro SD card

### DJI System Binding

- Bind DJI O4 Air Unit to Goggles N3
- Bind DJI FPV Remote Controller 3 to Goggles N3
- Configure audience mode if needed

## Flight Features

### Flight Modes

- **Acro Mode:** Full manual control for freestyle flying
- **Angle Mode:** Self-leveling mode for beginners
- **Horizon Mode:** Mix of acro and angle modes
- **GPS Rescue:** Automated return to home on signal loss

### Betaflight Features

- **PID Tuning:** Customizable PID gains for different flight characteristics
- **OSD (On-Screen Display):** Real-time telemetry via DJI goggles
- **Blackbox Logging:** Flight data recording for analysis and tuning
- **GPS Navigation:** Position hold and waypoint missions

## Software Setup

The quadcopter uses **Betaflight** firmware configured via Betaflight Configurator:

- **Initial Setup:** Flash Betaflight firmware to SpeedyBee F7 V3
- **Configuration:** Set up motor outputs, receiver, and GPS
- **Calibration:** Accelerometer calibration and ESC calibration
- **PID Tuning:** Adjust PIDs for stable flight
- **OSD Setup:** Configure on-screen display elements

## Assembly Notes

- Frame comes with comprehensive hardware kit including screws, standoffs, and TPU parts
- GPS mount (181 base) included for NEO-6M module
- Battery straps (2x 250mm) included
- Anti-vibration mounts for camera and flight controller stack

## Build Specifications

- **Frame Size:** 5-inch (220mm diagonal)
- **Weight:** ~450-500g (estimated dry weight)
- **Battery:** 6S 1400mAh (~150g)
- **Flight Time:** 4-6 minutes (estimated)
- **Top Speed:** 100+ km/h (depends on tuning)
- **Video System:** DJI O4 digital HD transmission

## Documentation

See [Parts.md](Parts.md) for complete parts list with purchase links.

Additional resources:

- Betaflight configuration backup
- GPS module wiring and setup
- DJI system binding procedures
- PID tuning guides
