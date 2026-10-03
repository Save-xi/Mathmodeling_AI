# Mathmodeling_AI

面向数学建模竞赛的 AI Skill 与 Agent 工作流，覆盖审题、建模、计算、验证、证据整理和中文论文写作。

这套工具在一次数学建模竞赛的准备与实战过程中逐步形成，赛后整理为独立仓库。它的重点是让建模判断、代码执行、结果验证与论文结论能够对应起来，并把尚未完成的工作明确记录下来。

> This repository is an archived and cleaned-up version of a mathematical modeling AI workflow originally developed during a modeling competition.

**状态：archived but reusable / experimental。** “归档”描述项目来源；本仓库仍可继续维护。原创 Skill、脚本、模板和文档采用 [MIT License](LICENSE)。

## 包含的 Skill

| Skill | 职责 | 入口 |
|---|---|---|
| `mathmodeling` | 原题与附件核对、逐问拆解、基线选择、实现、验证、论文与提交审计 | [SKILL.md](skills/mathmodeling/SKILL.md) |
| `mathmodeling-frontier` | 赛前整理文献与算法锚点，赛时离线匹配，并对具体缺口开展有时限的检索 | [SKILL.md](skills/mathmodeling-frontier/SKILL.md) |
| `guosai-paper` | 中文国赛论文起草、压缩、润色、语体校准与语言终审 | [SKILL.md](skills/guosai-paper/SKILL.md) |
| `project-evidence-review` | 独立核对完成声明、当前实现、运行证据与剩余缺口，也适用于其他项目 | [SKILL.md](skills/project-evidence-review/SKILL.md) |

主流程要求先读取原题、附件、附录代码和输出条件，按实际问数组织工作；从透明基线开始，集中管理参数、路径、单位与随机种子；记录求解状态、可行性、误差、不确定性与敏感性；将重要论点挂到可定位的结果产物上。

Skill 明确区分事实、推断、假设、提案和未知项，也区分“已实现”“已运行”和“已验证”。脚本检查提供结构和证据关联线索；数学正确性、验证充分性与论文是否可提交仍需要独立审查。

## 工作流程

```text
原题与附件核对
      ↓
逐问问题地图、假设与变量定义
      ↓
透明基线、按需匹配算法锚点、制定验证与时间预算
      ↓
逐问实现与计算
      ↓
可行性、误差、不确定性、敏感性与稳健性检查
      ↓
结果产物与论文论点的证据映射
      ↓
正文、图表与摘要写作
      ↓
结构审计、独立复核与提交检查
```

算法改进以可复现的基线缺口和公平比较为依据。前沿检索与语料查询按需介入；中文论文默认使用 LaTeX，实际竞赛要求优先。

## 仓库结构

```text
Mathmodeling_AI/
├─ README.md
├─ LICENSE
├─ .gitignore
├─ skills/
│  ├─ mathmodeling/
│  │  ├─ SKILL.md
│  │  ├─ agents/openai.yaml
│  │  ├─ assets/            # 中文 LaTeX 论文模板
│  │  ├─ references/        # 审题、路由、预算、验证、证据与写作指引
│  │  ├─ scripts/           # 初始化、编译、结构审计与共享契约
│  │  ├─ tests/
│  │  └─ archive/           # 带日期的历史资料
│  ├─ mathmodeling-frontier/
│  ├─ guosai-paper/
│  └─ project-evidence-review/
└─ examples/
   └─ two-question-panel/   # 合成题目、生成的脚手架与审计示例
```

## 使用方式

### 在 Codex 中安装

从希望存放仓库的目录执行以下 PowerShell 命令。先检查目标目录；若已安装同名 Skill，请自行比较版本后更新。

```powershell
git clone https://github.com/Save-xi/Mathmodeling_AI.git
Set-Location .\Mathmodeling_AI

$skillNames = @('mathmodeling', 'mathmodeling-frontier', 'guosai-paper', 'project-evidence-review')
$skillHome = if ($env:CODEX_HOME) {
    Join-Path $env:CODEX_HOME 'skills'
} else {
    Join-Path $HOME '.codex\skills'
}

foreach ($skillName in $skillNames) {
    if (Test-Path -LiteralPath (Join-Path $skillHome $skillName)) {
        throw "已存在同名 Skill，请先比较版本：$skillName"
    }
}
New-Item -ItemType Directory -Path $skillHome -Force | Out-Null
foreach ($skillName in $skillNames) {
    Copy-Item -LiteralPath (Join-Path '.\skills' $skillName) -Destination $skillHome -Recurse
}
```

安装后重新打开会话，使工具重新发现 Skill。在对话中调用：

```text
使用 $mathmodeling 分析我提供的题目和附件。
先给逐问问题地图、透明基线、假设与验证方案，指出缺失信息。
```

论文语言工作可调用 `$guosai-paper`，算法储备或具体文献缺口可调用 `$mathmodeling-frontier`，完成报告复核可调用 `$project-evidence-review`。

`agents/openai.yaml` 提供 Codex 的界面元数据。Skill 内部的一些命令示例使用默认安装目录；自定义 `CODEX_HOME` 时，将示例中的 Skill 路径改为实际安装位置。

### 在其他 AI 工具中使用

支持 `SKILL.md` 的 Agent 工具可按其安装约定加载整个 `skills/<name>/` 目录。对于 ChatGPT、Claude、Gemini 等纯对话场景，可以附上对应 `SKILL.md`，并提供它引用的当前任务所需文档；使用提示词不等于具备本地脚本、文件访问或联网能力。

跨工具加载方式与执行能力需要在目标环境确认。本仓库的脚本有本地运行记录，未验证所有平台适配。

## 环境与脚本

基础脚本使用 Python 3.10+，无需 GPU。下列依赖仅在使用对应功能时需要：

| 功能 | 依赖 |
|---|---|
| 工程初始化、锚点查找、候选排序、语言检查与改写比较 | Python 标准库 |
| PDF 页数与文档属性检查 | `pypdf` 或 Poppler `pdfinfo` |
| 优秀论文语料抽取 | Poppler `pdftotext` 或 `pypdf`；另需合法取得的自备语料 |
| 中文论文编译 | 带 `ctex` 的 XeLaTeX；参考文献配置可能需要 BibTeX 或 Biber |
| 完整自动测试 | `pytest`、`pypdf`；部分后端检查还需要 Poppler |

Skill 是给 Agent 的工作指引，实际建模仍可能需要题目对应的求解器、科学计算库或联网文献检索。

| 脚本 | 用途 |
|---|---|
| `mathmodeling/scripts/init_project.py` | 按实际问数生成工程骨架，支持 `--dry-run`，保留已有文件 |
| `mathmodeling/scripts/build_paper.py` | 编译声明的论文，并记录源稿与 PDF 的构建关联 |
| `mathmodeling/scripts/audit_project.py` | 检查占位、逐问产物、运行记录与证据链接；严格模式下问题未关闭时返回非零状态 |
| `mathmodeling-frontier/scripts/lookup_anchors.py` | 只读查询本地锚点目录，无网络请求 |
| `mathmodeling-frontier/scripts/rank_candidates.py` | 校验候选与证据字段，执行硬门槛并输出排序 |
| `guosai-paper/scripts/audit_style.py` | 输出需人工复核的语言问题线索 |
| `guosai-paper/scripts/check_revision.py` | 比较公式、引用、数字等受保护项的变化 |
| `guosai-paper/scripts/corpus_lookup.py` | 在自备 PDF 语料中定向检索短片段 |

语料目录通过 `--corpus "<目录>"` 或 `GUOSAI_CORPUS` 指定，默认回退到 `~/guosai-corpus`。无可用语料或抽取后端时，脚本会报告缺失信息。

## 最小示例

[two-question-panel](examples/two-question-panel/README.md) 使用合成场景：六个城市、八个月观测，分别讨论需求预测与资源分配。[题目](examples/two-question-panel/problem.md) 保留资源口径与决策时点等待确认事项，用于演示问题拆解与未知项记录。

在仓库根目录运行：

```powershell
python -B -X utf8 .\skills\mathmodeling\scripts\init_project.py .\demo-project --problems 2 --title '两问合成示例' --dry-run
python -B -X utf8 .\skills\mathmodeling\scripts\init_project.py .\demo-project --problems 2 --title '两问合成示例'
python -B -X utf8 .\skills\mathmodeling\scripts\audit_project.py .\demo-project --strict --format markdown
```

输出是 19 个文件的工程骨架：每问一个入口、集中参数、问题与假设记录、运行清单、证据映射及论文源稿。[已生成的骨架](examples/two-question-panel/scaffold/) 和 [历史审计输出](examples/two-question-panel/scaffold_audit.md) 已随仓库保存。

未填写的骨架会报告 `NOT_READY`，示例历史结果为 `BLOCKER=7`、`MAJOR=11`、退出码 2。这是预期结果。示例没有已完成的模型、计算结果或论文。

## 验证与维护

2026-10-01 归档时，自动测试记录为：`mathmodeling` 59 项、`mathmodeling-frontier` 33 项、`guosai-paper` 48 项，共 140 项通过。它们是脚本测试记录，行为用例、数学结论与论文质量需要分别验证。

安装测试依赖后，在仓库根目录运行：

```powershell
python -m pip install pytest pypdf
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
python -B -X utf8 -m pytest -q skills/mathmodeling/tests skills/mathmodeling-frontier/tests skills/guosai-paper/tests
```

关闭第三方 pytest 插件自动加载可避免现有环境插件干扰。也可以分别运行这三套测试；首次全套检查可能需要数分钟。

`cumcm-official.md`、前沿快照和算法目录都保存了各自的核验日期。参加新一届竞赛或提出“最新”主张前，应核对现行规则或来源。语料画像来自当年的自备论文集合，不能把旧计数当成本机现状。

本仓库保持原有提示词与脚本结构；维护时优先修复可复现的问题。可选 Nature 系列 Skill 与 `$codex-task-recovery` 未随仓库分发，缺失时按现有指引采取等效检查。

## 资料与许可证

原创 Skill、脚本、模板和文档使用 [MIT License](LICENSE)，版权署名为 Save-xi。使用、修改和分发时应保留许可证及版权声明。

竞赛真题、官方附件、优秀论文全文、付费资料和个人语料不随本仓库分发。参考资料中的短引文、论文与模型链接属于相应权利人，MIT 不为这些第三方内容重新授权。
