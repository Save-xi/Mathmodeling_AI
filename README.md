# Mathmodeling_AI

面向数学建模竞赛工作流的 AI Skill 集合 / An agent-skill toolkit for mathematical-modeling contests.

---

## 这是什么

这是一套面向数学建模竞赛的 AI Skill（Agent workflow）。它最初在一次数学建模竞赛的准备与实战过程中写成，
用来约束 AI 在审题、建模、求解、验证和论文写作中的行为；赛后整理为独立、可复用的项目。

Skill 不是"自动做题机器"。它给出的是一套可检查的工作方式和交付标准：先读原题与附件，先立透明基线，
把结论挂到可复现的结果产物上，并在交付前分级列出仍未解决的问题。

## 它解决什么问题

只列四套 Skill 中真实存在的能力：

- **审题与问题拆解**：先核对原题、附件、附录代码和输出要求，按题目实际问数组织工作，不套用固定题数模板。
- **建模假设与变量定义**：区分事实、推断、假设、提案与未知项，并单独记录执行与核验状态。
- **模型选择**：透明基线 → 主模型 → 备选，一次只增加一个可验证的改进，并给出拒绝条件。
- **数值分析与求解证据**：集中参数、固定随机种子、记录可行性、终止状态、目标口径、运行时间与最优性间隙。
- **代码生成与结构检查**：为每一问生成独立可运行的入口，并用结构审计脚本检查占位符、缺失产物与断链的证据引用。
- **结果解释与验证**：区分"跑通了"和"验证过"，要求不确定性、敏感性、稳健性和失败边界有对应证据。
- **论文结构与中文表达**：默认中文 LaTeX 交付，含页数与匿名等格式要求；另有独立的论文语言审校 Skill。
- **交叉验证与二审**：把"声明—实际实现—运行证据—剩余缺口"分开核查，不把类名、依赖列表或路线图当作已接入运行的证据。
- **防止 AI 无脑给答案**：禁止编造数据、运行、指标、p 值、区间、引用或改进幅度；未验证的结论必须写成未验证。

## 工作流程

主 Skill 的常规路径（`skills/mathmodeling/SKILL.md`）：

```
Problem intake        原题、附件、附录代码、输出要求与口径核对
        ↓
Problem map           逐问输入/输出/耦合/评价标准/验收证据
        ↓
Baseline & routing    透明基线、主模型、备选与拒绝条件
        ↓
Implementation        problem_i.py、集中参数、确定性种子、可复现运行
        ↓
Validation            可行性、终止状态、不确定性、敏感性、稳健性
        ↓
Evidence map          每个重要结论 → 可定位的结果产物
        ↓
Paper writing         中文 LaTeX 正文；摘要最后写
        ↓
Submission audit      BLOCKER / MAJOR / MINOR 分级，strict 模式下不允许残留前两级
```

两条辅助路线按需介入，不改变上面的主线：

- `skills/mathmodeling-frontier/SKILL.md`：赛前做文献与算法锚点准备，赛时将已核验锚点离线匹配到真实题目，只对决策相关的缺口做有时限的检索。
- `skills/guosai-paper/SKILL.md`：中文论文的起草、压缩、语料语体校准与全文终审，保护公式、数值、单位、约束方向与结论边界。

`skills/project-evidence-review/SKILL.md` 是通用的证据二审 Skill，用于核验项目书、算法声明或另一个 Agent 的完成报告，
也可以用在数模之外的仓库。

## 仓库结构

```
Mathmodeling_AI/
├─ README.md
├─ .gitignore
├─ skills/
│  ├─ mathmodeling/            # 主工作流：审题 → 建模 → 求解 → 验证 → 论文 → 终审
│  │  ├─ SKILL.md
│  │  ├─ agents/openai.yaml
│  │  ├─ archive/              # 兼容性归档（离线查询种子，不作为时效性证据）
│  │  ├─ assets/               # 中文竞赛论文 LaTeX 骨架
│  │  ├─ references/           # 按需加载的细分指引
│  │  ├─ scripts/              # init_project / build_paper / audit_project
│  │  └─ tests/
│  ├─ mathmodeling-frontier/   # 赛前锚点准备与赛时缺口检索
│  ├─ guosai-paper/            # 国赛中文论文写作与语言审校
│  └─ project-evidence-review/ # 通用证据二审
└─ examples/
   └─ two-question-panel/      # 合成示例：输入、脚手架与真实审计输出
```

## 使用方式

每个 Skill 都是一个独立目录，入口是各自的 `SKILL.md`。`SKILL.md` 采用常见的 skill 约定：
YAML frontmatter 提供 `name` 与 `description`，正文只写路由规则，细节放在 `references/` 里按需读取。

**Codex**（本仓库实际验证过的环境）：

```powershell
git clone https://github.com/Save-xi/Mathmodeling_AI.git
Copy-Item -Recurse -Force .\Mathmodeling_AI\skills\mathmodeling          "$HOME\.codex\skills\mathmodeling"
Copy-Item -Recurse -Force .\Mathmodeling_AI\skills\mathmodeling-frontier "$HOME\.codex\skills\mathmodeling-frontier"
Copy-Item -Recurse -Force .\Mathmodeling_AI\skills\guosai-paper          "$HOME\.codex\skills\guosai-paper"
Copy-Item -Recurse -Force .\Mathmodeling_AI\skills\project-evidence-review "$HOME\.codex\skills\project-evidence-review"
```

装好后在对话里用 `$mathmodeling`、`$guosai-paper` 等名字调用。
`agents/openai.yaml` 是 Codex 的界面元数据，其他工具可以忽略。

**其他支持 `SKILL.md` 约定的工具**：把 `skills/<name>/` 整个目录复制到该工具的 skills 目录即可。
本仓库只在 Codex 上做过运行验证，其他环境需要你自己确认加载方式。

**直接当作提示词使用**：如果所在工具没有 skill 机制，可以把对应 `SKILL.md` 全文作为系统提示或项目指令粘贴，
再把 `references/` 中当前任务需要的那几篇一并附上。正文里"按需读取"的引用在纯粘贴模式下要手动替换。

> 注意：`SKILL.md` 中的脚本示例用 `Join-Path $HOME ".codex\skills\mathmodeling"` 之类的写法定位安装目录。
> 如果你把 Skill 装到别的位置，只需要改这一个变量。

### 环境要求

- **Python 3.10+**，脚本只依赖标准库；`guosai-paper/scripts/corpus_lookup.py` 可选使用 `pypdf` 作为 PDF 抽取回退后端。
- **XeLaTeX**（可选）：只有编译中文论文 PDF 时才需要。`ctexart` 类需要完整的 TeX 发行版。
- **Poppler `pdftotext`**（可选）：语料抽取的首选后端，缺失时自动回退到 `pypdf`。

没有 GPU、没有 Docker、没有需要联网的运行时依赖。

## 最小示例

完整示例见 [`examples/two-question-panel/`](examples/two-question-panel/)，内容全部是合成的，不含任何竞赛真题或真实数据。

**输入**：一份虚构的两问题目 [`problem.md`](examples/two-question-panel/problem.md)。
它故意留了歧义（480 单位是月度还是两月合计、未来资源可得性、能否二次决策），用来观察 Skill 如何处理信息不足。

**处理**：主 Skill 先做问题地图与假设登记，再生成脚手架：

```powershell
$modelingSkill = Join-Path $HOME ".codex\skills\mathmodeling"
python -X utf8 "$modelingSkill\scripts\init_project.py" "<project-dir>" --problems 2 --title "项目标题" --dry-run
python -X utf8 "$modelingSkill\scripts\init_project.py" "<project-dir>" --problems 2 --title "项目标题"
```

**输出**：19 个文件的工程骨架，含每问一个 `problem_i.py`、集中参数文件、证据台账和论文源稿。
真实生成结果在 [`examples/two-question-panel/scaffold/`](examples/two-question-panel/scaffold/)。

在这个尚未填写的脚手架上跑结构审计，得到的是真实且符合预期的结果：
[`scaffold_audit.md`](examples/two-question-panel/scaffold_audit.md) 报告 `NOT_READY`、`BLOCKER=7`、`MAJOR=11`，退出码 2。
这正是这套 Skill 想要的行为——空壳不会被当成完成品。

## 脚本与测试

各 Skill 自带脚本，均为只读或幂等设计（`init_project.py` 不覆盖已有文件）：

| Skill | 脚本 | 作用 |
|---|---|---|
| mathmodeling | `init_project.py` | 按实际问数生成工程骨架，支持 `--dry-run` |
| mathmodeling | `build_paper.py` | 编译论文并写出构建回执 |
| mathmodeling | `audit_project.py` | 结构与证据关联审计，`--strict` 时返回非零退出码 |
| mathmodeling-frontier | `lookup_anchors.py` | 离线读取锚点目录，不联网、不评分 |
| mathmodeling-frontier | `rank_candidates.py` | 校验并通过硬门槛排序候选方案 |
| guosai-paper | `audit_style.py` | 中文论文语言审计（高精度低召回，命中只作人工复核线索） |
| guosai-paper | `check_revision.py` | 改写前后公式/引用/数字差异比较，不做语义判断 |
| guosai-paper | `corpus_lookup.py` | 对自备优秀论文语料做定向检索 |

运行测试：

```powershell
python -X utf8 -m pytest -q skills/mathmodeling/tests
python -X utf8 -m pytest -q skills/mathmodeling-frontier/tests
python -X utf8 -m pytest -q skills/guosai-paper/tests
```

当前状态：`mathmodeling` 59 passed / 38 subtests，`mathmodeling-frontier` 33 passed，`guosai-paper` 48 passed / 13 subtests。
测试只覆盖脚本的结构与行为，不构成建模正确性或论文质量的证明。

> 如果本机 conda 环境的 `hydra` pytest 插件与当前 Python 冲突，加 `-p no:hydra` 或设置 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`。

### 语料检索需要自备数据

`corpus_lookup.py` 面向的是本地优秀论文 PDF 语料。**这些 PDF 属于竞赛组委会与原作者，不随本仓库分发。**
请用 `--corpus "<目录>"` 或环境变量 `GUOSAI_CORPUS` 指向你自己的副本，默认回退到 `~/guosai-corpus`。
目录不存在时脚本会明确报错，这是环境缺失，不是脚本缺陷。

## 本仓库不包含什么

- 竞赛真题全文、官方规则附件、培训材料原文件；
- 优秀论文语料 PDF 或其他第三方版权资料；
- 任何 API key、token、cookie、密码或 `.env`；
- 个人环境路径、账号信息、缓存、日志与运行产物；
- 任何比赛成绩声明。本仓库不声称、也不暗示任何获奖或排名。

## 项目状态

> This repository is an archived and cleaned-up version of a mathematical modeling AI workflow originally developed during a modeling competition.

Status: **usable but experimental**。四套 Skill 在本机安装环境中通过上述测试并能实际运行，
但整理时只做了保持原行为的轻量清理，没有重构。结构审计脚本只证明结构与证据关联，不证明数学正确性。

## 已知限制

- 时间敏感的参考文件（`references/cumcm-official.md`、`references/frontier-*.md`）是带日期的快照，
  用于较晚年份的竞赛前必须重新核对官方现行规则。
- `archive/frontier-modeling-2026.md` 只是兼容性归档和离线查询种子，不能当作时效性证据。
- `guosai-paper` 的语料画像基于一份 57 篇的本地语料，不同 PDF 后端的可解析篇数不同；这些数字是当年的记录，不是通用结论。
- 语言审计脚本按高精度低召回校准：零命中不代表文字合格，仍需人工按 `references/final-audit.md` 复核。
- Skill 面向中文竞赛与中文论文；英文赛事（如 MCM/ICM）需要调整语言与格式默认值。
- 少数文件会引用本仓库之外的 Skill：`mathmodeling/references/nature-collaboration.md` 指向可选的论文配图/统计/语言类 Skill，
  `project-evidence-review/SKILL.md` 提到 `$codex-task-recovery`。它们都是可选的协作入口，缺失时按各文件写明的替代路径处理即可，不影响主流程。

## License

**尚未指定开源许可证。** 在作者选定之前，默认保留全部权利（all rights reserved）。
如需他人复用，可考虑 MIT 或 Apache-2.0；涉及论文语料的部分需另行确认。
