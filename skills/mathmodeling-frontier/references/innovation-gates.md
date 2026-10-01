# 创新筛选、消融与论文证据门

创新不是“模型更复杂”，而是相对透明基线出现了可解释、可测量、可复现的增量。优先选择一项建模创新加一项验证创新，避免把多个前沿名词堆成不可归因的系统。

## 1. 增量位置（`delta_location`）

这里描述创新增量落在流程哪里，不是论文主张强度。主 `$mathmodeling` 的 `claim_level`（Level 0--4）单独决定“采用/适配/集成/提出”等写法；两套标签不得互换。按下列位置寻找最小充分创新：

1. **问题表述创新**：改变状态、图结构、约束、目标或多尺度耦合，使模型更贴合机制；
2. **数据与证据创新**：新的特征构造、弱监督、迁移、缺失机制或数据融合，并有泄漏防护；
3. **不确定性与目标创新**：从点估计升级到区间、风险、鲁棒性或决策损失；
4. **求解与算法创新**：学习增强搜索、代理模型、热启动、分解、混合精确方法；
5. **验证创新**：时序外推、压力测试、反事实、稳定性、约束违背率或决策后悔值。

多数竞赛题用“一项模型创新 + 一项验证创新”已经足够。若新增模块不能形成独立消融，则应合并、降级或删除。

## 2. 硬拒绝门

出现任一项时，候选不能成为主模型：

- 机制适配分低于 3/5；
- 数据适配分低于 2/5；
- 验证强度低于 2/5；
- 没有经过核验且日期/适用边界明确的一手来源，或证据风险达到 4/5；赛前已核验的资料可复用，当前最新声明另做差分核验；
- 学习模块可能产生不可行解，且没有独立可行性检查或修复；
- 所需训练数据、权重、许可证、GPU、商业求解器或时间预算不可获得；
- 评价存在标签泄漏、时序穿越、调参集与测试集混用或不公平预算；
- 简单基线在相同协议下已经达到同等效果，而新模型没有提供新区间、鲁棒性、可解释性或决策能力。

硬门优先于总分和新颖度。

`feasibility_status=UNKNOWN`、`resource_status=UNKNOWN` 或 `problem_contract_status=PROVISIONAL` 不等于硬拒绝，但强制候选为 `WATCH`。缺失字段不得默认为通过。

## 3. 候选评分字段

每项使用 0--5 分。收益项：

- `mechanism_fit`：是否对应真实机制，而非仅相关性；
- `data_fit`：样本规模、维度、缺失、时空结构和标签条件是否匹配；
- `validation_strength`：能否用当前数据设计公平基准、消融和外推验证；
- `reproducibility`：实现细节、代码、数据、许可证和依赖；
- `explainability`：能否解释变量、约束、模块作用与失败边界；
- `compute_fit`：在比赛资源和时间内是否可运行；
- `novelty`：相对常规方案是否提供实质增量。

风险项：

- `assumption_risk`：假设失配或辨识不足；
- `implementation_risk`：实现、收敛、数值稳定和部署风险；
- `evidence_risk`：来源弱、未评审、缺代码、缺负面实验或元数据不确定。

评分脚本只帮助排序，不替代建模判断。完整且唯一的输入契约见 [live-search-protocol.md](live-search-protocol.md) 的 schema v2；下面只是其中一个 candidate 对象，不能单独作为脚本输入：

```json
{
  "name": "decision-focused forecasting plus MILP",
  "baseline_id": "B1",
  "evidence_ids": ["E1", "E2"],
  "delta": "replace forecast loss with downstream regret while retaining MILP feasibility",
  "fair_protocol": "same instances, information, solver limits and seeds",
  "ablation_plan": "predict-then-optimize vs decision-focused plus feasibility repair",
  "reject_condition": "no regret gain or total cost exceeds the contest budget",
  "feasibility_status": "PASS",
  "resource_status": "AVAILABLE",
  "mechanism_fit": 5,
  "data_fit": 4,
  "validation_strength": 5,
  "reproducibility": 4,
  "explainability": 4,
  "compute_fit": 4,
  "novelty": 4,
  "assumption_risk": 2,
  "implementation_risk": 3,
  "evidence_risk": 1
}
```

## 4. 冻结最小实验

在实现前固定：

- 数据划分与泄漏防线；时序题使用滚动或前向验证，空间题保留区域外推；
- 透明基线、主指标、决策指标、约束违背率、运行时间和显存/内存；
- 同一数据、同一信息集、同一调参预算、同一随机种子集合和同一求解终止条件；
- 一项主创新及其单独消融；
- 不确定性报告：重复运行、置信区间、bootstrap 或场景覆盖；
- 预先声明的晋级阈值和拒绝条件。

建议至少比较：

| 变体 | 含义 |
|---|---|
| B0 | 最简单可信基线 |
| B1 | 经过合理调参的强经典基线 |
| F | 完整前沿方案 |
| A | 删除或替换创新模块的消融方案 |
| R | 鲁棒性、分布偏移或压力测试方案 |

若 F 只在训练集、单个种子或额外预算下领先，不得晋级。

## 5. 晋级状态

- `PRIMARY`：硬门全部通过，迁移证据、资源与预注册协议足以优先进入本地 MVP；这是“主候选”，不是“本题已验证”；
- `BACKUP`：可落地且风险低，但预期增量、数据条件或解释性略弱，作为失败回退候选；
- `WATCH`：有潜力，但依赖预印本、特殊硬件、未释放代码或尚无公平验证；
- `REJECT`：触发硬门或在本题协议下没有净收益。

状态由 schema 中的真实引用关系和显式未知项产生：`source_count` 只能从去重后的 `evidence_ids` 推导；证据记录少于两条、只有预印本/Workshop/under-review 证据、问题契约未冻结、可行性或资源未知时，最高为 `WATCH`。脚本不能自动判断两条来源是否真正独立；排名脚本的 `PRIMARY` 仍只是“按所填证据通过门槛”，不是本题已验证。

本地同协议实验后再作第二次裁决：达到预声明阈值且消融支持模块作用时标 `RETAINED` 并进入论文；否则标 `REVERTED`，恢复经典主模型或 backup。`rank_candidates.py` 不生成这两个实验后状态。

## 6. 论文表述模板

用“问题缺口—最小改动—验证—边界”写创新点，而不是只报模型名：

```latex
\paragraph{模型创新与证据边界}
针对基线模型在\textbf{[具体机制或数据条件]}下的\textbf{[可观测缺陷]}，
本文引入\textbf{[一个明确的新模块或目标]}，并保持\textbf{[约束、信息集与计算预算]}一致。
在\textbf{[固定划分/滚动验证/压力场景]}上，相较于\textbf{[B0 与 B1]}，
该改动使\textbf{[主指标或决策指标]}由\textbf{[数值]}改善至\textbf{[数值]}；
删除该模块后，性能回落至\textbf{[消融数值]}，说明增益主要来自该设计。
该结论仅适用于\textbf{[数据规模、预测范围和约束条件]}，
在\textbf{[失败场景]}下仍需采用\textbf{[备选方案]}。
```

文献只用于说明方法来源和已知性质；“在本题上有效”必须来自本地同协议实验。正文、图表、附录和代码中的模型名、指标、样本数与结论边界必须一致。
