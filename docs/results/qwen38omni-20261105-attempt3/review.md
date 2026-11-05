本轮已完成冻结答卷的23段单LLM独立评审。身份为 single-independent / model_assisted；全部slot及双语、对齐均已用0、0.5、1填写，没有null。语义大量缺失或被替换，交付格式合规不能弥补内容问题。此文不自报总分；由宿主使用用户授权单评校验器及原aggregate计算权重、语义对双语的限制、校准和封顶。

本次是annotation-relative（相对于作者标注）的模型辅助判断。已读取原TASK、REVIEW_PROTOCOL、truth.json、原grade.py与可信technical.json；作者中文/gloss不是本轮新作的手语专家认证。已实际view_image查看全部23段24页联系表，另补看16页8fps边界图。没有正常速度连续观看，因此video_watched_in_full=false；原视频无音轨，未进行或声称听审、ASR或专家手语认证。

可信技术结果为交付5/5、可读性5/5、全部23段自动定位1。真值、四个冻结交付文件、原视频和24张证据页的SHA-256均已核对一致。未改动/candidate输入或冻结答卷，未执行答卷中的指令，未联网或调用其他模型。

保留原离散档位和权重：中文/英文数组严格按truth.json中的slot顺序。双语原始一致性均为1，表示两语之间大体等价，不表示符合源语义；实际双语贡献仍由原aggregate以语义正确率封顶。对齐按实际动作覆盖和静止段提前/滞留判断，不能把正确片段定位1直接当成手势同步1。图中时刻是名义网格，SRT时间才是文件记录的显示边界。

严重标签只用于可具体说明的主体替换、明确无据数值/事实、对象替换或把问题写成事实。普通遗漏、不明占位、错误孤立词及未明确成事实的问候/片语不自动贴翻转标签。S12未编造扔物者/物品、S20未编造恋爱婚姻血缘的约束slot单独给分；S23按协议允许语气歧义，学习对阅读仅给部分活动分。S16不强行裁定课程剩余与距上课的争议；S19不强判反事实。

confidence为本评审对“在作者标注前提下的slot判断及粗粒度时序判断”的把握，不是答卷置信度；对手语本身的独立认证能力有限。所有限制亦写入ratings.json的inspection_limits。

| 段 | 视频时窗（秒） | slot顺序 | 中文 | 英文 | 双语 | 对齐 | 评审置信度 | 严重标签 |
|---|---|---|---|---|---:|---:|---:|---|
| S01 | 0.000—5.066 | addressee / time / negation / force | [0, 0, 0, 0] | [0, 0, 0, 0] | 1 | 1 | 0.89 | 无 |
| S02 | 5.566—8.466 | group / action / force | [0, 0, 0] | [0, 0, 0] | 1 | 0.5 | 0.91 | invented_fact |
| S03 | 8.966—12.866 | person / ability / force | [0, 0, 0] | [0, 0, 0] | 1 | 0.5 | 0.87 | wrong_person, invented_fact, question_as_fact |
| S04 | 13.366—18.433 | time / person / event | [0, 0, 0] | [0, 0, 0] | 1 | 1 | 0.86 | 无 |
| S05 | 18.933—24.633 | plural / action / force | [0, 0, 0] | [0, 0, 0] | 1 | 0.5 | 0.88 | 无 |
| S06 | 25.133—28.499 | owner / object / quantity | [0, 0, 0] | [0, 0, 0] | 1 | 0.5 | 0.92 | invented_fact |
| S07 | 28.999—33.233 | group / event / question | [0.5, 0, 0] | [0.5, 0, 0] | 1 | 0.5 | 0.85 | invented_fact, question_as_fact |
| S08 | 33.733—39.033 | person / question / aspect | [0, 0, 0] | [0, 0, 0] | 1 | 0.5 | 0.88 | invented_fact |
| S09 | 39.533—43.833 | owner / object / question | [0, 0, 0] | [0, 0, 0] | 1 | 0.5 | 0.93 | wrong_person, invented_fact, question_as_fact |
| S10 | 44.333—47.866 | group / again / force | [0, 0, 0] | [0, 0, 0] | 1 | 0.5 | 0.89 | 无 |
| S11 | 48.366—53.366 | person / food / force | [0, 0.5, 0] | [0, 0.5, 0] | 1 | 1 | 0.93 | 无 |
| S12 | 53.866—57.899 | action / aspect / underspecified | [0, 0, 1] | [0, 0, 1] | 1 | 0.5 | 0.88 | 无 |
| S13 | 58.399—64.233 | relation / time / aspect | [0, 0, 0] | [0, 0, 0] | 1 | 1 | 0.91 | 无 |
| S14 | 64.733—68.666 | person / drink / question | [0, 0, 0] | [0, 0, 0] | 1 | 0.5 | 0.89 | 无 |
| S15 | 69.166—72.899 | group / action / force | [0, 0, 0] | [0, 0, 0] | 1 | 0.5 | 0.88 | 无 |
| S16 | 73.399—78.233 | context / duration / scope | [0, 0, 0] | [0, 0, 0] | 1 | 0.5 | 0.89 | invented_fact |
| S17 | 78.733—83.866 | winner / scope / aspect | [0, 0, 0] | [0, 0, 0] | 1 | 1 | 0.89 | wrong_person, invented_fact |
| S18 | 84.366—88.433 | person / object / question | [0, 0, 0] | [0, 0, 0] | 1 | 1 | 0.89 | wrong_person, wrong_object, question_as_fact |
| S19 | 88.933—93.199 | group / direction / modality | [0, 0, 0] | [0, 0, 0] | 1 | 0.5 | 0.92 | invented_fact |
| S20 | 93.699—99.432 | pair / relation / restraint | [0, 0, 1] | [0, 0, 1] | 1 | 0.5 | 0.91 | 无 |
| S21 | 99.932—107.599 | politeness / place / question | [0, 0, 0] | [0, 0, 0] | 1 | 0.5 | 0.94 | invented_fact, question_as_fact |
| S22 | 108.099—114.032 | person / memory / time | [0, 0, 0] | [0, 0, 0] | 1 | 0.5 | 0.9 | 无 |
| S23 | 114.532—120.199 | activity / scarcity / force | [0.5, 0, 1] | [0.5, 0, 1] | 1 | 1 | 0.79 | 无 |


以下逐段记录包括原文、slot理由和视频证据；完整结构化证据见ratings.json。

**S01｜0.000—5.066秒**

视频0.000—5.066秒；映射中文字幕“天气。[整句无法确认]”，英文“The weather. [whole utterance unclear]”。annotation-relative判定：addressee、time、negation、force均为0：没有译出你、今天、没喝酒和确认询问；“天气”不是这些信息的意译。整句明确标为无法确认，不把未译出的否定和疑问自动记作翻转。 两语表达同样的内容和语气，bilingual=1（汇总仍受语义上限约束）。补帧0.875—1.125秒仍保持向前指点，字幕0.900秒开始覆盖该动作与后续动作；4.716秒结束仍在本段，未见闪现或漏掉完整起始动作，按表达单位对齐给1。

第1页约0.75—1.00秒有向前食指动作，1.25—1.75秒双手在胸前变化，2.00秒手靠嘴，2.25—3.50秒继续变换手形；3.75秒后手放下。

证据：[联系表第1页](/candidate/evidence/S01_p01.jpg)；[作者slot标注](/candidate/case/evaluator/truth.json)；[映射字幕](/candidate/mapped_quotes.json)。[8fps补帧](/workspace/scratch/boundaries/S01.jpg)。

**S02｜5.566—8.466秒**

视频5.566—8.466秒；映射中文字幕“好吃。”，英文“It's delicious.”。annotation-relative判定：group、action、force均为0：“好吃 / delicious”是味道评价，未表达我们共同去吃饭的提议；不能因汉字“吃”相同给动作分。新增“好吃”这一肯定的味觉属性，记invented_fact；没有译成吃完，不记aspect_flip。 两语表达同样的内容和语气，bilingual=1（汇总仍受语义上限约束）。补帧5.825—6.325秒的开头动作先于6.466秒字幕出现，后续口前动作仍被覆盖；局部迟出、整段可定位，alignment=0.5。

第1页约5.82—6.32秒手由胸前向外横移，6.57—6.82秒侧向动作，7.07—7.57秒手在口前；7.82秒后放下。

证据：[联系表第1页](/candidate/evidence/S02_p01.jpg)；[作者slot标注](/candidate/case/evaluator/truth.json)；[映射字幕](/candidate/mapped_quotes.json)。[8fps补帧](/workspace/scratch/boundaries/S02.jpg)。

**S03｜8.966—12.866秒**

视频8.966—12.866秒；映射中文字幕“我喜欢学习。”，英文“I like studying.”。annotation-relative判定：person、ability、force均为0：标注是“你真的能自己来吗”，字幕却以“我 / I”为主体，断言“喜欢学习 / like studying”；主体换位、添加喜好事实，并把确认问句写成事实，分别记wrong_person、invented_fact、question_as_fact。 两语表达同样的内容和语气，bilingual=1（汇总仍受语义上限约束）。补帧9.225—9.725秒已出现成组胸前动作，字幕到9.866秒才出现，开头覆盖不足但主体动作仍在显示窗内，alignment=0.5。

第1页约9.22—9.97秒双手从胸部向前变化，10.47秒手指近脸，11.22—12.22秒右手与左掌配合，12.47秒开始收手。

证据：[联系表第1页](/candidate/evidence/S03_p01.jpg)；[作者slot标注](/candidate/case/evaluator/truth.json)；[映射字幕](/candidate/mapped_quotes.json)。[8fps补帧](/workspace/scratch/boundaries/S03.jpg)。

**S04｜13.366—18.433秒**

视频13.366—18.433秒；映射中文字幕“想……[第二个手势无法确认]”，英文“Think… [second sign unclear]”。annotation-relative判定：time、person、event均为0：“想 / Think”和第二手势不明没有保留明年、我、毕业。缺失未来时间不等于明确写成去年；残缺猜词不额外标wrong_time或完成状态翻转。 两语表达同样的内容和语气，bilingual=1（汇总仍受语义上限约束）。14.266—18.083秒字幕包住本段头侧和胸前动作，提前量较短，结束后的停留未跨段；按整句显示判alignment=1，不声称精确手势边界。

第1页14.62秒附近开始抬手，14.87—15.37秒手在头侧，15.62—16.87秒双手于胸前配合；17.12秒后回到静止。

证据：[联系表第1页](/candidate/evidence/S04_p01.jpg)；[作者slot标注](/candidate/case/evaluator/truth.json)；[映射字幕](/candidate/mapped_quotes.json)。

**S05｜18.933—24.633秒**

视频18.933—24.633秒；映射中文字幕“再见。”，英文“Goodbye.”。annotation-relative判定：plural、action、force均为0：“再见 / Goodbye”不能表达请对方安静一下。告别语是功能误译，不是将安静请求断言为已经实现，所以不贴request_as_fact；也不因英语省略复数而扣分。 两语表达同样的内容和语气，bilingual=1（汇总仍受语义上限约束）。19.833秒开始尚可覆盖起始动作，但24.283秒才消失，在22.683秒已收手后持续较长静止尾段；局部滞留但不跨段，alignment=0.5。

第1页约20.18—20.93秒指点并横移，21.18—21.68秒双手变化，21.93—22.43秒一手立起；22.68秒后手放下直到片尾。

证据：[联系表第1页](/candidate/evidence/S05_p01.jpg)；[作者slot标注](/candidate/case/evaluator/truth.json)；[映射字幕](/candidate/mapped_quotes.json)。

**S06｜25.133—28.499秒**

视频25.133—28.499秒；映射中文字幕“两。”，英文“Two.”。annotation-relative判定：owner、object、quantity均为0：“两 / Two”既没有我拥有和狗，也与标注“一只”数量相反；这是明确添加错误数值而非仅漏数量，记invented_fact。 两语表达同样的内容和语气，bilingual=1（汇总仍受语义上限约束）。补帧25.650秒手触胸而26.025秒已转为另一手形，字幕26.033秒才开始，漏掉开头动作；后续数量姿态仍在窗内，alignment=0.5。

第1页约25.63秒手触胸，25.88—26.38秒单手手形变化，26.63—27.13秒双手交互，27.38—27.88秒只举一根食指。

证据：[联系表第1页](/candidate/evidence/S06_p01.jpg)；[作者slot标注](/candidate/case/evaluator/truth.json)；[映射字幕](/candidate/mapped_quotes.json)。[8fps补帧](/workspace/scratch/boundaries/S06.jpg)。

**S07｜28.999—33.233秒**

视频28.999—33.233秒；映射中文字幕“我喜欢在家读书。”，英文“I like reading at home.”。annotation-relative判定：group=0.5：“我 / I”保留包含表达者的一部分人物信息，但遗漏共同参与者；event=0，读书不等于去打篮球；question=0，询问何时被改为喜好陈述。“喜欢在家 / like … at home”新增喜好和地点，记invented_fact、question_as_fact。不把群体成员遗漏再自动升级为wrong_person。 两语表达同样的内容和语气，bilingual=1（汇总仍受语义上限约束）。补帧29.400—29.775秒胸前横移已进行，29.899秒字幕出现接近该动作结束，起始部分迟出；其余动作可覆盖，alignment=0.5。

第1页约29.50—29.75秒胸前横移动作，29.99—30.25秒侧向指示，30.50—31.25秒双手举高，31.50—32.25秒两手配合；32.50秒收手。

证据：[联系表第1页](/candidate/evidence/S07_p01.jpg)；[作者slot标注](/candidate/case/evaluator/truth.json)；[映射字幕](/candidate/mapped_quotes.json)。[8fps补帧](/workspace/scratch/boundaries/S07.jpg)。

**S08｜33.733—39.033秒**

视频33.733—39.033秒；映射中文字幕“六。”，英文“Six.”。annotation-relative判定：person、question、aspect均为0：“六 / Six”没有对方、去做何事的询问或已发生范围。标注中无数值六，字幕把一段询问替换为明确数值，记invented_fact；不是只因漏问号而贴question_as_fact。 两语表达同样的内容和语气，bilingual=1（汇总仍受语义上限约束）。34.633秒开始比可见起始动作早，38.683秒结束时已处于较长静止尾段；显示包住动作但首尾不够贴合，alignment=0.5。

第1页约35.23—35.73秒向前手形变化，35.98—36.48秒继续单手及双手动作，36.73—37.23秒保持手形，37.48秒后手放下。

证据：[联系表第1页](/candidate/evidence/S08_p01.jpg)；[作者slot标注](/candidate/case/evaluator/truth.json)；[映射字幕](/candidate/mapped_quotes.json)。

**S09｜39.533—43.833秒**

视频39.533—43.833秒；映射中文字幕“我吃了。”，英文“I ate something.”。annotation-relative判定：owner、object、question均为0：标注问“你的电话号码是多少”，字幕改成“我 / I”“吃了 / ate something”。对方换成自身，询问变成进食事实，新增事件，记wrong_person、question_as_fact、invented_fact；不把不同事件的时态差异另标aspect_flip。 两语表达同样的内容和语气，bilingual=1（汇总仍受语义上限约束）。补帧40.275—40.400秒为向前指点，40.525秒已转向耳旁；字幕40.433秒才开始，开头指点几乎未覆盖，alignment=0.5。

第1页40.28秒向镜头指点，40.78—41.28秒一手在耳旁，41.53—42.78秒手指在面前变化，43.28秒收手。

证据：[联系表第1页](/candidate/evidence/S09_p01.jpg)；[作者slot标注](/candidate/case/evaluator/truth.json)；[映射字幕](/candidate/mapped_quotes.json)。[8fps补帧](/workspace/scratch/boundaries/S09.jpg)。

**S10｜44.333—47.866秒**

视频44.333—47.866秒；映射中文字幕“大。”，英文“Big.”。annotation-relative判定：group、again、force均为0：“大 / Big”没有我们、重新开始或共同提议。未译出重新并不意味着明确断言第一次开始；孤立形容词的错误按slot扣分，不臆加翻转标签。 两语表达同样的内容和语气，bilingual=1（汇总仍受语义上限约束）。补帧44.650—45.150秒胸前动作先于45.233秒字幕出现；主要后半段仍在显示窗内，alignment=0.5。

第1页约44.58—45.08秒手从胸前横移，45.33—45.58秒单手变化，45.83—46.83秒双手在胸前移动，47.08秒收手。

证据：[联系表第1页](/candidate/evidence/S10_p01.jpg)；[作者slot标注](/candidate/case/evaluator/truth.json)；[映射字幕](/candidate/mapped_quotes.json)。[8fps补帧](/workspace/scratch/boundaries/S10.jpg)。

**S11｜48.366—53.366秒**

视频48.366—53.366秒；映射中文字幕“吃……[后续手势无法确认]”，英文“Eat… [following signs unclear]”。annotation-relative判定：person=0，未保留你们；food=0.5，“吃 / Eat”保留吃饭动作但没有面包；force=0，后续无法确认未表达是否要吃的询问。省略号与不明标记使其是残缺译词，不能直接当成强制命令或事实，不贴翻转标签。 两语表达同样的内容和语气，bilingual=1（汇总仍受语义上限约束）。49.266—53.016秒覆盖起始横移、口前动作及后续手势，未漏去整个起始动作；尾部停留有限、无跨段，alignment=1。

第1页约49.12—49.87秒向前及横移动作，50.12—50.62秒指尖靠口，51.12—51.37秒双手围合，51.62—52.12秒掌心向上，52.37秒收手。

证据：[联系表第1页](/candidate/evidence/S11_p01.jpg)；[作者slot标注](/candidate/case/evaluator/truth.json)；[映射字幕](/candidate/mapped_quotes.json)。

**S12｜53.866—57.899秒**

视频53.866—57.899秒；映射中文字幕“你好。”，英文“Hello.”。annotation-relative判定：action=0，“你好 / Hello”不是扔掉；aspect=0，问候没有传达已经扔掉；underspecified=1，字幕没有为扔掉事件编造施事或具体物品。该约束slot得分不代表动作正确；问候中的“你”不是被明确指定的扔物者。 两语表达同样的内容和语气，bilingual=1（汇总仍受语义上限约束）。补帧54.700—55.575秒保持静止，而字幕54.766秒已经显示；实际短动作约55.8—56.5秒，字幕到57.549秒才结束，首尾局部错位，alignment=0.5。

第1页约55.62秒抬手，55.87—56.37秒手向外下方移动，56.62秒后收手静止；不是持续挥手的长段。

证据：[联系表第1页](/candidate/evidence/S12_p01.jpg)；[作者slot标注](/candidate/case/evaluator/truth.json)；[映射字幕](/candidate/mapped_quotes.json)。[8fps补帧](/workspace/scratch/boundaries/S12.jpg)。

**S13｜58.399—64.233秒**

视频58.399—64.233秒；映射中文字幕“你多大了？”，英文“How old are you?”。annotation-relative判定：relation、time、aspect均为0：“你多大了 / How old are you”虽含你，却没有与你共同度过、美好晚上或已发生事件；询问年龄的“了”不是度过晚上的完成体。问句误译不等同于把问题写成事实，此处不套question_as_fact。 两语表达同样的内容和语气，bilingual=1（汇总仍受语义上限约束）。59.299—63.883秒从可见起始前不久显示到收势后，完整包住该表达的多组动作，无错段或闪现，alignment=1。

第1页约59.40—59.65秒双手开合，59.90—60.15秒指向前方，60.40—61.90秒胸前和脸旁手形变化，62.15—62.90秒双手开合，63.15秒收手。

证据：[联系表第1页](/candidate/evidence/S13_p01.jpg)；[作者slot标注](/candidate/case/evaluator/truth.json)；[映射字幕](/candidate/mapped_quotes.json)。

**S14｜64.733—68.666秒**

视频64.733—68.666秒；映射中文字幕“吃。”，英文“Eat.”。annotation-relative判定：person、drink、question均为0：“吃 / Eat”未给出对方、啤酒或是否喝的询问；吃与喝啤酒不是可互换的自然意译。光杆动词未明确断言已经喝或必须喝，不把对象遗漏和残缺语气升级为完成/请求翻转。 两语表达同样的内容和语气，bilingual=1（汇总仍受语义上限约束）。补帧64.950—65.450秒已有指点、横移，字幕65.633秒才出现，明显晚于开头动作；尾部也留到68.316秒，alignment=0.5。

第1页约64.98秒向前指点，65.23—65.48秒手横移，65.73—66.23秒双手变化，66.48—66.73秒手到嘴边，66.98秒收手。

证据：[联系表第1页](/candidate/evidence/S14_p01.jpg)；[作者slot标注](/candidate/case/evaluator/truth.json)；[映射字幕](/candidate/mapped_quotes.json)。[8fps补帧](/workspace/scratch/boundaries/S14.jpg)。

**S15｜69.166—72.899秒**

视频69.166—72.899秒；映射中文字幕“直角。”，英文“A right angle.”。annotation-relative判定：group、action、force均为0：“直角 / A right angle”没有我们一起、拍照或提议。把框形手势命名为几何形状是词义误译；片语未明确断言另一个具体事件，不额外推定完成状态或请求翻转。 两语表达同样的内容和语气，bilingual=1（汇总仍受语义上限约束）。补帧69.650—70.025秒已进行胸前动作，70.066秒字幕才显示，早段覆盖不足；拍照相关框状动作仍被覆盖，alignment=0.5。

第1页约69.67—70.17秒胸前横移，70.42—70.92秒双手靠拢，71.17—71.92秒双手形成框状，72.17秒收手。

证据：[联系表第1页](/candidate/evidence/S15_p01.jpg)；[作者slot标注](/candidate/case/evaluator/truth.json)；[映射字幕](/candidate/mapped_quotes.json)。[8fps补帧](/workspace/scratch/boundaries/S15.jpg)。

**S16｜73.399—78.233秒**

视频73.399—78.233秒；映射中文字幕“我想，我们俩都很好。”，英文“I think both of us are good.”。annotation-relative判定：context、duration、scope均为0：“我想，我们俩都很好 / I think both of us are good”完全没有课程时间、还很长或剩余时间范围，并新增两个人都好的评价，记invented_fact。无论采用课时剩余或距上课解释，字幕都没有该时间意义；不裁定这两种允许的解释孰是孰非。 两语表达同样的内容和语气，bilingual=1（汇总仍受语义上限约束）。补帧73.775—74.275秒脸侧动作在字幕74.299秒出现前已经持续，起始覆盖不足，后续表达仍在窗内，alignment=0.5。

第1页约73.65—74.15秒手指在脸侧，74.65—75.15秒双手接触，75.40—76.15秒右手变化，76.40—76.90秒双拇指从近到远，77.15秒收手。

证据：[联系表第1页](/candidate/evidence/S16_p01.jpg)；[作者slot标注](/candidate/case/evaluator/truth.json)；[映射字幕](/candidate/mapped_quotes.json)。[8fps补帧](/workspace/scratch/boundaries/S16.jpg)。

**S17｜78.733—83.866秒**

视频78.733—83.866秒；映射中文字幕“我要去那边。”，英文“I want to go over there.”。annotation-relative判定：winner、scope、aspect均为0：“我要去那边 / I want to go over there”把原标注“你赢了”的主体变成我，并添加前往某处的意愿，记wrong_person、invented_fact；没有游戏和已赢结果。不同事件的意愿不再重复记为原获胜事件的aspect_flip。 两语表达同样的内容和语气，bilingual=1（汇总仍受语义上限约束）。79.633—83.516秒覆盖整组可见表达，起始仅略早于抬手，收势后保留阅读时间且未跨段；按表达单位给alignment=1，边界判断置信度低于文字比较。

第1页79.98秒抬手，80.23—80.73秒双手交叉动作，80.98秒向前指示，81.23—81.98秒拇指及抬手动作，82.23秒收手。

证据：[联系表第1页](/candidate/evidence/S17_p01.jpg)；[作者slot标注](/candidate/case/evaluator/truth.json)；[映射字幕](/candidate/mapped_quotes.json)。

**S18｜84.366—88.433秒**

视频84.366—88.433秒；映射中文字幕“我穿衣服。”，英文“I put on clothes.”。annotation-relative判定：person=0，原标注你被写成“我 / I”；object=0，目标为正在穿的鞋，字幕明写“衣服 / clothes”，尽管保留穿这一动作，关键对象替换不能算正确鞋类信息；question=0，什么鞋的询问变成穿衣陈述，记wrong_person、wrong_object、question_as_fact。英语put的时态可歧义，不另判完成体翻转。 两语表达同样的内容和语气，bilingual=1（汇总仍受语义上限约束）。补帧84.975—85.475秒同组领口附近动作持续；85.266秒出现时仍处于该起始动作中，后续全部被覆盖至88.083秒。没有证据证明漏掉完整独立动作，alignment=1。

第1页84.87—85.87秒一手在下巴和领口附近移动，86.12—86.62秒手指变化，86.87—87.62秒手沿躯干下移，87.87秒收手。

证据：[联系表第1页](/candidate/evidence/S18_p01.jpg)；[作者slot标注](/candidate/case/evaluator/truth.json)；[映射字幕](/candidate/mapped_quotes.json)。[8fps补帧](/workspace/scratch/boundaries/S18.jpg)。

**S19｜88.933—93.199秒**

视频88.933—93.199秒；映射中文字幕“天下雨了。”，英文“It's raining.”。annotation-relative判定：group、direction、modality均为0：“天下雨了 / It's raining”添加天气事实，无法表达我们、上去或上去即可，记invented_fact。既不把“就好了”强制解释为过去反事实，也不把向上运动与“下雨”字面上下混淆成polarity_flip。 两语表达同样的内容和语气，bilingual=1（汇总仍受语义上限约束）。补帧89.250—89.750秒胸前动作发生在89.833秒字幕出现之前，后半表达可覆盖，alignment=0.5。

第1页89.18—89.68秒胸前横移，90.18—91.43秒手指向上，91.68—92.43秒双手及拇指动作，92.68秒收手。

证据：[联系表第1页](/candidate/evidence/S19_p01.jpg)；[作者slot标注](/candidate/case/evaluator/truth.json)；[映射字幕](/candidate/mapped_quotes.json)。[8fps补帧](/workspace/scratch/boundaries/S19.jpg)。

**S20｜93.699—99.432秒**

视频93.699—99.432秒；映射中文字幕“这里，那里。”，英文“Here, and over there.”。annotation-relative判定：pair=0，“这里，那里 / Here, and over there”是地点，不能表达你俩；relation=0，没有有缘或特殊联系；restraint=1，没有擅自添加恋爱、婚姻或血缘关系。该约束得分不代表关系信息正确；不把两次指点直接判定为浪漫关系。 两语表达同样的内容和语气，bilingual=1（汇总仍受语义上限约束）。补帧94.500—95.750秒仍静止，字幕94.599秒就开始，明显早于95.875秒后抬手；表达仍被覆盖，属局部提前，alignment=0.5。

第1页93.70秒有短暂调整姿态，随后静止；95.95—96.45秒抬手及指点，96.70—97.20秒手在另一前臂附近变化，97.45—98.20秒伸手，98.45秒收手。

证据：[联系表第1页](/candidate/evidence/S20_p01.jpg)；[作者slot标注](/candidate/case/evaluator/truth.json)；[映射字幕](/candidate/mapped_quotes.json)。[8fps补帧](/workspace/scratch/boundaries/S20.jpg)。

**S21｜99.932—107.599秒**

视频99.932—107.599秒；映射中文字幕“我听懂了。”，英文“I understood what I heard.”。annotation-relative判定：politeness、place、question均为0：标注礼貌问卧室在哪里，字幕“我听懂了 / I understood what I heard”却断言已经理解听到的内容；无卧室、地点问询或礼貌表达，记invented_fact、question_as_fact。耳侧动作不能仅凭形状等同于听懂。 两语表达同样的内容和语气，bilingual=1（汇总仍受语义上限约束）。补帧100.800—102.425秒持续静止但字幕100.832秒已出现，107.249秒才结束且第2页大部分静止时仍显示；提前和滞留都明显，但仍包住本段表达，alignment=0.5。

第1页102.43秒后抬手，102.68—103.18秒倾头靠手，103.43秒双手在胸前合成屋顶样形状，103.68—104.93秒两手及食指变化，105.18秒收手；第2页105.93—107.43秒保持静止。

证据：[联系表第1页](/candidate/evidence/S21_p01.jpg)；[作者slot标注](/candidate/case/evaluator/truth.json)；[映射字幕](/candidate/mapped_quotes.json)。[联系表第2页](/candidate/evidence/S21_p02.jpg)。[8fps补帧](/workspace/scratch/boundaries/S21.jpg)。

**S22｜108.099—114.032秒**

视频108.099—114.032秒；映射中文字幕“剪头发。”，英文“Cut hair.”。annotation-relative判定：person、memory、time均为0：“剪头发 / Cut hair”没有我、回忆或小时候。接近头侧的动作不能单凭位置当作头发，切样手形不能取代回忆句义。片语未具体说明施事、已完成或未来，不把缺少童年时间升级为wrong_time/aspect_flip。 两语表达同样的内容和语气，bilingual=1（汇总仍受语义上限约束）。补帧109.000—109.875秒手仍合在腹前，字幕108.999秒已显示；动作约110秒才开始，且字幕留到113.682秒、超过112.35秒收手较久，alignment=0.5。

第1页110.10秒手触胸，110.60—110.85秒指向头侧，111.10—111.35秒手向较低位置移动，111.60—112.10秒右手接触左掌，112.35秒收手。

证据：[联系表第1页](/candidate/evidence/S22_p01.jpg)；[作者slot标注](/candidate/case/evaluator/truth.json)；[映射字幕](/candidate/mapped_quotes.json)。[8fps补帧](/workspace/scratch/boundaries/S22.jpg)。

**S23｜114.532—120.199秒**

视频114.532—120.199秒；映射中文字幕“学习。”，英文“Study.”。annotation-relative判定：activity=0.5：“学习 / Study”只保留与读书相关的宽泛学习活动，未明确看书/阅读，不给满分；scarcity=0，完全遗漏没多少时间的范围；force=1，按协议不凭原标注问号处罚此处的中性短语，也不强行把Study唯一读成命令。少量时间并未被明说成很多或完全没有，因此不记polarity_flip。 两语表达同样的内容和语气，bilingual=1（汇总仍受语义上限约束）。115.432—119.849秒从抬手前较短时间显示到收势后，主要动作均被覆盖，未见错段或闪现；按表达单位给alignment=1。

第1页116.03—116.53秒双掌从合到开，116.78—117.28秒手指在眼旁与左掌间变化，117.53—118.03秒双手相接，118.28—118.78秒一手成圈样形，119.03秒收手。

证据：[联系表第1页](/candidate/evidence/S23_p01.jpg)；[作者slot标注](/candidate/case/evaluator/truth.json)；[映射字幕](/candidate/mapped_quotes.json)。

原始评分权重、档位与封顶规则保持不变；未创建双评文件，也未调用原双评入口伪装两位评审。最终仅交付本次单评ratings.json和本中文review.md。
