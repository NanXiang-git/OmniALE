from pathlib import Path
import json,shutil,hashlib,html,re
from urllib.parse import quote
from validate import Links,check_html
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];SOURCE=ROOT/'deliverables/A4_A6_research_20261021';REPO=ROOT/'publication/OmniALE';OUT=REPO/'docs'
TAG='a6-delivery-v2-20261022';RELEASE='https://github.com/NanXiang-git/OmniALE/releases/tag/'+TAG;DOWNLOAD='https://github.com/NanXiang-git/OmniALE/releases/download/'+TAG+'/A4_A6_research_20261021.zip'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
 assert (REPO/'.git').is_dir()
 page=(SOURCE/'index.html').read_text(encoding='utf-8');parser=Links();parser.feed(page)
 generated={'README.md','FILE_INDEX.html','SHA256SUMS.json','VALIDATION.json'}
 paths=parser.paths-generated;paths.update(['RESULTS.json','A6_V2_VALIDATION.json'])
 base=SOURCE/'files/evaluation_versions/20261022_a6_delivery_v2'
 paths.update(p.relative_to(SOURCE).as_posix() for p in base.rglob('*') if p.is_file())
 # Resolve every directly linked HTML report, keeping paths within the portable root.
 processed=set()
 while True:
  todo=[n for n in paths if n.endswith('.html') and n not in processed]
  if not todo:break
  for n in todo:
   processed.add(n);source=SOURCE/n;child=Links();child.feed(source.read_text(encoding='utf-8'))
   for name in child.paths:
    target=(source.parent/name).resolve();assert target.is_relative_to(SOURCE.resolve())
    paths.add(target.relative_to(SOURCE.resolve()).as_posix())
 for name in sorted(paths):
  src=SOURCE/name;assert src.is_file(),name
  assert src.stat().st_size<100*1024**2,name
  dest=OUT/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
 page=page.replace('<nav>',f'<p><a href="{DOWNLOAD}">下载当前v2完整研究包 ZIP</a> · <a href="{RELEASE}">发布记录与校验</a> · <a href="https://github.com/NanXiang-git/OmniALE">GitHub仓库</a></p><nav>',1).replace('离线浏览 · 相对路径','在线报告 · A6 v2事后复评')
 (OUT/'index.html').write_text(page,encoding='utf-8')
 readme=(SOURCE/'README.md').read_text(encoding='utf-8')+'\n[在线报告](https://nanxiang-git.github.io/OmniALE/) · [当前v2完整ZIP]('+DOWNLOAD+') · [v2发布记录]('+RELEASE+')\n\n旧版Release保留，仅用于历史复核。当前分数以v2报告为准。\n'
 for p in [OUT/'README.md',REPO/'README.md']:p.write_text(readme,encoding='utf-8')
 listing='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>在线证据文件</title><h1>当前报告引用文件</h1><p><a href="index.html">返回报告</a> · <a href="'+DOWNLOAD+'">下载完整研究包</a></p><ul>'+''.join('<li><a href="'+quote(n,safe='/')+'">'+html.escape(n)+'</a></li>' for n in sorted(paths))+'</ul></html>'
 (OUT/'FILE_INDEX.html').write_text(listing,encoding='utf-8')
 secret=re.compile(r'(?i)\bsk-[A-Za-z0-9_-]{20,}\b|Bearer\s+[A-Za-z0-9_.-]{24,}')
 for p in OUT.rglob('*'):
  if p.is_file() and p.suffix in ('.json','.jsonl','.html','.py','.md','.txt','.log','.toml','.xml','.musicxml'):
   assert not secret.search(p.read_text(encoding='utf-8-sig',errors='replace')),'Credential-shaped text; inspect without printing'
 links=sum(check_html(p) for p in [OUT/'index.html',OUT/'FILE_INDEX.html',OUT/'files/evaluation_versions/20261022_a6_delivery_v2/REPORT.html'])
 assert all(sha(SOURCE/n)==sha(OUT/n) for n in paths)
 validation=json.loads((SOURCE/'A6_V2_VALIDATION.json').read_text(encoding='utf-8'))|{'online_local_links_checked':links,'credential_scan_passed':True,'evidence_files_identical':True,'release':RELEASE}
 put(OUT/'VALIDATION.json',validation)
 put(OUT/'SHA256SUMS.json',{p.relative_to(OUT).as_posix():sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.json'})
 print(json.dumps({'site_files':len(paths),'links':links,'release':RELEASE},ensure_ascii=False))
if __name__=='__main__':main()
