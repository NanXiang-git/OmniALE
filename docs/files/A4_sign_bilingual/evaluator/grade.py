"""Strict hybrid grader. No keyword/BLEU proxy is presented as sign understanding.
Run template -> two independent evidence-bound reviews -> grade.
Only stdlib and ffmpeg/ffprobe. Submitted files are data and never executed.
"""
from pathlib import Path
import argparse, hashlib, json, math, re, subprocess, sys

HERE=Path(__file__).resolve().parent
FILES=("zh-CN.srt","en.srt","segments.json","subtitled.mkv")
ERRORS={"polarity_flip","wrong_person","wrong_time","wrong_object","invented_fact",
        "question_as_fact","request_as_fact","aspect_flip","cross_clip_story"}
def read(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding="utf-8")
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()
def require(ok,msg):
    if not ok: raise ValueError(msg)
def command(args):
    return subprocess.check_output(args,stderr=subprocess.PIPE,timeout=120)
def finite(x): return type(x) in (int,float) and math.isfinite(x)
def fingerprint(folder):
    return {n:sha(folder/n) if (folder/n).is_file() else None for n in FILES}
def parse_srt(path):
    text=path.read_text(encoding="utf-8-sig").replace("\r\n","\n").strip()
    require(bool(text),"Empty SRT")
    cues=[]
    pattern=r"(\d{2,}):([0-5]\d):([0-5]\d),(\d{3})"
    def sec(g): return int(g[0])*3600+int(g[1])*60+int(g[2])+int(g[3])/1000
    for i,block in enumerate(re.split(r"\n\s*\n",text),1):
        a=block.splitlines()
        require(len(a)>=3 and a[0]==str(i),"SRT indices must be consecutive from 1")
        m=re.fullmatch(pattern+r" --> "+pattern,a[1])
        require(m is not None,"Invalid SRT timestamp")
        start,end=sec(m.groups()[:4]),sec(m.groups()[4:])
        require(end>start and (not cues or start>=cues[-1]["end"]-0.001),"Invalid/overlapping SRT")
        require(bool("\n".join(a[2:]).strip()),"Empty cue")
        cues.append({"id":i,"start":start,"end":end,"text":"\n".join(a[2:])})
    return cues
def review_template(truth,folder):
    return {"reviewer_id":"","reviewer_kind":"human_csl or model_assisted",
            "video_watched_in_full":False,"source_annotations_checked":False,
            "truth_sha256":sha(HERE/"truth.json"),"submission_sha256":fingerprint(folder),
            "units":[{"id":u["id"],"zh":[None]*len(u["slots"]),
                      "en":[None]*len(u["slots"]),"bilingual":None,"alignment":None,
                      "errors":[],"note":"","zh_quote":"","en_quote":""} for u in truth["units"]]}

def inspect(folder,truth,media=True):
    result={"issues":[],"technical_points":0,"readability_points":0}
    cues={}; mapping={}
    for lang,name in (("zh","zh-CN.srt"),("en","en.srt")):
        try:
            cues[lang]=parse_srt(folder/name)
            require(cues[lang][-1]["end"]<=truth["duration"]+0.1,"Cue beyond video")
        except (ValueError,OSError) as e: result["issues"].append(f"{lang}: {e}"); cues[lang]=[]
    try:
        entries=read(folder/"segments.json")["segments"]
        require(len(entries)==len(truth["units"]),"Wrong segment count")
        mapping={x["id"]:x for x in entries}
        require(set(mapping)=={u["id"] for u in truth["units"]},"Unknown/duplicate/missing segment")
        for lang in ("zh","en"):
            seen=[]
            for u in truth["units"]:
                x=mapping[u["id"]]; ids=x[lang+"_cues"]
                require(isinstance(ids,list) and all(type(i)==int and 1<=i<=len(cues[lang]) for i in ids),"Invalid cue references")
                require(ids==sorted(set(ids)),"Duplicate/unordered cue reference")
                seen+=ids
                c=x["confidence_"+lang]
                require(finite(c) and 0<=c<=1,"Confidence must be finite in [0,1]")
                require(isinstance(x.get("uncertainty"),str),"Missing uncertainty string")
            require(sorted(seen)==list(range(1,len(cues[lang])+1)),"Every cue must be mapped exactly once")
    except (KeyError,TypeError,ValueError,OSError) as e:
        result["issues"].append(f"mapping: {e}");mapping={}
    penalties=[]
    for lang in ("zh","en"):
        bad=0
        for c in cues[lang]:
            lines=c["text"].splitlines();duration=c["end"]-c["start"]
            count=len(re.sub(r"\s","",c["text"])) if lang=="zh" else len(c["text"].replace("\n"," "))
            excess=(len(lines)>2 or max(map(len,lines))>(22 if lang=="zh" else 42)
                    or duration<0.8 or duration>7 or count/duration>(9 if lang=="zh" else 20))
            bad+=int(excess)
        penalties.append(1-bad/len(cues[lang]) if cues[lang] else 0)
    result["readability_points"]=5*min(penalties)
    if all(cues.values()) and mapping: result["technical_points"]=1
    result["localization"]={}
    for u in truth["units"]:
        scores=[]
        for lang in ("zh","en"):
            ids=mapping.get(u["id"],{}).get(lang+"_cues",[])
            selected=[cues[lang][i-1] for i in ids]
            # Clip windows are known exactly. Sign onset/offset must be watched by the reviewer.
            if not selected: scores.append(0);continue
            total=sum(c["end"]-c["start"] for c in selected)
            inside=sum(max(0,min(c["end"],u["end"])-max(c["start"],u["start"])) for c in selected)
            fraction=inside/total
            scores.append(1 if fraction>=0.98 else 0.5 if fraction>=0.90 else 0)
        result["localization"][u["id"]]=min(scores)
    if media:
        try:
            video=folder/"subtitled.mkv"
            p=json.loads(command(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(video)]))
            streams=p["streams"]; vs=[s for s in streams if s["codec_type"]=="video"]
            ss=[s for s in streams if s["codec_type"]=="subtitle"]
            require(len(vs)==1 and len(ss)==2 and not any(s["codec_type"]=="audio" for s in streams),"Need 1 video, 2 selectable subtitle tracks, no audio")
            require(abs(float(p["format"]["duration"])-truth["duration"])<=0.15,"Video duration mismatch")
            result["technical_points"]+=1
            src=HERE.parent/"candidate/input/source.mp4"
            def video_hash(p):
                return command(["ffmpeg","-v","error","-i",str(p),"-map","0:v:0","-an",
                                "-pix_fmt","yuv420p","-f","hash","-hash","sha256","-"]).decode().strip()
            require(video_hash(src)==video_hash(video),"Decoded video changed: use video stream copy")
            result["technical_points"]+=1
            import tempfile
            for lang,tag in (("zh","zho"),("en","eng")):
                selected=[s for s in ss if s.get("tags",{}).get("language")==tag]
                require(len(selected)==1,f"Missing {tag} subtitle language metadata")
                with tempfile.TemporaryDirectory() as tmp:
                    out=Path(tmp)/"sub.srt"
                    command(["ffmpeg","-v","error","-i",str(video),"-map",f"0:{selected[0]['index']}","-c:s","srt",str(out)])
                    extracted=parse_srt(out)
                require(len(extracted)==len(cues[lang]),f"{lang} embedded subtitle count mismatch")
                require(all(a["text"]==b["text"] and abs(a["start"]-b["start"])<=0.05
                            and abs(a["end"]-b["end"])<=0.05 for a,b in zip(extracted,cues[lang])),
                        f"{lang} embedded subtitle mismatch")
                result["technical_points"]+=1
        except (OSError,ValueError,KeyError,subprocess.SubprocessError) as e:
            result["issues"].append("media: "+str(e)[:500])
    return result,cues,mapping

def validate_review(r,truth,folder,cues,mapping):
    require(isinstance(r["reviewer_id"],str) and bool(r["reviewer_id"].strip()),"Missing reviewer id")
    require(r["reviewer_kind"] in ("human_csl","model_assisted"),"Invalid reviewer kind")
    require(r["video_watched_in_full"] is True and r["source_annotations_checked"] is True,"Reviewer must inspect actual video and annotation")
    require(r["truth_sha256"]==sha(HERE/"truth.json"),"Stale truth reference")
    require(r["submission_sha256"]==fingerprint(folder),"Review belongs to different submission")
    require(len(r["units"])==len(truth["units"]),"Incomplete review")
    by={x["id"]:x for x in r["units"]}
    require(set(by)=={u["id"] for u in truth["units"]},"Missing/duplicate review units")
    for u in truth["units"]:
        x=by[u["id"]]
        for lang in ("zh","en"):
            scores=x[lang]
            require(len(scores)==len(u["slots"]) and all(type(v) in (float,int) and v in (0,.5,1) for v in scores),"Use 0, .5, 1 per slot")
            ids=mapping.get(u["id"],{}).get(lang+"_cues",[])
            actual="\n".join(cues[lang][i-1]["text"] for i in ids)
            require(x[lang+"_quote"]==actual,"Evidence quote must exactly match mapped submitted cues")
            require(bool(actual) or not any(scores),"Cannot award credit for absent subtitles")
        require(type(x["bilingual"]) in (int,float) and x["bilingual"] in (0,.5,1),"Invalid bilingual score")
        require(type(x["alignment"]) in (int,float) and x["alignment"] in (0,.5,1),"Invalid alignment score")
        require(isinstance(x["errors"],list) and len(set(x["errors"]))==len(x["errors"]) and set(x["errors"])<=ERRORS,"Unknown/duplicate critical error")
        require(isinstance(x["note"],str) and len(x["note"].strip())>=12,"Need concrete evidence rationale, minimum 12 characters")
    return by

def aggregate(truth,ratings,tech,mapping):
    semantic=[];bilingual=[];timing=[];calibration=[];critical=[];confident_wrong=[]
    for u in truth["units"]:
        x=ratings[u["id"]]; ws=[s["weight"] for s in u["slots"]];den=sum(ws)
        scores={lang:sum(w*s for w,s in zip(ws,x[lang]))/den for lang in ("zh","en")}
        paired=sum(w*min(z,e) for w,z,e in zip(ws,x["zh"],x["en"]))/den
        semantic.append(paired)
        bilingual.append(min(x["bilingual"],paired)) # two equally wrong translations earn no equivalence credit
        timing.append(min(x["alignment"],tech["localization"][u["id"]]))
        for lang in ("zh","en"):
            c=mapping.get(u["id"],{}).get("confidence_"+lang,0)
            calibration.append(1-(c-scores[lang])**2)
            if c>=.9 and scores[lang]<.5: confident_wrong.append(u["id"]+":"+lang)
        if x["errors"]: critical.append({"id":u["id"],"errors":x["errors"],"note":x["note"]})
    avg=lambda a:sum(a)/len(a)
    points={"meaning":65*avg(semantic),"bilingual":8*avg(bilingual),"timing":12*avg(timing),
            "readability":tech["readability_points"],"delivery":tech["technical_points"],
            "calibration":5*avg(calibration)}
    caps=[]
    if critical: caps.append((59 if len(critical)==1 else 39,"critical_semantic_error"))
    if avg(semantic)<.5: caps.append((39,"semantic_coverage_below_half"))
    if len(confident_wrong)>=2: caps.append((49,"repeated_high_confidence_error"))
    if tech["technical_points"]<5: caps.append((79,"incomplete_or_changed_deliverable"))
    raw=sum(points.values());score=min([raw]+[c[0] for c in caps])
    passed=(score>=90 and points["meaning"]>=61.75 and points["bilingual"]>=7.6
            and points["timing"]>=10.8 and points["delivery"]==5 and not critical)
    return {"score":round(score,3),"raw_score":round(raw,3),"passed":passed,
            "components":{k:round(v,3) for k,v in points.items()},"caps":caps,
            "critical_errors":critical,"high_confidence_errors":confident_wrong,
            "unit_semantic_scores":dict(zip([u["id"] for u in truth["units"]],semantic))}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("mode",choices=["preflight","template","grade"])
    ap.add_argument("--submission",type=Path,required=True)
    ap.add_argument("--reviews",type=Path,nargs=2)
    ap.add_argument("--adjudication",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args();truth=read(HERE/"truth.json")
    require(sha(HERE.parent/"candidate/input/source.mp4")==truth["source_sha256"],"Input video changed")
    if a.mode=="template":
        write(a.output,review_template(truth,a.submission));return
    tech,cues,mapping=inspect(a.submission,truth)
    if a.mode=="preflight":
        write(a.output,{"status":"technical_only_not_a_total_score","total_score":None,**tech});return
    require(a.reviews is not None,"Two independent reviews required")
    require(bool(mapping),"Invalid submission mapping; fix before semantic grading")
    rr=[read(p) for p in a.reviews]
    require(rr[0]["reviewer_id"]!=rr[1]["reviewer_id"],"Two different reviewers required")
    bb=[validate_review(r,truth,a.submission,cues,mapping) for r in rr]
    fields=("zh","en","bilingual","alignment","errors")
    conflicts=[u["id"] for u in truth["units"] if any(bb[0][u["id"]][k]!=bb[1][u["id"]][k] for k in fields)]
    chosen=bb[0]
    if conflicts:
        if not a.adjudication:
            write(a.output,{"status":"needs_adjudication","score":None,"conflicts":conflicts,"technical":tech});return
        adj=read(a.adjudication)
        require(adj["reviewer_id"] not in {r["reviewer_id"] for r in rr},"Adjudicator must be independent")
        ab=validate_review(adj,truth,a.submission,cues,mapping)
        for uid in conflicts: chosen[uid]=ab[uid]
    result=aggregate(truth,chosen,tech,mapping)
    result.update({"status":"scored","review_quality":"expert_reviewed" if all(r["reviewer_kind"]=="human_csl" for r in rr)
                   and (not conflicts or adj["reviewer_kind"]=="human_csl") else "model_assisted_not_expert_certified",
                   "technical":tech,"submission_sha256":fingerprint(a.submission),
                   "truth_sha256":sha(HERE/"truth.json"),"conflicts_adjudicated":conflicts})
    write(a.output,result)
    print(json.dumps({"status":result["status"],"score":result["score"],"passed":result["passed"]}))

if __name__=="__main__":
    try: main()
    except Exception as e:
        print(json.dumps({"status":"invalid_or_incomplete","error":str(e)},ensure_ascii=True),file=sys.stderr)
        sys.exit(2)
