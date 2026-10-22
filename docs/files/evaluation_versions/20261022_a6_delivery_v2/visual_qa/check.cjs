const fs=require('fs');
(async()=>{
 const pages=await (await fetch('http://127.0.0.1:9876/json')).json();const page=pages.find(x=>x.type==='page');
 const ws=new WebSocket(page.webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
 let id=0;const pending=new Map();ws.onmessage=e=>{let x=JSON.parse(e.data);if(pending.has(x.id)){pending.get(x.id)(x);pending.delete(x.id)}};
 async function call(method,params={}){let n=++id;const p=new Promise(r=>pending.set(n,r));ws.send(JSON.stringify({id:n,method,params}));const x=await p;if(x.error)throw Error(JSON.stringify(x.error));return x.result}
 await call('Page.enable');await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1500,deviceScaleFactor:1,mobile:false});
 await call('Page.navigate',{url:'http://127.0.0.1:8766/index.html'});
 for(let i=0;i<30;i++){const v=await call('Runtime.evaluate',{expression:'document.readyState'});if(v.result.value==='complete')break;await new Promise(r=>setTimeout(r,500))}
 const v=await call('Runtime.evaluate',{expression:"document.documentElement.style.scrollBehavior='auto';document.getElementById('A6').scrollIntoView();JSON.stringify({title:document.title,table:document.querySelector('#A6 table').innerText,scrollY:scrollY})",returnByValue:true});
 fs.writeFileSync(__dirname+'/dom.json',v.result.value);await new Promise(r=>setTimeout(r,1500));
 const shot=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(__dirname+'/a6-report.png',Buffer.from(shot.data,'base64'));console.log(v.result.value);ws.close();
})().catch(e=>{console.error(e);process.exit(1)});
