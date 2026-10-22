from pathlib import Path
import json, subprocess, hashlib, datetime
from PIL import Image, ImageOps, ImageDraw
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PACKAGE=ROOT/'deliverables/A4_A6_research_20261021'
PY=ROOT/'benchmark_runs/20261019_astra_cli_first/runtime/venv/Scripts/python.exe'
def put(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rows=json.loads((PACKAGE/'RESULTS.json').read_text(encoding='utf-8'))
 snapshot=HERE/'original_results.json'
 if not snapshot.exists():put(snapshot,rows)
 else:rows=json.loads(snapshot.read_text(encoding='utf-8'))
 inventory=[]
 for r in rows:
  if r['case']!='A6':continue
  sub=ROOT/r['submission'];out=HERE/'reviews'/r['id'];out.mkdir(parents=True,exist_ok=True)
  hashes={p.name:sha(p) for p in sub.glob('*') if p.is_file() and p.name in ('score.pdf','score.musicxml','score.mid','notes.md','alignment.json')}
  put(out/'input_hashes.json',hashes)
  tech=out/'technical.json'
  if sub.is_dir() and not tech.exists():
   result=subprocess.run([str(PY),'-E','-X','utf8',str(ROOT/'A6_piano_transcription/evaluator/grade.py'),str(sub),'--output',str(tech)],capture_output=True,text=True,encoding='utf-8',timeout=120)
   if result.returncode:raise RuntimeError(result.stderr[-2000:])
  pages=[]
  if (sub/'score.pdf').exists():
   if not list(out.glob('pdf-*.png')):
    subprocess.run(['pdftoppm','-scale-to','1500','-png',str(sub/'score.pdf'),str(out/'pdf')],capture_output=True,check=True,timeout=120)
   pages=sorted(out.glob('pdf-*.png'))
   for start in range(0,len(pages),4):
    group=pages[start:start+4];canvas=Image.new('RGB',(1600,1160*((len(group)+1)//2)),'#dddddd');draw=ImageDraw.Draw(canvas)
    for i,p in enumerate(group):
     im=Image.open(p).convert('RGB');im.thumbnail((780,1120));x=(i%2)*800;y=(i//2)*1160
     canvas.paste(im,(x,y+30));draw.text((x+10,y+8),f'{r["model"]} / page {start+i+1}',fill='black')
    canvas.save(out/f'contact-{start//4+1}.jpg',quality=92)
  t=json.loads(tech.read_text(encoding='utf-8')) if tech.exists() else {}
  item={'id':r['id'],'model':r['model'],'old_score':r['score'],'submission':r['submission'],'pages':len(pages),'files':hashes,'metrics':t.get('metrics',{}).get('values'),'consistency':t.get('consistency_f1'),'errors':t.get('errors',[]),'status':r['status']}
  inventory.append(item);print(json.dumps({k:v for k,v in item.items() if k!='files'},ensure_ascii=False),flush=True)
 put(HERE/'inventory.json',inventory)
 put(HERE/'FROZEN_RULE.json',{'rubric_sha256':sha(HERE/'rubric.json'),'protocol_sha256':sha(HERE/'RUBRIC.md'),'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'retrospective':True})
if __name__=='__main__':main()
