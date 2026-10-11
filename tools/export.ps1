$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$cli = 'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe'
New-Item -ItemType Directory -Force "$projectRoot/docs", "$projectRoot/manufacturing/gerbers" | Out-Null
& $cli pcb drc --format json --schematic-parity --exit-code-violations -o "$projectRoot/validation/drc.json" "$projectRoot/hardware/counter.kicad_pcb"
if ($LASTEXITCODE -ne 0) { throw 'PCB DRC/parity failed; do not export.' }
& $cli sch erc --format json --exit-code-violations -o "$projectRoot/validation/erc.json" "$projectRoot/hardware/counter.kicad_sch"
if ($LASTEXITCODE -ne 0) { throw 'Schematic ERC failed; do not export.' }
& $cli sch export netlist --format kicadxml -o "$projectRoot/validation/netlist.xml" "$projectRoot/hardware/counter.kicad_sch"
& $cli sch export pdf -o "$projectRoot/docs/schematic.pdf" "$projectRoot/hardware/counter.kicad_sch"
& $cli pcb export gerbers --layers 'F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts' --subtract-soldermask -o "$projectRoot/manufacturing/gerbers/" "$projectRoot/hardware/counter.kicad_pcb"
& $cli pcb export drill --format excellon --excellon-units mm --excellon-separate-th -o "$projectRoot/manufacturing/gerbers/" "$projectRoot/hardware/counter.kicad_pcb"
& $cli pcb export svg --layers 'F.Cu,F.SilkS,Edge.Cuts' --mode-single --fit-page-to-board --exclude-drawing-sheet -o "$projectRoot/docs/pcb-top.svg" "$projectRoot/hardware/counter.kicad_pcb"
& $cli pcb export svg --layers 'B.Cu,Edge.Cuts' --mirror --mode-single --fit-page-to-board --exclude-drawing-sheet -o "$projectRoot/docs/pcb-back.svg" "$projectRoot/hardware/counter.kicad_pcb"
& $cli pcb export svg --layers 'F.Fab,F.SilkS,Edge.Cuts' --black-and-white --sketch-pads-on-fab-layers --mode-single --fit-page-to-board --exclude-drawing-sheet -o "$projectRoot/docs/assembly-top.svg" "$projectRoot/hardware/counter.kicad_pcb"
if ($LASTEXITCODE -ne 0) { throw 'Export failed.' }
