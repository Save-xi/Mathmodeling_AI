<!-- 本文件由 mathmodeling/scripts/audit_project.py 真实执行产生，未做人工修改（仅把绝对路径改为相对路径）。 -->
<!-- 生成命令：python -X utf8 skills/mathmodeling/scripts/audit_project.py examples/two-question-panel/scaffold --strict --format markdown -->
<!-- mathmodeling-structural-audit-v2 -->
# mathmodeling 结构与证据关联检查

项目：scaffold
状态：NOT_READY
仍需独立终审：是
BLOCKER=7，MAJOR=11，MINOR=0

- [BLOCKER] PROBLEM_SOURCE_MISSING: 未找到声明的或可识别的原始赛题。
  证据：source_files / data/raw / docs/sources / root
- [MAJOR] DOC_PLACEHOLDER: 记录仍是未填写的模板占位内容。
  证据：docs/source_inventory.md
  方向：写入实际内容；确实无法解决的，改写为具名未知项（内容、对结论的影响、处理方式）并在论文局限中说明，不要只删占位词。
- [MAJOR] DOC_UNCHECKED_ITEM: 核对清单仍有未勾选条目，相应来源或规则尚未核验。
  证据：docs/source_inventory.md
  方向：逐项核对后改为 [x]；无法核对的条目改写为具名未知项并说明影响，不要直接删行冒充已完成。
- [MAJOR] DOC_PLACEHOLDER: 记录仍是未填写的模板占位内容。
  证据：docs/official_rules.md
  方向：写入实际内容；确实无法解决的，改写为具名未知项（内容、对结论的影响、处理方式）并在论文局限中说明，不要只删占位词。
- [MAJOR] DOC_UNCHECKED_ITEM: 核对清单仍有未勾选条目，相应来源或规则尚未核验。
  证据：docs/official_rules.md
  方向：逐项核对后改为 [x]；无法核对的条目改写为具名未知项并说明影响，不要直接删行冒充已完成。
- [MAJOR] DOC_PLACEHOLDER: 记录仍是未填写的模板占位内容。
  证据：docs/problem_map.md
  方向：写入实际内容；确实无法解决的，改写为具名未知项（内容、对结论的影响、处理方式）并在论文局限中说明，不要只删占位词。
- [MAJOR] DOC_PLACEHOLDER: 记录仍是未填写的模板占位内容。
  证据：docs/model_contract.md
  方向：写入实际内容；确实无法解决的，改写为具名未知项（内容、对结论的影响、处理方式）并在论文局限中说明，不要只删占位词。
- [MAJOR] DOC_PLACEHOLDER: 记录仍是未填写的模板占位内容。
  证据：docs/assumptions.md
  方向：写入实际内容；确实无法解决的，改写为具名未知项（内容、对结论的影响、处理方式）并在论文局限中说明，不要只删占位词。
- [MAJOR] DOC_PLACEHOLDER: 记录仍是未填写的模板占位内容。
  证据：docs/data_audit.md
  方向：写入实际内容；确实无法解决的，改写为具名未知项（内容、对结论的影响、处理方式）并在论文局限中说明，不要只删占位词。
- [MAJOR] DOC_PLACEHOLDER: 记录仍是未填写的模板占位内容。
  证据：docs/ai_usage_log.md
  方向：写入实际内容；确实无法解决的，改写为具名未知项（内容、对结论的影响、处理方式）并在论文局限中说明，不要只删占位词。
- [BLOCKER] QUESTION_RUN_MISSING: 有实际问题缺少选用运行及结果。
  证据：question=1
- [BLOCKER] QUESTION_RUN_MISSING: 有实际问题缺少选用运行及结果。
  证据：question=2
- [BLOCKER] CODE_PLACEHOLDER: 入口或共享实现仍含未完成内容。
  证据：problem_1.py
  方向：完成实际实现；故意抽象接口须由人工确认其不影响执行，不伪造已完成。
- [BLOCKER] CODE_PLACEHOLDER: 入口或共享实现仍含未完成内容。
  证据：problem_2.py
  方向：完成实际实现；故意抽象接口须由人工确认其不影响执行，不伪造已完成。
- [BLOCKER] EVIDENCE_INVALID: 关键论点未形成有效证据链接。
  证据：row 3: 存在空字段或占位内容
  方向：核对真实值、条件、运行及源文件；不得用弱化措辞或伪改状态替代验证。
- [BLOCKER] FINAL_PAPER_PLACEHOLDER: 最终源稿含占位内容。
  证据：scaffold\paper\main.tex
- [MAJOR] COMPILED_PDF_MISSING: 缺少声明的最终 PDF。
  证据：scaffold\paper\output\main.pdf
- [MAJOR] BUILD_RECEIPT_MISSING: 缺少本次源稿与 PDF 的构建关联。
  证据：scaffold\paper\output\main.build.json
  方向：使用 build_paper.py；人工数值/视觉验收另存 docs/qa_report.md。

验证边界：仅检查声明的结构、状态、运行/文件关联与可解析性；不证明记录真实、数值/推导正确、验证充分或论文可提交。时间戳是过期提示而非完整性证明；仍需独立重跑、数值和逐页视觉审查。
