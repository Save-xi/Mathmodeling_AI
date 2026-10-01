# 区域仓配货预测与资源分配（合成示例）

本项目按题目顺序组织，每个 problem_i.py 可独立运行；共享逻辑位于 src/common。

开始前：

1. 把原始赛题和附件放入项目根目录、data/raw 或 docs/sources，并将所需文件列入 mathmodeling.json 的 source_files。
2. 完成 docs/source_inventory.md、docs/official_rules.md、docs/problem_map.md 和 docs/model_contract.md。
3. 在 config/parameters.yaml 中冻结种子、单位、参数来源和求解器限制。
4. 运行各题入口，把真实结果/验证写入 results，并填写 results/run_manifest.json；不得把未执行的步骤标为完成。
5. 从 paper/main.tex 写作，用 Skill 的 build_paper.py 构建到独立目录；编译/页面/数字核验分别记录。
6. 用 audit_project.py --strict --report docs/structural_audit.md 检查结构与运行/证据链接。人工数值、视觉和规则验收保存在 docs/qa_report.md。

运行记录和证据表规范见已安装 Skill 的 references/project-evidence.md。STRUCTURE_CHECKS_PASSED 仍需独立数学与经验核验，不能直接作为提交许可。
