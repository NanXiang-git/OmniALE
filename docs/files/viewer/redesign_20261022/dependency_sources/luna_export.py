import csv, os, json, math, xml.etree.ElementTree as ET
from music21 import stream, note, meter, tempo, instrument, clef

out='/work/results'; os.makedirs(out,exist_ok=True)
ev=[]
with open('/tmp/events.csv') as f:
    for r in csv.DictReader(f):
        t=float(r['time']); m=int(r['midi']); d=float(r['duration'])
        if 1.230 <= t < 75.480: ev.append((t,m,d))
# q=2*t (120 quarter notes/minute); preserve measured offsets and durations.
parts=[]
for name,lo,hi,clefobj in [('Piano RH',60,128,clef.TrebleClef()),('Piano LH',0,60,clef.BassClef())]:
    p=stream.Part(); p.id=name; p.partName=name
    p.insert(0,instrument.Piano())
    p.insert(0,clefobj)
    # fixed 4/4 bars on a single continuous q axis
    p.insert(0,meter.TimeSignature('4/4'))
    p.insert(0,tempo.MetronomeMark(number=120))
    for t,m,d in ev:
        if not lo<=m<hi: continue
        q=round(t*24)/12; dur=round(min(max(d*2,1/12),8.0)*12)/12
        n=note.Note(m); n.duration.quarterLength=dur
        p.insert(q,n)
    parts.append(p)
# Export both formats from one quantized event list and a shared duration rule.
from music21 import pitch as m21pitch
prepared=[]
for t,m,d in ev:
    q=round(t*8)/4
    dur=max(.25,round(d*8)/4)
    dur=min(dur,4-(q%4))
    prepared.append((q,int(m),dur))
root=ET.Element('score-partwise',version='3.1')
work=ET.SubElement(root,'work'); ET.SubElement(work,'work-title').text='Piano transcription'
sp=ET.SubElement(root,'part-list')
for pid,name in [('P1','Right hand'),('P2','Left hand')]:
    el=ET.SubElement(sp,'score-part',id=pid); ET.SubElement(el,'part-name').text=name
for pid,isright in [('P1',True),('P2',False)]:
    pe=ET.SubElement(root,'part',id=pid)
    local=[e for e in prepared if (e[1]>=60)==isright]
    maxbar=int(max((q for q,_,_ in local),default=0)//4)+1
    for bar in range(maxbar+1):
        me=ET.SubElement(pe,'measure',number=str(bar+1))
        if bar==0:
            at=ET.SubElement(me,'attributes'); ET.SubElement(at,'divisions').text='4'
            ts=ET.SubElement(at,'time'); ET.SubElement(ts,'beats').text='4'; ET.SubElement(ts,'beat-type').text='4'
            cl=ET.SubElement(at,'clef'); ET.SubElement(cl,'sign').text='G' if isright else 'F'; ET.SubElement(cl,'line').text='2' if isright else '4'
            key=ET.SubElement(at,'key'); ET.SubElement(key,'fifths').text='0'
            direction=ET.SubElement(me,'direction'); dt=ET.SubElement(direction,'direction-type'); met=ET.SubElement(dt,'metronome'); ET.SubElement(met,'beat-unit').text='quarter'; ET.SubElement(met,'per-minute').text='120'; ET.SubElement(direction,'sound',tempo='120')
        es=[e for e in local if int(e[0]//4)==bar and e[0]<maxbar*4]
        lanes=[]
        for q,m,d in sorted(es):
            start=q-bar*4; dur=min(d,4-start)
            lane=next((i for i,end in enumerate(lanes) if end<=start+1e-6),None)
            if lane is None: lane=len(lanes); lanes.append(0)
            lanes[lane]=start+dur
            if 'events' not in locals(): events=[]
            events.append((q,m,dur))
        for li in range(max(1,len(lanes))):
            if li: ET.SubElement(me,'backup').append(ET.Element('duration')); me[-1][0].text='16'
            lanees=[]
            # Deterministically recreate lane assignment for serialization.
            ends=[]
            for q,m,d in sorted(es):
                start=q-bar*4; dur=min(d,4-start)
                lane=next((i for i,end in enumerate(ends) if end<=start+1e-6),None)
                if lane is None: lane=len(ends); ends.append(0)
                ends[lane]=start+dur
                if lane==li: lanees.append((start,m,dur))
            cursor=0
            for start,m,dur in lanees:
                if start>cursor:
                    fw=ET.SubElement(me,'forward'); ET.SubElement(fw,'duration').text=str(round((start-cursor)*4)); cursor=start
                n=ET.SubElement(me,'note'); pelem=m21pitch.Pitch(m)
                st=ET.SubElement(n,'pitch'); ET.SubElement(st,'step').text=pelem.step
                if pelem.accidental is not None and pelem.accidental.alter: ET.SubElement(st,'alter').text=str(int(pelem.accidental.alter))
                ET.SubElement(st,'octave').text=str(pelem.octave)
                ET.SubElement(n,'duration').text=str(round(dur*4)); ET.SubElement(n,'voice').text=str(li+1)
                typ=ET.SubElement(n,'type'); typ.text='whole' if dur>=4 else 'half' if dur>=2 else 'quarter' if dur>=1 else 'eighth' if dur>=.5 else '16th'
                ET.SubElement(n,'staff').text='1' if isright else '2'; cursor=start+dur
            if cursor<4:
                fw=ET.SubElement(me,'forward'); ET.SubElement(fw,'duration').text=str(round((4-cursor)*4))
        if bar==maxbar: ET.SubElement(me,'barline',location='right').append(ET.Element('bar-style')); me[-1][0].text='light-heavy'
ET.indent(root,space='  '); ET.ElementTree(root).write(out+'/score.musicxml',encoding='utf-8',xml_declaration=True)
import mido
mid=mido.MidiFile(type=1,ticks_per_beat=480)
for isright in (True,False):
    tr=mido.MidiTrack(); mid.tracks.append(tr)
    tr.append(mido.Message('program_change',program=0,channel=0 if isright else 1,time=0))
    if isright: tr.append(mido.MetaMessage('set_tempo',tempo=500000,time=0))
    messages=[]
    for q,m,dur in prepared:
        if (m>=60)!=isright: continue
        qstart=round(q*480); qend=qstart+round(dur*480)
        messages.extend([(qstart,mido.Message('note_on',note=m,velocity=75,channel=0 if isright else 1)),(qend,mido.Message('note_off',note=m,velocity=0,channel=0 if isright else 1))])
    messages.sort(key=lambda x:(x[0],x[1].type=='note_on'))
    prev=0
    for tick,msg in messages: msg.time=tick-prev; tr.append(msg); prev=tick
    tr.append(mido.MetaMessage('end_of_track',time=0))
mid.save(out+'/score.mid')
# Compact staff engraving for the complete score, in four 4/4 measures per page.
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import mm
from music21 import pitch
W,H=landscape(A4); c=canvas.Canvas(out+'/score.pdf',pagesize=(W,H))
lastq=max((t*2 for t,_,_ in ev),default=0); bars=int(lastq//4)+1
def staff_y(m,base,treble):
    p=pitch.Pitch(m); step=p.diatonicNoteNum
    ref= pitch.Pitch('E4').diatonicNoteNum if treble else pitch.Pitch('G2').diatonicNoteNum
    return base+(step-ref)*2.5*mm
for first in range(0,bars,4):
    c.setFont('Helvetica',9); c.drawString(12*mm,H-12*mm,f'Piano transcription  |  measures {first+1}-{min(first+4,bars)}  |  quarter = 120')
    for row,(part,treble) in enumerate([(0,True),(1,False)]):
        top=H-(50+row*75)*mm
        for k in range(5):
            y=top-k*5*mm; c.setLineWidth(.3); c.line(14*mm,y,W-12*mm,y)
        c.setFont('Helvetica',17); c.drawString(3*mm,top-13*mm,'G' if treble else 'F')
        for b in range(first,min(first+4,bars)+1):
            x=14*mm+(b-first)*(W-28*mm)/4
            c.setLineWidth(.4); c.line(x,top-20*mm,x,top)
        for t,m,d in ev:
            if (m>=60)!=(part==0): continue
            q=round(t*8)/4; bar=int(q//4)
            if bar<first or bar>=first+4: continue
            frac=(q%4)/4
            x=14*mm+(bar-first+frac)*(W-28*mm)/4
            y=staff_y(m,top-20*mm,treble)
            dur=max(.25,round(d*8)/4)
            c.saveState(); c.translate(x,y); c.rotate(-18)
            c.setFillColorRGB(1,1,1) if dur>=2 else c.setFillColorRGB(0,0,0)
            c.setLineWidth(.65); c.ellipse(-1.7*mm,-1.1*mm,1.7*mm,1.1*mm,fill=1,stroke=1); c.restoreState()
            if dur<4:
                c.setLineWidth(.55); c.line(x+1.5*mm,y,x+1.5*mm,y+9*mm)
                if dur<1:
                    c.setLineWidth(.45); c.line(x+1.5*mm,y+8*mm,x+3.4*mm,y+6.5*mm)
                    if dur<.5: c.line(x+1.5*mm,y+6*mm,x+3.4*mm,y+4.5*mm)
            # Ledger lines keep the full keyboard range on the five-line staff.
            edge=top-20*mm if y<top-20*mm else top
            if y<top-20*mm or y>top:
                yy=edge
                while (y<yy-2.5*mm if y<top-20*mm else y>yy+2.5*mm):
                    yy += -5*mm if y<top-20*mm else 5*mm
                    c.setLineWidth(.35); c.line(x-2.5*mm,yy,x+2.5*mm,yy)
    c.showPage()
c.save(); pages=(bars+3)//4
# q coverage includes every exported onset. anchors stay within [0,77.5].
anchors=[[float(q),round(float(q)/2,3)] for q in range(0,152,8)]
if anchors[-1][0] < 154: anchors.append([154.0,77.0])
with open(out+'/alignment.json','w') as f: json.dump({'anchors':anchors},f)
with open(out+'/notes.md','w') as f:
    f.write('''# 转写说明\n\n节拍轴采用恒定四分音符=120 BPM，MusicXML 从 q=0 开始；`alignment.json` 以 q=2t 将记谱位置线性映射到视频秒数，音符起音量化到四分之一拍网格。候选音符来自本地音频频谱的谐波模板分解，键盘画面用于确认双手演奏与全键盘范围。左右手按 MIDI 60 分置于高、低音谱表；时值按检测到的持续区间近似，最长记为一小节内的时值。\n\n范围按视频时间 `[1.230, 75.480)` 筛选起音，不补入片段前已按下的音；右端以后事件不纳入正文。频谱法可能漏掉弱音、重击同音和把泛音当作独立音符，时值及踏板释放亦不确定；未对整段逐音听审。\n''')
print('events',len(ev),'pages',pages)
