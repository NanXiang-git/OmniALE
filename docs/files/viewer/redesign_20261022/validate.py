from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re,hashlib,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];OUT=ROOT/'deliverables/A4_A6_research_20261021'
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.ids=set();self.errors=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if d.get('id'):
   if d['id'] in self.ids:self.errors.append('duplicate ID '+d['id'])
   self.ids.add(d['id'])
  for k,v in attrs:
   if k in ('href','src') and v:self.links.append(v)
def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 manifest=json.loads((OUT/'SITE_MANIFEST.json').read_text(encoding='utf-8'));seen=set();links=0;js=0
 for n in ['index.html','sign/index.html','piano/index.html','sign/traces.html','piano/traces.html']:
  p=OUT/n;text=p.read_text(encoding='utf-8');parser=Links();parser.feed(text);assert not parser.errors,parser.errors
  for u in parser.links:
   x=urlsplit(u)
   if x.scheme or x.netloc:continue
   t=(p.parent/unquote(x.path)).resolve() if x.path else p.resolve()
   assert t.is_relative_to(OUT.resolve()),u
   assert t.is_file(),(n,u)
   if x.fragment and not x.query and '=' not in x.fragment and t.suffix=='.html':
    q=Links();q.feed(t.read_text(encoding='utf-8'));assert unquote(x.fragment) in q.ids,(n,u)
   links+=1;seen.add(str(t.relative_to(OUT.resolve())))
  for attrs,body in re.findall(r'<script([^>]*)>(.*?)</script>',text,re.S):
   if 'application/json' in attrs:continue
   if not body.strip():continue
   result=subprocess.run(['node','--check'],input=body,text=True,encoding='utf-8',capture_output=True);assert result.returncode==0,result.stderr;js+=1
  assert '<th scope="col">预算 / 用时</th>' not in text and '<th scope="col">执行状态</th>' not in text
 for p in (OUT/'assets').glob('*.js'):
  result=subprocess.run(['node','--check',str(p)],capture_output=True,text=True);assert result.returncode==0,result.stderr;js+=1
 for slug,case in manifest['cases'].items():
  scores=[r['score'] for r in case['rows']];assert scores==sorted(scores,reverse=True)
  assert case['category']=='A2' and len(case['rows'])==5
  for r in case['rows']:
   p=OUT/'traces'/f"{r['id']}.jsonl";events=[json.loads(l) for l in p.read_text(encoding='utf-8').splitlines()]
   assert len(events)==r['trace']['events']
   assert [e['seq'] for e in events]==list(range(1,len(events)+1))
   assert all(not any(k in e for k in ('text','output','command')) for e in events if e['kind']=='reasoning')
 assert digest(OUT/'RESULTS.json')==manifest['source_results_sha256']
 for files in manifest['submission_hashes'].values():
  for p,hash in files.items():assert digest(ROOT/p)==hash and digest(OUT/'files'/p)==hash,p
 sensitive=re.compile(r'(?i)\bsk-[A-Za-z0-9_-]{20,}\b|Bearer\s+[A-Za-z0-9_.-]{24,}')
 for p in [OUT/n for n in manifest['assets'] if (OUT/n).suffix in ('.html','.js','.json','.jsonl','.md','.txt')]:assert not sensitive.search(p.read_text(encoding='utf-8-sig',errors='replace')),'Credential-like content in '+str(p)
 report={'passed':True,'pages':5,'local_links_checked':links,'javascript_checks':js,'scores_sorted':True,'scores_unchanged':True,'submission_files_unchanged':sum(len(x) for x in manifest['submission_hashes'].values()),'trace_counts_verified':True,'reasoning_bodies_excluded':True,'credential_scan_passed':True,'files_referenced':sorted(seen)}
 (HERE/'VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='files_referenced'},ensure_ascii=False))
if __name__=='__main__':main()
