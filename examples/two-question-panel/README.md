# 最小示例：两问面板预测与资源分配

这个示例演示 `skills/mathmodeling/` 的入口形态：**输入是什么、Skill 生成什么、审计会说什么**。
全部内容都是合成的，不含任何竞赛真题、真实数据或第三方材料。

## 1. 输入

[`problem.md`](problem.md) 是一份虚构的两问题目：6 个城市、8 个月的出库量与资源投放记录，
问题一预测未来两个月，问题二在资源约束下做分配。

题目故意保留了几处歧义，用来观察 Skill 在信息不足时的处理方式：

- 480 单位资源是两月合计还是每月额度；
- 未来两个月的资源可得性与产能上限是否随时间变化；
- `next_month_realized_price` 的生成时点与可用范围；
- 是否允许第二个月根据首月结果重新决策。

按主 Skill 的规则，这些不阻塞工作：可以做带标签的合理选择先推进，但必须保留为具名未知项，
不能悄悄按其中一种解释算出"最优解"再当成结论。

## 2. 处理

```powershell
$modelingSkill = Join-Path $HOME ".codex\skills\mathmodeling"

# 先看将要生成什么，不写盘
python -X utf8 "$modelingSkill\scripts\init_project.py" "<project-dir>" --problems 2 --title "区域仓配货预测与资源分配（合成示例）" --dry-run

# 确认后生成；已存在的文件不会被覆盖
python -X utf8 "$modelingSkill\scripts\init_project.py" "<project-dir>" --problems 2 --title "区域仓配货预测与资源分配（合成示例）"
```

`--problems 2` 对应题目的实际问数。主 Skill 不预设四问模板，问数由题面决定。

## 3. 输出

生成 19 个文件的工程骨架，实际结果在 [`scaffold/`](scaffold/)：

| 类别 | 文件 | 用途 |
|---|---|---|
| 入口 | `problem_1.py`、`problem_2.py` | 每问一个独立可运行入口，尚未实现 |
| 配置 | `config/parameters.yaml` | 集中路径、种子、单位与实验参数 |
| 契约 | `mathmodeling.json` | 项目元数据与问数声明 |
| 记录 | `docs/problem_map.md`、`assumptions.md`、`model_contract.md`、`data_audit.md` | 问题地图、假设登记、模型契约、数据审计 |
| 证据 | `docs/evidence_map.md`、`results/run_manifest.json` | 结论到结果产物的映射 |
| 合规 | `docs/official_rules.md`、`ai_usage_log.md` | 官方规则核对与 AI 使用记录 |
| 验收 | `docs/qa_report.md` | 人工数值与视觉验收记录 |
| 论文 | `paper/main.tex` | 中文 LaTeX 骨架，占位待填 |
| 共享 | `src/common/paths.py` | 路径解析等公共逻辑 |

骨架里的 `[待填：...]` 是刻意的：它们让"还没做"在审计中可见，而不是被一段流畅的文字盖过去。

## 4. 审计输出（真实执行结果）

在尚未填写的脚手架上直接跑结构审计：

```powershell
python -X utf8 "$modelingSkill\scripts\audit_project.py" "<project-dir>\scaffold" --strict --format markdown
```

结果见 [`scaffold_audit.md`](scaffold_audit.md)：`NOT_READY`，`BLOCKER=7`，`MAJOR=11`，退出码 2。

报出的问题包括：缺少原始赛题来源、`problem_1.py` / `problem_2.py` 仍含占位实现、
未填写的问题地图与证据台账、最终论文源稿含占位内容、缺少编译产物与构建回执。

这正是这套 Skill 的设计目标之一：**空壳不会被判为完成**。
`STRUCTURE_CHECKS_PASSED` 也只说明结构检查通过，不代表数学正确或可以提交。

## 5. 这个示例到哪里为止

示例停在脚手架和审计这一步，没有继续填入建模与求解代码。
原因是示例一旦填入结果，就需要真实的数据、运行日志和验证过程作为支撑，
否则就变成了演示虚构数字——那恰好是这套 Skill 明确禁止的行为。

想继续走完流程，可以按这个顺序补：

1. 填 `docs/source_inventory.md` 与 `docs/problem_map.md`，把题目歧义写成具名未知项；
2. 决定基线模型与是否需要一个可验证的主模型改进，写进 `docs/model_contract.md`；
3. 实现 `problem_1.py` / `problem_2.py`，把参数收进 `config/parameters.yaml`；
4. 跑出结果，登记到 `results/` 与 `docs/evidence_map.md`；
5. `build_paper.py` 编译论文，逐页目视检查后再跑一次 `audit_project.py --strict`。
