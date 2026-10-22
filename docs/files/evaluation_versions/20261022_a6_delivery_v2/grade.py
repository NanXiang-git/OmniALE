"""A6 delivery-v2 aggregation; independent of model identity and old scores."""
from pathlib import Path
import json, hashlib, xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def put(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
RUBRIC=read(HERE/'rubric.json')
LABELS={'ready':'完整可用','major_revision':'需大幅修订','unusable_or_inconsistent':'不可用或实质不一致','missing_core':'缺关键交付','empty':'无可评内容'}
def aggregate(technical,review):
 if any(review.get(k) is None for k in ('layout','notation','fidelity','delivery_level')):return {'final_score':None,'reason':'Unresolved review'}
 assert all(review[k] in RUBRIC['visual_levels'] for k in ('layout','notation','fidelity'))
 level=review['delivery_level'];factor=RUBRIC['delivery_factors'][level]
 # Objective defects constrain the reviewer's delivery level; they cannot be waived.
 objective_level='ready'
 if 'xml_note_count' in technical:
  if technical['xml_note_count']==0 and technical.get('midi_note_count',0)==0:objective_level='empty'
  elif technical['xml_note_count']==0 or technical.get('midi_note_count',0)==0 or technical.get('points',{}).get('notation_review')==0:objective_level='missing_core'
 if RUBRIC['delivery_factors'][objective_level]>0.25 and technical.get('consistency_f1',0)<0.8:objective_level='unusable_or_inconsistent'
 elif RUBRIC['delivery_factors'][objective_level]>0.6 and (technical.get('consistency_f1',0)<0.95 or min(review[k] for k in ('layout','notation','fidelity'))<0.75 or technical.get('points',{}).get('notes_present',1)==0):objective_level='major_revision'
 if RUBRIC['delivery_factors'][objective_level]<factor:level=objective_level;factor=RUBRIC['delivery_factors'][level]
 metrics=technical.get('metrics',{});values=dict(metrics.get('values',{}))
 values.update(midi_xml_consistency=technical.get('consistency_f1',0),**{k:review[k] for k in ('layout','notation','fidelity')})
 components={k:weight*values.get(k,0) for k,weight in RUBRIC['weights'].items()}
 raw=sum(components.values());scaled=raw*factor
 tp=metrics.get('coarse_tp',0);precision=tp/max(1,metrics.get('predicted_count',0));recall=tp/max(1,metrics.get('reference_count',0));a=RUBRIC['acceptance']
 checks={'delivery_ready':level=='ready','pitch_precision':precision>=a['pitch_precision'],'pitch_recall':recall>=a['pitch_recall'],'strict_f1':values.get('rhythm_strict_f1',0)>=a['strict_f1'],'time_coverage':bool(metrics.get('time_bins')) and all(x['f1']>=a['minimum_time_bin_f1'] for x in metrics['time_bins']),'register_coverage':bool(metrics.get('register_bins')) and all(x['f1']>=a['minimum_register_bin_f1'] for x in metrics['register_bins']),'midi_consistency':values['midi_xml_consistency']>=a['consistency_f1'],'visual_minimum':all(review[k]>=a['minimum_visual_level'] for k in ('layout','notation','fidelity'))}
 total=scaled if all(checks.values()) else min(scaled,a['failure_cap'])
 return {'components':components,'raw_score':raw,'delivery_level':level,'delivery_label':LABELS[level],'delivery_factor':factor,'after_delivery_factor':scaled,'acceptance_checks':checks,'acceptance_cap_applied':total<scaled,'accepted':all(checks.values()) and total>=a['minimum_total'],'final_score':round(total,6),'unrounded_final_score':total,'pitch_precision':precision,'pitch_recall':recall}
def main():
 assert sha(HERE/'rubric.json')==read(HERE/'FROZEN_RULE.json')['rubric_sha256']
 decisions=read(HERE/'review_decisions.json');rows=read(HERE/'original_results.json');results=[]
 for row in rows:
  if row['case']!='A6':continue
  out=HERE/'reviews'/row['id'];sub=ROOT/row['submission'];hashes=read(out/'input_hashes.json')
  assert hashes=={p.name:sha(p) for p in sub.glob('*') if p.is_file() and p.name in ('score.pdf','score.musicxml','score.mid','notes.md','alignment.json')}
  tech=read(out/'technical.json') if (out/'technical.json').exists() else {}
  if row['score'] is None and not hashes:
   review={'reason':'历史基础设施/进程失败且无可评音乐交付，保持未评分，不把它记成能力零分。'};result={'final_score':None,'delivery_label':'未评分','accepted':False}
  else:
   review=decisions.get(row['id'])
   if review is None:
    nonempty=tech.get('xml_note_count',0)>0 or tech.get('midi_note_count',0)>0
    review={'layout':0,'notation':0,'fidelity':0,'delivery_level':'missing_core' if nonempty else 'empty','reasons':['缺少PDF，已有可解析的音乐数据仅按残缺交付计分；未凭文件存在授予谱面分。' if nonempty else '实际作答后没有非空可评音乐内容。']}
   result=aggregate(tech,review)
  xml_audit={}
  if (sub/'score.musicxml').exists():
   tree=ET.parse(sub/'score.musicxml');notes=tree.findall('.//note')
   xml_audit={'written_notes':sum(n.find('pitch') is not None for n in notes),'rests':sum(n.find('rest') is not None for n in notes),'hidden_rests':sum(n.find('rest') is not None and n.get('print-object')=='no' for n in notes),'forwards':len(tree.findall('.//forward')),'measures':len(tree.findall('.//measure')),'clefs':[ET.tostring(x,encoding='unicode') for x in tree.findall('.//clef')],'sample_measures':[ET.tostring(x,encoding='unicode') for x in tree.findall('.//measure') if x.get('number') in ('1','11','17','29','38','41')]}
  put(out/'xml_audit.json',xml_audit)
  evidence=[str(p.relative_to(ROOT)).replace('\\','/') for p in sorted(out.glob('pdf-*.png'))]
  limits=['事后制定的统一v2复评，非答题前冻结规则；未重跑或修复答卷。','本会话LLM视觉判读与既有独立评审证据结合，非新增独立评委；无完整听审或钢琴家试奏。','PDF逐页检查；XML一致性为逐系统与关键小节核对，不声称每个图形逐音穷尽验证。']
  result.update(id=row['id'],case='A6',model=row['model'],version=RUBRIC['version'],retrospective=True,old_score=row['score'],old_scorepath=row['scorepath'],submission=row['submission'],submission_sha256=hashes,rubric_sha256=sha(HERE/'rubric.json'),protocol_sha256=sha(HERE/'RUBRIC.md'),technical_path=str((out/'technical.json').relative_to(ROOT)).replace('\\','/'),review=review,evidence_pages=evidence,limits=limits,metric_errors=tech.get('errors',[]))
  put(out/'score.json',result);results.append(result)
 put(HERE/'SUMMARY.json',{'version':RUBRIC['version'],'retrospective':True,'records':results})
 print(json.dumps([{k:r.get(k) for k in ['id','old_score','raw_score','delivery_factor','final_score']} for r in results],ensure_ascii=False,indent=2))
if __name__=='__main__':main()
