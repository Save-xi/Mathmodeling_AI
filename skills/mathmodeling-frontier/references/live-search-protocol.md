# 前沿检索协议

本协议用于真正需要联网的赛前准备、赛时补漏或专项研究。先按 [precontest-anchors.md](precontest-anchors.md) 选模式；有日期的一手证据可以离线复用。明确要求“截至现在最新”时做定向刷新，不因此重启全领域检索。普通锚点匹配不必读取本协议的全部字段。

## 1. 先冻结题目契约

赛前先定义问题族、数据/资源包络并完成有条件的文献与算法卡，可标记资料 `PREPARED`；这不需要尚未公布的赛题。面向实际题目采用/排名时，再记录以下字段及 `problem_contract_status = FROZEN | PROVISIONAL`。关键原题/附件/资源缺失时不得给本题 `PRIMARY` 或 `BACKUP`，但可以继续准备有来源的条件候选。

- 精确题号与输出物：预测、解释、评价、优化、仿真、控制或组合任务；
- 对象与机制：守恒、排队、传播、博弈、库存、路径、调度、时空关联等；
- 数据结构：样本量、特征数、频率、时间跨度、缺失、异常、空间关系、标签质量；
- 时间信息：预测步长、滚动更新方式、是否存在概念漂移与分布偏移；
- 决策信息：变量、硬约束、软约束、目标函数、单位和不确定性来源；
- 资源限制：CPU/GPU、求解器、联网、外部权重、比赛时限与复现实验预算；
- 基线与评价：最简单可信基线、主指标、决策指标、约束违背率和运行时间。

## 2. 设置时间窗与检索矩阵

赛前宽检索覆盖近 24 个月与必要的成熟锚点；领域稀疏时适当扩展，不强制每个路线新找 3--5 篇。赛时从所选锚点已核验的 cutoff、缺失条件及差分 queries 出发，只查能改变本题决策的内容。旧论文的具体条件尚未核清时也可回读旧文，不把“差分”误解为只查发布日期更新。对预印本、Workshop、审稿中或软件发布分别记录状态。

围绕机制和数据条件，而非只围绕算法名，组合以下查询：

1. `(任务或领域) AND (机制或数据条件) AND (候选模型族)`；
2. `(候选模型族) AND (benchmark OR ablation OR generalization)`；
3. `(候选模型族) AND (failure OR limitation OR negative result OR distribution shift)`；
4. `(候选模型族) AND (code OR dataset OR reproducibility)`；
5. 若模型将进入优化决策，再检索 `(decision-focused OR predict-then-optimize OR feasibility)`。

中文题目先提炼中英文同义词，再检索英文主流数据库。保存完整查询串，不能只记录数据库名称。

## 3. 来源优先级

优先顺序如下：

1. 期刊或会议官网、出版社页面、DOI 落地页；
2. OpenReview、PMLR、NeurIPS、AAAI、ACM 等官方论文页；
3. 作者正式预印本或 arXiv，并标明尚未同行评审；
4. 作者或机构的正式代码仓库，用于核验代码、权重、许可证和资源需求；
5. 博客、新闻和排行榜仅用于发现关键词，不能单独支撑论文结论。

赛前尽可能交叉使用不同一手索引；一次定向元数据核对不强制凑两个数据库。元数据冲突时，以正式版本记录页和论文 PDF 为准。无法联网时保留已核验锚点及原日期，写明未做此次补漏；不得称今天最新或搜索完整，也不必阻断已具备证据的经典建模。

## 4. 逐篇抽取证据

每篇候选分配唯一 `evidence_id`，并至少记录：

| 字段 | 内容 |
|---|---|
| 标识 | `evidence_id`、标题、作者、年份、期刊/会议、DOI 或稳定 URL |
| 状态 | 正式发表、录用、预印本、Workshop 或其他 |
| 主张 | 作者声称解决了什么问题，不能改写成更强结论 |
| 数据条件 | 样本规模、维数、领域、预测长度、训练/测试划分 |
| 比较协议 | 基线、指标、预算、种子、显著性或置信区间 |
| 可复现性 | 代码、数据、权重、许可证、依赖和硬件 |
| 负面证据 | 失败场景、消融、局限、外推和分布偏移表现 |
| 数模迁移 | 对本题具体替换哪个模块，产生什么可检验增量 |

去重优先使用 DOI；无 DOI 时使用“标准化标题 + 第一作者”。同一工作的预印本和正式版只保留正式版为主记录，并保留版本关系。

## 5. 论文与模型分开评级

论文质量高，不等于模型适合题目；模型很新，也不等于创新可落地。

- 论文证据等级：来源、同行评审、实验完整性、代码数据、独立复现；
- 模型适配等级：机制、数据、资源、可解释性、可验证性、约束与单位；
- 只有两类评级都通过，才能进入候选评分。

不得把作者在公开基准上的优势直接外推为本题优势，也不得用引用量替代适配性判断。

## 6. 停止条件

赛前充分性与赛时停止条件不同。赛时优先按锚点协议的时间/查询上限停止；没有会改变决定的新证据，不必为了填满下面各项再检索一轮。深入准备或实质新候选通常需要：

- 每个入围模型族至少有 2 个相互独立的一手来源；
- 至少找到 1 个基准、局限或负面结果来源；
- 获得足够的实现细节或可用代码，能够估算复现成本；
- 已明确透明基线、一个主候选和一个备选；
- 新查询只产生重复条目，或关键适配判断已明确。

上述资料可以来自已核验的赛前记录，不要求赛时重新获取。两个来源的独立性也不能靠把同一论文的预印本、正式版与 GitHub 算三篇来满足。

## 7. 唯一机器可读契约（schema v2）

`docs/innovation_matrix.json` 是实际题目搜索、证据与排名的结构化接口；赛前复用目录是独立的 `algorithm-anchors.json`，不能冒充目标题排名。不要手填 `source_count`。最小结构如下：

```json
{
  "schema_version": 2,
  "problem_contract_status": "FROZEN",
  "live_search_verified": true,
  "search": {
    "searched_at": "2026-09-01T22:20:00+08:00",
    "timezone": "Asia/Shanghai",
    "cutoff": "2026-09-01T22:20:00+08:00",
    "sites": ["PMLR", "OpenReview"],
    "queries": ["mechanism AND candidate AND limitation"],
    "failures": []
  },
  "baselines": [
    {"id": "B1", "name": "seasonal naive", "defect": "rolling joint coverage fails"}
  ],
  "evidence": [
    {
      "id": "E1",
      "title": "verified primary-source paper title",
      "primary_url": "https://example.org/official-paper-page",
      "publication_status": "PEER_REVIEWED",
      "verified_at": "2026-09-01T22:20:00+08:00",
      "code_status": "UNKNOWN",
      "compute_status": "UNREPORTED"
    }
  ],
  "candidates": [
    {
      "name": "joint conformal calibration",
      "baseline_id": "B1",
      "evidence_ids": ["E1"],
      "delta": "replace marginal intervals with a joint multi-horizon region",
      "fair_protocol": "same rolling origins, horizon, information set and tuning budget",
      "ablation_plan": "B1 vs B1+marginal calibration vs B1+joint calibration",
      "reject_condition": "joint coverage misses target or width destroys decision value",
      "feasibility_status": "PASS",
      "resource_status": "AVAILABLE",
      "mechanism_fit": 5,
      "data_fit": 4,
      "validation_strength": 5,
      "reproducibility": 3,
      "explainability": 4,
      "compute_fit": 4,
      "novelty": 3,
      "assumption_risk": 2,
      "implementation_risk": 2,
      "evidence_risk": 1
    }
  ]
}
```

约束如下：

- `searched_at`、`cutoff`、每条 `verified_at` 必须带 UTC offset；时区单独记录，避免只写日期；必须满足 `searched_at <= cutoff` 且 `verified_at <= cutoff`；
- 复用赛前资料时保留真实历史时间和检索记录，在 dossier/search log 标明 `ANCHOR_REUSE` 与所选 anchor IDs；`live_search_verified` 是兼容字段，表示证据确经联网核验，不能解释为当前任务刚搜索过。需要本日最新声明时记录实际 `GAP_REFRESH`；
- `sites`、`queries` 必须非空，`failures` 即使为空也要保留；搜索失败不能从日志中消失；
- `baseline_id` 必须引用带可复现 `defect` 的 baseline；`evidence_ids` 必须引用去重后的证据记录，来源数由此推导；少于两条证据记录时最多为 `WATCH`，但脚本不能自动判断二者是否真正独立；
- `delta`、`fair_protocol`、`ablation_plan`、`reject_condition` 不能为空；
- `feasibility_status` 使用 `PASS | FAIL | UNKNOWN`，`resource_status` 使用 `AVAILABLE | UNAVAILABLE | UNKNOWN`；`UNKNOWN` 强制 `WATCH`，不得靠高分覆盖；
- `publication_status` 使用 `PEER_REVIEWED | ACCEPTED | PREPRINT | WORKSHOP | UNDER_REVIEW | OTHER`；只有预印本/Workshop/审稿中证据时，候选最多为 `WATCH`；
- `code_status` 使用 `AVAILABLE | UNAVAILABLE | UNKNOWN`，`compute_status` 使用 `REPORTED | PARTIAL | UNREPORTED | UNKNOWN`；未披露成本必须原样保留。

`scripts/rank_candidates.py` 只验证此契约中的可解析关系和自报状态，不访问网络，也不判断论文真假、公式正确或本题效果。

为避免旧项目命令直接失效，脚本仍可读取 schema v1，但只把未触发硬拒绝的条目标为 `WATCH`，并返回 `migration_required=true`；不得用 v1 输出形成主方案。迁移时必须补齐 baseline、evidence、search metadata、delta、同协议、消融、拒绝条件和显式资源状态，不能伪造占位来源。

## 8. 检索日志模板

```markdown
# Frontier Search Log

- 题目/题号：
- 搜索日期与时区：
- 截止时间：
- 数据库/站点：
- 失败或受限来源：
- 原题与附件核验状态：

## Queries
1. ...

## Deduplicated evidence
| ID | Paper | Status | Problem fit | Code/data | Negative evidence | Decision |
|---|---|---|---|---|---|---|

## Verification boundary
检索证明了哪些元数据与公开主张；哪些数学正确性、运行结果和本题优势仍需本地实验验证。
```

最终交付按实际记录精度写明来源核验边界，区分文献事实、推断和本地实证。真实联网时记录完整时间/时区；日精度旧资料写“原资料核验至 YYYY-MM-DD，本轮离线复用”，不能补造小时分钟。准备库的现成引用不等于当下完成的新搜索。
