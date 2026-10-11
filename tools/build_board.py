"""Reproducible KiCad 10 carrier for the CL3641AH and a Waveshare ESP32-S3-Zero.
Run with KiCad's Python. The output must be routed and checked before release.
"""
from pathlib import Path
import json, uuid, csv
import pcbnew as p

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'hardware'
LIB=Path('C:/Program Files/KiCad/10.0/share/kicad/footprints')
CUSTOM=OUT/'Counter.pretty'; CUSTOM.mkdir(exist_ok=True)
B=p.BOARD(); B.SetCopperLayerCount(2)
B.GetDesignSettings().SetBoardThickness(p.FromMM(1.6))
uid=lambda:str(uuid.uuid4())
sheet=uid(); parts=[]; nets={}
vec=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def net(name):
    if name not in nets:
        nets[name]=p.NETINFO_ITEM(B,name);B.Add(nets[name])
    return nets[name]
def line(target,a,b,layer=p.F_SilkS,width=.15):
    s=p.PCB_SHAPE(target)
    s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(vec(*a));s.SetEnd(vec(*b))
    s.SetLayer(layer);s.SetWidth(p.FromMM(width));target.Add(s)
def rect(target,x1,y1,x2,y2,layer,width=.15):
    points=[(x1,y1),(x2,y1),(x2,y2),(x1,y2),(x1,y1)]
    for a,b in zip(points,points[1:]):line(target,a,b,layer,width)
def text(label,x,y,size=1,layer=p.F_SilkS):
    t=p.PCB_TEXT(B);t.SetText(label);t.SetPosition(vec(x,y));t.SetTextSize(vec(size,size))
    t.SetTextThickness(p.FromMM(.15));t.SetLayer(layer);B.Add(t)
def pad(f,num,x,y,diam=1.8,drill=1.0):
    a=p.PAD(f);a.SetNumber(str(num));a.SetPosition(vec(x,y));a.SetSize(vec(diam,diam))
    a.SetDrillSize(vec(drill,drill));a.SetAttribute(p.PAD_ATTRIB_PTH)
    a.SetShape(p.PAD_SHAPE_RECT if num==1 else p.PAD_SHAPE_CIRCLE)
    a.SetLayerSet(p.PAD.PTHMask());f.Add(a)
def custom(name):
    f=p.FOOTPRINT(B);f.SetFPIDAsString('Counter:'+name);f.SetAttributes(p.FP_THROUGH_HOLE);return f
def save_custom(f):
    p.PCB_IO_MGR.FindPlugin(p.PCB_IO_MGR.KICAD_SEXP).FootprintSave(str(CUSTOM),f)
def add(ref,value,foot,xy,connections,pin_names=None,angle=0,types=None):
    if isinstance(foot,str):
        lib,name=foot.split(':');f=p.FootprintLoad(str(LIB/(lib+'.pretty')),name)
        if f is None:raise ValueError(foot)
        f.SetFPIDAsString(foot)
    else:f=foot;foot=f.GetFPIDAsString()
    f.SetReference(ref);f.SetValue(value);f.Value().SetVisible(False)
    f.SetOrientationDegrees(angle);f.SetPosition(vec(*xy))
    f.Reference().SetTextSize(vec(.9,.9));f.Reference().SetTextThickness(p.FromMM(.15))
    # All references remain readable above their physical parts.
    f.Reference().SetPosition(vec(xy[0]+(3.81 if ref.startswith('R') else 0),xy[1]-2.4))
    f.Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
    identifier=uid();f.SetPath(p.KIID_PATH('/'+sheet+'/'+identifier))
    pins={}
    for a in f.Pads():
        n=a.GetNumber()
        if not n:continue
        pins[n]={'name':(pin_names or {}).get(n,n),'type':(types or {}).get(n,'passive')}
        if n in connections:a.SetNet(net(connections[n]))
    B.Add(f)
    parts.append(dict(ref=ref,value=value,footprint=foot,uuid=identifier,nets=connections,pins=pins))
    return f

# USB faces down, ceramic antenna faces the carrier's top notch.
# P15 numbering follows the Waveshare schematic. Header row spacing: 15.24 mm.
f=custom('Waveshare_ESP32_S3_Zero_USB_Down')
for i in range(9):
    pad(f,9-i,0,i*2.54);pad(f,10+i,15.24,i*2.54)
rect(f,-1.38,-1.59,16.62,21.91,p.F_Fab,.1)
rect(f,-1.88,-2.09,17.12,22.41,p.F_CrtYd,.05)
rect(f,-1.3,-1.3,1.3,21.62,p.F_SilkS)
rect(f,13.94,-1.3,16.54,21.62,p.F_SilkS);save_custom(f)
labels={str(i):v for i,v in enumerate(['IO43','IO44','IO13','IO12','IO11','IO10','IO9','IO8','IO7','IO6','IO5','IO4','IO3','IO2','IO1','3V3','GND','VBUS'],1)}
connections={i:n for i,n in labels.items() if n not in ['IO3','VBUS']}
types={i:('power_out' if n=='3V3' else 'passive' if n in ['GND','VBUS','IO3'] else 'input' if n in ['IO8','IO9','IO10','IO11'] else 'output') for i,n in labels.items()}
j=add('J1','Waveshare ESP32-S3-Zero',f,(51,1.6),connections,labels,types=types)
j.Reference().SetPosition(vec(58.62,25.1))
for i in range(9):
    text(labels[str(9-i)].replace('IO',''),48.3 if i<2 else 54,1.6+i*2.54,.8)
    text(labels[str(10+i)].replace('IO',''),68.8 if i<2 else 63.2,1.6+i*2.54,.8)
text('USB-C DOWN',59,28,.8)

f=custom('CL3641AH_30x14_P2.54_R10.16')
for i in range(6):
    pad(f,i+1,-6.35+2.54*i,5.08,1.7,.9)
    pad(f,12-i,-6.35+2.54*i,-5.08,1.7,.9)
rect(f,-15.25,-7.25,15.25,7.25,p.F_SilkS)
rect(f,-15.5,-7.5,15.5,7.5,p.F_CrtYd,.05)
rect(f,-15,-7,15,7,p.F_Fab,.1);save_custom(f)
dpins={'11':'A','7':'B','4':'C','2':'D','1':'E','10':'F','5':'G','3':'DP','12':'DIG1','9':'DIG2','8':'DIG3','6':'DIG4'}
d=add('DS1','CL3641AH common cathode',f,(35,40),{n:'SEG_'+v if len(v)<3 else v for n,v in dpins.items()},dpins)
d.Reference().SetPosition(vec(35,39))
text('P1',25,38,.8);text('P2 ROTATED',44,38,.8);text('DOTS DOWN',35,42,.8)

# QA..QH drive A..DP at 3V3 through individual 1k resistors.
outputs=[15,1,2,3,4,5,6,7]
unets={str(pin):'DRV_'+seg for pin,seg in zip(outputs,['A','B','C','D','E','F','G','DP'])}
unets.update({'8':'GND','10':'3V3','11':'IO1','12':'IO2','13':'GND','14':'IO43','16':'3V3'})
unames={str(pin):'Q'+chr(65+i) for i,pin in enumerate(outputs)}
unames.update({'8':'GND','9':'QH_SERIAL','10':'SRCLR_N','11':'SRCLK','12':'RCLK','13':'OE_N','14':'SER','16':'VCC'})
utypes={str(pin):'output' for pin in outputs+[9]}
utypes.update({str(pin):'input' for pin in [10,11,12,13,14]});utypes.update({'8':'passive','16':'power_in'})
u=add('U1','SN74HC595N 3V3','Package_DIP:DIP-16_W7.62mm',(12,52),unets,unames,types=utypes)
u.Reference().SetPosition(vec(15.81,49.5))
R='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal'
for i,seg in enumerate(['A','B','C','D','E','F','G','DP']):
    cx=[25,40][i%2];y=4.5+(i//2)*4.5
    add(f'R{i+1}','1k',R,(cx-3.81,y),{'1':'DRV_'+seg,'2':'SEG_'+seg})
driver_centers=[28,40,52,64]
for i,(gpio,cx) in enumerate(zip([4,5,6,7],driver_centers),1):
    rb=add(f'R{8+i}','1k',R,(cx-3.81,54),{'1':f'IO{gpio}','2':f'BASE{i}'});rb.Reference().SetPosition(vec(cx,56.4))
    q=add(f'Q{i}','2N3904','Package_TO_SOT_THT:TO-92_Inline',(cx-1.27,60),{'1':'GND','2':f'BASE{i}','3':f'DIG{i}'},{'1':'E','2':'B','3':'C'})
    q.Reference().SetPosition(vec(cx+4.5,60));text('E B C',cx,63,.8)
    rr=add(f'R{12+i}','10k',R,(cx-3.81,66),{'1':f'BASE{i}','2':'GND'});rr.Reference().SetPosition(vec(cx,68.3))
    add(f'R{16+i}','10k',R,(cx-3.81,72),{'1':'3V3','2':f'IO{7+i}'})
for i,(gpio,y,name) in enumerate(zip([8,9,10,11],[12,30,48,66],['MINUS','SELECT','PLUS','RESOURCE']),1):
    f=custom('Switch_2wire_2.54_or_5.08')
    pad(f,1,0,0);pad(f,2,2.54,0);pad(f,2,5.08,0)
    rect(f,-1.5,-3,6.58,3,p.F_CrtYd,.05);rect(f,-1.2,-2.5,6.28,2.5,p.F_SilkS);save_custom(f)
    sw=add(f'SW{i}',name+' two-prong',f,(2.46,y),{'1':f'IO{gpio}','2':'GND'})
    sw.Reference().SetPosition(vec(5,y-4));text(name,5,y+5,.8)
for i,(gpio,cx) in enumerate(zip([12,13,44],[25,35,45]),1):
    d=add(f'D{i}','RED','LED_THT:LED_D5.0mm',(cx-1.27,28.5),{'1':'GND','2':f'LED{i}_A'},{'1':'K','2':'A'})
    d.Reference().SetPosition(vec(cx+3.8,28.5))
    rr=add(f'R{20+i}','1k','Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical',(cx-1.27,22.5),{'1':f'IO{gpio}','2':f'LED{i}_A'});rr.Reference().SetPosition(vec(cx-4.2,22.5))
c=add('C1','100n','Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm',(54.5,30),{'1':'3V3','2':'GND'});c.Reference().SetPosition(vec(57,32.5))
c=add('C2','10u 10V','Capacitor_THT:CP_Radial_D5.0mm_P2.00mm',(59,40),{'1':'3V3','2':'GND'},{'1':'+','2':'-'});c.Reference().SetPosition(vec(60,36.5))
c=add('C3','100n','Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm',(24,50.5),{'1':'3V3','2':'GND'});c.Reference().SetPosition(vec(31.7,50.5))
for i,xy in enumerate([(4,4),(66,30),(4,76),(66,77)],1):add(f'H{i}','M3','MountingHole:MountingHole_3.2mm_M3',xy,{})
text('CL3641AH / S3-ZERO / E1',36,77.5,.85)
outline=[(0,0),(53.5,0),(53.5,5.5),(63.5,5.5),(63.5,0),(70,0),(70,80),(0,80),(0,0)]
for a,b in zip(outline,outline[1:]):line(B,a,b,p.Edge_Cuts,.05)
z=p.ZONE(B);z.SetIsRuleArea(True)
layers=p.LSET();layers.AddLayer(p.F_Cu);layers.AddLayer(p.B_Cu);z.SetLayerSet(layers)
z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowZoneFills(True)
poly=z.Outline();poly.NewOutline()
for x,y in [(53.5,0),(63.5,0),(63.5,8),(53.5,8)]:poly.Append(p.FromMM(x),p.FromMM(y))
B.Add(z)
settings=B.GetDesignSettings().m_NetSettings
default=settings.GetDefaultNetclass();default.SetClearance(p.FromMM(.2));default.SetTrackWidth(p.FromMM(.3))
default.SetViaDiameter(p.FromMM(.7));default.SetViaDrill(p.FromMM(.35))
p.SaveBoard(str(OUT/'counter.kicad_pcb'),B)
(OUT/'electrical.json').write_text(json.dumps({'sheet_uuid':sheet,'parts':parts},indent=2))
(OUT/'fp-lib-table').write_text('(fp_lib_table (lib (name "Counter")(type "KiCad")(uri "${KIPRJMOD}/Counter.pretty")(options "")(descr "Compact counter custom footprints")))\n')
assert p.ExportSpecctraDSN(B,str(ROOT/'validation/unrouted.dsn'))
with (ROOT/'manufacturing/pin-map.csv').open('w',newline='') as file:
    w=csv.writer(file);w.writerow(['reference','pad','function','net','x_mm','y_mm'])
    for foot in B.GetFootprints():
        for a in foot.Pads():w.writerow([foot.GetReference(),a.GetNumber(),labels.get(a.GetNumber(),'') if foot.GetReference()=='J1' else '',a.GetNetname(),p.ToMM(a.GetPosition().x),p.ToMM(a.GetPosition().y)])
print('Wrote compact 70 x 80 mm carrier with antenna notch:',len(parts),'parts')

