# Flesh and Blood life tracker

Current compact E1 source snapshot of a personal two-player tabletop life/resource
counter project. The counter supports selectable 20/40 starting life, undo, reset
confirmation and resource tracking. It is intended for Flesh and Blood and can also
be used as a game-neutral counter; no game artwork or logos are included.

## Current hardware and firmware

- ESP32-S3-Zero module, native ESP-IDF/FreeRTOS through PlatformIO.
- CL3641AH four-digit common-cathode display and SN74HC595 shift register.
- Debounced button events, state ownership, multiplexed display updates and resource LEDs.
- 70 x 80 mm two-layer KiCad carrier board with editable schematic, footprints and BOM.
- Host tests for game-state and shift-register behavior.

Read `README.txt` for the exact GPIO map, parts and assembly instructions. Build from
`firmware` with PlatformIO. Host test sources and CMake configuration are in
`firmware/tests`. The complete original workspace also contains historical Pico,
normal-ESP32 and older carrier variants; they are intentionally not mixed into this
current revision snapshot. Paths in historical prose may refer to those excluded
variants. Do not substitute their pin maps for the compact S3 board.

## Validation status

This repository preserves the current design and source. PCB/firmware reports describe
digital verification only. Physical fabrication, assembly, display behavior, battery
operation and fit require real-device tests and are not claimed here.
