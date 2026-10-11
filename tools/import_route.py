from pathlib import Path
import pcbnew as p
r=Path(__file__).resolve().parents[1]
b=p.LoadBoard(str(r/'hardware/counter.kicad_pcb'))
assert p.ImportSpecctraSES(b,str(r/'validation/routed.ses'))
p.SaveBoard(str(r/'hardware/counter.kicad_pcb'),b)
print('Imported routes. Run DRC with schematic parity before export.')
