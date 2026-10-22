(()=>{'use strict';
const data=JSON.parse(document.getElementById('trace-data').textContent), model=document.getElementById('model'), kind=document.getElementById('kind'), events=document.getElementById('events'), stats=document.getElementById('stats');
const labels={command_execution:'命令与输出',file_change:'文件修改',agent_message:'对外说明',reasoning:'推理事件计数',error:'运行提示',mcp_tool_call:'MCP 工具',tool_call:'工具调用',web_search:'网页检索'};
function el(tag,txt,cls){const x=document.createElement(tag);if(txt!==undefined)x.textContent=txt;if(cls)x.className=cls;return x}
for(const m of data){const o=el('option',m.model);o.value=m.id;model.append(o)}
function selected(){return data.find(m=>m.id===model.value)||data[0]}
function render(){const m=selected();events.replaceChildren();const visible=m.events.filter(e=>kind.value==='all'||(kind.value==='tools'?['command_execution','file_change','mcp_tool_call','tool_call','web_search'].includes(e.kind):e.kind===kind.value));stats.textContent=`${m.model} · ${m.stats.events} 个事件 · ${m.stats.tools} 次工具操作 · 推理事件 ${m.stats.reasoning} 条（仅计数） · 当前显示 ${visible.length} 个事件`;
document.getElementById('raw').href=m.observable_url;document.getElementById('run').href=m.run_url;
for(const e of visible){const a=el('article',undefined,'event');a.id='event-'+e.seq;a.append(el('h3',`#${e.seq} · ${labels[e.kind]||e.kind}`));const mt=[e.item_id?'日志 ID '+e.item_id:'',e.status?'记录状态 '+e.status:'',e.exit_code!==undefined&&e.exit_code!==null?'退出码 '+e.exit_code:''].filter(Boolean).join(' · ');if(mt)a.append(el('div',mt,'meta'));
if(e.kind==='reasoning')a.append(el('p','日志记录了一个推理事件。本页仅保留事件位置和计数，不展示内部推理正文。','muted'));
if(e.command){const d=el('details');d.open=true;d.append(el('summary','执行命令'),el('pre',e.command));a.append(d)}
if(e.output){const d=el('details');d.append(el('summary',e.output_truncated?'命令输出（较长，显示首尾；完整内容见可观察日志）':'命令输出'),el('pre',e.output));a.append(d)}
if(e.text)a.append(el('div',e.text,'event-text'));if(e.files)a.append(el('pre',e.files.map(f=>`${f.kind||'修改'}  ${f.path}`).join('\n')));events.append(a)}
if(!visible.length)events.append(el('p','这一类别没有记录。','empty'));const q=new URLSearchParams(location.hash.slice(1));q.set('model',m.id);history.replaceState(null,'','#'+q.toString())}
model.addEventListener('change',render);kind.addEventListener('change',render);document.getElementById('jump').addEventListener('click',()=>{const n=Number(document.getElementById('event-number').value);if(!selected().events.some(e=>e.seq===n)){stats.textContent='这个事件编号不存在，请输入列表范围内的编号。';return}kind.value='all';render();const t=document.getElementById('event-'+n);t.scrollIntoView({behavior:'smooth',block:'start'});t.tabIndex=-1;t.focus({preventScroll:true})});
const initial=new URLSearchParams(location.hash.slice(1)).get('model');if(data.some(m=>m.id===initial))model.value=initial;render();
})();
