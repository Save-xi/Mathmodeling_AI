#!/usr/bin/env python3
"""Create a non-destructive, Chinese-first math-modeling project skeleton."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from project_contract import (
    DIRECTORIES, RUN_MANIFEST, checked_path, default_manifest, load_json,
    validate_manifest,
)


SKILL_ROOT = Path(__file__).resolve().parents[1]
LATEX_TEMPLATE = SKILL_ROOT / "assets" / "chinese-contest-paper.tex"


def positive_int(value: str) -> int:
    number = int(value)
    if not 1 <= number <= 20:
        raise argparse.ArgumentTypeError("题目数量必须在 1 到 20 之间")
    return number


def write_if_missing(path: Path, content: str, dry_run: bool) -> bool:
    """Return True when a file would be or was created; never overwrite."""
    if path.exists():
        return False
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with path.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(content)
        except FileExistsError:
            return False
    return True


def problem_entrypoint(index: int) -> str:
    return f'''"""第 {index} 问独立运行入口。

共享的数据读取、模型和绘图逻辑请放在 src/common 或其他共享模块中。
"""

from __future__ import annotations


def main() -> None:
    """运行第 {index} 问并把规范结果写入 results。"""
    raise NotImplementedError("待补：实现第 {index} 问、保存规范结果并记录运行信息")


if __name__ == "__main__":
    main()
'''


def latex_escape(value: str) -> str:
    """Escape a plain-text project title for LaTeX."""
    escapes = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "$": r"\$",
        "&": r"\&",
        "#": r"\#",
        "%": r"\%",
        "_": r"\_",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(escapes.get(character, character) for character in value)


def latex_paper(title: str, problems: int) -> str:
    """Render the bundled Chinese contest-paper template."""
    template = LATEX_TEMPLATE.read_text(encoding="utf-8")
    required_tokens = ("@@PAPER_TITLE@@", "@@QUESTION_SECTIONS@@")
    missing = [token for token in required_tokens if token not in template]
    if missing:
        raise RuntimeError(f"LaTeX 模板缺少占位标记：{', '.join(missing)}")

    question_sections = "\n\n".join(
        f"""\\section{{第 {index} 问：模型建立、求解与结果}}

\\subsection{{建模思路与基线}}

待补：解释机制、基线、主模型选择及备选方案。

\\subsection{{模型建立与求解}}

待补：给出变量、目标、约束、算法、参数和可复现的求解信息。

\\subsection{{结果解释与本问验证}}

待补：报告带条件的定量结果，并关联规范表图、基线比较和验证证据。"""
        for index in range(1, problems + 1)
    )
    return (
        template.replace("@@QUESTION_SECTIONS@@", question_sections)
        .replace("@@PAPER_TITLE@@", latex_escape(title))
    )


def build_templates(title: str, problems: int) -> dict[str, str]:
    created_at = datetime.now(timezone.utc).isoformat()
    manifest = default_manifest(title, problems)
    manifest["created_at_utc"] = created_at
    yaml_title = json.dumps(title, ensure_ascii=False)
    question_rows = "\n".join(
        f"| 第 {index} 问 | 待补 | 待补 | 待补 | 待补 | 待补 | 待补 |"
        for index in range(1, problems + 1)
    )
    contract_sections = "\n".join(
        f"## 第 {index} 问\n\n待补：变量/单位、信息时点、目标/约束、baseline、验证与输出。\n"
        for index in range(1, problems + 1)
    )

    templates = {
        ".gitignore": """__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/
.venv/
venv/
results/tmp/
work/
paper/build/
""",
        "README.md": f"""# {title}

本项目按题目顺序组织，每个 problem_i.py 可独立运行；共享逻辑位于 src/common。

开始前：

1. 把原始赛题和附件放入项目根目录、data/raw 或 docs/sources，并将所需文件列入 mathmodeling.json 的 source_files。
2. 完成 docs/source_inventory.md、docs/official_rules.md、docs/problem_map.md 和 docs/model_contract.md。
3. 在 config/parameters.yaml 中冻结种子、单位、参数来源和求解器限制。
4. 运行各题入口，把真实结果/验证写入 results，并填写 results/run_manifest.json；不得把未执行的步骤标为完成。
5. 从 paper/main.tex 写作，用 Skill 的 build_paper.py 构建到独立目录；编译/页面/数字核验分别记录。
6. 用 audit_project.py --strict --report docs/structural_audit.md 检查结构与运行/证据链接。人工数值、视觉和规则验收保存在 docs/qa_report.md。

运行记录和证据表规范见已安装 Skill 的 references/project-evidence.md。STRUCTURE_CHECKS_PASSED 仍需独立数学与经验核验，不能直接作为提交许可。
""",
        "mathmodeling.json": json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        "config/parameters.yaml": f"""project:
  title: {yaml_title}
  seed: 42

data:
  raw_dir: "data/raw"
  processed_dir: "data/processed"

solver:
  name: ""
  time_limit_seconds: 600
  mip_gap: 0.001

uncertainty:
  scenario_count: null
  confidence_level: null

# 按实际任务设置适用参数并记录依据；不需要随机场景时不要机械生成场景。
""",
        "src/common/__init__.py": '"""跨问题共享的数据、模型、验证和绘图逻辑。"""\n',
        "src/common/paths.py": '''"""项目规范路径。"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
RESULTS = PROJECT_ROOT / "results"
TABLES = RESULTS / "tables"
FIGURES = RESULTS / "figures"
LOGS = RESULTS / "logs"
''',
        "docs/source_inventory.md": """# 原题与附件清单

| 状态 | 文件 | 版本/时间 | 用途 | 已核对字段、单位与数值条件 | 备注 |
|---|---|---|---|---|---|
| [ ] | 待补 | 待补 | 待补 | 待补 | 待补 |

说明：文件存在不等于内容已核验；只有逐项检查后才能改为 [x]。
""",
        "docs/official_rules.md": """# 当年官方规则清单

| 状态 | 赛事/年份 | 文件或页面 | 官方 URL | 发布/修订日期 | 本地路径 | 关键约束 | 是否被替代 |
|---|---|---|---|---|---|---|---|
| [ ] | 待补 | 论文格式/参赛规则/提交通知/AI 使用规定 | 待补 | 待补 | 待补 | 页数、匿名、文件格式、大小、披露 | 待核验 |

说明：校内培训计划、选拔通知和往年格式不能替代当年全国规则；缺失或过期时从赛事官网核验并归档。
""",
        "docs/problem_map.md": f"""# 问题地图

| 问题 | 请求输出/决策 | 输入与单位 | 机制与耦合 | 评价指标 | 验收证据 | 主要风险 |
|---|---|---|---|---|---|---|
{question_rows}
""",
        "docs/model_contract.md": f"""# 模型契约

对每一问冻结：集合与索引、参数及来源/单位、变量域、目标、约束、信息时序、边界条件、基线、主模型、备选模型、验证协议和规范输出路径。

基线、最终模型和回退是角色，可以共用同一实现。记录独立样本单位、实际部署对象、剩余时间、搜索/求解上限、模型冻结和论文/验证保留时间。

{contract_sections}
""",
        "docs/assumptions.md": """# 事实、推断、假设、提案与未知项

## FACT（原题/附件/已执行结果）

- 待补：陈述、来源锚点、单位和适用条件。

## INFERENCE（从明确前提得到的推断）

- 待补：推理、假设、范围及验证方式。

## ASSUMPTION（为可辨识或可求解而引入）

- 待补：假设、影响和验证/敏感性测试。

## PROPOSAL（尚未实现）

- 待补：候选方法及采用条件。

## UNKNOWN（缺失或不可辨识的信息）

- 待补：未知内容、对结论的影响、解决方式或结论边界。

另记 not_implemented / implemented / executed / verified 进度；源文件陈述可直接标 unverified / verified。执行过不等于独立核验。
""",
        "docs/data_audit.md": """# 数据质量审计

待补：字段、类型、单位、主键、连接、缺失、异常、合法选项、粒度、样本量、泄漏边界、变换和参数来源。
""",
        "docs/evidence_map.md": """# 论点—证据映射

| Claim ID | Question | Run ID | Paper claim | Source artifact | Metric/value | Conditions | Paper location | Verification |
|---|---|---|---|---|---|---|---|---|
| C-01 | 1 | 待补 | 待补 | 待补 | 待补 | 待补 | 待补 | unverified |
""",
        "docs/ai_usage_log.md": """# AI 使用记录

| 时间 | 工具/版本 | 使用目的与环节 | 主要提示方式/过程 | 输出用途 | 采纳与人工修改 | 人工核验 |
|---|---|---|---|---|---|---|
| 待补 | 待补 | 待补 | 待补 | 待补 | 待补 | 待补 |

提交前按当年规则从本日志生成 LaTeX 版 AI 使用声明和适用时的 `AI工具使用详情.pdf`；不得虚构或遗漏实际使用记录。
""",
        "docs/qa_report.md": """# QA 报告

待补：运行命令、环境、输入版本、种子、关键测试、审计结论和验证边界。
""",
        RUN_MANIFEST: json.dumps({"schema_version": 1, "runs": []}, indent=2) + "\n",
        "paper/main.tex": latex_paper(title, problems),
    }
    for index in range(1, problems + 1):
        templates[f"problem_{index}.py"] = problem_entrypoint(index)
    return templates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="创建不会覆盖已有文件的数学建模竞赛项目骨架"
    )
    parser.add_argument("project_dir", type=Path, help="目标项目目录")
    parser.add_argument("--problems", type=positive_int, required=True, help="实际问题数量（必须显式填写）")
    parser.add_argument("--title", default="数学建模竞赛项目", help="项目标题")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只显示将创建和跳过的文件，不写入磁盘",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.project_dir.expanduser().resolve()
    if root.exists() and not root.is_dir():
        raise SystemExit(f"目标路径不是目录：{root}")

    try:
        manifest_path = root / "mathmodeling.json"
        if manifest_path.exists():
            existing = validate_manifest(load_json(manifest_path), root)
            if existing["problem_count"] != args.problems:
                raise ValueError("已有问题数量与 --problems 不同；请先审查现有清单，不自动混合项目结构")
            expected = default_manifest(args.title, args.problems)
            # This guard is about a second PATH LAYOUT, so compare only the path-bearing
            # keys. submission may also carry the optional page_limit/anonymity contest
            # limits, which change no path and must not block a rerun.
            paths_only = {key: value for key, value in existing.get("submission", expected["submission"]).items()
                          if key in {"source", "pdf"}}
            if existing["entrypoints"] != expected["entrypoints"] or paths_only != expected["submission"] or any(
                existing.get(key, expected[key]) != expected[key]
                for key in ("canonical_directories", "run_manifest")
            ):
                raise ValueError("已有项目使用自定义路径；请沿用原结构，不用默认初始化器追加另一套文件")
        templates = build_templates(args.title, args.problems)
        # Preflight every destination before the first write, including dry-run.
        for relative in (*DIRECTORIES, *templates):
            target = checked_path(root, relative)
            for component in (target, *target.parents):
                if component == root:
                    break
                if component.is_symlink() or getattr(component, "is_junction", lambda: False)():
                    raise ValueError(f"初始化目标包含链接/junction，拒绝间接写入：{component}")
            if relative in DIRECTORIES and target.exists() and not target.is_dir():
                raise ValueError(f"目录位置已有普通文件：{target}")
            if relative in templates and target.exists() and not target.is_file():
                raise ValueError(f"文件位置已有目录或特殊文件：{target}")
        if not args.dry_run:
            root.mkdir(parents=True, exist_ok=True)
            for relative in DIRECTORIES:
                (root / relative).mkdir(parents=True, exist_ok=True)
    except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
        print(f"初始化失败：{exc}")
        return 3

    created: list[str] = []
    skipped: list[str] = []
    try:
        for relative, content in templates.items():
            if write_if_missing(root / relative, content, args.dry_run):
                created.append(relative)
            else:
                skipped.append(relative)
    except OSError as exc:
        print(f"写入失败，已有文件未覆盖；本次已创建 {len(created)} 个文件：{exc}")
        return 3

    mode = "DRY RUN" if args.dry_run else "DONE"
    print(f"[{mode}] 项目目录：{root}")
    print(f"创建/计划创建：{len(created)} 个文件")
    for relative in created:
        print(f"  + {relative}")
    print(f"保留未覆盖：{len(skipped)} 个文件")
    for relative in skipped:
        print(f"  = {relative}")
    print("下一步：补齐原题/附件清单、问题地图和模型契约，再实现各 problem_i.py。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
