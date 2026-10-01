# 数学建模前沿种子图谱（2026-08-26）

> 本文件保留 2026-08-26 的历史种子。当前按 [precontest-anchors.md](precontest-anchors.md) 调用已准备的路线；无需因读取旧表而重新检索全部来源。历史条目未在当前目录复核时保持其原状态，对本题需要的条件/版本缺口定向补漏，不用旧日期声称今天最新。

## 1. 小样本表格建模

### TabPFN

- 官方来源：[Accurate predictions on small data with a tabular foundation model, Nature 2025](https://www.nature.com/articles/s41586-024-08328-6)
- 可用场景：小中型表格分类/回归、快速强基线、概率预测和重复建模。
- 已知边界：论文核心基准聚焦不超过 10,000 个样本、500 个特征、10 个类别的数据集；需要核对推理内存、预训练先验与本题数据生成机制的偏差。
- 数模用法：与线性模型和 CatBoost/XGBoost 做嵌套交叉验证；更适合作为强基线、残差模块或不确定性候选，而不是替代机理分析。

## 2. 时间序列基础模型与公平基准

- [A decoder-only foundation model for time-series forecasting（TimesFM）, ICML 2024](https://proceedings.mlr.press/v235/das24c.html)：零样本预测候选，核对上下文长度、预测长度与外生变量支持。
- [Chronos: Learning the Language of Time Series, TMLR 2024](https://openreview.net/forum?id=gerNCVqqtR)：把数值量化为 token 的预训练路线，需核对概率输出和领域迁移。
- [Moirai-MoE: Empowering Time Series Foundation Models with Sparse Mixture of Experts, ICML 2025](https://proceedings.mlr.press/v267/liu25an.html)：稀疏专家适应异质序列，比较专家路由成本与普通集成。
- [TimeFuse: Unified Multi-Scale Representation for Time Series Forecasting, ICML 2025](https://proceedings.mlr.press/v267/liu25cm.html)：强调多尺度融合；其基准讨论也提醒不存在对所有设置都一致占优的单模型。
- [Benchmarking Time Series Foundation Models on their Accuracy and Energy Consumption, PMLR 2026](https://proceedings.mlr.press/v309/guibert26a.html)：2026 年准确率—能耗基准显示性能具有明显数据集依赖，能耗和延迟也应进入数模比较表。
- [Are Time-Series Foundation Models Better Than Simple Models for Cloud Resource Forecasting?, PMLR 2025](https://proceedings.mlr.press/v296/toner25a.html)：负面证据种子；在其云资源场景中，简单线性基线可胜过多种知名基础模型。

数模结论：基础模型应进入同一滚动起点、相同信息集和相同预算的候选池。推荐创新形式是“按序列属性分流/融合 + 共形区间或决策损失”，而不是直接写“采用大模型提高精度”。

## 3. 学习增强组合优化

- [Decision-Focused Learning: Foundations, State of the Art, Benchmark and Future Opportunities, JAIR 2024](https://doi.org/10.1613/jair.1.15320)：把预测误差改为下游决策质量的系统路线；适合“预测参数—执行优化”的两阶段题。
- [Machine learning augmented branch and bound for mixed integer linear programming, Mathematical Programming 2024](https://link.springer.com/article/10.1007/s10107-024-02130-y)：学习增强分支定界；适合大量相关 MILP 实例和求解器级研究，必须保留可行性与最优性界。
- [Neural Neighborhood Search for Multi-objective Optimization, ICLR 2024](https://openreview.net/forum?id=2NpAw2QJBY)：学习邻域搜索候选；需与经典 LNS/局部搜索在同一时限和实例分布下比较。
- [RL4CO: an Extensive Reinforcement Learning for Combinatorial Optimization Benchmark, KDD 2025](https://doi.org/10.1145/3711896.3737433)：统一强化学习组合优化基准，适合核对训练/测试分布、模型规模和泛化协议。
- [Preference-Guided Diffusion for Multi-Objective Combinatorial Optimization, NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/175fa4fc8f275f877ec85340131c5d7a-Abstract-Conference.html)：扩散式多目标候选；除非代码、训练实例和同预算验证齐备，否则列为 `WATCH`。

数模结论：最稳妥的创新通常是“经典 MILP/CP-SAT 主体 + 学习热启动、变量筛选或邻域建议 + 独立可行性检查”。只有单个实例时，不宜训练端到端策略网络。

## 4. 不确定性、区间与情景生成

- [Distributionally robust optimization, Acta Numerica 2025](https://www.cambridge.org/core/journals/acta-numerica/article/distributionally-robust-optimization/5B4E65E3A5A2AEF24E218A6B34E6EAA2)：DRO 的系统理论入口；用于选择歧义集、对偶重构与样本外保证。
- [ConForME: Multi-horizon Time Series Forecasting with Conformal Prediction, PMLR 2024](https://proceedings.mlr.press/v230/galvao-lopes24a.html)：多预测期共形区间候选；需明确覆盖保证类型与交换性/漂移条件。
- [TSDiff: Time Series Diffusion Models, NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/hash/5a1a10c2c2c9b9af1514687bc24b8f3d-Abstract.html)：较早的扩散时间序列锚点，可用于概率预测与隐式插补。
- [Retrieval-Augmented Diffusion Models for Time Series Forecasting, NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/053ee34c0971568bfa5c773015c10502-Paper-Conference.pdf)：检索增强情景生成候选，需审计相似片段泄漏和尾部保持。

数模结论：不确定性创新必须落到覆盖率、尾部损失、CVaR、后悔值或约束违背概率。情景“看起来真实”不是证据。

## 5. 神经算子、PDE 基础模型与混合物理模型

- [Poseidon: Efficient Foundation Models for PDEs, NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/84e1b1ec17bb11c57234e96433022a9a-Abstract-Conference.html)：多尺度算子 Transformer，公开代码、模型和数据；适合多查询 PDE 迁移研究。
- [Neural general circulation models for weather and climate, Nature 2024](https://www.nature.com/articles/s41586-024-07744-y)：NeuralGCM 的机理—学习混合路线。
- [Probabilistic weather forecasting with machine learning, Nature 2024](https://www.nature.com/articles/s41586-024-08252-9)：GenCast 的概率集合预报路线。
- [A foundation model for the Earth system, Nature 2025](https://www.nature.com/articles/s41586-025-09005-y)：Aurora 的地球系统基础模型路线。
- [Riesz Neural Operator for Solving Partial Differential Equations, ICLR 2026](https://openreview.net/forum?id=Vjw7q1quNt)：2026 年局部导数与全局谱信息融合候选；在其他 PDE 或边界条件上使用前仍需独立外推验证。

数模结论：大规模天气/PDE 基础模型证明了路线潜力，不意味着比赛附件足以训练或迁移。可落地创新优先考虑“数值机理块 + 小型残差校正”“算子代理 + 独立守恒检查”或“多保真仿真”。

## 6. 因果发现与符号回归

- [CUTS+: High-dimensional Causal Discovery from Irregular Time-series, AAAI 2024](https://ojs.aaai.org/index.php/AAAI/article/view/29034)：不规则高维时序因果发现候选；需核对缺失机制和识别假设。
- [Tangent Space Causal Inference: Leveraging Vector Fields for Causal Discovery in Dynamical Systems, NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/d9253fba38ed8a140f86fa22d89344ec-Abstract-Conference.html)：以动力系统向量场和同步性替代部分 CCM 路线；需核对数据质量和可识别性。
- [Advancing symbolic regression for earth science with a focus on evapotranspiration modeling, npj Climate and Atmospheric Science 2024](https://www.nature.com/articles/s41612-024-00861-5)：其 KG-DSR 方法把领域知识加入符号搜索，适合可解释方程发现。
- [RAG-SR: Retrieval-Augmented Generation for Symbolic Regression, ICLR 2025](https://openreview.net/forum?id=NdHka08uWn)：检索增强符号回归候选；检索库、复杂度惩罚和外推验证必须公开。

数模结论：因果与符号方法的价值是给出可检验结构，不是把相关性换一个名称。量纲一致、结构稳定、外部验证和可识别性说明是硬要求。

## 7. 高维贝叶斯优化与多目标代理

- [Vanilla Bayesian Optimization Performs Great in High Dimensions, ICML 2024](https://proceedings.mlr.press/v235/hvarfner24a.html)：提醒先公平调校标准 BO，再引入复杂高维结构。
- [Cylindrical Thompson Sampling for High-Dimensional Bayesian Optimization, AISTATS 2024](https://proceedings.mlr.press/v238/rashidi24a.html)：面向高维域的几何/采样候选；需验证其结构假设。
- [$\alpha$-PFN: In-Context Learning Entropy Search, ICLR 2025 Workshop](https://openreview.net/forum?id=IMVqPGYxyD)：Workshop 级基础模型种子，只能列为 `WATCH`，实时检索时须重新核验状态。

数模结论：在函数评价昂贵且预算严格时，创新应围绕样本效率、多保真、约束和多目标偏好；若函数调用便宜，传统搜索或确定性优化通常更可靠。

## 8. 世界模型与安全控制

- [Mastering diverse control tasks through world models（DreamerV3）, Nature 2025](https://www.nature.com/articles/s41586-025-08744-2)：通用世界模型控制路线，需要大量交互或可靠模拟器。
- [OASIS: Conditional Distribution Shaping for Offline Safe Reinforcement Learning, NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/8f75af4704feac629a560f4ad6b67cef-Abstract-Conference.html)：用条件扩散重塑离线安全 RL 数据分布；需核对约束形式、离线覆盖和违规评估。

数模结论：没有可信模拟器、离线覆盖或安全回退时，世界模型/RL 不能做主方案。优先使用 MPC、动态规划或鲁棒控制，再把学习模块限制在状态预测或候选动作生成。

## 9. 截止日综合判断

截至本快照日期，最值得迁移到竞赛数模的不是“最大的模型”，而是以下组合：

1. **经典可解释主体 + 一个前沿增量**；
2. **学习辅助优化 + 精确可行性兜底**；
3. **基础预测模型 + 滚动基准 + 校准区间/决策损失**；
4. **机理数值模型 + 小型学习残差或代理**；
5. **创新模型 + 明确消融、负面证据和失败边界**。

基础模型没有自动优势；2025--2026 的基准越来越强调数据集依赖、能耗、延迟和简单强基线。因果、扩散、强化学习、LLM 启发式及新近 2026 模型应获得更严格的数据、计算和复现审查。
