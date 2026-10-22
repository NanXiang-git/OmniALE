from pathlib import Path
import json, hashlib, re, subprocess
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from grade import aggregate,read,put,sha
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PACKAGE=ROOT/'deliverables/A4_A6_research_20261021'
class Links(HTMLParser):
 def __init__(self):super().__init__();self.paths=set()
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ('href','src') and v and not v.startswith('#') and not urlsplit(v).scheme:self.paths.add(unquote(urlsplit(v).path))
def check_html(path):
 text=path.read_text(encoding='utf-8');p=Links();p.feed(text)
 missing=[x for x in p.paths if not (path.parent/x).is_file()];assert not missing,(str(path),missing)
 for attrs,body in re.findall(r'<script([^>]*)>(.*?)</script>',text,re.S):
  if 'application/json' not in attrs and body.strip():
   r=subprocess.run(['node','--check'],input=body,text=True,encoding='utf-8',capture_output=True);assert not r.returncode,r.stderr
 return len(p.paths)
def main():
 rows=read(PACKAGE/'RESULTS.json');old=read(HERE/'original_results.json')
 assert [r for r in rows if r['case']=='A4']==[r for r in old if r['case']=='A4']
 scores=read(HERE/'SUMMARY.json')['records'];checked=0
 for q in scores:
  for name,digest in q['submission_sha256'].items():
   assert sha(ROOT/q['submission']/name)==digest
   assert sha(PACKAGE/'files'/q['submission']/name)==digest;checked+=1
  row=next(x for x in rows if x['id']==q['id']);assert row['score']==q['final_score']
  if q['final_score'] is not None:
   recomputed=aggregate(read(ROOT/q['technical_path']),q['review']);assert recomputed['final_score']==q['final_score']
 paths=[ROOT/'benchmark_viewer.html',ROOT/'benchmark_report.html',PACKAGE/'index.html',HERE/'REPORT.html',PACKAGE/'files'/HERE.relative_to(ROOT)/'REPORT.html']
 links=sum(check_html(p) for p in paths)
 current=[r for r in rows if r['case']=='A6' and not r.get('historical_only') and not r.get('superseded_by') and r['attempt']!='historical' and r['score'] is not None]
 expected={r['model']:r['score'] for r in current};assert len(expected)==5 and all(0<x<60 for x in expected.values())
 page=(ROOT/'benchmark_viewer.html').read_text(encoding='utf-8');data=json.loads(re.search(r'<script type="application/json" id="benchmark-data">(.*?)</script>',page,re.S)[1]);a6=next(x for x in data['cases'] if x['id']=='A6')
 assert {m['id']:m['score']['low'] for m in a6['models'] if m['id'] in expected}==expected
 assert all('历史' in m['id'] for m in a6['models'] if m['id'] not in expected)
 for path in [ROOT/'benchmark_report.html',PACKAGE/'index.html']:
  text=path.read_text(encoding='utf-8');assert '<th>预算 / 用时</th>' not in text and '<th>执行状态</th>' not in text
  for name,value in expected.items():assert str(value) in text
 output={'passed':True,'version':'A6-delivery-v2.0','retrospective':True,'current_scores':expected,'records_reviewed':len(scores),'scored_records':sum(q['final_score'] is not None for q in scores),'unscored_preserved':sum(q['final_score'] is None for q in scores),'original_submission_hashes_checked':checked,'a4_records_unchanged':True,'local_links_checked':links,'all_scores_recomputed':True,'no_budget_or_status_table_columns':True,'visual_review':'30 PDF pages re-rendered and inspected in page-labelled contact sheets; existing independent XML renders and review evidence checked; no full listening or musician trial'}
 put(HERE/'VALIDATION.json',output);put(PACKAGE/'A6_V2_VALIDATION.json',output);print(json.dumps(output,ensure_ascii=False))
if __name__=='__main__':main()
