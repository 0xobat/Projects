# Spydar — FPV Quadcopter

Embedded C project targeting Raspberry Pi Pico (RP2040) with Pico SDK.

## Tech Stack

- **Language:** C
- **SDK:** Raspberry Pi Pico SDK
- **Build:** CMake
- **Target:** RP2040 (ARM Cortex-M0+)
- **Toolchain:** arm-none-eabi-gcc

## Source Layout

- `pico_src/` — Main Pico C source code
  - `sensors/` — GPS, IMU (MPU), motor control, RC control modules
  - `CMakeLists.txt` — Build configuration
- `archive/` — Legacy Arduino sketches (reference only)
- `datasheet/` — Hardware documentation

## Building

```bash
cd pico_src/build
cmake ..
make
```

## Agent Harness

This project uses the harness convention. See `harness/` directory:

- `harness/init.sh` — Check build tools are available
- `harness/verify.sh` — Verify source files and build config
- `harness/features.json` — Feature inventory with pass/fail status
- `harness/progress.txt` — Read this first to see what previous sessions did
