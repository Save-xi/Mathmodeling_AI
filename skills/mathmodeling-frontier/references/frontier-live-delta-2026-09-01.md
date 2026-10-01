# 数学建模前沿实时增量（核验至 2026-09-01）

> 历史核验截止：2026-09-01 22:21（Asia/Shanghai）。来源包括 PMLR、OpenReview、NeurIPS、期刊/DOI、arXiv 与作者代码。此文件保留当时的增量；当前匹配入口是 [precontest-anchors.md](precontest-anchors.md)。按原日期复用，赛时只对本题缺口补漏，不要求每道题重新核验全表。

## 检索结论与边界

- 本次查询没有发现 2026-08-28 至 2026-09-01 首次出现、且足以推翻现有 `baseline -> defect -> one delta -> same-protocol ablation` 路线的一手工作。
- 新增价值主要来自正式发表状态与更精确的适用门：预测输出对象、在线漂移、参数—结构失配、摊销成本、因果界、决策 regret、方程后验与隐喻元启发式反证。
- 以下成熟度是**竞赛采用风险**，不是论文质量：`MATURE`、`MODERATE`、`RESEARCH-STAGE`、`WATCH`。
- 这里只核验元数据、公开方法主张、代码可得性和已披露边界；没有在具体竞赛数据上复现实验，不能据此宣称优越。

## 会改变路由的九个决策门

| ID | 路由增量 | 只有在……才进入 | 硬拒绝/降级 | 最小基线与消融 | 竞赛状态 |
|---|---|---|---|---|---|
| D01 | 参数—结构 discrepancy 分离与摊销物理校准 | 有一族相关物理系统、可微机理模型、稀疏观测，且需反复校准未见 realization | 单一实例；无相关系统族；参数与结构项不可辨识；总训练成本无摊销空间 | 传统参数估计/KOH 或 Bayesian calibration；`physics only`、`residual only`、`parameter+discrepancy`；合成参数恢复与未见系统 | `MODERATE` |
| D02 | 局部物理状态残差或局部导数 neural operator | 直接算子在数据稀缺或局部非平稳区域稳定失效，且有多查询 PDE 任务 | 数值求解器已足够快；只有单轨迹；无可靠近邻状态/局部结构；不做守恒和边界外推 | 数值解、FNO/CNO；direct operator vs residual/local operator，同训练轨迹与预算 | `MODERATE` / `RESEARCH-STAGE` |
| D03 | 预测对象从边际区间升级为联合区域/轨迹 | 决策关心多步全程、累计、峰值或多源联合事件 | 只需点估计；样本不足以估依赖；把逐点 coverage 冒充路径安全 | 季节朴素/强经典预测器 + marginal conformal；再加 joint/trajectory calibration | `MODERATE` |
| D04 | 时序漂移下的 predict-then-update 在线校准 | 部署时目标会在预测后陆续到达，且存在可记录的 covariate/concept shift | 当前真实值修正当前预测；随机拆分；无在线反馈；不写覆盖/证书条件 | 固定 backbone、滚动再训练/简单残差更新、在线校准；报告 prequential error、coverage、宽度和更新成本 | `RESEARCH-STAGE` |
| D05 | 因果点估计降级为 partial identification | 点识别失败，但 RCT、单调性、工具变量或结构限制能给出可解释界 | 无处理定义/时间顺序/重叠；把界中点写成效应；假设不可辩护 | 关联预测/情景分析；不同识别假设下的界宽与敏感性 | `MATURE`（原则） |
| D06 | 鲁棒 decision-focused learning | 有许多相关“特征→参数→优化”实例，预测损失与决策 regret 确有错位并可能分布漂移 | 单一静态 MILP；无训练实例；不能保留可行性；总成本超过直接优化 | predict-then-optimize、经典鲁棒/随机优化、DFL；同实例/solver 时限，报告 regret/CVaR、可行率、oracle 调用和总成本 | `MODERATE` |
| D07 | 符号回归的复杂度控制或表达式后验 | 题目真正要求发现公式，且噪声下存在多条合理表达式或过拟合风险 | 只需预测；不做量纲/留出工况；用训练拟合度选式；把相关公式写成因果机理 | 量纲分析、稀疏回归/SINDy、确定性 SR；BIC/MDL 或 Bayesian SR；报告结构稳定、外推和候选公式不确定性 | `RESEARCH-STAGE` |
| D08 | 时空 OOD 的检索/动态图增强 | 真实图与持续流数据存在，固定图时序模型在预注册时间/区域外推上稳定失败 | 阈值强行造图；节点太少；只做 IID 随机划分；动态图不做边扰动/解释 | 无图时序、固定图、动态图/检索增强；留时间/区域外推与图消融 | `RESEARCH-STAGE` |
| D09 | 隐喻元启发式默认负门 | 仅在任务结构、分解、代理或精确—启发式混合提供可解释增量时考虑 | 只换动物名、chaos、Lévy、opposition、初始化或参数并称重大创新 | Random Search、题目原生启发式、经典同类算法、精确小实例/松弛界；同函数评估预算与 anytime 曲线 | `MATURE`（反证门） |

## 一手证据卡

### D01 物理校准与 discrepancy

- Venkataramanan, Vemuri, Denzler, 2026, *APIC: Amortized Physics-Informed Calibration using Neural Processes*, UAI 2026, PMLR 337. [PMLR](https://proceedings.mlr.press/v337/venkataramanan26a.html) · [作者代码](https://github.com/cvjena/APIC)
- 路由价值：把 instance-specific 物理参数与跨系统共享的 state-dependent 结构失配分开，并面向相关系统族摊销校准；公开代码当前聚焦一维 advection-diffusion-reaction PDE，不能写成通用物理校准器。
- 必审：合成参数/失配恢复、未见 realization、后验/区间校准、与 non-amortized calibration 的总成本和 break-even 次数。代码许可证和完整硬件成本若未现场核到，保持 `unknown`。

### D02 数据稀缺与局部非平稳 neural operator

- Yue, Yang, Zhu, 2025, *DeltaPhi: Physical States Residual Learning for Neural Operators in Data-Limited PDE Solving*, NeurIPS 2025. [Proceedings](https://proceedings.neurips.cc/paper_files/paper/2025/hash/12bf28fb68f295f855a5bf0c5a217d6e-Abstract-Conference.html) · [作者代码](https://github.com/yuexihang/DeltaPhi)
- Liu, Yang, Chen, 2026, *Riesz Neural Operator for Solving Partial Differential Equations*, ICLR 2026 Poster. [OpenReview](https://openreview.net/forum?id=Vjw7q1quNt)
- 路由价值：DeltaPhi 是目标/状态残差设计，RNO 结合全局谱与局部方向导数；都只解决特定 operator baseline 的结构缺陷，不能因 PDE 关键词自动使用。RNO 的公开实现若未核到，记 `code_status=UNKNOWN`。

### D03--D04 联合预测区域、依赖与在线漂移

- Zhang et al., 2026, *CAPTAIN: Conformal-Prediction-Based Multi-Source Time-Series Forecasting*, accepted by TMLR. [OpenReview](https://openreview.net/forum?id=WJjlXHo4yS&noteId=4MpRl5I4FZ) · [作者代码](https://github.com/zshuai8/2026-TMLR-CAPTAIN)
- English, Lippert, 2026, *FLIPR: FLexible and Interpretable Prediction Regions for time series*, PMLR 328. [PMLR](https://proceedings.mlr.press/v328/english26a.html)
- Barber, Pananjady, 2026, *Predictive inference for time series: why is split conformal effective despite temporal dependence?*, ALT 2026, PMLR 313. [PMLR](https://proceedings.mlr.press/v313/barber26a.html)
- Huang, Ma, Michailidis, 2026, *Model-Agnostic Online Certificate-Driven Calibration for Time Series Forecasting Under Distribution Shift*, UAI 2026, PMLR 337. [PMLR](https://proceedings.mlr.press/v337/huang26b.html)
- 路由价值：先选择统计对象，再选择方法。Barber--Pananjady 的理论结果针对相应依赖类与条件，不能扩写成“任意时序上的 distribution-free 保证”；在线校准严格遵守 predict-then-update 信息时点。

### D05 因果界而不是伪点估计

- Zhang, Skalnes, Chen, Oberst, 2026, *Bounding the Causal Impact of ML-assisted Decision-Making via Counterfactual Correctness*, UAI 2026, PMLR 337. [PMLR](https://proceedings.mlr.press/v337/zhang26b.html)
- 路由价值：在 prior RCT 与额外单调性假设下构造 causal-effect bounds，代表“识别不足时给界”的工作方式；不是对任意政策题自动适用。论文主张必须保留其外部证据与单调性条件。

### D06 决策聚焦学习与可行性兜底

- Yamao et al., 2026, *Robust Decision-Focused Learning via Worst-Case Regret Minimization*, UAI 2026, PMLR 337. [PMLR](https://proceedings.mlr.press/v337/yamao26a.html) · [作者代码](https://github.com/isct-nakatalab/UAI2026_Robust_Decision-Focused_Learning_via_Worst-Case_Regret_Minimization)
- Jeon et al., 2026, *Decision-focused Sparse Tangent Portfolio Optimization*, ICML 2026. [OpenReview](https://openreview.net/forum?id=KV7XHF0IbK) · [作者代码](https://github.com/feuerwerksh/Diffble-card-SR)
- 路由价值：前者强调 regret 对观测误差/分布漂移的鲁棒化，后者是结构保持的可微优化层与离散选择代理的领域实例。可迁移的是“下游目标 + 结构化决策层 + 独立可行性”，不是照搬投资模型。

### D07 方程复杂度与结构不确定性

- Bastiani et al., 2026, *Complexity-Aware Deep Symbolic Regression with Robust Risk-Seeking Policy Gradients*, AISTATS 2026, PMLR 300. [PMLR](https://proceedings.mlr.press/v300/bastiani26a.html) · [作者代码](https://github.com/ZakBastiani/CADSR)
- Boussif et al., 2026, *Bayesian Symbolic Regression with Entropic Reinforcement Learning*, UAI 2026, PMLR 337. [PMLR](https://proceedings.mlr.press/v337/boussif26a.html)
- 路由价值：CADSR 用复杂度—拟合准则约束表达式，ERRLESS 面向表达式后验而非单一最优式。竞赛默认仍先做量纲分析、稀疏方程发现和简单 SR；没有代码/算力核验的 Bayesian 路线保留 `RESEARCH-STAGE`。

### D08--D09 时空 OOD 与元启发式反证

- Zhang et al., 2025, *STRAP: Spatio-Temporal Pattern Retrieval for Out-of-Distribution Generalization*, NeurIPS 2025. [OpenReview](https://openreview.net/forum?id=Y5wMoIbdDs) · [作者代码](https://github.com/HoweyZ/STRAP)
- Vermetten et al., 2024, *Large-Scale Benchmarking of Metaphor-Based Optimization Heuristics*, GECCO 2024. [DOI](https://doi.org/10.1145/3638529.3654122) · [复现工件](https://zenodo.org/records/10561215)
- 路由价值：STRAP 只在真实 STOOD 缺陷上进入；元启发式基准作为负面证据，说明排名会受预算、指标和协议影响，不能从新隐喻名推断算法进步。

## 当前停止条件

使用此历史 delta 不自动要求联网；按所选锚点判断是否有条件、版本或遗漏差分。必要的定向查询只出现重复条目或无法改变路线时即停止，转入 MVP 实验。论文能否保留“创新”由本题实验与 `claim_level` 审计决定。
