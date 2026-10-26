# OmniALE · A2 本地化与使用方式适配

[案例首页](https://nanxiang-git.github.io/OmniALE/) · [手语字幕](https://nanxiang-git.github.io/OmniALE/sign/) · [钢琴转谱](https://nanxiang-git.github.io/OmniALE/piano/)

两题已拆为独立案例页，运行轨迹各自放在 traces.html。当前成绩按得分倒序排列，展示分数四舍五入保留两位小数，原始评分数据保留完整精度。分类依据项目原始 A1/A2/A3 定义，两题均属于 A2；归档文件中的旧编号保留。

2026-10-26 新增 A4/A6 Astra 专项复盘：完整分项得分、原始分与封顶 / 交付系数、工程亮点、具体错误实例、分音区 / 分时段诊断和根因判断。此次不重新评分，所有原始成绩与答卷保持不变。手语 GLM 仍为已确认小计。A6 历史答卷为 v2 事后复评；最新 Astra 独立记录注明 v2 在该次答题前已冻结。

轨迹事件合并开始与结束，推理事件只计数，不发布内部推理正文。依赖按本轮实际使用统计，包括预装包；Python 包与系统媒体工具分别列出。

离线使用：在本目录运行 `python -m http.server 8000`，打开 http://localhost:8000/ 。

[历史研究包（不含本次 Astra 更新）](https://github.com/NanXiang-git/OmniALE/releases/download/a2-analysis-rewrite-20261022/A4_A6_research_20261021.zip) · [发布记录](https://github.com/NanXiang-git/OmniALE/releases/tag/a2-analysis-rewrite-20261022)

## 本次汇报更新

- [A4 得分、亮点、错误与根因](https://nanxiang-git.github.io/OmniALE/sign/#astra-report)
- [A6 得分、亮点、错误与根因](https://nanxiang-git.github.io/OmniALE/piano/#astra-report)
- [完整研究包 ZIP（2026-10-26）](https://github.com/NanXiang-git/OmniALE/releases/download/a4-a6-report-20261026/A4_A6_research_20261021.zip) · [发布记录与校验文件](https://github.com/NanXiang-git/OmniALE/releases/tag/a4-a6-report-20261026)
- `REPORT_ANALYSIS.json` 保留新增分析的数据与证据路径；根因是分析判断，不作为新增专家评审或重评分。
