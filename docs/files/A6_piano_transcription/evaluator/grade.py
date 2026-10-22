"""Offline, data-only grader. See REVIEW_PROTOCOL.md. Never runs submission code."""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
from collections import defaultdict, deque
import numpy as np
import mido
from music21 import converter

ROOT = Path(__file__).resolve().parent
RUBRIC = json.loads((ROOT / 'rubric.json').read_text(encoding='utf-8-sig'))

def read_json(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def dump(p, obj):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8')

def checked_file(p, limit=20_000_000):
    if not p.is_file() or p.stat().st_size > limit:
        raise ValueError('missing or oversized: ' + p.name)

def xml_notes(p):
    checked_file(p)
    data = p.read_text(encoding='utf-8-sig')
    if '<!ENTITY' in data.upper():
        raise ValueError('XML entities are not accepted')
    s = converter.parseData(data, format='musicxml')
    if any(x.classes and ('Repeat' in x.classes or 'RepeatExpression' in x.classes)
           for x in s.recurse()):
        s = s.expandRepeats()
    s = s.stripTies(inPlace=False, matchByPitch=True)
    notes = []
    for part in s.parts:
        for n in part.flatten().notes:
            q, d = float(n.offset), float(n.quarterLength)
            for pitch in n.pitches:
                v = float(pitch.ps)
                if not (0 <= v <= 127 and abs(v-round(v)) < 1e-7 and math.isfinite(q+d)):
                    raise ValueError('Only finite 12-tone MIDI pitches are supported')
                notes.append({'q': q, 'd': d, 'p': int(round(v))})
    if len(notes) > 50000:
        raise ValueError('too many events')
    return sorted(notes, key=lambda n: (n['q'], n['p'], n['d']))

def midi_notes(p):
    checked_file(p)
    m = mido.MidiFile(p)
    if m.type == 2 or m.ticks_per_beat <= 0:
        raise ValueError('Use synchronous MIDI type 0 or 1 with PPQ timebase')
    active = defaultdict(deque)
    q, seconds, tempo = 0., 0., 500000
    notes, tempi = [], [(0., 0., tempo/1e6)]
    for e in mido.merge_tracks(m.tracks):
        dq = e.time / m.ticks_per_beat
        q += dq
        seconds += dq*tempo/1e6
        if e.type == 'set_tempo':
            tempo = e.tempo
            tempi.append((q, seconds, tempo/1e6))
        if e.type == 'note_on' and e.velocity:
            active[(e.channel, e.note)].append((q, seconds))
        elif e.type == 'note_off' or (e.type == 'note_on' and not e.velocity):
            key = (e.channel, e.note)
            if active[key]:
                onset, t = active[key].popleft()
                notes.append({'q': onset, 'd': q-onset, 'p': e.note, 't': t})
    if any(active.values()):
        raise ValueError('unclosed MIDI notes')
    if len(notes)>50000:
        raise ValueError('too many events')
    return sorted(notes, key=lambda n:(n['q'],n['p'],n['d'])), tempi

def matching(pred, ref, tolerance, field='t'):
    """Maximum-cardinality, one-to-one order-preserving match, separately per pitch.
    Sorted equal-radius interval matching admits the earliest-feasible greedy rule.
    No pitch substitution, transposition, time shift, or score-dependent warping.
    """
    pp, rr = defaultdict(list), defaultdict(list)
    for i,n in enumerate(pred): pp[n['p']].append(i)
    for i,n in enumerate(ref): rr[n['p']].append(i)
    pairs=[]
    for pitch in sorted(pp.keys() | rr.keys()):
        a=sorted(pp[pitch],key=lambda i:pred[i][field]); b=sorted(rr[pitch],key=lambda i:ref[i][field])
        i=j=0
        while i<len(a) and j<len(b):
            delta=pred[a[i]][field]-ref[b[j]][field]
            if delta < -tolerance-1e-9: i+=1
            elif delta > tolerance+1e-9: j+=1
            else:
                pairs.append((a[i],b[j])); i+=1; j+=1
    return pairs

def f1(tp, npred, nref):
    return 2*tp/(npred+nref) if npred+nref else 1.

def note_metrics(pred, ref, start, end):
    coarse=matching(pred,ref,RUBRIC['pitch_onset_tolerance_seconds'])
    strict=matching(pred,ref,RUBRIC['rhythm_onset_tolerance_seconds'])
    # Bins use one global assignment. Cross-boundary correct matches count in
    # their own prediction/reference denominators, avoiding artificial bin misses.
    def bins(which, count):
        rows=[]
        for k in range(count):
            npred=sum(which(n)==k for n in pred); nref=sum(which(n)==k for n in ref)
            mp=sum(which(pred[i])==k for i,j in coarse)
            mr=sum(which(ref[j])==k for i,j in coarse)
            value=(mp+mr)/(npred+nref) if npred+nref else 1.
            rows.append({'bin':k,'predicted':npred,'reference':nref,'f1':value})
        return rows
    tb=bins(lambda n:min(5,max(0,int((n['t']-start)/(end-start)*6))),6)
    rb=bins(lambda n:0 if n['p']<60 else (1 if n['p']<78 else 2),3)
    vals={'pitch_global_f1':f1(len(coarse),len(pred),len(ref)),
          'pitch_time_macro_f1':float(np.mean([b['f1'] for b in tb])),
          'pitch_register_macro_f1':float(np.mean([b['f1'] for b in rb])),
          'rhythm_strict_f1':f1(len(strict),len(pred),len(ref))}
    points={k: v*RUBRIC['criteria'][k] for k,v in vals.items()}
    return {'values':vals,'points':points,'note_points':sum(points.values()),
            'predicted_count':len(pred),'reference_count':len(ref),
            'coarse_tp':len(coarse),'strict_tp':len(strict),
            'false_positive':len(pred)-len(coarse),'false_negative':len(ref)-len(coarse),
            'time_bins':tb,'register_bins':rb,'matched_pairs':coarse}

def map_time(notes, sidecar, tempi):
    if sidecar is not None:
        if set(sidecar) != {'anchors'}:
            raise ValueError('alignment must contain only anchors; no event list')
        a=np.asarray(sidecar['anchors'],dtype=float)
        if a.ndim != 2 or a.shape[1]!=2 or not 2<=len(a)<=160 or not np.isfinite(a).all():
            raise ValueError('invalid anchors')
        dq=np.diff(a[:,0]);dt=np.diff(a[:,1])
        if np.any(dq<.5-1e-9) or np.any(dt<.5-1e-9) or np.any(dt>8+1e-9):
            raise ValueError('anchors require >=0.5 quarter and 0.5..8 seconds separation')
        slopes=dt/dq
        if np.any(slopes<.15) or np.any(slopes>3) or (len(slopes)>1 and np.any(np.maximum(slopes[1:]/slopes[:-1],slopes[:-1]/slopes[1:])>4)):
            raise ValueError('implausible or discontinuous tempo mapping')
        if a[0,1]<0 or a[-1,1]>77.5 or a[0,0]<0:
            raise ValueError('anchors outside clip/score domain')
        if notes and (min(n['q'] for n in notes)<a[0,0]-1e-8 or max(n['q'] for n in notes)>a[-1,0]+1e-8):
            raise ValueError('anchors must cover all XML note onsets')
        return [dict(n,t=float(np.interp(n['q'],a[:,0],a[:,1]))) for n in notes], 'piecewise-linear submitted beat/time anchors'
    if tempi is None:
        raise ValueError('No valid alignment.json or MIDI tempo map')
    clean=[]
    for item in tempi:
        if clean and abs(item[0]-clean[-1][0])<1e-9:
            clean[-1]=item
        elif not clean or abs(item[2]-clean[-1][2])>1e-9:
            clean.append(item)
    if len(clean)>160 or any(not .15<=x[2]<=3 for x in clean):
        raise ValueError('MIDI tempo outside 20..400 BPM or too many changes')
    for a,b in zip(clean,clean[1:]):
        if b[0]-a[0]<.5-1e-9 or b[1]-a[1]<.5-1e-9 or max(a[2]/b[2],b[2]/a[2])>4:
            raise ValueError('MIDI tempo changes too dense or discontinuous; use sparse alignment.json')
    tempi=clean
    qs=np.array([x[0] for x in tempi])
    result=[]
    for n in notes:
        i=max(0,int(np.searchsorted(qs,n['q'],side='right'))-1)
        q,t,slope=tempi[i]
        result.append(dict(n,t=t+(n['q']-q)*slope))
    return result, 'submitted MIDI tempo map, no fitted shift'

def grade(submission, truth_path):
    sub=Path(submission).resolve(); truth=read_json(truth_path)
    errors=[]; xml=[]; midi=[]; tempi=None; valid_xml=False
    try:
        xml=xml_notes(sub/'score.musicxml'); valid_xml=bool(xml)
    except Exception as e: errors.append('MusicXML: '+str(e))
    try: midi,tempi=midi_notes(sub/'score.mid')
    except Exception as e: errors.append('MIDI: '+str(e))
    pairs=matching(midi,xml,1/96,field='q')
    good=sum(abs(midi[i]['d']-xml[j]['d']) <= max(1/32,.2*xml[j]['d'])+1e-8 for i,j in pairs)
    consistency=f1(good,len(midi),len(xml)) if xml and midi else 0.
    mapped=[];method=None
    try:
        sidecar=None
        if (sub/'alignment.json').exists():
            checked_file(sub/'alignment.json',50000); sidecar=read_json(sub/'alignment.json')
        mapped,method=map_time(xml,sidecar,tempi)
    except Exception as e: errors.append('Alignment: '+str(e))
    start,end=truth['scored_window_seconds']
    pred=[n for n in mapped if start<=n['t']<end]
    metrics=note_metrics(pred,truth['notes'],start,end)
    points=metrics['points'].copy()
    points.update(xml_valid_nonempty=float(valid_xml),midi_xml_consistency=3*consistency,
                  notes_present=float((sub/'notes.md').is_file() and (sub/'notes.md').stat().st_size>0))
    pdf=sub/'score.pdf'; pdf_header=pdf.is_file() and pdf.open('rb').read(5)==b'%PDF-'
    points['notation_review']=None if pdf_header else 0
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sub.iterdir()
            if p.is_file() and p.name in ['score.musicxml','score.mid','score.pdf','notes.md','alignment.json']}
    return {'rubric_version':RUBRIC['version'],'status':'pending_review' if pdf_header else 'automatic_complete_missing_pdf',
            'automatic_score':sum(v for k,v in points.items() if k!='notation_review'),
            'automatic_max':90,'pending_points':10 if pdf_header else 0,'final_score':None if pdf_header else sum(points.values()),
            'points':points,'errors':errors,'mapping_method':method,'consistency_f1':consistency,
            'xml_note_count':len(xml),'midi_note_count':len(midi),'metrics':metrics,
            'predicted_events':pred,'submission_sha256':hashes,
            'truth_sha256':hashlib.sha256(Path(truth_path).read_bytes()).hexdigest(),
            'rubric_sha256':hashlib.sha256((ROOT/'rubric.json').read_bytes()).hexdigest()}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('submission',type=Path)
    ap.add_argument('--truth',type=Path,default=ROOT/'truth.json')
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    result=grade(args.submission,args.truth);dump(args.output,result)
    print(json.dumps({k:result[k] for k in ['status','automatic_score','automatic_max','pending_points','final_score','errors']},ensure_ascii=False))
if __name__=='__main__': main()
