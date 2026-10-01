# 数学建模前沿方法知识层（2026-08-27 兼容归档）

**归档核验截止：2026-08-27；不是当前路由源。** 本文件保留上一版方法卡和离线检索词，避免旧项目链接失效。当前“最新/前沿”请求应由 `$mathmodeling-frontier` 执行实时一手来源检索并维护 dated delta；主 Skill 不再并行更新本文件。只有 specialist 不可用且需要离线构造查询时，才按相关小节取关键词，不能引用本文件日期证明现状。

## 使用边界与状态标记

### 限时单卡采用索引（采用策略，不是实时文献排名）

此索引按通常的本科竞赛、72 小时和单卡 8GB 预算判断。`USE` 表示任务需要时优先考虑；`CONDITIONAL` 必须先具备数据、实现、资源与验证条件；`AVOID` 表示通常不在赛中临时建设。均不表示已在本机跑通。下文的来源日期与研究状态仍保持归档身份，实际权重/接口/论文状态交给 specialist 核验。

| 方法族 | 采用策略 | 条件/退出边界 |
|---|---|---|
| 数值 ODE/PDE、状态空间、受约束最小二乘 | USE | 先建立可复算基线，核对收敛和可辨识性 |
| PINN、RoPINN、Neural ODE | CONDITIONAL | 小问题、明确方程、可靠代码；无稳定增益或优化失败则回数值法 |
| Neural SDE | AVOID | 扩散辨识、训练和路径分布验证负担高 |
| Differentiable simulation | CONDITIONAL | 已有可信可微模拟器，不在临场从零改造 |
| DeepONet、FNO、CNO、DeltaPhi | CONDITIONAL | 已有同类轨迹、小规模实现和可摊销查询；残差配对不得泄漏 |
| Geometry/graph neural operator | AVOID | 几何接口、数据和外推验证链过长 |
| DPOT、UPT、Poseidon | CONDITIONAL | 仅匹配任务且已试跑的现有权重；从零预训练排除 |
| MoE-POT、HyPINO | AVOID | 临场多域训练/复杂数据管线通常不合预算；已有完整项目另判 |
| PINTO、physics-informed fine-tuning | CONDITIONAL | 可靠实现与匹配方程/权重先存在，只做可验证增量 |
| Physics Transformer、test-time operator splitting/composition | AVOID | 新实现或算子库/搜索成本缺少竞赛级保障 |
| Physics-informed GP | CONDITIONAL | 中小数据与低维推断，检查核假设和校准 |
| DiffusionPDE、diffusion/flow inverse、Diffusion Last Layer | AVOID | 生成、采样与分布验证通常超出必要工作 |
| ARIMA/ETS、历史信息内分解、轻量分位数/概率预测 | USE | 数据条件与风险对象匹配，滚动验证 |
| TCN、GRU/LSTM、Transformer、modern SSM | CONDITIONAL | 有依赖与样本证据，先测端到端时间/显存及系统/CUDA 兼容 |
| TimesFM、Moirai 等预训练时序模型 | CONDITIONAL | 先做小成本零样本比较，冻结版本/权重/协变量和校准协议 |
| GCN、GAT、message passing、固定图时序 | CONDITIONAL | 真实图、足够独立数据、无图/固定图消融 |
| 动态/自适应/异构图 | CONDITIONAL | 低于简单固定图的优先级；额外数据、时间与消融必须先满足 |
| SCM/DAG 作为识别工具 | USE | 适用于因果任务；图本身不证明识别 |
| 处理效应、反事实、Causal ML、因果+优化 | CONDITIONAL | 识别、重叠、干扰与独立评价先成立 |
| 因果发现（含归档新动力因果方法） | AVOID | 不以临场发现图当作已确认的干预机制 |
| 正确单位 bootstrap、低维 Bayesian/GP、conformal | CONDITIONAL | 依赖/交换性与区间对象要匹配，不把边际覆盖改成路径保证 |
| 小规模 ensemble | USE | 控制预算；共同偏差不会因集成消失 |
| Bayesian optimization、surrogate/多保真优化 | CONDITIONAL | 原始评价昂贵且维度/结构合适，最终回原模型验证 |
| LLM-guided BO | AVOID | 通常先普通 BO，额外先验和调用需独立增量证据 |
| Symbolic regression、SINDy、PDE/对称性发现、蒸馏 | CONDITIONAL | 限制搜索库和复杂度，检验导数噪声、量纲、极限和未见工况 |
| LP/MILP/DP、可解释情景/鲁棒/CVaR | USE | 结构匹配且可复算；不确定集/风险参数有依据 |
| DRO、SDDP、复杂分解、learning-to-optimize | CONDITIONAL | 有必要规模/结构，学习成本可摊销且保留可行性与界 |
| OR+RL、offline RL、multi-agent RL | AVOID | 未已有可信模拟器/日志覆盖/评价链时不临场搭建 |
| PSO、GA、SA、DE | CONDITIONAL | 近似求解工具；同函数评估预算、多种子、简单/精确基线 |
| 动物换名、chaos/opposition/Lévy 包装 | AVOID | 不作为优先创新；有用性与命名无关 |
| 机理残差修正、预测+校准情景+决策 | USE | 缺陷明确且各组件满足其条件；不为组合本身声称创新 |
| LLM 辅助检索/编码/审计 | USE | 按比赛规则核验和记录；模型组件需要额外独立验证 |

按需索引：A 科学计算；B 时序；C 图；D 因果；E 不确定性；F 方程发现；G 运筹与学习；H 元启发式；I 组合；J 工具；K 原始来源。普通路线不要加载下面全部方法卡。

- `MATURE`：理论、工具和复现路径较成熟；仍需在本题验证。
- `MODERATE`：已有同行评审/公开实现或较多复现，但竞赛数据与环境适配成本明显。
- `RESEARCH-STAGE`：研究原型或复现条件较重，结果依赖专门数据/算力。
- `WATCH`：较新的预印本、Workshop 工作或状态仍可能变化；只能作为高风险候选。

状态标记描述的是**采用风险与证据成熟度**，不是论文质量。任何网页、代码或论文可用性均可能变化；明确要求“最新”时应实时检索。

统一标签采用：

```text
[任务 | 数据 | 结构 | 机制 | 解释性 | 算力 | 实现难度 | 比赛风险 | 创新潜力 | 代码成熟度]
```

例如：

```text
[prediction,inverse-problem | medium-data | PDE | hybrid,physics-informed
 | medium | high | high | high | high | research-stage]
```

标签是起点，不替代题目数据审计、baseline、消融和外推验证。

## A. Scientific Machine Learning

### 先问是不是一个科学计算问题

进入本节前至少确认一项：

- 有明确 ODE/PDE、守恒律、几何、边界/初值或可微模拟器；
- 目标是参数/源项/状态反演，而不仅是普通表格预测；
- 需要在许多参数、初值、边界或几何上重复求解同一类算子；
- 观测稀疏但机理足以提供可核验约束。

若只是“有物理含义的变量”，但没有可写出的机制约束，优先普通回归/时序模型；不得把领域名词当成 PINN 的依据。

### 经典科学计算 baseline

至少保留一种：有限差分/有限体积/有限元/谱方法、常微分方程积分器、状态空间/系统辨识、受约束最小二乘或 Bayesian 逆问题。记录网格、时间步、收敛性、初边值条件、求解器容差和守恒误差。

### 基础 Scientific ML 方法卡片

| 方法 | 真正解决的问题与数据条件 | 不适合/主要风险 | 竞赛采用建议与组合 | 状态与标签摘要 |
|---|---|---|---|---|
| PINN | 已知 ODE/PDE，通过方程残差、初边值和少量观测联合训练；适合小规模正/逆问题 | 刚性、多尺度、高频、长时域、损失失衡与优化失败；并不天然优于数值法 | 先给数值/解析 baseline；用于参数辨识、稀疏观测融合或 learned correction；检查残差外的真实解误差 | `MODERATE`；`inverse/simulation, small-medium, PDE/ODE, physics-informed, compute=medium-high, risk=medium-high` |
| RoPINN | 把 PINN 的点约束扩展为局部区域优化，针对散点配点的泛化缺陷 | 仍继承 PINN 的方程、可微和优化要求；不是所有 PDE 都稳定改善 | 有现成实现且 baseline PINN 已失败时作为训练增强；必须比较 PINN vs RoPINN | `MODERATE`；`implementation=medium, risk=medium, code=mature` |
| Neural ODE | 把隐藏状态导数参数化并交给 ODE 求解器，适合连续时间、不规则采样和未知动力学 | 可辨识性、刚性、反向积分误差和训练成本；不能替代已知可信 ODE | 与经典 ODE/状态空间比较；可做“已知动力学 + learned residual” | `MODERATE`；`prediction/discovery, medium-data, ODE, hybrid/data-driven, risk=medium` |
| Neural SDE | 用随机微分方程表达随机动力与路径分布，适合本征噪声、连续时间不确定性 | 数据需求和训练诊断重，扩散项难辨识；比赛中易把观测噪声误作过程噪声 | 只有点预测明显不足且风险概率重要时使用；与随机状态空间/传统 SDE 比较 | `RESEARCH-STAGE`；`probabilistic prediction, medium-large, ODE, data-driven/hybrid, compute=high, risk=high` |
| Differentiable simulation | 对模拟器/离散求解过程求梯度，用于参数反演、控制和设计 | 求解器需可微/可改造；梯度不稳定、内存高、离散化偏差 | 若已有可信模拟器且目标是校准/优化，通常比从零训练大模型更贴题 | `MODERATE`；`inverse/optimization, small-medium, PDE/ODE, mechanistic-hybrid, risk=medium` |
| DeepONet | 学习输入函数到输出函数的算子，branch/trunk 结构适合传感器值到任意查询点 | 训练轨迹和传感器布局要求；跨几何/跨物理外推弱 | 当同类 PDE 需批量快速求解时使用；与数值解和简单 surrogate 比较 | `MODERATE`；`prediction/simulation, medium-large, PDE, data-driven/hybrid, compute=medium-high, risk=medium-high` |
| FNO | 在频域学习全局算子，适合规则网格、平滑场和参数化 PDE | 复杂几何、边界细节、高频/不规则网格和 OOD 工况 | 是 neural operator 的强 baseline，不应把它当最终创新；报告跨分辨率和谱误差 | `MODERATE`；`prediction/simulation, large-data, PDE/spatial, data-driven, risk=medium-high` |
| CNO | 连续感知的卷积算子，强调离散化一致性与多尺度局部结构 | 仍需大量高质量轨迹；不规则几何需额外处理 | 规则/可重采样场上与 FNO 比较，关注边界、分辨率迁移和局部细节 | `MODERATE`；`prediction, large-data, PDE/spatial, data-driven, risk=medium-high` |
| Geometry/graph neural operator | 在网格、点云或粒子图上学习算子 | 图构造和消息传递可能制造偏差；长程耦合成本高 | 仅在几何/网格确实不规则时进入，保留插值+普通算子 baseline | `RESEARCH-STAGE`；`prediction, large-data, PDE/graph, data-driven/hybrid, compute=high, risk=high` |

### PDE foundation/operator frontier

这些模型多用于跨 PDE 预训练、迁移或零/少样本求解。它们在竞赛中通常不是“从零训练”的现实选择；只有公开权重、域匹配和复现实验齐备时，才可作为 Aggressive 方案。

| 方法 | 核心结构价值 | 数据/实现条件 | 3–4 天比赛窗口判断 | 状态 |
|---|---|---|---|---|
| DPOT | 自回归去噪预训练 + Fourier attention，展示大规模 PDE 语料预训练路线 | 多 PDE 轨迹、重型预训练；论文实验规模远超普通竞赛 | 不从零复现；仅在权重和任务接口匹配时评估迁移 | `RESEARCH-STAGE` |
| UPT | 把不同网格/粒子集合压缩为共享 latent tokens，并在连续时空查询 | 复杂数据接口和大状态训练；需检查几何压缩误差 | 可借鉴“编码—潜空间演化—查询”结构；完整复现高风险 | `RESEARCH-STAGE` |
| Poseidon | 多尺度 operator Transformer、时间条件化和 semigroup-aware 训练 | 预训练域主要影响迁移；需权重、显存和 PDE 数据适配 | 作为公开预训练模型比较项，而非默认主模型 | `RESEARCH-STAGE` |
| MoE-POT | 方程依赖路由、共享/专用专家，缓解异质 PDE 干扰 | 专家训练、路由和大规模多域语料，调试与算力高 | 对普通竞赛通常只作研究展望；“加 MoE”本身不构成创新 | `RESEARCH-STAGE` |
| HyPINO | hypernetwork + manufactured solutions + physics-informed 无标签训练，面向跨参数 PDE | 需构造解析/制造解并训练多任务网络；实现链长 | 若题目天然提供 PDE 家族和制造解，可借鉴混合监督；否则高风险 | `RESEARCH-STAGE` |
| DeltaPhi | 学习物理相近状态之间的残差关系，改变预测目标而非简单加深网络 | 需定义“相近状态”并避免配对泄漏 | 残差重参数化思想可低成本借鉴；必须做 full-state vs residual 消融 | `MODERATE` |
| PINTO | 用物理损失训练 Transformer neural operator，减少对稠密模拟标签的依赖 | 明确 PDE/初边值、自动微分和稳定训练；论文为预印本路线 | 可作为无标签 operator 候选；没有现成可靠实现时列 `WATCH` | `WATCH` |
| Physics-informed fine-tuning | 在 PDE foundation model 适配阶段加入物理约束 | 必须先有可用 foundation model；权重、方程和接口均匹配 | 只做增量微调和严格消融，不作为普通题默认路线 | `WATCH`（2026 Workshop） |
| Physics Transformer | 把场视为连续函数，局部自适应基投影后形成 physics tokens | 2026 新预印本；大规模 2D/3D 任务、复杂实现和算力 | 只作 Aggressive/Watch；不得写成已成熟通用解法 | `WATCH`（2026 preprint） |
| Test-time operator composition/splitting | 不改权重，在测试时搜索/组合已有物理算子以适配新任务 | 需要可组合且接口一致的预训练算子库；搜索空间和稳定性未知 | 适合研究项目，不适合临时搭建；可借鉴“模块组合 + 物理检查” | `WATCH`（2026 preprint） |

### 不确定、逆问题与生成式科学计算

| 方法 | 适用条件 | 关键证据 | 竞赛风险 |
|---|---|---|---|
| Physics-informed GP | 中小数据、需要函数空间后验且物理约束可写入均值/核/状态空间 | 后验校准、覆盖率、核/物理假设、计算复杂度 | 中；高维场需稀疏/结构化推断 |
| DiffusionPDE | 部分观测下可能存在多解/后验分布，需生成多个物理可行场 | 数据一致性、物理残差、样本多样性、覆盖与校准 | 高；生成成本和评价复杂 |
| Diffusion/flow inverse solver | 逆问题后验非高斯或多峰，有足够模拟训练对 | posterior recovery、coverage、simulation-based calibration | 高；不得只展示漂亮样本 |
| Diffusion Last Layer | 给已有 deterministic operator 增加条件函数空间分布 | 与 ensemble/GP/conformal 比较，校准和区间宽度 | 高；2026 新工作，只作 `WATCH` |

不确定性不是“附加一张阴影图”。如果区间进入决策，必须评价 coverage、sharpness、calibration、tail risk 与决策质量。

### 科学机器学习验证底线

- 数值/解析 baseline；同一参数域和网格协议；
- 随机点误差之外，报告相对 `L1/L2`、边界误差、守恒残差、谱误差和长时稳定性；
- 网格/步长收敛、跨分辨率、跨参数区间和 held-out geometry/regime；
- inverse problem 做 synthetic recovery、可辨识性和噪声敏感性；
- 组合模型做 `mechanistic` vs `mechanistic+learned` 消融；
- 把生成模拟数据与真实观测分开报告，避免同一求解器分布上的虚假泛化。

## B. 时序与动态系统

### 按数据条件选择

| 条件 | 首选 baseline | 可升级候选 | 关键检查 |
|---|---|---|---|
| 单条短序列/小样本 | naive、seasonal naive、ETS、ARIMA、结构状态空间 | 正则化回归、分解+轻量模型 | 参数数、结构突变、滚动窗口稳定性 |
| 多条相关短序列 | 分层/面板回归、共享状态空间 | global RNN/TCN、轻量 Transformer、预训练 TSFM | 实体泄漏、跨序列归一化、冷启动 |
| 中等长度、局部依赖 | ARIMA/ETS/线性、树模型 | TCN、GRU/LSTM | 感受野、外生变量、残差自相关 |
| 长序列、长依赖 | seasonal naive、线性、状态空间 | Transformer、modern SSM | 窗口长度、漂移、训练成本、消融 |
| 非平稳/多尺度 | naive、分解、状态空间 | decomposition + TCN/SSM/Transformer | 分解是否只用过去数据、变点与外推 |
| 多变量 | VAR/动态回归/状态空间 | TCN、RNN、Transformer、SSM | 变量同步、共线、目标泄漏、因果误读 |
| 多节点且有真实空间关系 | 每节点/全局时序、固定空间滞后 | spatiotemporal GNN、dynamic graph + temporal/SSM | 图来源、固定/动态图消融、空间外推 |
| 有物理动力学 | ODE/state-space baseline | mechanistic + residual、Neural ODE/SDE | 连续时间、可辨识性、物理一致性 |
| 需要区间/风险 | 历史残差区间、分位数回归 | probabilistic forecast、ensemble、conformal | coverage、sharpness、风险传播 |

### 模型家族卡片

- **ARIMA/ETS/state space — `MATURE`：** 低算力、可解释、适合短中序列与明确趋势季节；状态空间还可处理缺失、潜变量和动态参数。不要因“老”而删除。
- **TCN — `MODERATE`：** 卷积感受野适合局部/多尺度依赖，训练并行；在中等数据上常比重型 attention 更可控。检查 receptive field 与边界填充。
- **GRU/LSTM — `MODERATE`：** 适合中等序列和多序列 global model；长依赖和训练速度有限，但代码成熟。
- **Transformer — `MODERATE`：** 只有足够序列/实体、长依赖或复杂协变量交互时合理；必须和线性、TCN/SSM 比较。
- **Modern SSM — `MODERATE`：** 以状态递推表达长序列并改善复杂度；竞赛中更适合有成熟库和长序列证据时，不能只凭“长序列”采用。
- **Foundation model for time series — `RESEARCH-STAGE`：** TimesFM、Moirai 等支持零样本/少样本迁移，但域匹配、外生变量、上下文长度、概率输出和资源差异决定结果。
- **Decomposition + forecasting — `MATURE`：** 只有分解步骤不看未来、各分量职责可解释且消融有效时才算结构增强。
- **Probabilistic forecasting — `MODERATE`：** 当资源储备、极端风险或服务水平依赖尾部时必需；评价 CRPS/coverage/quantile loss，而非只看 RMSE。

### Foundation model 的负证据

TimesFM 与 Moirai 在 ICML 2024 提供了有代表性的零样本时序 foundation 路线；但后续实证表明性能高度依赖数据域和协议。ICLR 2025 Workshop 的云数据研究中，多个 foundation model 被简单线性 baseline 稳定超过；2026 的 accuracy-energy benchmark 也显示准确率具有数据集依赖，而能耗/延迟与架构密切相关。因此：

1. 不把预训练规模当成题目适配证据；
2. 同时报告准确率、稳定性、运行时间和资源；
3. 保留 naive、ARIMA/ETS、线性或专用模型；
4. 零样本失败时允许降级，不为“前沿”强行微调。

## C. 图模型

### 图是否真实存在

只有节点/边对应可解释实体与作用通道时，才使用图模型。边可来自道路、流量、供应、接触、通信、空间邻接、物理耦合或明确相互作用。把表格行按相似度连边必须说明阈值、稳定性和相对普通 tabular 模型的必要性。

### 固定图与动态图

```text
固定关系：A 由道路/拓扑/距离等外部事实给定
时变关系：A_t = f(X_t)，边权/邻接由当时状态生成
```

若使用 `A_t`，必须约束对称性/方向、稀疏度、自环、可达性与信息时间；`f(X_t)` 不能读取预测期未来状态。比较：

```text
无图时序  vs  固定 A + 时序  vs  A_t + 时序
```

### 图模型方法卡片

| 方法 | 适合 | 不适合/风险 | 标签摘要 |
|---|---|---|---|
| GCN | 固定同质图、平滑聚合 | 异配图、动态图、过平滑 | `prediction/classification, graph, data-driven, compute=medium, risk=medium` |
| GAT | 邻居贡献不同且 attention 可审计 | attention 不等于因果解释；稠密图成本高 | `graph, data-driven, interpretability=medium-low, risk=medium` |
| Message passing | 边/节点有物理或组合语义，可自定义局部更新 | 深层长程传播和稳定性 | `graph/network, hybrid possible, implementation=medium` |
| Graph temporal model | 固定网络上的节点序列 | 没有真实图或时间对齐差 | `spatiotemporal, medium-large data, risk=medium-high` |
| Dynamic/adaptive graph | 关系确实随拥堵、需求、接触或状态变化 | 容易学习噪声/泄漏，解释和消融要求高 | `spatiotemporal, data-driven/hybrid, compute=high, risk=high` |
| Heterogeneous graph | 节点/边类型语义与约束确实不同 | 为复杂而分类型；数据更稀疏 | `graph/network, implementation=high, risk=high` |

城市交通的 Balanced 路线通常是：季节/状态空间 baseline → 固定路网 + TCN/GRU/SSM → 若残差证明关系时变，再加动态邻接并做消融。

## D. 因果推断

### 预测不等于干预

```text
P(Y | X) != P(Y | do(X))
```

如果题目问“预测会发生什么”，关联模型可能足够；如果问“增加投入/实施政策会导致什么”，必须检查干预、混杂和反事实。

| 方法族 | 用途 | 最低条件 | 主要风险 |
|---|---|---|---|
| SCM / DAG | 明确变量生成与干预结构 | 时间顺序、领域知识、可说明的图假设 | 图不唯一、隐藏混杂 |
| Treatment effect | ATE/CATE、政策效果异质性 | 处理、结果、混杂、重叠性和 SUTVA 类假设 | 选择偏差、外推到无重叠区域 |
| Causal discovery | 从观测/时序寻找候选结构 | 可辨识假设、足够样本、稳定性 | 不能把发现图直接写成已证因果 |
| Counterfactual | 个体/情景反事实 | 已识别结构模型和可校准噪声 | 不可验证部分多，需敏感性分析 |
| Causal ML | 高维 nuisance/异质效应 | cross-fitting、重叠、独立评价 | 预测性能不能替代因果识别 |
| Causal + optimization | 在因果效应上配置资源或设计干预 | 效应可识别、约束与目标明确 | 识别误差被决策放大 |

2026 年 `Causal Discovery from Heteroscedastic Stochastic Dynamical Systems under Imperfect Physical Models` 探索把不完美物理模型与随机动力因果发现结合；截至核验日为预印本，只能作为 `WATCH`。原始材料中把该 arXiv 号对应成另一标题的写法已纠正。

任何因果方案都要列出：DAG/时间顺序、识别策略、不可检验假设、负对照/安慰剂或敏感性、重叠诊断和结论边界。数据不足时降级为“关联 + 情景分析”。

## E. 不确定性量化

把 UQ 视为模型或决策的增强层：

```text
prediction + uncertainty
prediction + calibrated interval + decision
posterior/scenario + robust or stochastic optimization
```

| 需求 | 推荐路线 | 必须报告 |
|---|---|---|
| 描述性或低风险点估计 | point estimate + residual/sensitivity | 误差分布、适用域 |
| 单次预测需要区间 | bootstrap、Bayesian、GP、quantile、conformal | coverage、宽度、分组覆盖 |
| 需要事件风险概率 | 概率模型/ensemble/posterior predictive | calibration、Brier/log score、尾部样本 |
| 高风险资源配置 | 预测分布/集合 + stochastic/robust optimization | 可靠性、保守成本、决策后悔 |
| 昂贵黑箱优化 | GP/ensemble surrogate + Bayesian optimization | acquisition、噪声、预算、重复点、最终验证 |
| 函数/场不确定性 | GP/operator posterior/generative operator | pointwise 与 simultaneous coverage、物理一致 |

- **Bayesian modeling/GP — `MATURE`：** 中小数据、先验和不确定性传播强，但高维/大样本的可扩展实现仍有明显成本。
- **Ensemble — `MATURE`：** 易实现但成员相关性会低估不确定性。
- **Conformal prediction — `MODERATE`：** 在交换性或适当时序校准条件下给有限样本覆盖；时序漂移时需专门校准，不能机械套分割 conformal。
- **Bayesian optimization — `MATURE`：** 适合昂贵、低到中维黑箱；高维和约束问题需要结构化 surrogate/acquisition。
- **LLM-guided BO — `WATCH`：** LLM 可提供语义先验或偏好，但错误先验必须可退化到普通 BO；仅“调用 LLM”不算创新。

## F. Symbolic Regression / Equation Discovery

目标不是把黑箱换成更花哨的黑箱，而是发现可检验的数学结构。

| 路线 | 适合 | 主要风险 | 标签摘要 |
|---|---|---|---|
| Symbolic regression | 经验公式、变量关系、无量纲组合 | 搜索空间大、复杂度偏置、伪规律 | `discovery, small-medium, tabular/ODE, interpretable, compute=medium-high, risk=medium-high` |
| SINDy/稀疏动力学 | 状态及导数可估、真实方程在候选库中稀疏 | 微分放大噪声、库错配、共线 | `discovery, small-medium, ODE/PDE, mechanistic-hybrid, risk=medium` |
| PDE equation discovery | 时空场及导数、未知项稀疏 | 采样/边界/噪声导致伪项 | `discovery, medium-large, PDE, risk=high` |
| Symmetry-informed discovery | 已知平移/旋转/尺度等对称性 | 错误先验会排除真式 | `discovery, mechanistic, innovation=high if justified` |
| Interpretable scientific ML | 黑箱预测 + 可审计结构/蒸馏 | 后验解释不等于真实机制 | `prediction/discovery, hybrid, risk=medium-high` |

最低验证集：cross validation、留出工况、量纲一致、物理约束、噪声/抽样扰动、公式选择频率、已知极限和外部机制检查。不得仅凭训练误差或公式简洁度声称“发现定律”。

## G. 运筹优化与学习

### 经典 OR 是主干

| 结构 | 优先方法 | 前沿增强的合理位置 |
|---|---|---|
| 线性连续/离散 | LP/MILP、网络流、匹配 | 分解、cut/branch 选择、warm start、代理筛选 |
| 非线性 | NLP、凸优化、全局/分段线性化 | surrogate、多保真、Bayesian optimization |
| 多阶段随机 | stochastic programming、SDDP 类方法 | 场景生成/缩减、学习价值函数 |
| 分布不确定 | robust/DRO、chance constraint、CVaR | 学习不确定集/分布，但需独立校准 |
| 多目标 | epsilon-constraint、lexicographic、Pareto | surrogate-assisted Pareto search |
| 大规模可分 | Benders、Dantzig-Wolfe、Lagrangian/ADMM 类分解 | learning-assisted 选 cut/列/分支 |
| 序贯反馈 | MDP、近似动态规划 | online/offline RL、OR + RL |

### 学习与优化的角色

- **Surrogate-assisted optimization：** 当真实目标昂贵时学习代理；最终解必须回到真实模型/实验验证。
- **Bayesian optimization：** 适合昂贵少评估，不适合廉价可微或高维无结构问题。
- **Learning to optimize：** 可预测 warm start、分支、cut、列或启发式优先级；不得抛弃可行性和界。
- **RL + OR：** RL 处理状态反馈/策略，OR 处理硬约束/局部精确决策，是比“RL 替代 MILP”更可信的组合。
- **Offline RL：** 仅在日志策略数据覆盖目标状态动作且奖励可定义时使用；报告 distribution shift 与 off-policy evaluation 风险。
- **Multi-agent RL：** 只有多个决策主体、局部观测和策略交互真实存在时使用；非平稳训练和信用分配使其比赛风险很高。

所有优化学习方案仍须报告可行率、目标、runtime、bound/gap（若适用）、跨规模泛化和失败 fallback。

## H. 元启发式算法

PSO、GA、SA、DE 等可作为非凸/组合问题的近似求解工具，但“换动物名称”不是方法论创新。以下变化通常只到 Level 1：PSO→WOA/GWO/SSA、chaos、opposition learning、Lévy flight、改初始化或调参。

更有价值的路线：

- 利用问题分解、对称性、支配关系或可行域结构；
- exact + heuristic：小/局部子问题精确求解，外层启发式；
- surrogate、多保真或自适应评估预算；
- feasibility-preserving 编码/修复；
- learning-assisted search，但保留随机/贪心/松弛界；
- uncertainty-aware/robust objective。

至少运行多随机种子，报告分布、可行率、时间和相对简单启发式/精确小实例的 gap。只报告最优一次运行属于高风险证据。

## I. 组合创新与数据流

下列组合具有潜力，但每项必须在 `innovation-routing.md` 中完成职责和消融契约：

```text
mechanistic model -> residual -> residual learner -> corrected state
forecast -> calibrated scenarios -> robust/stochastic optimizer -> decision
observations -> causal identification -> treatment effect -> constrained allocation
node histories + A or A_t -> graph encoder -> temporal/SSM -> node forecast
field/parameters -> neural operator -> predicted field -> inverse/optimization loop
data -> symbolic discovery -> dimensional/physical tests -> retained equation
state/log data -> offline policy -> OR feasibility projection -> executable action
```

组合应由一个缺陷驱动，默认只加一个主要创新模块。若 `A+B+C` 无法在比赛中完成 `A`、`A+B`、`A+B+C` 的最低消融，则降为研究展望。

## J. 工具生态（按需安装）

Skill 只指导选择，不要求预装：

| 任务 | 常用生态 |
|---|---|
| 经典 ML/时序 | scikit-learn、statsmodels |
| 深度时序/Scientific ML | PyTorch、JAX、DeepXDE、NeuralOperator |
| 图学习 | PyTorch Geometric、DGL |
| Bayesian/GP/UQ | PyMC、GPyTorch、ArviZ |
| 调参与 BO | Optuna、BoTorch |
| OR | Pyomo、Gurobi、OR-Tools、CVXPY、PuLP |
| 多目标/元启发式 | pymoo、SciPy |
| RL | stable-baselines3、RL4CO（研究型组合优化） |
| 符号发现 | PySR、SINDy 类实现 |

使用前检查许可证、版本、硬件和最小可运行示例。依赖不存在时优先降级到可解释 backup，而不是在截止前搭建重型环境。

## K. 代表性来源（精简且可路由）

只保留用于确认方法定位的代表论文；具体题目引用时重新检索并核对元数据。

### Scientific ML 与 operator learning

- Raissi, Perdikaris, Karniadakis, 2019, *Physics-informed neural networks: A deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations*, Journal of Computational Physics. [DOI](https://doi.org/10.1016/j.jcp.2018.10.045)
- Chen et al., 2018, *Neural Ordinary Differential Equations*, NeurIPS. [Proceedings](https://proceedings.neurips.cc/paper/2018/hash/69386f6bb1dfed68692a24c8686939b9-Abstract.html)
- Lu et al., 2021, *Learning nonlinear operators via DeepONet based on the universal approximation theorem of operators*, Nature Machine Intelligence. [Article](https://www.nature.com/articles/s42256-021-00302-5) · [Code](https://github.com/lululxvi/deeponet)
- Li et al., 2021, *Fourier Neural Operator for Parametric Partial Differential Equations*, ICLR. [OpenReview](https://openreview.net/forum?id=c8P9NQVtmnO) · [Framework](https://github.com/neuraloperator/neuraloperator)
- Raonic et al., 2023, *Convolutional Neural Operators for Robust and Accurate Learning of PDEs*, NeurIPS. [arXiv](https://arxiv.org/abs/2302.01178) · [Code](https://github.com/camlab-ethz/ConvolutionalNeuralOperator)
- Wu et al., 2024, *RoPINN: Region Optimized Physics-Informed Neural Networks*, NeurIPS. [Proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/hash/c745bfa5b50544882938ff4f89ff26ac-Abstract-Conference.html) · [Code](https://github.com/thuml/RoPINN)
- Hao et al., 2024, *DPOT: Auto-Regressive Denoising Operator Transformer for Large-Scale PDE Pre-Training*. [arXiv](https://arxiv.org/abs/2403.03542)
- Alkin et al., 2024, *Universal Physics Transformers: A Framework for Efficiently Scaling Neural Operators*, NeurIPS. [Proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/hash/2cd36d327f33d47b372d4711edd08de0-Abstract-Conference.html)
- Herde et al., 2024, *Poseidon: Efficient Foundation Models for PDEs*, NeurIPS. [arXiv](https://arxiv.org/abs/2405.19101) · [Code](https://github.com/camlab-ethz/poseidon)
- Huang et al., 2024, *DiffusionPDE: Generative PDE-Solving under Partial Observation*, NeurIPS. [Proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/hash/eb3878c1dcbfff9ee95d5d033e5f5942-Abstract-Conference.html)
- Bischof et al., 2025, *HyPINO: Multi-Physics Neural Operators via HyperPINNs and the Method of Manufactured Solutions*, NeurIPS. [arXiv](https://arxiv.org/abs/2509.05117) · [DOI](https://doi.org/10.52202/085713-4845)
- Yue et al., 2025, *DeltaPhi: Physical States Residual Learning for Neural Operators in Data-Limited PDE Solving*, NeurIPS. [Proceedings](https://proceedings.neurips.cc/paper_files/paper/2025/hash/12bf28fb68f295f855a5bf0c5a217d6e-Abstract-Conference.html)
- Wang et al., 2025, *Mixture-of-Experts Operator Transformer for Large-Scale PDE Pre-Training* (MoE-POT), NeurIPS. [arXiv](https://arxiv.org/abs/2510.25803) · [DOI](https://doi.org/10.52202/085713-1057)

### 2026 观察项

- Boya and Subramani, 2024 (revised 2025), *A physics-informed transformer neural operator for learning generalized solutions of initial boundary value problems* (PINTO), preprint. [arXiv:2412.09009](https://arxiv.org/abs/2412.09009)
- Medvedev et al., 2026, *Physics-informed fine-tuning of foundation models for partial differential equations*, ICLR 2026 Workshop on AI and PDEs. [arXiv:2603.15431](https://arxiv.org/abs/2603.15431)
- Sun et al., *Physics Transformer: Tailoring Transformer for General PDE Prediction*, preprint submitted 2026-07-27; v1 notes that an update is planned. [arXiv:2607.24513](https://arxiv.org/abs/2607.24513)
- Serrano et al., 2026, *Test-time Generalization for Physics through Neural Operator Splitting*, preprint, revised 2026-08-10. [arXiv:2602.00884](https://arxiv.org/abs/2602.00884)
- Park et al., 2026, *Generative Neural Operators through Diffusion Last Layer*; the arXiv record notes ICML 2026 and code availability. [arXiv:2602.04139](https://arxiv.org/abs/2602.04139)
- Chen et al., 2026, *Causal Discovery from Heteroscedastic Stochastic Dynamical Systems under Imperfect Physical Models*, preprint. [arXiv:2602.04907](https://arxiv.org/abs/2602.04907)
- Yuan et al., 2026, *Unleashing LLMs in Bayesian Optimization: Preference-Guided Framework for Scientific Discovery*; the arXiv record notes an ICLR 2026 conference paper. [arXiv:2605.17976](https://arxiv.org/abs/2605.17976)

### 时序、符号发现与负证据

- Das et al., 2024, *A decoder-only foundation model for time-series forecasting* (TimesFM), ICML. [PMLR](https://proceedings.mlr.press/v235/das24c.html) · [Code](https://github.com/google-research/timesfm)
- Woo et al., 2024, *Unified Training of Universal Time Series Forecasting Transformers* (Moirai), ICML. [PMLR](https://proceedings.mlr.press/v235/woo24a.html) · [Code](https://github.com/SalesforceAIResearch/uni2ts)
- Toner et al., 2025, *Performance of Zero-Shot Time Series Foundation Models on Cloud Data*, ICLR Workshop/PMLR；提供 foundation model 被简单线性 baseline 超过的域内负证据。[PMLR](https://proceedings.mlr.press/v296/toner25a.html)
- Guibert et al., 2026, *Benchmarking Time Series Foundation Models on their Accuracy and Energy Consumption*, PMLR；说明准确率的数据集依赖和架构相关能耗差异。[PMLR](https://proceedings.mlr.press/v309/guibert26a.html)
- Brunton, Proctor, Kutz, 2016, *Discovering governing equations from data by sparse identification of nonlinear dynamical systems* (SINDy), PNAS. [DOI](https://doi.org/10.1073/pnas.1517384113)

## L. 从 Deep Research 保留与降级的边界

### 保留

- 方法的结构定位、所需数据/机理、与经典模型的互补关系；
- PINN/Neural ODE/Operator、时序、图、因果、UQ、符号发现、OR+learning 等可迁移方法族；
- 2024–2026 少量代表论文、正式状态和可核验入口；
- test-time composition、residual target、physics-informed adaptation 等可形成结构创新的思想；
- foundation model 的负证据、算力和竞赛交付风险。

### 降级为 `WATCH` 或研究展望

- 2026 年新预印本、Workshop 工作和缺少竞赛级复现链的方法；
- 0.5B 级预训练、超大多物理语料、大型 MoE/3D CFD 等超出常规比赛资源的路线；
- 需要完整预训练算子库或复杂测试时搜索的 operator composition；
- LLM 引导 BO、LLM/Agent 自动建模等尚需严格边界验证的角色。

### 剔除

- 只有“更大/更新”叙述、却没有题目结构路由价值的模型罗列；
- 未经确认的 benchmark 数字、性能提升、GitHub 地址或发表状态；
- 无法在本题建立公平 baseline 和消融的模型堆叠；
- 把普通算法替换、动物元启发式或使用 LLM 本身称作重大创新的表述。

最终判断只有四种：`能用`、`值得用`、`有证据算创新`、`只是包装`。前两项由结构和可行性决定，第三项由 baseline、消融与验证决定。
