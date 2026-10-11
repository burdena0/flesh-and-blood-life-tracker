"""Editable labeled connectivity schematic with electrically typed module pins."""
from pathlib import Path
import json,uuid
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'hardware'
data=json.loads((OUT/'electrical.json').read_text());rootid=data['sheet_uuid']
uid=lambda:str(uuid.uuid4());q=lambda s:json.dumps(str(s))
defs=[];instances=[];wires=[]
for index,part in enumerate(data['parts']):
    ref=part['ref'];symbol_id='Counter:'+ref
    x=round((45+(index%6)*90)/1.27)*1.27;y=round((30+(index//6)*52)/1.27)*1.27
    pinlist=sorted(part['pins'].items(),key=lambda kv:int(kv[0]))
    half=(len(pinlist)+1)//2;height=max(7.62,half*2.54)
    symbolpins=[];endpoints=[]
    for j,(number,pin) in enumerate(pinlist):
        right=j>=half;local_y=-(j-half if right else j)*2.54
        local_x=20.32 if right else -20.32
        symbolpins.append(f'(pin {pin["type"]} line (at {local_x} {local_y} {180 if right else 0}) (length 5.08) (name {q(pin["name"])} (effects (font (size 1 1)))) (number {q(number)} (effects (font (size 1 1)))))')
        endpoints.append((number,x+local_x,y-local_y,right))
    defs.append(f'''(symbol {q(symbol_id)} (pin_names (offset 0.8)) (in_bom yes) (on_board yes)
      (property "Reference" {q(ref)} (at 0 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Value" {q(part['value'])} (at 0 2.54 0) (effects (font (size 1.1 1.1))))
      (symbol "{ref}_0_1" (rectangle (start -15.24 2.54) (end 15.24 {-height}) (stroke (width .254) (type default)) (fill (type background))))
      (symbol "{ref}_1_1" {''.join(symbolpins)}))''')
    instances.append(f'''(symbol (lib_id {q(symbol_id)}) (at {x} {y} 0) (unit 1) (in_bom {'no' if ref.startswith('H') else 'yes'}) (on_board yes) (dnp no) (uuid {q(part['uuid'])})
      (property "Reference" {q(ref)} (at {x} {y-8} 0) (effects (font (size 1.27 1.27))))
      (property "Value" {q(part['value'])} (at {x} {y-5} 0) (effects (font (size 1.1 1.1))))
      (property "Footprint" {q(part['footprint'])} (at {x} {y} 0) (effects (font (size 1 1)) hide))
      (instances (project "counter" (path "/{rootid}" (reference {q(ref)}) (unit 1)))))''')
    for number,px,py,right in endpoints:
        if number not in part['nets']:
            wires.append(f'(no_connect (at {px} {py}) (uuid "{uid()}"))');continue
        lx=px+(5.08 if right else -5.08)
        wires.append(f'(wire (pts (xy {px} {py}) (xy {lx} {py})) (stroke (width 0) (type default)) (uuid "{uid()}"))')
        wires.append(f'(label {q(part["nets"][number])} (at {lx} {py} {0 if right else 180}) (effects (font (size 1 1)) (justify left bottom)) (uuid "{uid()}"))')
text=f'''(kicad_sch (version 20250114) (generator "eeschema") (uuid "{rootid}") (paper "A2")
 (title_block (title "Compact S3 / CL3641AH counter") (rev "E1 prototype")
 (comment 1 "J1: Waveshare ESP32-S3-Zero, 15.24 mm rows. U1: SN74HC595N at 3.3V.")
 (comment 2 "Q: 1=E, 2=B, 3=C. DS1: common cathode. R: 1/4 W."))
 (lib_symbols {''.join(defs)}) {''.join(instances)} {''.join(wires)})'''
(OUT/'counter.kicad_sch').write_text(text,encoding='utf-8')
(OUT/'Counter.kicad_sym').write_text('(kicad_symbol_lib (version 20250114) (generator "kicad_symbol_editor") '+''.join(d.replace('"Counter:', '"') for d in defs)+')',encoding='utf-8')
(OUT/'sym-lib-table').write_text('(sym_lib_table (lib (name "Counter")(type "KiCad")(uri "${KIPRJMOD}/Counter.kicad_sym")(options "")(descr "Carrier connectivity symbols")))\n')
project={'meta':{'filename':'counter.kicad_pro','version':1},
 'board':{'design_settings':{'rules':{'min_clearance':.2,'min_track_width':.25,'min_via_diameter':.7,'min_through_hole_diameter':.3,'min_copper_edge_clearance':.5,'min_hole_clearance':.25}}},
 'net_settings':{'classes':[{'name':'Default','clearance':.2,'track_width':.3,'via_diameter':.7,'via_drill':.35}], 'meta':{'version':3}}}
(OUT/'counter.kicad_pro').write_text(json.dumps(project,indent=2))
print('Wrote schematic and project.')
