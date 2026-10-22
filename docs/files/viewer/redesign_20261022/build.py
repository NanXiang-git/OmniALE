"""Build the two A2 case pages from frozen results. No model calls or regrading."""
from pathlib import Path
from collections import Counter
from html import escape
from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import quote
import json, re, shutil, hashlib

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=ROOT/'deliverables/A4_A6_research_20261021'
TAG='a2-analysis-rewrite-20261022'
RELEASE='https://github.com/NanXiang-git/OmniALE/releases/tag/'+TAG
DOWNLOAD='https://github.com/NanXiang-git/OmniALE/releases/download/'+TAG+'/A4_A6_research_20261021.zip'
ROWS=json.loads((OUT/'RESULTS.json').read_text(encoding='utf-8'))
SELECTED={
 'sign':['A4_gpt-6-astra_high40_rerun','A4_gpt-6-sol_20261022_k3a6_60_sola4_40_serial','A4_k3_20261021_k3_a4_a6_isolated','A4_gpt-6-luna_new_20261021','A4_glm-5.3-flash_20261021_glm53_flash_a4_a6_50min'],
 'piano':['A6_gpt-6-sol_new_20261021','A6_gpt-6-astra_20261022_a6astra_high40','A6_k3_20261022_k3_a6_60_clean','A6_glm-5.3-flash_20261021_glm53_flash_a4_a6_50min','A6_gpt-6-luna_missing8']}
CASES={slug:sorted([next(r for r in ROWS if r['id']==i) for i in ids],key=lambda r:(r['score'] is None,-(r['score'] or 0))) for slug,ids in SELECTED.items()}
TITLES={'sign':'中国手语视频 → 中英文字幕','piano':'钢琴演奏视频 → 乐谱与 MIDI'}
TOOLS={'command_execution','file_change','mcp_tool_call','tool_call','web_search'}
ASSETS=set()
DEPENDENCIES=json.loads((HERE/'DEPENDENCIES.json').read_text(encoding='utf-8'))['rows']

def obj(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def esc(s):return escape(str(s),quote=True)
def score_text(value):return format(Decimal(str(value)).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP),'.2f')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def ensure(path):
 path=str(path).replace('\\','/');dest=OUT/'files'/path
 if not dest.exists():
  assert (ROOT/path).is_file(),path
  dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/path,dest)
 ASSETS.add('files/'+path)
 return '../files/'+quote(path,safe='/')
def link(path,label):return '<a href="'+ensure(path)+'">'+esc(label)+'</a>'
def table(headers,rows,cls=''):
 return '<div class="scroll"><table class="'+cls+'"><thead><tr>'+''.join('<th scope="col">'+x+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(c)+'</td>' for c in r)+'</tr>' for r in rows)+'</tbody></table></div>'
def header(title,slug=None):
 prefix='../' if slug else ''
 nav=f'<a href="{prefix}index.html">案例首页</a><a href="{prefix}sign/index.html">手语字幕</a><a href="{prefix}piano/index.html">钢琴转谱</a>'
 return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(title)+' · OmniALE</title><link rel="stylesheet" href="'+prefix+'assets/style.css"></head><body><main><div class="eyebrow">OMNIALE · A2 本地化与使用方式适配</div><h1>'+esc(title)+'</h1><nav>'+nav+'</nav>'
def footer():return f'<footer>依据既有实验与冻结答卷整理 · 页面更新：2026-10-22<br><a href="{DOWNLOAD}">历史研究包 ZIP（本次 Astra 更新另见逐项评分）</a> · <a href="{RELEASE}">版本与校验文件</a> · <a href="https://github.com/NanXiang-git/OmniALE">GitHub</a></footer></main></body></html>'
def crop_text(t,limit=16000):
 if len(t)<=limit:return t,False
 return t[:limit//2]+'\n\n[…中间省略，完整输出见可观察日志…]\n\n'+t[-limit//2:],True

def trace(row):
 """Only observable messages/actions; reasoning bodies never enter published files."""
 p=ROOT/row['events_path'];raw=[]
 for l in p.read_text(encoding='utf-8-sig').splitlines():
  try:raw.append(json.loads(l))
  except ValueError:raise AssertionError('Malformed event log: '+str(p))
 completed={e.get('item',{}).get('id') for e in raw if e.get('type')=='item.completed'}
 seen=set();events=[];observable=[];installs=[]
 for line,e in enumerate(raw,1):
  i=e.get('item',{});kind=i.get('type');typ=e.get('type');iid=i.get('id')
  if typ=='item.started' and iid not in completed and kind in TOOLS:pass
  elif typ=='item.completed':pass
  elif typ in ('error','turn.failed'):i={'message':e.get('message') or e.get('error',{}).get('message','运行结束异常，见运行记录')};kind='error';iid=None
  else:continue
  key=iid or ('line',line)
  if key in seen:continue
  seen.add(key)
  if kind not in TOOLS|{'reasoning','agent_message','error'}:continue
  v={'seq':len(events)+1,'kind':kind,'item_id':iid,'source_line':line,'status':i.get('status','未结束' if typ=='item.started' else 'completed')}
  if kind=='reasoning':
   v['body_omitted']=True
  elif kind=='command_execution':
   v.update(command=i.get('command',''),exit_code=i.get('exit_code'))
   full=i.get('aggregated_output','');v['output'],v['output_truncated']=crop_text(full)
   if re.search(r'\b(?:pip3?|conda|apt-get|apt|npm|uv)\b[^\n]*\binstall\b',v['command']):
    installs.append({'event':v['seq'],'command':v['command'],'exit_code':v['exit_code'],'output_tail':full[-2000:]})
  elif kind=='file_change':v['files']=i.get('changes',[])
  elif kind in ('agent_message','error'):v['text']=i.get('text') or i.get('message','')
  else:
   v['text']=json.dumps({k:i[k] for k in ('server','tool','arguments','result','query') if k in i},ensure_ascii=False)
  events.append(v)
  safe=dict(v)
  if kind=='command_execution':safe['output']=i.get('aggregated_output','');safe['output_truncated']=False
  observable.append(safe)
 counts=Counter(e['kind'] for e in events)
 deps=DEPENDENCIES[row['id']]
 assert deps['source_log_sha256']==sha(p), 'Re-audit dependency evidence if source log changes'
 dest=OUT/'traces'/f"{row['id']}.jsonl";dest.parent.mkdir(exist_ok=True)
 dest.write_text(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in observable),encoding='utf-8')
 ASSETS.add(dest.relative_to(OUT).as_posix())
 return {'id':row['id'],'model':row['model'],'stats':{'events':len(events),'raw_jsonl_lines':len(raw),'tools':sum(counts[k] for k in TOOLS),'reasoning':counts['reasoning'],'kinds':dict(counts),'dependency_installs':installs,'used_dependencies':deps},'events':events,'observable_url':'../traces/'+dest.name,'run_url':ensure(row['runpath']),'source_sha256':sha(p)}

def sign_metrics(r):
 s=r['score_detail'];a=s.get('native_aggregate')
 if a:return a['components'],a['unit_semantic_scores']
 co={};unit={}
 for u in s['units']:
  typ=u['id'].split('.')[-1]
  if u['points'] is not None:co[typ]=co.get(typ,0)+u['points']
  if typ=='meaning':unit[u['id'].split('.')[0]]=u['points']/u['weight']
 co['timing']=None
 return co,unit
def srt_quotes(r):
 d=ROOT/r['submission'];seg=obj(d/'segments.json')['segments'];all_cues={}
 for lang,name in [('zh','zh-CN.srt'),('en','en.srt')]:
  text=(d/name).read_text(encoding='utf-8-sig');all_cues[lang]={int(b.splitlines()[0]):' '.join(b.splitlines()[2:]) for b in re.split(r'\n\s*\n',text.strip()) if b.strip()}
 return {s['id']:{l:' / '.join(all_cues[l][i] for i in s[l+'_cues']) for l in ('zh','en')} for s in seg}
def evidence_link(r,label='评分证据'):return link(r['scorepath'],label)

def sign_analysis(rows):
 metrics={r['model']:sign_metrics(r) for r in rows};quotes={r['model']:srt_quotes(r) for r in rows}
 truth=obj(ROOT/'A4_sign_bilingual/evaluator/truth.json');by={u['id']:u for u in truth['units']}
 out='<section id="analysis"><h2>四、失败分析</h2><p class="lead">五份答卷都完成了字幕文件和视频封装，主要问题出在翻译内容：有的只识别出零散词语，有的把整句话译成了另一件事，还有的全篇留空。</p>'
 out+='<h3>1. 大部分片段没有译全</h3><p>可读性和文件交付两项，五个模型都拿到了满分。语义项满分 65 分，最高只有 23.36 分。按已有信息点标注，23 段中，Astra 有 2 段拿到了全部语义分，其余模型均未出现满分片段。其他片段的得分主要来自识别对的人物、动作等局部内容。</p>'
 rr=[]
 for r in rows:
  c,u=metrics[r['model']];rr.append([esc(r['model']),score_text(c['meaning'])+' / 65',f"{sum(v>=1-1e-9 for v in u.values())} / 23",score_text(c['readability']+c['delivery'])+' / 10',evidence_link(r)])
 out+=table(['模型','语义得分','信息点全部满分的片段','可读性＋文件交付','依据'],rr)
 out+='<h3>2. 关键动作和整句话的意思被换掉了</h3><p>第 2 段的标注是“我们去吃饭吧”。K3 写成“我爱唱歌”，Sol 写成“给[无法确认]打电话说一声”。吃饭、唱歌、打电话是三件不同的事，观众看到这些字幕，会误解说话者要做什么。</p>'
 out+=table(['模型','第 2 段的实际中文字幕','实际英文字幕'],[[esc(r['model']),esc(quotes[r['model']]['S02']['zh']),esc(quotes[r['model']]['S02']['en'])] for r in rows])
 out+='<p>第 23 段的标注涉及“没有多少时间看书”，Astra 却写成“书看完了”，把时间不够译成了已经读完。K3 的“祝你生日快乐”和 GLM 的“我会说一点中文”则与原话完全偏离。</p>'
 out+=table(['片段','作者标注','Astra 字幕','K3 字幕','GLM 字幕'],[['S23',esc(by['S23']['zh_reference']),esc(quotes['gpt-6-astra']['S23']['zh']),esc(quotes['k3']['S23']['zh']),esc(quotes['glm-5.3-flash']['S23']['zh'])]])
 out+='<p class="muted">'+link('A4_sign_bilingual/evaluator/truth.json','作者标注与信息点')+'</p>'
 out+='<h3>3. 英文字幕沿用了中文里的错误</h3><p>K3 把“我爱唱歌”译成了“I love singing”。英文准确对应了它生成的中文，也把前一步对手语的误读一起带了过去。修改这类字幕，需要先回到视频核对原意，再重做中英文两版。</p>'
 out+='<h3>4. 大量内容留在“无法确认”</h3><p>Luna 的 23 段全部写成“[无法确认] / [unclear]”，没有提供实际译文。它的 26.99 分来自时间对齐、可读性、文件交付和置信度项目，语义与双语内容均为 0.00 分。</p><p>Sol 用占位符标出了一部分缺口，但保留下来的内容也有错误。例如第 2 段虽然没有确定人物，却写出了原话中没有的“打电话”这一动作。这些片段需要整句重新核对。</p>'
 out+='<h3>后续需要补的工作</h3><p>这批字幕还需要由熟悉中国手语的人逐段核对，补全漏译，纠正动作、对象和句意，再检查英文及字幕时间。文件封装已经完成，主要返工量在翻译本身。</p><p>评审依据为原始字幕、作者标注和已有片段抽帧检查。Astra 的最终得分为 39.00，触发了严重语义错误及覆盖不足的封顶规则。GLM 当前为 21.57 分小计，另有 12 分时间对齐待核验。</p>'
 out+='<details><summary>查看全部 23 段的语义信息点得分比例</summary><p class="muted">语义明细表说明：每格为该片段已获得的语义信息点分数占比，100% 表示该片段的信息点全部得分。</p>'
 out+=table(['片段']+[esc(r['model']) for r in rows],[[esc(sid)]+[f"{metrics[r['model']][1][sid]*100:.1f}%" for r in rows] for sid in by], 'compact')+'</details></section>'
 return out

def piano_analysis(rows):
 from piano_current_analysis import render
 import sys
 return render(sys.modules[__name__],rows)


def assets_section(slug,rows):
 out='<section id="submissions"><h2>五、查看模型交付</h2><p>按上表顺序查看原始交付。预览用于阅读；下载链接保留模型提交的文件。</p>'
 for r in rows:
  out+='<details id="'+r['id']+'"><summary>'+esc(r['model'])+' · '+score_text(r['score'])+' 分 · 展开交付文件</summary><div class="links">'
  for f in r['files']:out+=link(f,Path(f).name)
  out+=evidence_link(r,'逐项评分')+'</div>'
  if slug=='sign':
   v=next(p for p in r['previews'] if p['type']=='video');ASSETS.add(v['path']);out+='<div class="preview"><video controls preload="none" src="../'+v['path']+'">'
   for t in r['previews']:
    if t['type']=='track':ASSETS.add(t['path']);out+='<track kind="subtitles" src="../'+t['path']+'" srclang="'+t['lang']+'" label="'+('中文' if t['lang']=='zh' else 'English')+'"'+(' default' if t['lang']=='zh' else '')+'>'
   out+='</video><p class="muted">浏览器播放预览，可在播放器中切换字幕。原始 MKV 见下载链接。</p></div>'
  else:
   out+='<div class="pages">'
   for i,p in enumerate(r['score_detail']['evidence_pages'],1):
    u=ensure(p);out+=f'<figure><a href="{u}"><img loading="lazy" src="{u}" alt="{esc(r["model"])} 原提交 PDF 第 {i} 页"></a><figcaption>第 {i} 页</figcaption></figure>'
   out+='</div>'
  out+='</details>'
 return out+'</section>'

def task_section(slug):
 root='A4_sign_bilingual' if slug=='sign' else 'A6_piano_transcription';task=(ROOT/root/'candidate/TASK.md').read_text(encoding='utf-8');task=task.replace('# 第四题：','# 任务：').replace('# A6：','# 任务：')
 if slug=='sign':
  text='<p>给定约两分钟的真实中国手语视频，含 23 个独立表达、12 位表达者。要求制作简体中文和英文字幕，并封装为可切换字幕的成片，让不懂手语的观众理解原意。</p><p>交付四个文件：中文字幕、英文字幕、保留原视频的双字幕 MKV，以及片段对应和置信度记录。不能把独立镜头编成连续故事，也不能根据背景物品猜译。</p>'
  video=root+'/candidate/input/source.mp4';rule='<p>评分共 100 分：语义 65、双语 8、时间对齐 12、可读性 5、交付 5、置信度校准 5。达到 90 分并满足分项门槛才通过；严重语义错误和覆盖不足按原规则封顶。</p>'
  refs=link(root+'/evaluator/rubric.json','评分量表')+' · '+link(root+'/evaluator/REVIEW_PROTOCOL.md','评审协议')
 else:
  text='<p>给定一段 77 秒的真实钢琴演奏视频，结合录音与键盘画面，将指定区间的实际击键转写成可以阅读、编辑和演奏的乐谱。</p><p>交付 MusicXML、完整 PDF、与谱面对应的 MIDI 和转写说明；可另交符合规则的时间映射。谱面必须记录这一次演奏，不能用记忆中的出版谱替换。</p>'
  video=root+'/candidate/input/performance.mp4';rule='<p>当前使用交付导向 v2 评分：音高与覆盖 35、严格起音 20、MIDI/XML 一致性 10、谱面可读性与记谱 35。加权分再乘交付系数；不可用的作品保留部分分，但不能靠文件齐全获得高分。</p><p class="note">这是对已完成答卷的事后复评。原始答题任务与旧评分均保留，模型没有按新规则重跑。60 分以上还需满足准确性与交付门槛。</p>'
  refs=link('evaluation_versions/20261022_a6_delivery_v2/RUBRIC.md','当前评分标准')+' · '+link('evaluation_versions/20261022_a6_delivery_v2/REPORT.html','逐项复评与旧分')
 return '<section id="task"><h2>一、任务定义</h2>'+text+'<div class="preview"><video controls preload="metadata" src="'+ensure(video)+'"></video></div><p class="links">'+link(video,'下载输入视频')+' '+link(root+'/candidate/TASK.md','原始任务文件')+'</p>'+rule+'<p>'+refs+'</p><details><summary>展开答题时的完整题面</summary><pre>'+esc(task)+'</pre></details></section>'

def results_section(slug,rows):
 rr=[]
 for r in rows:
  score=score_text(r['score']);suffix=' <span class="badge">已确认小计</span>' if slug=='sign' and r['model']=='glm-5.3-flash' else ''
  rr.append(['<a href="#'+r['id']+'">'+esc(r['model'])+'</a>','Codex CLI',esc(r['reasoning_effort']),'<span class="score">'+score+'</span>'+suffix,'未通过' if not suffix else '尚未形成完整总分',evidence_link(r)+' · <a href="traces.html#model='+r['id']+'">轨迹</a>'])
 out='<section id="results"><h2>二、运行结果</h2><p>按当前展示分数从高到低排列，满分 100。每个模型展示当前采用的一次答卷。</p>'+table(['模型','Harness','推理强度','得分 / 100','交付判断','查看'],rr)
 if slug=='sign':out+='<p class="note">GLM 的 21.57 是已确认小计，另有 12 分时间对齐待核验，完整总分尚未形成。排序按当前已确认分；它与其他模型的完整判分并非完全同口径。</p>'
 out+='<details><summary>历史运行与评分版本</summary><p class="muted">以下仅供追溯，不参与当前排名。没有有效分数的记录标为“未评分”。原始编号保留在归档文件中。</p>'
 historical=[r for r in ROWS if r['case']==('A4' if slug=='sign' else 'A6') and r['id'] not in SELECTED[slug]]
 historical.sort(key=lambda r:(r['score'] is None,-(r['score'] or 0)))
 out+=table(['模型','归档记录','归档分数','证据'],[[esc(r['model']),esc(r['attempt']),score_text(r['score']) if r['score'] is not None else '未评分',link(r['runpath'],'运行记录')+((' · '+link(r['scorepath'],'评分')) if r.get('scorepath') and (ROOT/r['scorepath']).exists() else '')] for r in historical])+'</details></section>'
 return out

def trace_section(traces):
 out='<section id="trajectory"><h2>三、运行轨迹</h2><p>完整操作放在独立页面，可按模型和事件类型查看。这里给出同一口径的统计。</p>'
 rr=[]
 for t in traces:
  s=t['stats'];d=s['used_dependencies'];deptext='Python：'+esc('、'.join(d['python_packages']))+'（'+str(len(d['python_packages']))+' 个）<br><span class="muted">工具：'+esc('；'.join(d['system_tools']))+'</span>'
  rr.append(['<a href="traces.html#model='+t['id']+'">'+esc(t['model'])+'</a>',s['events'],s['tools'],str(s['reasoning']) if s['reasoning'] else '0（日志未记录）',deptext])
 out+=table(['模型','事件数','工具调用','可见推理步¹','使用的依赖'],rr)
 return out+'<p><a href="traces.html">打开运行轨迹浏览器 →</a></p><p class="muted">事件数按去重后的操作、对外说明、显式推理事件和运行提示统计；一次工具操作的开始与结束不重复计数。工具调用含命令执行和文件修改。¹ 仅统计日志显式记录的 reasoning 事件，不代表模型真实思考次数；未记录不等于没有思考。内部推理正文不公开。依赖列统计本轮实际使用的第三方 Python 包（包括预装包），并另列媒体工具；不含标准库、仅检查是否存在的包或导入失败的包。</p></section>'

def trace_page(slug,traces):
 text=header(TITLES[slug]+' · 运行轨迹',slug)+'<p><a href="index.html#trajectory">← 返回案例页</a></p><p>查看模型实际执行的命令、返回结果、文件修改与对外说明。事件按日志顺序排列；显式推理事件仅保留计数与位置。</p><details><summary>统计口径与日志限制</summary><p>开始和结束按同一事件 ID 合并；没有结束记录的调用保留为未结束。工具调用包含命令、文件修改及日志中其他显式工具事件。CLI 事件流可能不记录部分原生看图等操作，因此统计是日志可见下限。“使用的依赖”包括分析、制作、自检及工具探索中实际调用的第三方包，无论预装还是现场安装；不将仅探测可用性或导入失败算成使用。不同日志未暴露的推理步骤不作估计。</p><p>为方便浏览，超过 16,000 字符的命令输出显示首尾；可观察日志下载保留完整输出。临时脚本若只记录文件修改路径而没有补丁，就不能从这里恢复其完整源码。</p></details><div class="controls"><label>模型<select id="model"></select></label><label>事件类型<select id="kind"><option value="all">全部事件</option><option value="tools">工具操作</option><option value="agent_message">对外说明</option><option value="reasoning">推理事件计数</option><option value="error">运行提示</option></select></label><label>跳到事件<input type="number" id="event-number" min="1" value="1"></label><button id="jump">跳转</button></div><p id="stats" aria-live="polite"></p><div id="dependencies" class="note"></div><p class="links"><a id="raw" href="'+traces[0]['observable_url']+'">下载完整可观察日志</a><a id="run" href="'+traces[0]['run_url']+'">运行配置记录</a></p><div id="events"></div>'
 payload=json.dumps(traces,ensure_ascii=False).replace('<','\\u003c').replace('&','\\u0026')
 return text+'<script id="trace-data" type="application/json">'+payload+'</script><script src="../assets/traces.js"></script>'+footer()

def main():
 (OUT/'assets').mkdir(exist_ok=True)
 for name in ('style.css','traces.js'):shutil.copy2(HERE/name,OUT/'assets'/name);ASSETS.add('assets/'+name)
 before={r['id']:{p:sha(ROOT/p) for p in r['files']} for rows in CASES.values() for r in rows}
 manifest={'version':'A2-analysis-rewrite-20261022','classification':{'A1':'音视频内容制作与编排','A2':'本地化与使用方式适配','A3':'素材整理、检索与证据构建'},'cases':{},'source_results_sha256':sha(OUT/'RESULTS.json')}
 for slug,rows in CASES.items():
  traces=[trace(r) for r in rows];(OUT/slug).mkdir(exist_ok=True)
  body=header(TITLES[slug],slug)+'<p class="lead">'+('把手语表达准确地交给不懂手语的观众。' if slug=='sign' else '把这一次真实演奏变成可以照着弹的乐谱。')+'</p><p class="links"><a href="#task">任务定义</a><a href="#results">运行结果</a><a href="#trajectory">运行轨迹</a><a href="#analysis">失败分析</a><a href="#submissions">模型交付</a></p>'
  body+=task_section(slug)+results_section(slug,rows)+trace_section(traces)+(sign_analysis(rows) if slug=='sign' else piano_analysis(rows))+assets_section(slug,rows)
  body+='<script>function reveal(){const e=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(e&&e.tagName==="DETAILS")e.open=true}addEventListener("hashchange",reveal);reveal();</script>'+footer()
  (OUT/slug/'index.html').write_text(body,encoding='utf-8');(OUT/slug/'traces.html').write_text(trace_page(slug,traces),encoding='utf-8')
  ASSETS.update([slug+'/index.html',slug+'/traces.html'])
  manifest['cases'][slug]={'category':'A2','title':TITLES[slug],'rows':[{'id':r['id'],'model':r['model'],'score':r['score'],'scorepath':r['scorepath'],'trace':t['stats'],'source_log_sha256':t['source_sha256']} for r,t in zip(rows,traces)]}
 landing=header('真实媒体的创作与适配')+'<p class="lead">两项 A2 任务：将已有内容转换为新的语言或使用形式。各案例分别展示任务、成绩、失败分析和模型交付，完整操作轨迹另页查看。</p><div class="cards">'
 for slug in CASES:
  landing+='<article class="card"><span class="badge">A2 · 本地化与使用方式适配</span><h2>'+TITLES[slug]+'</h2><p>'+('23 个独立表达，12 位表达者；交付中英文字幕与可切换字幕的成片。' if slug=='sign' else '77 秒真实钢琴演奏；交付 MusicXML、PDF、MIDI 和转写说明。')+'</p><p><a href="'+slug+'/index.html">查看案例与结果 →</a> · <a href="'+slug+'/traces.html">运行轨迹</a></p></article>'
 landing+='</div><h2>A 类任务如何划分</h2>'+table(['分类','主要交付'],[['A1 · 音视频内容制作与编排','制作新的成片、节目或内容编排。'],['A2 · 本地化与使用方式适配','面向新语言、受众或使用方式转换内容；本页两题均属于此类。'],['A3 · 素材整理、检索与证据构建','交付可检索的素材、事件索引或可追溯证据包。']])+'<p class="muted">历史文件沿用原来的题目编号，以便核对实验记录。页面按主要交付目标分类。</p><p class="links"><a href="RESULTS.json">全部历史与当前成绩</a><a href="SITE_MANIFEST.json">当前页面与统计清单</a><a href="FILE_INDEX.html">研究包文件索引</a></p>'
 # Keep links sent before the redesign working, including model anchors.
 landing+='<script>(()=>{const h=decodeURIComponent(location.hash.slice(1));const p=h.startsWith("A4")?"sign":h.startsWith("A6")?"piano":null;if(p)location.replace(p+"/index.html"+(h.length>2?"#"+encodeURIComponent(h):""));})();</script>'+footer()
 (OUT/'index.html').write_text(landing,encoding='utf-8');ASSETS.add('index.html')
 readme='# OmniALE · A2 本地化与使用方式适配\n\n[案例首页](https://nanxiang-git.github.io/OmniALE/) · [手语字幕](https://nanxiang-git.github.io/OmniALE/sign/) · [钢琴转谱](https://nanxiang-git.github.io/OmniALE/piano/)\n\n两题已拆为独立案例页，运行轨迹各自放在 traces.html。当前成绩按得分倒序排列，展示分数四舍五入保留两位小数，原始评分数据保留完整精度。分类依据项目原始 A1/A2/A3 定义，两题均属于 A2；归档文件中的旧编号保留。\n\n本次仅补评已完成的 Astra A6 答卷，替换此前当前记录；其他模型分数保持不变。手语 GLM 为已确认小计，12 分时间对齐待核验；钢琴使用交付导向 v2 事后复评。\n\n轨迹事件合并开始与结束，推理事件只计数，不发布内部推理正文。依赖按本轮实际使用统计，包括预装包；Python 包与系统媒体工具分别列出。\n\n离线使用：在本目录运行 `python -m http.server 8000`，打开 http://localhost:8000/ 。\n\n[历史研究包（不含本次 Astra 更新）]('+DOWNLOAD+') · [发布记录]('+RELEASE+')\n'
 (OUT/'README.md').write_text(readme,encoding='utf-8')
 for name in ('benchmark_report.html','benchmark_viewer.html'):
  target='deliverables/A4_A6_research_20261021/index.html';(ROOT/name).write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OmniALE · 案例首页</title><p><a href="'+target+'">打开 A2 案例首页</a></p><script>location.replace('+json.dumps(target)+'+location.hash);</script></html>',encoding='utf-8')
 after={r['id']:{p:sha(ROOT/p) for p in r['files']} for rows in CASES.values() for r in rows};assert before==after
 manifest['submission_hashes']=after;manifest['assets']=sorted(ASSETS);put(OUT/'SITE_MANIFEST.json',manifest)
 put(HERE/'BUILD.json',{'passed':True,'source_results_unchanged':sha(OUT/'RESULTS.json')==manifest['source_results_sha256'],'original_submissions_unchanged':True,'pages':['index.html','sign/index.html','sign/traces.html','piano/index.html','piano/traces.html'],'trace_stats':{slug:[{'model':t['model'],**t['trace']} for t in manifest['cases'][slug]['rows']] for slug in CASES}})
 print(json.dumps(obj(HERE/'BUILD.json'),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
