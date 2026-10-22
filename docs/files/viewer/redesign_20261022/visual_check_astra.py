"""Inspect our generated local pages in a dedicated headless browser."""
from pathlib import Path
import sys,json,subprocess,urllib.request,time,base64,os
sys.path.insert(0,'D:/Temp/omni-html-qa-deps')
import websocket
HERE=Path(__file__).resolve().parent;OUT=HERE/'visual_qa';OUT.mkdir(exist_ok=True)
browser=subprocess.Popen(['C:/Program Files/Google/Chrome/Application/chrome.exe','--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check','--remote-debugging-port=9883','--user-data-dir='+str((OUT/'chrome-profile-astra').resolve()),'about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
try:
 for i in range(30):
  try:targets=json.load(urllib.request.urlopen('http://127.0.0.1:9883/json'));break
  except Exception:time.sleep(.5)
 ws=websocket.create_connection(next(t['webSocketDebuggerUrl'] for t in targets if t['type']=='page'),timeout=30,suppress_origin=True);n=0
 def call(method,params=None):
  global n;n+=1;ws.send(json.dumps({'id':n,'method':method,'params':params or {}}))
  while True:
   x=json.loads(ws.recv())
   if x.get('id')==n:
    assert not x.get('error'),x
    return x.get('result',{})
 def ev(expr):
  r=call('Runtime.evaluate',{'expression':expr,'returnByValue':True});assert not r.get('exceptionDetails'),r
  return r['result'].get('value')
 def shot(name):(OUT/(name+'.png')).write_bytes(base64.b64decode(call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})['data']))
 call('Page.enable');call('Runtime.enable');checks=[]
 for mobile in (False,True):
  width,height=(390,844) if mobile else (1440,1100);call('Emulation.setDeviceMetricsOverride',{'width':width,'height':height,'deviceScaleFactor':1,'mobile':mobile})
  for slug in ('','sign/','piano/','sign/traces.html','piano/traces.html'):
   call('Page.navigate',{'url':'http://127.0.0.1:8773/'+slug});time.sleep(1)
   name=('mobile-' if mobile else 'desktop-')+(slug.replace('/','-').replace('.html','') or 'home')
   if slug in ('sign/','piano/'):ev("document.documentElement.style.scrollBehavior='auto';document.getElementById('results').scrollIntoView({behavior:'instant'})")
   info=ev("({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,title:document.title,events:document.querySelectorAll('article.event').length,videos:[...document.querySelectorAll('video')].map(v=>({error:v.error?.code||null})),images:[...document.querySelectorAll('img')].filter(i=>i.complete&&i.naturalWidth===0).length})")
   assert info['scrollWidth']<=info['width']+2,(slug,info)
   assert not any(v['error'] for v in info['videos']),(slug,info)
   checks.append({'page':slug,'mobile':mobile,**info});shot(name)
   if 'traces' in slug:
    counts=ev("JSON.parse(document.getElementById('trace-data').textContent).map(x=>({id:x.id,n:x.stats.events,tools:x.stats.tools}))")
    for m in counts:
     ev("document.getElementById('model').value="+json.dumps(m['id'])+";document.getElementById('model').dispatchEvent(new Event('change'))")
     assert ev("document.querySelectorAll('article.event').length")==m['n']
     assert '使用的 Python 包' in ev("document.getElementById('dependencies').textContent")
     ev("document.getElementById('kind').value='tools';document.getElementById('kind').dispatchEvent(new Event('change'))")
     assert ev("document.querySelectorAll('article.event').length")==m['tools']
     ev("document.getElementById('kind').value='all';document.getElementById('kind').dispatchEvent(new Event('change'))")
    ev("document.getElementById('event-number').value=10;document.getElementById('jump').click()")
    assert ev("document.activeElement.id")=='event-10'
  call('Page.navigate',{'url':'http://127.0.0.1:8773/piano/#analysis'});time.sleep(1);shot('mobile-analysis' if mobile else 'desktop-analysis')
  call('Page.navigate',{'url':'http://127.0.0.1:8773/#A6_gpt-6-sol_new_20261021'});time.sleep(1)
  assert '/piano/' in ev('location.pathname') and ev("document.getElementById('A6_gpt-6-sol_new_20261021').open")
  if not mobile:
   call('Page.navigate',{'url':'http://127.0.0.1:8773/sign/#A4_gpt-6-astra_high40_rerun'});time.sleep(1)
   result=ev("({open:document.getElementById('A4_gpt-6-astra_high40_rerun').open,tracks:document.querySelector('#A4_gpt-6-astra_high40_rerun video').textTracks.length})")
   assert result['open'] and result['tracks']==2,result
   shot('desktop-sign-submission')
 report={'passed':True,'viewport_checks':checks,'all_model_switches_passed':True,'filter_counts_match':True,'event_jump_passed':True,'legacy_hash_redirect_passed':True,'deep_link_opens_submission':True,'subtitle_tracks_present':True}
 (OUT/'DOM_CHECKS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False))
 call('Browser.close');ws.close()
finally:
 if browser.poll() is None:browser.terminate()
