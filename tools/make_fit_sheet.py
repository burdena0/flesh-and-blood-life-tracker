"""Print-at-100-percent fit sheet, derived from the current PCB pad export."""
from pathlib import Path
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
r=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((r/'manufacturing/pin-map.csv').open()))
c=canvas.Canvas(str(r/'docs/fit-check.pdf'),pagesize=A4)
c.setTitle('Compact CL3641AH / Waveshare S3-Zero - E1 fit check')
def txt(x,y,s,size=9):
    c.setFont('Helvetica',size);c.drawString(x*mm,y*mm,s)
def pt(x,y):return (25+x)*mm,(245-y)*mm
def rect(x,y,w,h):
    px,py=pt(x,y+h);c.rect(px,py,w*mm,h*mm)
txt(20,281,'COMPACT COUNTER: actual-size fit check',16)
txt(20,272,'CL3641AH + Waveshare ESP32-S3-Zero | revision E1 | 70 x 80 mm',10)
txt(20,264,'Print at 100%. Disable Fit to Page. Verify the 100 mm calibration line.',9)
c.setLineWidth(.15*mm)
outline=[(0,0),(53.5,0),(53.5,5.5),(63.5,5.5),(63.5,0),(70,0),(70,80),(0,80),(0,0)]
for a,b in zip(outline,outline[1:]):c.line(*pt(*a),*pt(*b))
c.setStrokeColorRGB(.15,.3,.7);rect(20,33,30,14)
c.setStrokeColorRGB(.4,.4,.4);rect(49.62,.01,18,23.5)
rect(10.45,50.5,10.72,20.78)
c.setStrokeColorRGB(0,0,0)
for row in rows:
    ref=row['reference'];x=float(row['x_mm']);y=float(row['y_mm']);px,py=pt(x,y)
    c.setStrokeColorRGB(0,0,0) if ref in ['J1','DS1','U1'] or ref.startswith('SW') else c.setStrokeColorRGB(.6,.6,.6)
    c.circle(px,py,(1.6 if ref.startswith('H') else .45)*mm)
    if row['pad']=='1' and not ref.startswith('H'):c.rect(px-.8*mm,py-.8*mm,1.6*mm,1.6*mm)
    if ref=='DS1':
        c.setFont('Helvetica',5);c.drawCentredString(px,py+(1.2 if y<40 else -2.2)*mm,row['pad'])
    if ref=='J1':
        c.setFont('Helvetica',4.5)
        c.drawCentredString(px+(3.2 if x<60 else -3.2)*mm,py-.5*mm,row['function'].replace('IO',''))
    if ref=='U1':
        c.setFont('Helvetica',4);c.drawCentredString(px+(1.6 if x<15 else -1.6)*mm,py-.5*mm,row['pad'])
for x,y,label in [(35,40,'CL3641AH'),(35,49,'DOTS DOWN'),(58.6,26,'USB-C DOWN'),(15.8,61,'U1')]:
    px,py=pt(x,y);c.setFont('Helvetica',6);c.drawCentredString(px,py,label)
for i,label in enumerate(['MINUS','SELECT','PLUS','RESOURCE']):
    px,py=pt(5,17+18*i);c.setFont('Helvetica',4);c.drawCentredString(px,py,label)
for x in [25,35,45]:
    c.setStrokeColorRGB(.4,.4,.4);c.circle(*pt(x,28.5),2.5*mm)
for i,line in enumerate([
    'J1: Waveshare S3-Zero', '18 x 23.5 mm body.', 'Two 9-pin headers.',
    '2.54 mm pitch; 15.24 mm rows.', 'Antenna UP over the notch.', 'USB-C DOWN toward display.', '',
    'DS1: CL3641AH', '30 x 14 mm body.', 'Six pins per row.',
    '2.54 mm pitch; 10.16 mm rows.', 'Decimal points DOWN.', '',
    'U1: SN74HC595N DIP16', 'Notch UP; pin1 upper-left.', '',
    'SW: square pad = signal.', 'Choose ONE round GND pad.',
    '2.54 or 5.08 mm spacing.', 'Wire buttons if needed.'
]):txt(108,244-i*4,line,8)
c.setStrokeColorRGB(0,0,0);c.setLineWidth(.2*mm)
c.line(25*mm,154*mm,125*mm,154*mm)
for x in [25,125]:c.line(x*mm,152*mm,x*mm,156*mm)
txt(52,148,'THIS LINE MUST BE 100 mm',9)
for i,line in enumerate([
    '1. Compare the unplugged S3-Zero and display against their hole rows.',
    '2. Check every module pin label. The original 30-pin ESP32 does not fit J1.',
    '3. Check button lead spacing. Use wires if the unknown switch body does not fit.',
    '4. Seat the module on female headers so its underside clears the carrier.',
    '5. Keep the ceramic antenna and the notch clear of metal and nearby components.',
    '6. This sheet checks nominal geometry only. Physical fit and operation are untested.',
    '',
    'The breadboard model is separate: it uses your normal ESP32 and original firmware.',
    'Assembly, BOM, GPIO map and build instructions: compact-cl3641ah/README.txt.'
]):txt(20,137-i*5,line,9)
c.showPage();c.save()
print('Created 1:1 compact fit-check PDF')
