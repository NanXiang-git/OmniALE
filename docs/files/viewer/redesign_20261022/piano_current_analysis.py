"""Current piano analysis uses the selected scored submissions and cited review evidence."""
def render(b,rows):
    by={r['model']:r for r in rows};a=by['gpt-6-astra'];q=a['score_detail']
    out='<section id="analysis"><h2>四、失败分析</h2><p class="lead">当前 Astra 采用 20261022_a6astra_high40 的完整答卷和补评结果；此前 14.02 分对应的旧答卷保留在历史记录。以下指标和谱面证据均对应当前表格中的提交。</p>'
    out+='<h3>1. 音符匹配与起音准确性</h3>'
    rr=[]
    for r in rows:
        s=r['score_detail'];c=s['components'];valid=not s.get('metric_errors')
        rr.append([b.esc(r['model']),f"{c['pitch_global_f1']/20:.3f}" if valid else '无法评估¹',f"{c['rhythm_strict_f1']/20:.3f}" if valid else '无法评估¹',f"{c['midi_xml_consistency']/10*100:.2f}%",b.evidence_link(r)])
    out+=b.table(['模型','音高匹配 F1 · 200ms','严格起音 F1 · 80ms','MIDI/XML 一致性','依据'],rr)
    out+='<p>F1 综合反映同音高匹配的精确率与召回率，不能单独当作音符正确率。MIDI/XML 一致性衡量两份输出是否对应，不表示它们与原演奏一致。¹ K3 的时间映射未通过规则检查，相关项目按原规则计零。</p>'
    out+=f'<p>当前 Astra 的音高匹配精确率为 {q["pitch_precision"]*100:.2f}%，召回率为 {q["pitch_recall"]*100:.2f}%；其余未匹配事件可能涉及漏音、错音或起音偏差，仍需对照原演奏复核。</p>'
    out+='<h3>2. 当前 Astra 的谱面与交付等级</h3><p>配置 API 的评审失败后，按用户要求由当前 Codex 会话直接单评，逐页检查提交 PDF，并独立渲染 MusicXML 对照。此次评分使用答题前已冻结的 A6-delivery-v2.0，沿用原权重、档位和封顶规则；没有采用外部 Sol 评审结果。</p><ul>'
    out+=''.join('<li>'+b.esc(s)+'</li>' for s in q['review']['reasons'])+'</ul>'
    out+=f'<p>加权原始分 {q["raw_score"]:.6f} × 交付系数 {q["delivery_factor"]}，最终为 <strong>{q["final_score"]:.6f} / 100</strong>；交付等级为“{b.esc(q["delivery_label"])}”。'+('未满足合格底线，额外应用 59 分封顶。' if q['acceptance_cap_applied'] else '')+'</p>'
    out+='<div class="figures">'
    from PIL import Image
    for model,label in [('gpt-6-astra','当前 Astra'),('gpt-6-sol','当前 Sol')]:
        row=by[model];source=row['score_detail']['evidence_pages'][0]
        dest=b.OUT/'assets'/('evidence-'+model+'.png');im=Image.open(b.ROOT/source);w,h=im.size;im.crop((0,0,w,int(h*.38))).save(dest)
        b.ASSETS.add(dest.relative_to(b.OUT).as_posix())
        out+='<figure><a href="'+b.ensure(source)+'"><img loading="lazy" src="../assets/'+dest.name+'" alt="'+label+' 原提交 PDF 第 1 页局部"></a><figcaption>'+label+' 原提交 PDF 第 1 页局部，点击查看整页。</figcaption></figure>'
    out+='</div>'+b.link(a['scorepath'],'本次逐项评分')+' · '+b.link(a['review_report_path'],'本次完整评审与页码证据')
    out+='<h3>3. 其他交付仍需返工</h3><p>Sol 的谱面较清楚，但音符匹配覆盖不足，部分跨拍附点时值需要重写。GLM 的 PDF 存在超出谱表、边界裁切和重叠；Luna 的谱号、拍号与变音记号不完整，MIDI/XML 一致性也很低。K3 的 PDF 与 XML 在第 17、38 小节有实质差异，时间映射锚点间隔还违反题目要求。这些记录沿用原有评分，未因本次 Astra 补评而修改。</p>'
    out+='<h3>后续需要补的工作</h3><p>按原演奏核对音符与起音，整理节奏、声部及排版，再从同一份谱导出 PDF 和 MIDI，并逐页核对。当前排序仅反映各自采用的一次交付，不能据此证明模型间的稳定差异。</p><p>本次评审包含谱面检查和机器匹配，没有完整听审或钢琴家试奏。旧 Astra 的 PDF 缺字结论只适用于历史答卷，不作为本次评分依据。</p></section>'
    return out
