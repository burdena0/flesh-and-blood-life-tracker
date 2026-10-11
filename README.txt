COMPACT CL3641AH LIFE / MANA / RESOURCE COUNTER - REV E1
2026-10-02

CURRENT COMPACT PCB
70 x 80 mm bounding outline, two copper layers, 1.6 mm FR4. The top notch
leaves the S3-Zero ceramic antenna over air. The bounding area is 44% less
than the previous 100 x 100 mm carrier. This does not describe battery/case size.

Use a genuine Waveshare ESP32-S3-Zero or ESP32-S3-Zero-M (headers fitted),
4 MB flash / 2 MB PSRAM, 18 x 23.5 mm body. Fit two 1x9 female socket strips
on the carrier, 15.24 mm apart. USB-C faces DOWN into the board; antenna UP.
The module's two 9-pin headers are sufficient. Its underside pads are unused.
Buy: https://www.waveshare.com/esp32-s3-zero.htm
Official documentation: https://docs.waveshare.com/ESP32-S3-Zero

The new raw display is CL3641AH, 30 x 14 mm, 12 pins, COMMON CATHODE.
Its pin rows are 10.16 mm apart, six pins per row at 2.54 mm pitch.
The older 5641AS footprint (15.24 mm rows) DOES NOT fit this display.
Display decimal points face the lower board edge; pin 1 is bottom-left.
The display pin numbers agree electrically with the old display, but the
compact board uses a different ESP32 GPIO map and one SN74HC595N.

NORMAL ESP32 BREADBOARD IS A SEPARATE BUILD
Your original 30-pin ESP32 uses the direct-drive firmware and no shift chip:
../breadboard-5641as/docs/cl3641ah/solderless-830-layout.png
../breadboard-5641as/docs/cl3641ah/solderless-830-wired.png
../breadboard-5641as/docs/cl3641ah/solderless-830-instructions.txt
../breadboard-5641as/platformio.ini
Do not upload the compact S3 firmware to the original ESP32.

NEW PARTS FOR THIS COMPACT PCB
- Waveshare ESP32-S3-Zero-M (or solder 2x9 male pins to the plain version).
- SN74HC595N, 16-pin through-hole DIP; optional 16-pin DIP socket.
  Use HC at 3.3V, not HCT or a 5V-only substitute.
- Two 1x9 female headers for the S3-Zero.
- One additional 100nF ceramic capacitor, C3, beside U1.
Reuse the CL3641AH, four 2N3904, four two-prong buttons, three red LEDs,
15 x 1k and 8 x 10k resistors, 100nF C1 and 10uF C2. Full BOM: manufacturing/bom.csv.
R21-R23 stand vertically on 2.54mm lead spacing; the other resistors lie flat
on 7.62mm spacing. Keep folded resistor leads insulated from nearby parts.

GPIO MAP - COMPACT S3 ONLY
74HC595 SER pin14 = GPIO43; SRCLK pin11 = GPIO1; RCLK pin12 = GPIO2.
74HC595 VCC pin16 and /SRCLR pin10 = 3V3; GND pin8 and /OE pin13 = GND.
QH' pin9 is unused. QA..QH pins15/1/2/3/4/5/6/7 feed R1..R8 then A..DP.
CL3641AH A/B/C/D/E/F/G/DP pins = 11/7/4/2/1/10/5/3.
Digit 1/2/3/4 cathode pins = 12/9/8/6, through Q1/Q2/Q3/Q4 to GND.
Digit base GPIOs = 4/5/6/7, each through 1k, with 10k base-emitter pull-down.
Minus/Select/Plus/Resource = GPIO8/9/10/11, each 10k pull-up to 3V3.
Resource LEDs 1/2/3 = GPIO12/13/44, each through 1k; cathodes to GND.
GPIO3 and all boot straps are unused. USB GPIO19/20 remain dedicated to USB.
UART0 GPIO43/44 are repurposed, so console/programming uses native USB.
Onboard RGB GPIO21 and PSRAM are unused. No wireless task is started.

ASSEMBLY
1. Print docs/fit-check.pdf at 100%, disable page scaling; measure its ruler.
   Check both display pin rows and both module header rows against your parts.
2. Solder resistors and socket(s). U1 notch faces UP; pin1 is upper-left.
3. Fit C1/C3 (100nF ceramic, either direction). C2 is 10uF, >=10V:
   positive to square pad, negative stripe to the round GND pad.
4. Fit Q1-Q4, flat face toward the LOWER edge. E/B/C are left-to-right for
   the standard onsemi 2N3904 TO-92 pinout. The board labels every terminal.
5. LED cathodes (short leg/flat edge) go to square pad1, left; anodes right.
6. Insert CL3641AH with decimal points DOWN. Digit commons must not be tied
   directly to ground: Q1-Q4 switch them individually.
7. Four two-prong buttons: square pad is signal; choose ONE round GND pad
   at 2.54 or 5.08mm, or use short wires to the same pads. Both round pads
   are ground, so a button across only those two pads will not work.
8. Insert S3-Zero with USB-C DOWN and antenna UP over the notch. Headers
   hold the module above the carrier; do not solder underside test pads.
9. With USB unplugged, inspect for bridges and check 3V3-to-GND resistance.
   Connect USB only after orientation and pin labels agree with the template.

FIRMWARE / PLATFORMIO
Open compact-cl3641ah/firmware in VS Code + PlatformIO. The default s3zero
environment is native ESP-IDF 5.4.0 on espressif32@6.10.0, with FreeRTOS.
Run pio run, pio run -t upload, then pio device monitor (115200).
For first flash, hold the board's BOOT button while plugging in USB-C, then
release BOOT and upload. If several devices are attached, set upload_port
and monitor_port to the S3's COM port. No device was flashed by this session.
The board profile fixes 4MB flash. PSRAM is deliberately unused.

The input task debounces buttons and queues events; the state task owns the
game state; an ESP timer task scans the digits at 2ms each. Each scan disables
all digits, waits 3us, shifts eight bits MSB-first, latches once, then enables
one digit. A critical section makes frame updates coherent. Startup clears
the shift-register output while digit transistors remain off. Host tests
cover game behavior and an independent rising-edge model of all 256 bytes.
USB Serial/JTAG carries logs, leaving GPIO43/44 available to the circuit.

CONTROLS
Choose 20 or 40 life, then enable/disable mana. Select changes player;
minus/plus edit the active life or mana total. Hold Select 1.2s for menus
(resume, life/mana, undo, clear mana, reset). Resource cycles 0-1-2-3-0 for
the selected player; the three LEDs show that player's count. Player 2's
two digits rotate in software. State is RAM-only and is lost on power-off.
Hold Select during reset to run the display and three-LED self-test.

POWER AND BATTERY
Power/program through the S3-Zero USB-C socket. The previous external USB-C
LiPo charger + protected output + 5V USB boost solution remains compatible;
use a USB-A to USB-C data/power cable. See docs/LIPO-POWER.txt.
The carrier and S3-Zero do not contain a battery charger. Disconnect the
boost/load while charging with the selected TP4056; it has no load sharing.
Do not connect a raw LiPo directly to the carrier's 3V3 or the raw display.
This revision does not add haptics, an enclosure or a metal plate.

MANUFACTURING
Open hardware/counter.kicad_pro in KiCad 10. Upload ONLY
../compact-cl3641ah-gerbers.zip for the new bare PCB. Select FR4, 2 layers,
70 x 80 mm bounding size, 1.6mm thickness, 1oz copper and standard mask/finish.
The preview must show the top antenna notch, 18 module header holes, 12
display holes, a DIP16 footprint, four button groups and three LEDs.
Get a delivered quote before paying. No order or purchase was placed.
The older 5641AS and integrated revision-D order files target other hardware.

VALIDATION AND LIMITS
validation/release-check.txt records current DRC/ERC/parity, circuit/netlist,
mechanical geometry, firmware build, host tests and package integrity checks.
The fit PDF comes from the final pad coordinates. No physical prototype,
brightness, button fit, RF performance or battery runtime has been tested.
1k segment resistors limit current to roughly 1mA peak; brightness is modest
at 1/4 duty and also depends on the HC595 output drop. Test one prototype.

REBUILD
KiCad Python: tools/build_board.py then tools/build_schematic.py.
Export the XML schematic netlist; run tools/prepare_route.py, Freerouting on
validation/prepared.dsn, then tools/import_route.py. Run tools/export.ps1
for fresh DRC/ERC and exports. Run tools/make_fit_sheet.py, render_previews.py,
and check_release.py. Builds overwrite generated files. Never order unrouted CAD.
Firmware: pio run in firmware/. Host tests: CMake/Ninja in firmware/tests/;
run CTest FROM its build directory. Normal-ESP32 firmware stays separate.

SOURCES
https://www.xlitx.com/datasheet/CL3641AH.pdf
https://docs.waveshare.com/ESP32-S3-Zero/Resources-And-Documents
https://files.waveshare.com/wiki/ESP32-S3-Zero/ESP32-S3-Zero-Sch.pdf
https://files.waveshare.com/wiki/ESP32-S3-Zero/ESP32-S3-Zero-2D-size.jpg
https://www.ti.com/lit/ds/symlink/sn74hc595.pdf
https://www.onsemi.com/pdf/datasheet/2n3903-d.pdf
