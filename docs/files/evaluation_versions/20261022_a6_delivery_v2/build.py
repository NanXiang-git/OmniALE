"""Publishable local report and portable-package integration, without solver calls."""
from pathlib import Path
import copy, json, re, html, os, importlib.util, subprocess, sys, shutil
from urllib.parse import quote
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
BASE=HERE.relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def put(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 original=read(HERE/'original_results.json');rows=copy.deepcopy(original);scores={x['id']:x for x in read(HERE/'SUMMARY.json')['records']}
 for row in rows:
  if row['case']!='A6':continue
  q=scores[row['id']];row.update(score=q['final_score'],scorepath=BASE+'/reviews/'+row['id']+'/score.json',score_detail=q,rubric_version=q['version'],exact_score_display=True,score_label='A6 v2 可用交付复评（事后规则）',reasons=q['review'].get('reasons',[q['review'].get('reason','')]),limits=q['limits'])
  row['reasons']=[f'v2最终分 {q["final_score"]}；旧v1分数 {q["old_score"]} 仅作历史对照。']+row['reasons']
 assert [r for r in rows if r['case']=='A4']==[r for r in original if r['case']=='A4']
 put(HERE/'REVIEWED_RESULTS.json',rows)
 pack=module('pack',ROOT/'benchmark_runs/20261021_a4luna_a6sol_serial/package_report.py')
 current=[r for r in rows if r['case']=='A6' and pack.display_record(r)]
 e=html.escape
 def href(p,label):
  if not (ROOT/p).is_file():return '<span>'+e(label)+'（原文件未留存，见历史结果快照）</span>'
  target=quote(os.path.relpath(ROOT/p,HERE).replace('\\','/'),safe='/')
  return '<a href="'+target+'">'+e(label)+'</a>'
 report='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>A6 v2 可用交付复评</title><style>body{font:16px/1.7 system-ui,sans-serif;max-width:1100px;margin:32px auto;padding:0 20px;color:#183044}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccd6df;padding:9px;text-align:left}pre{white-space:pre-wrap;overflow-wrap:anywhere}img{max-width:100%;max-height:600px}a{color:#06768a}details{padding:14px;border:1px solid #ddd;margin:14px 0}.notice{background:#fff3d5;padding:18px}h2{margin-top:40px}</style><h1>A6 v2 · 可用交付复评</h1><p class="notice">事后规则：不是新模型实验，不是答题前预注册结果。所有原始答卷、旧评分与输入哈希保留。不可交付有低分区分，只有无可评内容才为0；无实际可评尝试维持未评分。</p>'
 report+='<p>'+href(BASE+'/RUBRIC.md','完整标准')+' · '+href(BASE+'/rubric.json','机器可读规则')+' · '+href(BASE+'/grade.py','计分实现')+' · '+href(BASE+'/SUMMARY.json','全部12条复评记录')+'</p>'
 report+='<h2>当前五份交付</h2><table><tr><th>模型</th><th>旧v1</th><th>v2加权原始分</th><th>交付系数</th><th>v2最终分</th><th>可交付合格</th></tr>'
 for row in sorted(current,key=lambda x:-x['score']):
  q=row['score_detail'];report+=f'<tr><td>{e(row["model"])}</td><td>{q["old_score"]:.6f}</td><td>{q["raw_score"]:.6f}</td><td>{q["delivery_factor"]}</td><td><b>{q["final_score"]:.6f}</b></td><td>{"通过" if q["accepted"] else "未达标"}</td></tr>'
 report+='</table><p>公式：加权原始分 × 交付等级系数；未满足音乐准确性与可用性底线时封顶59。上表当前没有答卷触发额外59分封顶，低分来自实际分项与交付等级。</p><h2>评分标准全文</h2><pre>'+e((HERE/'RUBRIC.md').read_text(encoding='utf-8'))+'</pre>'
 for row in [r for r in rows if r['case']=='A6']:
  q=row['score_detail'];report+='<h2 id="'+row['id']+'">'+e(row['model']+' · '+row['attempt'])+'</h2><p>v2：'+str(q['final_score'])+'；旧v1：'+str(q['old_score'])+'。'+e(q['delivery_label'])+'</p>'
  report+='<p>'+href(row['scorepath'],'逐项评分JSON')+' · '+href(q['old_scorepath'],'历史评分')+' · '+href(BASE+'/reviews/'+row['id']+'/input_hashes.json','原提交哈希')+'</p>'
  if q.get('components'):
   report+='<table><tr><th>分项</th><th>得分</th><th>满分</th></tr>'+''.join(f'<tr><td>{e(k)}</td><td>{v:.6f}</td><td>{read(HERE/"rubric.json")["weights"][k]}</td></tr>' for k,v in q['components'].items())+'</table>'
  report+='<ul>'+''.join('<li>'+e(s)+'</li>' for s in row['reasons'])+'</ul>'
  if q['review'].get('prior_review'):report+='<p>'+href(q['review']['prior_review'],'复核所引用的旧独立评审证据')+'</p>'
  report+='<details><summary>本次渲染的全部PDF页</summary>'+''.join(href(p,'原提交第'+str(i+1)+'页')+'<br><img loading="lazy" src="'+quote(os.path.relpath(ROOT/p,HERE).replace('\\','/'),safe='/')+'">' for i,p in enumerate(q['evidence_pages']))+'</details>'
  report+='<details><summary>客观指标、限制与完整公式</summary><pre>'+e(json.dumps(q,ensure_ascii=False,indent=2))+'</pre></details>'
 report+='</html>'; (HERE/'REPORT.html').write_text(report,encoding='utf-8')
 backup=HERE/'before_publication';backup.mkdir(exist_ok=True)
 for name in ['benchmark_viewer.html','benchmark_report.html']:
  if not (backup/name).exists():shutil.copy2(ROOT/name,backup/name)
 # Apply only the A6 overlay to the current viewer payload.
 viewer=ROOT/'benchmark_viewer.html';page=viewer.read_text(encoding='utf-8');match=re.search(r'(<script type="application/json" id="benchmark-data">)(.*?)(</script>)',page,re.S)
 data=json.loads(match[2]);before=copy.deepcopy(data)
 overlay=module('v2',ROOT/'viewer/a6_delivery_v2_overlay.py');overlay.apply(data)
 assert [c for c in data['cases'] if c['id']!='A6']==[c for c in before['cases'] if c['id']!='A6']
 encoded=json.dumps(data,ensure_ascii=False).replace('<','\\u003c');viewer.write_text(page[:match.start(2)]+encoded+page[match.end(2):],encoding='utf-8')
 subprocess.run([sys.executable,'-X','utf8',str(ROOT/'viewer/build_report.py')],check=True,cwd=ROOT)
 pack.COPIES.update(pack.read(pack.OUT/'FILE_PROVENANCE.json',{}))
 for p in HERE.rglob('*'):
  if p.is_file() and p.name!='browser_pid.txt' and not any(x in ('before_publication','__pycache__') or x.startswith('chrome-profile') for x in p.parts):pack.copy_file(p)
 for p in [ROOT/'viewer/a6_delivery_v2_overlay.py',ROOT/'viewer/build_report.py',ROOT/'viewer/build_viewer.py',ROOT/'benchmark_runs/20261021_a4luna_a6sol_serial/package_report.py']:pack.copy_file(p)
 pack.put(pack.OUT/'FILE_PROVENANCE.json',pack.COPIES)
 pack.build_html(rows)
 page=(pack.OUT/'index.html').read_text(encoding='utf-8').replace('完整评分量表','历史v1评分量表').replace('本包不发布到网络。','当前报告同步发布于GitHub Pages。')
 (pack.OUT/'index.html').write_text(page,encoding='utf-8')
 readme='# OmniALE A4 / A6 完整研究包\n\n当前A6已按v2可用交付标准统一事后复评；A4结果未变。原始答卷和历史v1分数保留，不是新一轮作答。\n\n'
 readme+='|模型|A6 v2分数|\n|---|---:|\n'+''.join(f'|{r["model"]}|{r["score"]:.6f}|\n' for r in current)
 readme+='\n打开index.html查看结果，或files/'+BASE+'/REPORT.html查看标准全文、旧新分对照和证据。HTML表格不展示预算/用时或执行状态列。\n\n完整包含隐藏真值，不可整体交给答题模型；仅分发candidate目录。原始XML/PDF/MIDI未修改，预览图为派生文件。使用python -m http.server 8000可在本地浏览。\n'
 (pack.OUT/'README.md').write_text(readme,encoding='utf-8')
 listing='<!doctype html><meta charset="utf-8"><title>A4/A6文件索引</title><h1>归档文件</h1><a href="index.html">返回报告</a><ul>'+''.join('<li><a href="'+quote(p.relative_to(pack.OUT).as_posix(),safe='/')+'">'+e(p.relative_to(pack.OUT).as_posix())+'</a></li>' for p in sorted(pack.OUT.rglob('*')) if p.is_file() and p.name not in ('FILE_INDEX.html','SHA256SUMS.json'))+'</ul>'
 (pack.OUT/'FILE_INDEX.html').write_text(listing,encoding='utf-8')
 pack.R=HERE;pack.validate_and_zip(make_zip=False)
 print(json.dumps({'current_scores':{r['model']:r['score'] for r in current},'a4_unchanged':True,'root_other_cases_unchanged':True},ensure_ascii=False))
if __name__=='__main__':main()
