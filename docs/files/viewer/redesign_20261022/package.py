"""Prepare portable deliverables and the existing GitHub Pages checkout."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote,quote
from html import escape
import json,shutil,hashlib,zipfile,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];SOURCE=ROOT/'deliverables/A4_A6_research_20261021';REPO=ROOT/'publication/OmniALE';SITE=REPO/'docs'
def obj(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
class Links(HTMLParser):
 def __init__(self):super().__init__();self.paths=set()
 def handle_starttag(self,t,a):
  for k,v in a:
   if k in ('src','href') and v and not urlsplit(v).scheme and not v.startswith('#'):self.paths.add(unquote(urlsplit(v).path))
def index(base,label):
 names=sorted(p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file() and p.name!='FILE_INDEX.html')
 text='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+label+'</title><link rel="stylesheet" href="assets/style.css"><main><h1>'+label+'</h1><p><a href="index.html">返回案例首页</a></p><ul>'
 text+=''.join('<li><a href="'+quote(n,safe='/')+'">'+escape(n)+'</a></li>' for n in names)+'</ul></main></html>'
 (base/'FILE_INDEX.html').write_text(text,encoding='utf-8')
def hashes(base):put(base/'SHA256SUMS.json',{p.relative_to(base).as_posix():sha(p) for p in sorted(base.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.json'})
def prepare():
 validation=obj(HERE/'VALIDATION.json');visual=obj(HERE/'visual_qa/DOM_CHECKS.json');assert validation['passed'] and visual['passed']
 evidence=SOURCE/'files/viewer/redesign_20261022';evidence.mkdir(parents=True,exist_ok=True)
 for p in HERE.iterdir():
  if p.is_file() and p.suffix in ('.py','.js','.css','.json'):shutil.copy2(p,evidence/p.name)
 shutil.copytree(HERE/'dependency_sources',evidence/'dependency_sources',dirs_exist_ok=True)
 (evidence/'visual_qa').mkdir(exist_ok=True)
 for p in (HERE/'visual_qa').iterdir():
  if p.is_file() and p.suffix in ('.png','.json') and p.name!='results-table.png':shutil.copy2(p,evidence/'visual_qa'/p.name)
 put(SOURCE/'VALIDATION.json',validation|{'visual_checks':visual,'version':'A2-dependencies-20261022'})
 manifest=obj(SOURCE/'SITE_MANIFEST.json');paths=set(manifest['assets'])|{'index.html','README.md','RESULTS.json','SITE_MANIFEST.json','VALIDATION.json'}
 paths.update(p.relative_to(SOURCE).as_posix() for p in evidence.rglob('*') if p.is_file())
 # Follow HTML evidence links without publishing the entire 1.5 GB archive to Pages.
 done=set()
 while True:
  todo=[n for n in paths if n.endswith('.html') and n not in done]
  if not todo:break
  for n in todo:
   done.add(n);p=SOURCE/n;q=Links();q.feed(p.read_text(encoding='utf-8'))
   for u in q.paths:
    if u in ('FILE_INDEX.html','SHA256SUMS.json'):continue
    t=(p.parent/u).resolve();assert t.is_relative_to(SOURCE.resolve()) and t.is_file(),(n,u)
    paths.add(t.relative_to(SOURCE.resolve()).as_posix())
 for n in sorted(paths):
  p=SOURCE/n;assert p.is_file(),n;assert p.stat().st_size<100*1024**2,n
  d=SITE/n;d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d)
 shutil.copy2(SOURCE/'README.md',REPO/'README.md')
 index(SOURCE,'完整研究包文件索引');index(SITE,'在线证据文件索引');hashes(SOURCE);hashes(SITE)
 assert all(sha(SOURCE/n)==sha(SITE/n) for n in paths)
 site_bytes=sum(p.stat().st_size for p in SITE.rglob('*') if p.is_file());assert site_bytes<1024**3,site_bytes
 put(HERE/'PACKAGE.json',{'passed':True,'identical_files':len(paths),'site_bytes':site_bytes,'paths':sorted(paths)})
 print(json.dumps({'passed':True,'identical_files':len(paths),'site_bytes':site_bytes}))
def pack():
 p=SOURCE.with_suffix('.zip');temp=p.with_suffix('.new.zip')
 files=sorted(q for q in SOURCE.rglob('*') if q.is_file())
 with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for f in files:z.write(f,f.relative_to(SOURCE.parent).as_posix())
 with zipfile.ZipFile(temp) as z:
  assert len(z.namelist())==len(files)
  for n in ['index.html','sign/index.html','piano/index.html','sign/traces.html','piano/traces.html','RESULTS.json','SITE_MANIFEST.json','SHA256SUMS.json']:
   assert hashlib.sha256(z.read(SOURCE.name+'/'+n)).hexdigest()==sha(SOURCE/n),n
 temp.replace(p)
 check={'file':p.name,'sha256':sha(p),'bytes':p.stat().st_size,'files':len(files)}
 put(p.with_suffix('.zip.sha256.json'),check);shutil.copy2(p.with_suffix('.zip.sha256.json'),REPO/p.with_suffix('.zip.sha256.json').name)
 print(json.dumps(check),flush=True)
if __name__=='__main__':{'prepare':prepare,'pack':pack}[sys.argv[1]]()
