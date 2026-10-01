---
name: guosai-paper
description: "Draft, polish, corpus-calibrate, and audit Chinese CUMCM papers while preserving mathematical meaning and evidence. Use for 国赛论文写作、中文润色、摘要压缩、结果叙述、优秀论文语体校准、终稿语言审校; do not choose algorithms, invent results, certify mathematics/code, or replace official contest requirements."
---

# 国赛论文写作与润色

让读者找到每问的答案，理解建模判断，并沿文字追到结果与适用条件。中文表达、章节组织、论证衔接和语料校准由本 Skill 负责；建模计算、实验验证、官方规则及完整论文编译交付由 `$mathmodeling` 负责。优秀论文提供表达样本，不提供当前题目的算法、数值、结论或正确性保证。

## 先确定编辑范围

- **局部润色/压缩**：直接处理用户提供的段落及已给证据。没有完整原题、原始数据或日志，不阻断语序、措辞和冗余修订；只对依赖缺失信息的判断列待核项。不新建项目、不默认检索全库或编译。
- **起草/实质重写**：用题面、模型与结果材料组织论证。缺少决定性证据时保留具体缺口；机制解释若仅为推测，应写明或移出完成结论。
- **语料校准**：需要真实用法时，只选相关章节的少数段落，核对文件、PDF 页和上下文；借组织方式，不复刻句子或算法。
- **全文终审**：复核逐问覆盖、术语、摘要与正文一致性及主张来源，输出分级问题。审查请求不自动变成整篇重写。

“冲国一”要求提高答案可见性、论证密度和解释质量，不自动增加篇幅、算法术语、最高级或每段的限制声明。已有清楚且准确的句子可以保留。

## 保护事实与语义

保护公式、符号、数值及对应对象、正负号、单位、题号、引用/图表/文件标识、约束方向、时间口径、样本范围、求解状态与结论范围。用户提供的结果可以作为本轮写作依据，但不得称本轮已经独立复算。

已核验事实与原稿中的夸张判断要分开。无依据的“显著、因果、全局最优、任何场景可靠”不能靠润色保留为事实；按已给证据修正并简要标明这种实质变化。事实本身有冲突时，不静默挑选一个数字或编造解释。默认保留作者的有效判断，不把所有结论都改成空泛的“可能”。

压缩时优先删重复背景、重复方法介绍和不承载信息的评价词；保留会改变解释的条件、比较对象、关键数值和失败边界。增加派生数值须先核算并说明来源；没有必要就保留原数值表达。

## 按需读取与执行

- 局部润色、压缩、改写验收：读 [references/revision-workflow.md](references/revision-workflow.md)。
- 摘要起草或压缩：读 [references/abstract.md](references/abstract.md)；区分定量、定性、证明/反例任务，不强行凑数字或检验结尾。
- 问题分析、假设、模型或结论：读 [references/section-writing.md](references/section-writing.md)。
- 图表、结果、敏感性和事件叙述：读 [references/results-and-style.md](references/results-and-style.md)。
- 查真实语料：读 [references/corpus-examples.md](references/corpus-examples.md)，按所列文件/页定向回查；需要语料覆盖和后端口径时再读 [references/corpus-profile.md](references/corpus-profile.md)。
- 全文审校：读 [references/final-audit.md](references/final-audit.md)。只有涉及官方格式、匿名或提交要求时，才由 `$mathmodeling` 核对带来源的当年全国规则；校内培训和往年文件不替代现行规则。

只加载当前任务需要的引用。没有明确语体缺口时可不查询语料；一次校准通常观察两三段就足够，不默认遍历全部 PDF 或另做算法研究。

## 写作顺序

1. 从提供的材料确认本段/本问要交付什么，及哪些内容可改、哪些须保留。局部任务用简短说明即可，不强制制作证据台账。
2. 先组织判断与证据，再检查条件、方法角色、解释和上下文承接。它们是可选择的论证部件，不是每段都必须填满的五句模板。
3. 结果段突出能改变判断的差异、规律或失败情形；不逐项复述表格，不添加数据不支持的机制解释。
4. 按原稿和依据复核保护项，并检查数字仍属于原对象、否定与不等式方向未变。需要时使用只读比较工具辅助。
5. 完整论文在正文和 canonical 结果稳定后定稿摘要，核对每问答案与图表；局部摘要润色可先完成措辞并注明证据边界。
6. 交付可直接使用的正文和必要待核项。证据、覆盖和表达已满足请求时停止，不反复同义改写。

## 工具

从安装目录定位脚本，不要求切换项目目录。以下工具均不修改原稿、原 PDF 或模型结果：

```powershell
$paperSkill = Join-Path $HOME ".codex\skills\guosai-paper"
python -X utf8 "$paperSkill\scripts\audit_style.py" "<paper.tex>" --format json
python -X utf8 "$paperSkill\scripts\check_revision.py" "<before.tex>" "<after.tex>"
python -X utf8 "$paperSkill\scripts\corpus_lookup.py" --list
python -X utf8 "$paperSkill\scripts\corpus_lookup.py" --paper B226 --grep "基础上" --limit 3
```

语言审计区分 .tex 注释与 Markdown 百分号；`--input-format` 可覆盖识别，`--abstract-kind qualitative|quantitative` 可声明摘要任务。命中只供人工复核；`--strict` 返回码不等于已确认错误或提交结论。该脚本按高精度低召回校准：在写得规范的正文上几乎不误报，但也会漏掉 [references/results-and-style.md](references/results-and-style.md) 自己逐条列出的部分说法。零命中同样不代表文字合格，仍须人工把该文件的“常见空泛表达”表和 [references/final-audit.md](references/final-audit.md) 的逐段五问过一遍。

改写比较报告公式、引用、数字/常见单位、文件/状态标识和关系符号的增删；新增计算、合并重复数字或格式等价也可能触发。零差异不能发现同一数字被换给另一个对象、中文否定或语义反转，仍需人工对照。

语料 `--list` 只列文件；`--abstract` 和 `--paper` 先唯一定位文件再抽取。正文查询返回 PDF 物理页码，摘要查询说明开始页与边界。`--stats` 才执行显式全库统计；文本缓存保存在系统临时目录，失败与后端需要保留。

## 默认交付

润色先给可直接替换的中文正文；原稿为 LaTeX 时保留命令和可编译语法。完整论文默认 .tex + 编译 PDF；没有明确请求不转 Word。原稿是 .docx 时，请用户先自行导出为纯文本或 .tex 再使用上述工具（audit_style.py 只接受 Markdown/纯文本/LaTeX 输入），本 Skill 不做格式转换。术语、状态码、结果文件路径等只有在帮助读者定位或理解时才进入正文，内部检查状态和编辑台账放在随附说明中。

起草缺项标 `[待填：具体内容]`；局部已完整的正文不要为了模板插入新占位符。审校按 BLOCKER / MAJOR / MINOR 给出位置、依据和修改方向；全文改写只在授权范围内执行。
