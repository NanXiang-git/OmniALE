# 单评记录

评审身份：`single-sol`，`model_assisted`。本轮按用户授权作一份冻结答卷单评。
语义判定均相对于 CE-CSL 作者的中文和 gloss 标注，英文参考不作为唯一译法；本人不具中国手语专家身份。
原片无音轨，无法直接听音；本次实际检查全部23段每段五幅有序图像，S12、S17、S21加密抽帧。未以正常速度连续观看，故 `video_watched_in_full=false`。
可信技术结果见 `/work/technical.json`：交付5分、可读性5分，各段定位比例档均为1。本记录不自报总分，由宿主授权单评校验器和原 aggregate 计算。

| 段 | 时窗 | 中文slot | 英文slot | 双语 | 对齐 | 严重错误类别 | 证据与理由 |
|---|---|---|---|---:|---:|---|---|
| S01 | 0.00–5.07s | [1, 0, 0, 0.5] | [1, 0, 0, 0.5] | 1 | 1 | wrong_object, invented_fact | 0.00–5.07s，标注相对：addressee保留“你”；time“今天”和negation“没喝酒”全失。字幕“爱吃苹果/like apples”另造对象与喜好，force仅保留问句形式而无确认否定的语气。 中文证据“你爱吃苹果吗？”；英文证据“Do you like apples?”。 |
| S02 | 5.57–8.47s | [0, 0, 0] | [0, 0, 0] | 1 | 1 | wrong_person, invented_fact | 5.57–8.47s，标注相对：group原为“我们”，字幕改“我/I”；action“去吃饭”换成“唱歌/singing”，force共同提议改成个人喜好的事实。 中文证据“我爱唱歌。”；英文证据“I love singing.”。 |
| S03 | 8.97–12.87s | [0, 0, 0] | [0, 0, 0] | 1 | 1 | invented_fact | 8.97–12.87s，标注相对：person“你”、ability“能自己来”和force确认询问均无；“吃/Eating”并非该段作者标注的动作，[无法确认]/[unclear]不补回这些槽。 中文证据“吃[无法确认]。”；英文证据“Eating [unclear].”。 |
| S04 | 13.37–18.43s | [0, 1, 0] | [0, 1, 0] | 1 | 1 | invented_fact | 13.37–18.43s，标注相对：person“我/I”保留；time“明年”和event“毕业”均未表达。“想/want to”是原标注没有的意愿，未知内容不能补足毕业。 中文证据“我想[无法确认]。”；英文证据“I want to [unclear].”。 |
| S05 | 18.93–24.63s | [0, 0, 0] | [0, 0, 0] | 1 | 1 | wrong_person, request_as_fact, invented_fact | 18.93–24.63s，标注相对：plural“你们”改成“我/I”，action“安静一下”缺失；force礼貌请求改为“我十五岁/I am fifteen”这一既定事实。 中文证据“我十五岁。”；英文证据“I am fifteen years old.”。 |
| S06 | 25.13–28.50s | [0, 0, 0] | [0, 0, 0] | 1 | 1 | wrong_object, invented_fact | 25.13–28.50s，标注相对：owner原为“我有”宠物狗，字幕“我十一岁/I am eleven”没有拥有关系；object狗和quantity一只均缺，十一岁是凭空年龄。 中文证据“我十一岁。”；英文证据“I am eleven years old.”。 |
| S07 | 29.00–33.23s | [0, 0.5, 0] | [0, 0.5, 0] | 1 | 1 | wrong_person, question_as_fact, invented_fact | 29.00–33.23s，标注相对：event“篮球/basketball”局部保留，但加入“写字/writing”，且没有“去”；group“我们”改“我”，question“什么时候”改为爱好陈述。 中文证据“我爱打篮球和写字。”；英文证据“I love playing basketball and writing.”。 |
| S08 | 33.73–39.03s | [0.5, 0, 0] | [1, 0, 0] | 1 | 1 | invented_fact | 33.73–39.03s，标注相对：person中文“你”弱化“你们”，英语you可兼容复数；question原问“去做什么”而字幕问“爱我吗/love me”，aspect已做过的事也消失。 中文证据“你爱我吗？”；英文证据“Do you love me?”。 |
| S09 | 39.53–43.83s | [0.5, 0, 0] | [0.5, 0, 0] | 1 | 1 | wrong_object, invented_fact | 39.53–43.83s，标注相对：owner仅保留“你/you”的人称线索，未表达“你的”号码；object电话号码与question询问号码均被“能听见我说话/can you hear me”替换。 中文证据“你能听见我说话吗？”；英文证据“Can you hear me?”。 |
| S10 | 44.33–47.87s | [0, 0, 0] | [0, 0, 0] | 1 | 1 | wrong_person, invented_fact | 44.33–47.87s，标注相对：group“我们”变“我/I”，again“重新开始”全无；force共同提议变为“爱游泳和照相/love swimming and taking photos”这一自述。 中文证据“我爱游泳和照相。”；英文证据“I love swimming and taking photos.”。 |
| S11 | 48.37–53.37s | [0, 0.5, 0] | [0, 0.5, 0] | 1 | 1 | wrong_person, wrong_object, question_as_fact | 48.37–53.37s，标注相对：food仅“吃/eating”相关，其面包被改饺子/dumplings；person你们改我，force是否要吃的问句变成“我爱吃/I love eating”事实。 中文证据“我爱吃饺子。”；英文证据“I love eating dumplings.”。 |
| S12 | 53.87–57.90s | [0, 0, 0] | [0, 0, 0] | 1 | 0.5 | invented_fact | 53.87–57.90s，标注相对：action“扔掉”和aspect“已经完成”均无；“不客气/You’re welcome”是另一种礼貌回应，underspecified也无法代替原事件。密集帧显示字幕早于动作结束。 中文证据“不客气。”；英文证据“You're welcome.”。 |
| S13 | 58.40–64.23s | [0, 0, 0] | [0, 0, 0] | 1 | 1 | invented_fact | 58.40–64.23s，标注相对：relation“和你一起度过”、time“美好的晚上”和aspect已发生均无；“我爱我的家/I love my home”改写对象和事件。 中文证据“我爱我的家。”；英文证据“I love my home.”。 |
| S14 | 64.73–68.67s | [0, 0, 0] | [0, 0, 0] | 1 | 1 | wrong_person, wrong_object, question_as_fact | 64.73–68.67s，标注相对：person“你们”改“我/I”；drink“啤酒”换成水/water，question“喝吗”变成“我爱喝/I love drinking”陈述。 中文证据“我爱喝水。”；英文证据“I love drinking water.”。 |
| S15 | 69.17–72.90s | [0.5, 0, 0] | [0.5, 0, 0] | 1 | 1 | invented_fact | 69.17–72.90s，标注相对：group“我/I”只保留说话人，遗漏“我们一起”；action“照相”和force“吧”的提议均无。“我爱中国/I love China”是另造的爱国陈述。 中文证据“我爱中国。”；英文证据“I love China.”。 |
| S16 | 73.40–78.23s | [0, 0, 0] | [0, 0, 0] | 1 | 1 | invented_fact | 73.40–78.23s，标注相对：context“上课”、duration“还很长”和scope时间范围全无；“我想吃/I want to eat”另造饮食意愿，[无法确认]不等于课程时长。 中文证据“我想吃[无法确认]。”；英文证据“I want to eat [unclear].”。 |
| S17 | 78.73–83.87s | [0, 0, 0] | [0, 0, 0] | 1 | 1 | wrong_person, invented_fact | 78.73–83.87s，标注相对：winner原为“你赢了”，字幕用“我爱/I love”换人称且无输赢；scope“这把游戏”和aspect已赢均无，未确认对象也不能补回。 中文证据“我爱[无法确认]。”；英文证据“I love [unclear].”。 |
| S18 | 84.37–88.43s | [0, 0, 0] | [0, 0, 0] | 1 | 1 | wrong_person, question_as_fact, invented_fact | 84.37–88.43s，标注相对：person原问“你”，字幕变“我”；object所穿鞋子和question鞋种均缺。“想一个人/I want to be alone”是新增意愿且把问句改事实。 中文证据“我想一个人[无法确认]。”；英文证据“I want to be alone [unclear].”。 |
| S19 | 88.93–93.20s | [0.5, 0, 0] | [0.5, 0, 0] | 1 | 1 | invented_fact | 88.93–93.20s，标注相对：group“我”仅部分包含说话人，缺“我们”；direction“上去”和modality“就好/即可”均无。“爱/love”另造态度，未确认内容不补方向。 中文证据“我爱[无法确认]。”；英文证据“I love [unclear].”。 |
| S20 | 93.70–99.43s | [0, 0, 0] | [0, 0, 0] | 1 | 1 | wrong_object, invented_fact | 93.70–99.43s，标注相对：pair“你俩”和relation“有缘分”均无；字幕改问“这件衣服多少钱/how much is this piece of clothing”，对象和话题另造。restraint不能靠无关句获得分数。 中文证据“这件衣服多少钱？”；英文证据“How much is this piece of clothing?”。 |
| S21 | 99.93–107.60s | [0, 0, 0] | [0, 0, 0] | 1 | 1 | wrong_object, question_as_fact, invented_fact | 99.93–107.60s，标注相对：politeness请问、place卧室、question在哪里均无；“我在家睡觉/I sleep at home”只出现泛指家，不能当卧室，且把问路改成自述。 中文证据“我在家睡觉，[无法确认]。”；英文证据“I sleep at home; [unclear].”。 |
| S22 | 108.10–114.03s | [1, 0, 0] | [1, 0, 0] | 1 | 1 | invented_fact | 108.10–114.03s，标注相对：person“我/I”保留；memory“回忆起”被“想学/want to learn”替换，time小时候/童年消失，手语/sign language是新增学习对象。 中文证据“我想学手语。”；英文证据“I want to learn sign language.”。 |
| S23 | 114.53–120.20s | [0, 0, 0] | [0, 0, 0] | 1 | 1 | invented_fact | 114.53–120.20s，标注相对：activity看书与scarcity没多少时间均无；“祝你生日快乐/Happy birthday”是另一种祝福。force原问号有歧义，零分依据是内容改写，非标点。 中文证据“祝你生日快乐。”；英文证据“Happy birthday to you.”。 |

## 证据限制

- 原视频无音轨；没有直接听音或ASR证据。
- 通过ffmpeg抽取全部23段每段5幅有序画面并实际用view_image检查；S12、S17、S21另以0.4秒间隔补帧，未以正常速度连续观看全片。
- 非中国手语专家。语义分数相对于CE-CSL作者中文/gloss标注，不能作为独立手语认证；未作专家冲突仲裁。
- 对齐是基于可见动作抽帧与SRT时间窗的估计，帧间瞬态动作可能遗漏。
