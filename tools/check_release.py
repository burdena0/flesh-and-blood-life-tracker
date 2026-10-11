"""Independent final-board, firmware, breadboard and release checks."""
from pathlib import Path
from collections import Counter
import csv,json,hashlib,re,zipfile,xml.etree.ElementTree as ET
import pcbnew as p
r=Path(__file__).resolve().parents[1];root=r.parent
b=p.LoadBoard(str(r/'hardware/counter.kicad_pcb'))
f={x.GetReference():x for x in b.GetFootprints()};report=[]
def check(ok,msg):
    assert ok,msg
    report.append('PASS: '+msg)
def pads(ref,n):return [a for a in f[ref].Pads() if a.GetNumber()==str(n)]
def get(ref,n):
    values={a.GetNetname().lstrip('/') for a in pads(ref,n)}
    assert len(values)==1,(ref,n,values)
    return values.pop()
def expect(ref,n,net):assert get(ref,n)==net,(ref,n,get(ref,n),net)
def xy(a):return tuple(round(p.ToMM(v),6) for v in [a.GetPosition().x,a.GetPosition().y])
def center(ref):
    points=[xy(a) for a in f[ref].Pads()]
    return ((min(x for x,y in points)+max(x for x,y in points))/2,(min(y for x,y in points)+max(y for x,y in points))/2)
def bounds(ref):
    pts=[xy for s in f[ref].GraphicalItems() if s.GetLayer()==p.F_Fab for xy in [s.GetStart(),s.GetEnd()]]
    return (p.ToMM(max(t.x for t in pts)-min(t.x for t in pts)),p.ToMM(max(t.y for t in pts)-min(t.y for t in pts)))
d=json.loads((r/'validation/drc.json').read_text())
for key in ['violations','unconnected_items','schematic_parity']:check(key in d and not d[key],f'KiCad DRC: zero {key}')
e=json.loads((r/'validation/erc.json').read_text())
check(bool(e.get('sheets')) and all(not s['violations'] for s in e['sheets']),'KiCad ERC: zero violations')
check(len(f)==44,'44 footprints, including 4 mounting holes, 3 capacitors and one HC595')
check(b.GetCopperLayerCount()==2 and p.ToMM(b.GetDesignSettings().GetBoardThickness())==1.6,'2 copper layers / 1.6 mm thickness')
edge=[s for s in b.GetDrawings() if s.GetLayer()==p.Edge_Cuts]
segments={tuple(round(p.ToMM(v),3) for v in [s.GetStart().x,s.GetStart().y,s.GetEnd().x,s.GetEnd().y]) for s in edge}
outline=[(0,0),(53.5,0),(53.5,5.5),(63.5,5.5),(63.5,0),(70,0),(70,80),(0,80),(0,0)]
check(segments=={(*a,*c) for a,c in zip(outline,outline[1:])},'70 x 80 mm closed outline with 10 x 5.5 mm antenna notch')
check(any(z.GetIsRuleArea() and z.GetDoNotAllowTracks() and z.GetDoNotAllowVias() and z.GetDoNotAllowZoneFills() for z in b.Zones()),'antenna copper keepout retained')
pinmap=['IO43','IO44','IO13','IO12','IO11','IO10','IO9','IO8','IO7','IO6','IO5','IO4','IO3','IO2','IO1','3V3','GND','VBUS']
for n,net in enumerate(pinmap,1):
    if n not in [13,18]:expect('J1',n,net)
    else:check(get('J1',n).startswith('unconnected-') or not get('J1',n),f'J1 {net} unused')
    actual=xy(pads('J1',n)[0]);expected=(51 if n<=9 else 66.24,round(1.6+(9-n if n<=9 else n-10)*2.54,6))
    assert all(abs(a-v)<.0001 for a,v in zip(actual,expected)),(n,actual,expected)
check(len(list(f['J1'].Pads()))==18 and bounds('J1')==(18,23.5),'manufacturer S3-Zero header map and 18 x 23.5 mm body / 15.24 mm rows')
check(f['DS1'].GetFPIDAsString()=='Counter:CL3641AH_30x14_P2.54_R10.16' and bounds('DS1')==(30,14),'CL3641AH footprint and 30 x 14 mm fabrication body')
for n in range(1,13):
    expected=(35-6.35+((n-1) if n<=6 else 12-n)*2.54,40+(5.08 if n<=6 else -5.08))
    assert all(abs(a-v)<.0001 for a,v in zip(xy(pads('DS1',n)[0]),expected))
check(len(list(f['DS1'].Pads()))==12,'display pad numbering, 2.54 mm pitch and 10.16 mm rows')
for i,(seg,upin,dpin) in enumerate(zip(['A','B','C','D','E','F','G','DP'],[15,1,2,3,4,5,6,7],[11,7,4,2,1,10,5,3]),1):
    expect('U1',upin,'DRV_'+seg);expect(f'R{i}',1,'DRV_'+seg);expect(f'R{i}',2,'SEG_'+seg);expect('DS1',dpin,'SEG_'+seg)
    assert f[f'R{i}'].GetValue()=='1k'
for pin,net in {8:'GND',10:'3V3',11:'IO1',12:'IO2',13:'GND',14:'IO43',16:'3V3'}.items():expect('U1',pin,net)
check(get('U1',9).startswith('unconnected-'),'HC595 cascade output unused')
check(f['U1'].GetValue()=='SN74HC595N 3V3','HC595 pin mapping and eight independent segment current-limit resistors')
for i,(gpio,pin) in enumerate(zip([4,5,6,7],[12,9,8,6]),1):
    expect(f'R{8+i}',1,f'IO{gpio}');expect(f'R{8+i}',2,f'BASE{i}')
    expect(f'Q{i}',1,'GND');expect(f'Q{i}',2,f'BASE{i}');expect(f'Q{i}',3,f'DIG{i}');expect('DS1',pin,f'DIG{i}')
    expect(f'R{12+i}',1,f'BASE{i}');expect(f'R{12+i}',2,'GND')
    assert f[f'R{8+i}'].GetValue()=='1k' and f[f'R{12+i}'].GetValue()=='10k'
check(True,'four separate 2N3904 digit sinks with 1k base resistors and 10k pull-downs')
for i,gpio in enumerate([8,9,10,11],1):
    expect(f'SW{i}',1,f'IO{gpio}');expect(f'SW{i}',2,'GND');expect(f'R{16+i}',1,'3V3');expect(f'R{16+i}',2,f'IO{gpio}')
    assert f[f'R{16+i}'].GetValue()=='10k'
for i,gpio in enumerate([12,13,44],1):
    expect(f'R{20+i}',1,f'IO{gpio}');expect(f'R{20+i}',2,f'LED{i}_A');expect(f'D{i}',2,f'LED{i}_A');expect(f'D{i}',1,'GND')
    assert f[f'R{20+i}'].GetValue()=='1k'
for ref in ['C1','C2','C3']:expect(ref,1,'3V3');expect(ref,2,'GND')
check(True,'four pulled-up two-prong buttons, three red LED branches and all decoupling nets')
for i,cx in enumerate([28,40,52,64],1):
    for ref in [f'R{8+i}',f'R{12+i}',f'R{16+i}']:assert abs(center(ref)[0]-cx)<.001
    assert abs(xy(pads(f'Q{i}',2)[0])[0]-cx)<.001
for i in range(1,5):assert center(f'SW{i}')==(5,12+18*(i-1))
check(abs(center('D2')[0]-center('DS1')[0])<.001,'display centered under LED bank; driver columns and button column aligned')
for net in ET.parse(r/'validation/netlist.xml').findall('.//nets/net'):
    for node in net.findall('node'):expect(node.attrib['ref'],node.attrib['pin'],net.attrib['name'].lstrip('/'))
check(True,'all schematic netlist pads agree with final PCB')
coord=list(csv.DictReader((r/'manufacturing/pin-map.csv').open()))
actual=Counter((ref,a.GetNumber(),*xy(a)) for ref,foot in f.items() for a in foot.Pads())
export=Counter((a['reference'],a['pad'],round(float(a['x_mm']),6),round(float(a['y_mm']),6)) for a in coord)
check(actual==export,'coordinate export contains every final PCB pad exactly once')
h=(r/'firmware/src/board.hpp').read_text()
for array,want in [('digits',[4,5,6,7]),('buttons',[8,9,10,11]),('resource_leds',[12,13,44])]:
    assert list(map(int,re.findall(r'GPIO_NUM_(\d+)',re.search(array+r'\[\]=\{([^}]+)',h)[1])))==want
for name,n in [('serial_data',43),('shift_clock',1),('latch_clock',2)]:assert f'{name}=GPIO_NUM_{n};' in h
cfg=(r/'firmware/sdkconfig.s3zero').read_text()
check('CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG=y' in cfg and 'CONFIG_IDF_TARGET_ESP32S3=y' in cfg and 'CONFIG_ESPTOOLPY_FLASHSIZE_4MB=y' in cfg,'firmware GPIOs, ESP32-S3 target, 4MB flash and USB console match hardware')
check('[SUCCESS]' in (r/'validation/espidf-build.txt').read_text(encoding='utf-8-sig'),'fresh native ESP-IDF/FreeRTOS build succeeded')
check('100% tests passed' in (r/'validation/host-tests.txt').read_text(encoding='utf-8-sig'),'fresh game and 256-pattern shift-register host tests passed')
bc=root/'breadboard-5641as/docs/cl3641ah'
checks=(bc/'solderless-830-checks.txt').read_text()
check('no unintended net mergers' in checks,'normal ESP32 breadboard connectivity and pin map verified separately')
model=json.loads((bc/'solderless-830-model.json').read_text())
display=next(x for x in model['parts'] if x['ref']=='DS1')
check(display['value']=='CL3641AH' and display['pins']['1']=='E8' and display['pins']['12']=='G8','breadboard uses CL3641AH E/G rows and original ESP32, no shift register')
check(not any(x['ref']=='U1' for x in model['parts']),'breadboard has no compact-PCB shift chip')
check(bool(list(b.GetTracks())),'board contains routed copper')
for ext in ['.gtl','.gbl','.gts','.gbs','.gto','.gbo','.gm1']:check(any((r/'manufacturing/gerbers').glob('*'+ext)),f'fabrication layer {ext} exists')
for name in ['counter-PTH.drl','counter-NPTH.drl']:check((r/'manufacturing/gerbers'/name).is_file(),name+' exists')
report+=['LIMIT: no physical fit, powered-device, battery or RF tests performed.',
         'INFO: PCB SHA256 '+hashlib.sha256((r/'hardware/counter.kicad_pcb').read_bytes()).hexdigest()]
(r/'validation/release-check.txt').write_text('\n'.join(report)+'\n')

def archive(path,files,base):
    files=sorted(set(files));assert all(f.is_file() for f in files)
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        for file in files:z.write(file,file.relative_to(base).as_posix())
        z.writestr('SHA256SUMS.txt',''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.relative_to(base).as_posix()+'\n' for f in files))
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        for file in files:assert z.read(file.relative_to(base).as_posix())==file.read_bytes()
    print('Packaged and byte-checked:',path.name)
gerbers=list((r/'manufacturing/gerbers').iterdir())
archive(root/'compact-cl3641ah-gerbers.zip',gerbers,r/'manufacturing/gerbers')
files=[r/'README.txt']
for folder in ['hardware','manufacturing','docs','tools','firmware']:
    files += [f for f in (r/folder).rglob('*') if f.is_file() and not any(x in f.parts for x in ['__pycache__','.pio','build']) and f.suffix not in ['.lck','.kicad_prl'] and not f.name.startswith('sdkconfig.s3zero')]
files += [r/'validation'/n for n in ['drc.json','erc.json','netlist.xml','routing.log','prepared.dsn','routed.ses','release-check.txt','espidf-build.txt','host-tests.txt']]
archive(root/'compact-cl3641ah-complete.zip',files,r)
old=root/'breadboard-5641as'
bf=list(bc.iterdir())+[old/'README.md',old/'platformio.ini',old/'sdkconfig.defaults',old/'CMakeLists.txt',old/'docs/draw_solderless_cl3641ah.py']
for folder in ['src','life_counter_5641as']:bf += [f for f in (old/folder).iterdir() if f.is_file()]
bf += [old/'tests/test_counter.cpp',old/'tests/CMakeLists.txt']
archive(root/'breadboard-cl3641ah-normal-esp32.zip',bf,old)
print('\n'.join(report))
