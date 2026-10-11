from pathlib import Path
import xml.etree.ElementTree as ET
import pcbnew as p
r=Path(__file__).resolve().parents[1]
b=p.LoadBoard(str(r/'hardware/counter.kicad_pcb'))
fp={f.GetReference():f for f in b.GetFootprints()}
old={n.GetNetname():n for _,n in b.GetNetsByName().items()}
for elem in ET.parse(r/'validation/netlist.xml').findall('.//nets/net'):
    name=elem.attrib['name'];n=old.get(name.lstrip('/'))
    if n:n.SetNetname(name)
    else:n=p.NETINFO_ITEM(b,name);b.Add(n)
    for node in elem.findall('node'):
        for pad in fp[node.attrib['ref']].Pads():
            if pad.GetNumber()==node.attrib['pin']:pad.SetNet(n)
p.SaveBoard(str(r/'hardware/counter.kicad_pcb'),b)
assert p.ExportSpecctraDSN(b,str(r/'validation/prepared.dsn'))
print('Synchronized exported schematic nets and wrote routing input.')
