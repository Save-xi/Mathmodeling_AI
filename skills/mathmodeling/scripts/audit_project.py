#!/usr/bin/env python3
"""Check explicit contest project/run/evidence contracts without executing code."""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from project_contract import (
    BUILD_MARKER, REPORT_MARKER, checked_path, file_stamp, inspect_pdf,
    is_numeric, load_json, project_paths, validate_manifest,
)


PLACEHOLDER_RE = re.compile(
    r"\b(?:TODO|FIXME|TBD)\b|(?:待补|待填写)(?:[：:。\s]|$)|@@[A-Z_]+@@", re.I
)
IGNORED_DIRS = {".git", ".venv", "venv", "__pycache__", "build", "tmp", "cache", "drafts", "archive"}
DOCS = (
    "source_inventory.md", "official_rules.md", "problem_map.md", "model_contract.md",
    "assumptions.md", "data_audit.md", "ai_usage_log.md",
)
HEADERS = {
    "id": {"claim id", "id", "论点编号"},
    "question": {"question", "问题", "问号"},
    "run": {"run id", "run_id", "运行编号"},
    "claim": {"paper claim", "claim", "论文论点", "论点"},
    "source": {"source artifact", "source", "来源文件", "来源", "证据文件"},
    "value": {"metric/value", "指标/数值", "数值", "value"},
    "conditions": {"conditions", "条件"},
    "location": {"paper location", "论文位置"},
    "verification": {"verification", "状态", "核验", "verification status"},
}
VERIFIED = {"verified", "已核验"}
# Optional column. `verified` is self-asserted and the tool cannot check whether the
# value, units and denominator were actually reconciled — but it can require that the
# claimer name WHO did it, which keeps an assistant self-check from reading as a
# teammate's review. Absent, nothing is reported; present, the value must be one of these.
VERIFIED_BY_HEADER = {"verified by", "verified_by", "核验人", "核验方式", "核验主体"}
VERIFIED_BY = {
    "self-check", "assistant", "自查", "助手自查",
    "independent-rerun", "independent", "独立复算", "独立重跑",
    "team-member", "human", "队员核验", "人工核验",
}
MODEL_KINDS = {
    "regression", "classification", "prediction", "time_series", "panel", "graph",
    "optimization", "prediction_optimization", "simulation", "inverse", "analytical",
    "ranking", "clustering", "causal", "multi_objective", "robust_optimization",
    "uncertainty_quantification",
}


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    message: str
    evidence: list[str]
    fix: str


class Review:
    def __init__(self, root: Path, max_file: int, max_total: int, max_files: int):
        self.root = root
        self.issues: list[Issue] = []
        self.cache: dict[Path, str] = {}
        self.protected: set[Path] = set()
        self.max_file, self.max_total, self.max_files = max_file, max_total, max_files
        self.bytes_read = 0
        self.skipped: list[str] = []

    def rel(self, path: Path) -> str:
        try:
            return path.relative_to(self.root).as_posix()
        except ValueError:
            return str(path)

    def add(self, severity: str, code: str, message: str, evidence: object = "", fix: str = "") -> None:
        self.issues.append(Issue(severity, code, message, [str(evidence)] if evidence else [], fix))

    def path(self, value: object) -> Path:
        path = checked_path(self.root, value)
        self.protected.add(path.resolve())
        return path

    def nonempty(self, path: Path) -> bool:
        self.protected.add(path.resolve())
        return path.is_file() and path.stat().st_size > 0

    def read(self, path: Path) -> str:
        if path in self.cache:
            return self.cache[path]
        self.protected.add(path.resolve())
        try:
            size = path.stat().st_size
            if size > self.max_file or self.bytes_read + size > self.max_total or len(self.cache) >= self.max_files:
                raise ValueError("超过单文件、总文本或文件数量预算")
            text = path.read_text(encoding="utf-8-sig")
            self.bytes_read += size
        except (OSError, UnicodeError, ValueError) as exc:
            self.skipped.append(self.rel(path))
            self.add("MAJOR", "SCAN_INCOMPLETE", "文件未被成功检查。", f"{self.rel(path)}: {exc}", "处理编码/权限或按需提高读取预算；不要把跳过当作无问题。")
            text = ""
        self.cache[path] = text
        return text

    def json(self, path: Path) -> object:
        return json.loads(self.read(path))


def timestamp(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("时间须为带时区的 ISO-8601 字符串")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("时间缺少时区")
    return parsed


def strings(value: object, field: str, nonempty: bool = True) -> list[str]:
    if not isinstance(value, list) or (nonempty and not value) or any(not isinstance(x, str) or not x.strip() for x in value):
        raise ValueError(f"{field} 须为{'非空' if nonempty else ''}路径/字符串列表")
    if len(set(value)) != len(value):
        raise ValueError(f"{field} 含重复项")
    return value


def result_file(path: Path, paths: dict[str, Path]) -> bool:
    return not (
        path.resolve().is_relative_to(paths["logs"].resolve())
        or path == paths["runs"] or path == paths["build_receipt"]
        or path.suffix.lower() == ".log" or path.name in {".gitkeep", "qa_report.md", "structural_audit.md"}
    )


def inspect_runs(review: Review, entries: list[Path], paths: dict[str, Path]) -> dict[int, dict]:
    selected: dict[int, dict] = {}
    if not review.nonempty(paths["runs"]):
        review.add("MAJOR", "RUN_MANIFEST_MISSING", "缺少逐问选用运行记录。", review.rel(paths["runs"]), "按 references/project-evidence.md 记录真实执行；旧项目不自动迁移。")
        return selected
    try:
        data = review.json(paths["runs"])
        if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] != 1 or not isinstance(data.get("runs"), list):
            raise ValueError("运行清单需要 schema_version=1 和 runs 列表")
        ids: set[str] = set()
        for index, run in enumerate(data["runs"], 1):
            try:
                if not isinstance(run, dict):
                    raise ValueError("run 必须为对象")
                question = run.get("question")
                if type(question) is not int or not 1 <= question <= len(entries):
                    raise ValueError("question 超出实际题数")
                if question in selected:
                    raise ValueError("每问只能声明一个当前选用运行；探索历史请保留在日志中")
                run_id = run.get("run_id")
                if not isinstance(run_id, str) or not run_id.strip() or run_id in ids:
                    raise ValueError("run_id 为空或重复")
                ids.add(run_id)
                selected[question] = run
                for key in ("command", "environment"):
                    if not isinstance(run.get(key), str) or not run[key].strip():
                        raise ValueError(f"缺少 {key}")
                if run.get("status") != "completed":
                    raise ValueError("当前选用运行未 completed，不得用旧结果替代失败执行")
                if run.get("model_kind") not in MODEL_KINDS:
                    raise ValueError("model_kind 未声明或不支持")
                if not is_numeric(run.get("runtime_seconds")) or run["runtime_seconds"] < 0:
                    raise ValueError("runtime_seconds 必须为非负有限数")
                start, finish = timestamp(run.get("started_at")), timestamp(run.get("finished_at"))
                if start > finish or finish.timestamp() > datetime.now(timezone.utc).timestamp() + 300:
                    raise ValueError("运行时间顺序无效或位于未来")
                code = [review.path(x) for x in strings(run.get("code"), "code")]
                if entries[question - 1].resolve() not in {x.resolve() for x in code}:
                    raise ValueError("code 必须包含该问实际入口以及用到的共享代码/配置")
                inputs = [review.path(x) for x in strings(run.get("inputs"), "inputs")]
                artifacts = [review.path(x) for x in strings(run.get("artifacts"), "artifacts")]
                validation = run.get("validation")
                if not isinstance(validation, dict) or validation.get("status") != "passed":
                    raise ValueError("缺少当前运行的 passed 验证记录")
                if not isinstance(validation.get("protocol"), str) or not validation["protocol"].strip():
                    raise ValueError("validation.protocol 必须说明实际验证协议和适用对象")
                checks = [review.path(x) for x in strings(validation.get("artifacts"), "validation.artifacts")]
                baseline = review.path(validation.get("baseline_artifact"))
                if baseline.resolve() not in {x.resolve() for x in artifacts + checks}:
                    raise ValueError("baseline_artifact 必须关联当前运行的结果/验证产物；baseline 可等于最终模型")
                if not all(result_file(x, paths) for x in artifacts + checks):
                    raise ValueError("日志、运行清单或自动审计报告不能替代结果/验证产物")
                if {x.resolve() for x in artifacts + checks} & {x.resolve() for x in code + inputs}:
                    raise ValueError("输入或代码不能同时冒充本次运行的结果/验证产物")
                stamps = run.get("file_stamps")
                if not isinstance(stamps, dict):
                    raise ValueError("缺少本次执行的 file_stamps（仅关键声明文件的 size/mtime_ns，不是全项目 hash）")
                for path in code + inputs + artifacts + checks:
                    if not review.nonempty(path):
                        raise ValueError(f"缺少或空文件：{review.rel(path)}")
                    if stamps.get(review.rel(path)) != file_stamp(path):
                        raise ValueError(f"执行后文件身份标记发生变化：{review.rel(path)}；请重跑/核对真实版本")
                    # A fast stale-run hint; timestamps are not a tamper-proof integrity check.
                    if path.stat().st_mtime > finish.timestamp() + 2:
                        raise ValueError(f"文件晚于声明的执行：{review.rel(path)}；需重跑或核对记录")
                for path in artifacts + checks:
                    if path.stat().st_mtime < start.timestamp() - 2:
                        raise ValueError(f"输出早于当前执行：{review.rel(path)}，可能为旧产物")
                randomness = run.get("randomness")
                if not isinstance(randomness, dict) or randomness.get("mode") not in {"deterministic", "stochastic"}:
                    raise ValueError("randomness.mode 必须明确 deterministic/stochastic")
                if randomness["mode"] == "stochastic":
                    seeds = randomness.get("seeds")
                    if not isinstance(seeds, list) or not seeds or any(type(x) is not int for x in seeds):
                        raise ValueError("随机工作必须记录整数 seeds")
                    repetitions = randomness.get("repetitions")
                    if type(repetitions) is not int or repetitions < 1:
                        raise ValueError("随机工作必须记录正整数 repetitions")
                solver = run.get("solver")
                if run["model_kind"] in {"optimization", "prediction_optimization", "multi_objective", "robust_optimization"} or solver is not None:
                    if not isinstance(solver, dict):
                        raise ValueError("优化运行缺少 solver 证据")
                    if any(not isinstance(solver.get(key), str) or not solver[key].strip() for key in ("name", "version")):
                        raise ValueError("solver 必须记录实际 name 和 version")
                    if solver.get("status") not in {"optimal", "feasible", "time_limit"} or solver.get("feasibility_verified") is not True:
                        raise ValueError("最终优化方案不可行、未复核或终止状态不可用")
                    if solver.get("has_incumbent") is not True or not is_numeric(solver.get("objective")):
                        raise ValueError("优化方案没有有限目标值和有效 incumbent")
                    if solver.get("problem_type") not in {"lp", "mip", "cp", "nlp", "global", "heuristic"}:
                        raise ValueError("solver.problem_type 必须明确")
                    if solver["problem_type"] in {"mip", "global"}:
                        if not is_numeric(solver.get("bound")) or not is_numeric(solver.get("gap")) or solver["gap"] < 0:
                            raise ValueError("MIP/global 运行缺少有限 bound 和非负 gap")
            except (OSError, TypeError, ValueError) as exc:
                review.add("BLOCKER", "RUN_INVALID", "选用运行记录不可用。", f"run[{index}]: {exc}", "修正运行、真实状态和产物链接；不要仅改完成标签。")
    except (OSError, TypeError, ValueError) as exc:
        review.add("BLOCKER", "RUN_MANIFEST_INVALID", "运行清单无法可靠解析。", exc)
    for question in range(1, len(entries) + 1):
        if question not in selected:
            review.add("BLOCKER", "QUESTION_RUN_MISSING", "有实际问题缺少选用运行及结果。", f"question={question}")
    return selected


def inspect_claims(review: Review, paths: dict[str, Path], runs: dict[int, dict]) -> int:
    path = paths["evidence"]
    if not review.nonempty(path):
        review.add("MAJOR", "EVIDENCE_MAP_MISSING", "缺少论点—运行—证据映射。", review.rel(path))
        return 0
    text = review.read(path)
    table = [re.split(r"(?<!\\)\|", line.strip().strip("|")) for line in text.splitlines() if line.strip().startswith("|")]
    if len(table) < 3:
        review.add("MAJOR", "EVIDENCE_TABLE_INVALID", "证据表必须有表头和实际条目。", review.rel(path))
        return 0
    header = [x.strip().casefold() for x in table[0]]
    columns = {key: next((i for i, name in enumerate(header) if name in aliases), -1) for key, aliases in HEADERS.items()}
    missing = [key for key, index in columns.items() if index < 0]
    if missing:
        review.add("MAJOR", "EVIDENCE_COLUMNS_MISSING", "证据表缺少必要字段。", ", ".join(missing), "参照 project-evidence.md；旧表不能仅凭含 verified 的文本通过。")
        return 0
    verified_by_index = next((i for i, name in enumerate(header) if name in VERIFIED_BY_HEADER), -1)
    ids: set[str] = set()
    count = 0
    covered: set[int] = set()
    for row_index, row in enumerate(table[2:], 3):
        try:
            if len(row) != len(header):
                raise ValueError("表格列数不一致；单元格中的竖线须转义")
            values = {key: row[index].strip().strip("`") for key, index in columns.items()}
            if any(not value or PLACEHOLDER_RE.search(value) for value in values.values()):
                raise ValueError("存在空字段或占位内容")
            if values["id"] in ids:
                raise ValueError("Claim ID 重复")
            ids.add(values["id"])
            if values["verification"].casefold() not in VERIFIED:
                raise ValueError(f"条目未明确核验：{values['verification']}")
            if verified_by_index >= 0:
                actor = row[verified_by_index].strip().strip("`").casefold()
                if actor not in VERIFIED_BY:
                    raise ValueError(
                        f"核验主体无效：{actor or '(空)'}；须为 {'/'.join(sorted(VERIFIED_BY))} 之一，"
                        "助手自查不得记为队员核验"
                    )
            question = int(values["question"])
            run = runs.get(question)
            if not run or run.get("run_id") != values["run"]:
                raise ValueError("条目未关联该问当前选用 run_id")
            source = values["source"]
            match = re.fullmatch(r"\[[^\]]+\]\(([^)]+)\)", source)
            if match:
                source = match.group(1)
            artifact = review.path(source)
            if not review.nonempty(artifact):
                raise ValueError(f"引用文件不存在或为空：{source}")
            declared = [review.path(x).resolve() for x in strings(run.get("artifacts"), "artifacts")]
            validation = run.get("validation", {})
            if isinstance(validation, dict):
                declared += [review.path(x).resolve() for x in strings(validation.get("artifacts", []), "validation.artifacts", False)]
            if artifact.resolve() not in declared:
                raise ValueError("引用文件不是该 run 声明的结果/验证产物")
            count += 1
            covered.add(question)
        except (OSError, TypeError, ValueError) as exc:
            review.add("BLOCKER", "EVIDENCE_INVALID", "关键论点未形成有效证据链接。", f"row {row_index}: {exc}", "核对真实值、条件、运行及源文件；不得用弱化措辞或伪改状态替代验证。")
    for question in runs:
        if question not in covered:
            review.add("MAJOR", "QUESTION_CLAIM_MISSING", "该问缺少可核验的结果论点。", f"question={question}")
    return count


def inspect_code(review: Review, entries: list[Path], runs: dict[int, dict]) -> None:
    candidates = set(entries)
    source = review.root / "src"
    if source.is_dir():
        for folder, dirs, files in os.walk(source, followlinks=False):
            dirs[:] = [d for d in dirs if d.casefold() not in IGNORED_DIRS and not Path(folder, d).is_symlink() and not getattr(Path(folder, d), "is_junction", lambda: False)()]
            for name in files:
                if name.lower().endswith(".py"):
                    candidates.add(Path(folder, name))
                if len(candidates) > review.max_files:
                    review.add("MAJOR", "SCAN_FILE_LIMIT", "源码数量超过扫描预算；检查未完成。", source)
                    break
            if len(candidates) > review.max_files:
                break
    for run in runs.values():
        code = run.get("code", [])
        if isinstance(code, list):
            for value in code:
                try:
                    path = review.path(value)
                    if path.suffix.lower() == ".py":
                        candidates.add(path)
                except ValueError:
                    pass  # RUN_INVALID already reports the invalid path.
    for path in sorted(candidates):
        try:
            checked_path(review.root, review.rel(path))
            if not review.nonempty(path):
                review.add("BLOCKER", "CODE_MISSING", "缺少或空入口/共享代码。", review.rel(path))
                continue
            text = review.read(path)
            tree = ast.parse(text, filename=str(path))
            pending = PLACEHOLDER_RE.search(text)
            for node in ast.walk(tree):
                if isinstance(node, ast.Raise):
                    name = node.exc.func if isinstance(node.exc, ast.Call) else node.exc
                    if isinstance(name, ast.Name) and name.id == "NotImplementedError":
                        pending = True
            if pending:
                review.add("BLOCKER", "CODE_PLACEHOLDER", "入口或共享实现仍含未完成内容。", review.rel(path), "完成实际实现；故意抽象接口须由人工确认其不影响执行，不伪造已完成。")
        except (OSError, SyntaxError, ValueError) as exc:
            review.add("BLOCKER", "CODE_INVALID", "源码无法安全检查或语法无效。", f"{review.rel(path)}: {exc}")


def inspect_paper(review: Review, paths: dict[str, Path], submission: dict | None = None) -> dict:
    source, pdf, receipt = (paths[key] for key in ("paper_source", "paper_pdf", "build_receipt"))
    submission = submission or {}
    page_limit = submission.get("page_limit")
    anonymity = submission.get("anonymity") is True
    detail: dict = {"source": review.rel(source), "pdf": review.rel(pdf), "visual_review_required": True}
    if not review.nonempty(source):
        review.add("BLOCKER", "LATEX_SOURCE_MISSING", "缺少声明的最终 LaTeX 源稿。", source)
    elif PLACEHOLDER_RE.search(review.read(source)):
        review.add("BLOCKER", "FINAL_PAPER_PLACEHOLDER", "最终源稿含占位内容。", source)
    if not review.nonempty(pdf):
        review.add("MAJOR", "COMPILED_PDF_MISSING", "缺少声明的最终 PDF。", pdf)
    else:
        try:
            pages, identity = inspect_pdf(pdf, with_identity=True)
            detail["pages"] = pages
            # Page limit and anonymity are disqualification-class contest rules,
            # so a declared limit is checked here rather than left to a final read.
            if page_limit is not None:
                detail["page_limit"] = page_limit
                if pages > page_limit:
                    review.add("BLOCKER", "PAGE_LIMIT_EXCEEDED", "PDF 页数超过声明的上限。",
                               f"{review.rel(pdf)}: {pages} > {page_limit}",
                               "按当年规则压缩正文或移入附录；确认上限本身取自当年官方规则。")
            if anonymity:
                detail["identity_metadata"] = sorted(identity)
                if identity:
                    review.add("BLOCKER", "PDF_IDENTITY_METADATA", "PDF 文档属性仍含可识别身份信息。",
                               "; ".join(f"{key}={value}" for key, value in sorted(identity.items()))[:300],
                               "清除 /Author /Title /Subject /Keywords 后重新构建；正文、文件名与压缩包条目仍需人工检查。")
            # Report each limit separately: declaring only one silently disables the
            # other, which is the easiest way to lose a disqualification-class check.
            undeclared = [name for name, declared in
                          (("page_limit", page_limit is not None), ("anonymity", anonymity)) if not declared]
            if undeclared:
                review.add("MINOR", "SUBMISSION_LIMITS_UNDECLARED",
                           "提交限制未声明，相应检查未运行。", f"submission 缺少：{', '.join(undeclared)}",
                           "按当年官方规则在 mathmodeling.json 的 submission 中填写 page_limit 与 anonymity；"
                           "只填其中一项，另一项不会被检查。见 references/latex-paper.md。")
        except Exception as exc:
            # An unparsable PDF (encryption included) means the declared limits could not
            # be evaluated at all, so it must not read as a lesser finding than a page overrun.
            gated = page_limit is not None or anonymity
            review.add("BLOCKER" if gated else "MAJOR", "PDF_UNVERIFIED",
                       "PDF 无法解析；不能按文件名宣称已编译"
                       + ("，且声明的页数/匿名检查因此未能执行。" if gated else "。"), exc,
                       "重新构建出可解析且未加密的 PDF；加密或损坏的交付物不能视为已核验。" if gated else "")
    if not review.nonempty(receipt):
        review.add("MAJOR", "BUILD_RECEIPT_MISSING", "缺少本次源稿与 PDF 的构建关联。", receipt, "使用 build_paper.py；人工数值/视觉验收另存 docs/qa_report.md。")
        return detail
    try:
        record = review.json(receipt)
        if not isinstance(record, dict) or record.get("tool") != BUILD_MARKER or record.get("status") != "compiled":
            raise ValueError("构建收据类型或状态无效")
        if record.get("source") != review.rel(source) or record.get("pdf") != review.rel(pdf) or record.get("pdf_stamp") != file_stamp(pdf):
            raise ValueError("收据未对应当前源稿/PDF")
        inputs = record.get("inputs")
        if not isinstance(inputs, dict) or review.rel(source) not in inputs:
            raise ValueError("构建收据没有源稿输入")
        for relative, stamp in inputs.items():
            path = review.path(relative)
            if file_stamp(path) != stamp:
                raise ValueError(f"构建后输入发生变化：{relative}")
            if path.suffix.lower() in {".tex", ".bib"} and PLACEHOLDER_RE.search(review.read(path)):
                review.add("BLOCKER", "FINAL_PAPER_PLACEHOLDER", "论文实际依赖仍含占位内容。", relative)
        warnings = record.get("warnings", [])
        minor_warnings = record.get("minor_warnings", [])
        if not isinstance(warnings, list) or not isinstance(minor_warnings, list):
            raise ValueError("构建 warnings 格式无效")
        # build_paper.py separates layout warnings by measured magnitude: material
        # overflow blocks strict submission, a fraction of a point does not.
        if warnings:
            review.add("MAJOR", "BUILD_WARNINGS", "当前 PDF 有实质版面警告，需逐条查看渲染结果。",
                       "; ".join(str(x) for x in warnings[:8]),
                       "重排该表/图/公式或改用 tabularx 等宽度控制；确认无法消除的，在 docs/qa_report.md 记录目检结论。")
        if minor_warnings:
            review.add("MINOR", "BUILD_MINOR_WARNINGS", "存在轻微版面警告，通常不影响可读性。",
                       "; ".join(str(x) for x in minor_warnings[:8]))
    except (OSError, TypeError, ValueError) as exc:
        review.add("MAJOR", "BUILD_STALE_OR_INVALID", "构建关联无效或产物已过期。", exc)
    return detail


def audit(root: Path, problem_count: int | None = None, *, max_file: int = 2_000_000, max_total: int = 20_000_000, max_files: int = 5000) -> tuple[list[Issue], dict, set[Path]]:
    review = Review(root, max_file, max_total, max_files)
    manifest: dict = {}
    manifest_path = root / "mathmodeling.json"
    if manifest_path.exists():
        try:
            manifest = validate_manifest(review.json(manifest_path), root)
            if problem_count is not None and manifest["problem_count"] != problem_count:
                raise ValueError("--problem-count 与清单不一致；请核对实际题数")
        except (OSError, TypeError, ValueError) as exc:
            review.add("BLOCKER", "MANIFEST_INVALID", "项目清单无法可靠确定问题和路径。", exc)
            manifest = {}
    elif problem_count is None:
        review.add("MAJOR", "QUESTION_COUNT_UNKNOWN", "缺少题数契约；不能由现有入口推断已覆盖全部问题。", manifest_path, "提供 mathmodeling.json 或 --problem-count。")
    paths = project_paths(root, manifest)
    for path in paths.values():
        review.protected.add(path.resolve())
    if manifest:
        entries = [review.path(x) for x in manifest["entrypoints"]]
    elif problem_count is not None:
        entries = [root / f"problem_{i}.py" for i in range(1, problem_count + 1)]
    else:
        entries = sorted(path for path in root.glob("problem_*.py") if re.fullmatch(r"problem_[1-9]\d*\.py", path.name))
    if not entries:
        review.add("BLOCKER", "ENTRYPOINTS_UNKNOWN", "没有可审查的问题入口。", root)
    sources: list[Path] = []
    if manifest.get("source_files"):
        for value in manifest["source_files"]:
            path = review.path(value)
            if review.nonempty(path):
                sources.append(path)
            else:
                review.add("BLOCKER", "SOURCE_FILE_MISSING", "声明的原题/附件缺失或为空。", value)
    else:
        # Legacy convenience only; content/attachment completeness remains manual.
        for folder in (root, paths["raw_data"], root / "docs/sources"):
            if folder.is_dir():
                for path in folder.iterdir():
                    if path.suffix.lower() in {".pdf", ".doc", ".docx", ".txt", ".md"} and re.search(r"题|problem|statement", path.stem, re.I) and review.nonempty(path):
                        checked_path(root, review.rel(path))
                        sources.append(path)
    if not sources:
        review.add("BLOCKER", "PROBLEM_SOURCE_MISSING", "未找到声明的或可识别的原始赛题。", "source_files / data/raw / docs/sources / root")
    for name in DOCS:
        path = root / "docs" / name
        if not review.nonempty(path):
            review.add("MAJOR", "DOC_MISSING", "缺少提交核验记录。", review.rel(path))
        else:
            # An unfilled template and a consciously open checklist item are different
            # defects; reporting them under one code produced a self-contradictory fix
            # hint and invited deleting the marker word instead of resolving the gap.
            text = review.read(path)
            if PLACEHOLDER_RE.search(text):
                review.add("MAJOR", "DOC_PLACEHOLDER", "记录仍是未填写的模板占位内容。", review.rel(path),
                           "写入实际内容；确实无法解决的，改写为具名未知项（内容、对结论的影响、处理方式）并在论文局限中说明，不要只删占位词。")
            if "[ ]" in text:
                review.add("MAJOR", "DOC_UNCHECKED_ITEM", "核对清单仍有未勾选条目，相应来源或规则尚未核验。", review.rel(path),
                           "逐项核对后改为 [x]；无法核对的条目改写为具名未知项并说明影响，不要直接删行冒充已完成。")
    configs = [root / "config" / f"parameters{x}" for x in (".yaml", ".yml", ".json", ".toml")]
    if not any(review.nonempty(path) for path in configs):
        review.add("MAJOR", "PARAMETERS_MISSING", "缺少集中参数文件。", "config/parameters.*")
    runs = inspect_runs(review, entries, paths)
    inspect_code(review, entries, runs)
    claim_count = inspect_claims(review, paths, runs)
    paper = inspect_paper(review, paths, manifest.get("submission", {}))
    counts = {severity: sum(issue.severity == severity for issue in review.issues) for severity in ("BLOCKER", "MAJOR", "MINOR")}
    summary = {
        "root": str(root), "status": "STRUCTURE_CHECKS_PASSED" if not counts["BLOCKER"] and not counts["MAJOR"] else "NOT_READY",
        "review_required": True, "counts": counts,
        "entrypoints": [review.rel(x) for x in entries], "problem_sources": sorted({review.rel(x) for x in sources}),
        "selected_runs": len(runs), "linked_claims": claim_count, "paper": paper,
        "scan": {"text_files": len(review.cache), "text_bytes": review.bytes_read, "skipped": review.skipped},
        "verification_boundary": "仅检查声明的结构、状态、运行/文件关联与可解析性；不证明记录真实、数值/推导正确、验证充分或论文可提交。时间戳是过期提示而非完整性证明；仍需独立重跑、数值和逐页视觉审查。",
    }
    # Protect manual QA even if it did not exist when the audit ran.
    review.protected.add((root / "docs/qa_report.md").resolve())
    return review.issues, summary, review.protected


def render(issues: list[Issue], summary: dict, format_: str) -> str:
    if format_ == "json":
        return json.dumps({"tool": REPORT_MARKER, "summary": summary, "issues": [asdict(x) for x in issues]}, ensure_ascii=False, indent=2) + "\n"
    markdown = format_ == "markdown"
    lines = [f"<!-- {REPORT_MARKER} -->" if markdown else f"tool: {REPORT_MARKER}", "# mathmodeling 结构与证据关联检查" if markdown else "mathmodeling 结构与证据关联检查", "", f"项目：{summary['root']}", f"状态：{summary['status']}", "仍需独立终审：是", "，".join(f"{k}={v}" for k, v in summary["counts"].items()), ""]
    for issue in issues:
        lines += [f"- [{issue.severity}] {issue.code}: {issue.message}", "  证据：" + "; ".join(issue.evidence)]
        if issue.fix:
            lines.append("  方向：" + issue.fix)
    lines += ["", "验证边界：" + summary["verification_boundary"]]
    return "\n".join(lines) + "\n"


def save_report(root: Path, relative: str, output: str, protected: set[Path]) -> None:
    path = checked_path(root, relative)
    if path.suffix.lower() not in {".md", ".txt", ".json"} or path.resolve() in protected:
        raise ValueError("报告不能覆盖输入、源码、提交物、运行证据或人工 QA；请选择 docs/structural_audit.md")
    for component in (path, *path.parents):
        if component == root:
            break
        if component.is_symlink() or getattr(component, "is_junction", lambda: False)():
            raise ValueError("报告目标包含链接/junction，拒绝间接写入")
    if path.exists():
        if not path.is_file():
            raise ValueError("报告目标不是普通文件")
        old = path.read_text(encoding="utf-8-sig")
        owned = old.startswith(f"<!-- {REPORT_MARKER} -->\n") or old.startswith(f"tool: {REPORT_MARKER}\n")
        if not owned:
            try:
                obj = json.loads(old)
                owned = isinstance(obj, dict) and obj.get("tool") == REPORT_MARKER
            except ValueError:
                pass
        if not owned:
            raise ValueError("已有目标不是本工具生成的报告，已保留；请使用新路径")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent, prefix=".audit-", suffix=".tmp", delete=False) as stream:
            temporary = stream.name
            stream.write(output)
        os.replace(temporary, path)
    finally:
        if temporary and Path(temporary).exists():
            Path(temporary).unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description="只读检查数学建模提交结构与执行/证据关联；不替代独立终审")
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--problem-count", type=int, default=None, help="旧项目的实际题数；必须与已有清单一致")
    parser.add_argument("--strict", action="store_true", help="BLOCKER 返回 2，MAJOR 返回 1")
    parser.add_argument("--format", choices=("text", "markdown", "json"), default="text")
    parser.add_argument("--report", help="另存项目内报告；只更新本工具生成的报告，不覆盖其他文件")
    parser.add_argument("--max-file-bytes", type=int, default=2_000_000)
    parser.add_argument("--max-total-bytes", type=int, default=20_000_000)
    parser.add_argument("--max-files", type=int, default=5000)
    args = parser.parse_args()
    root = args.project_dir.expanduser().resolve()
    try:
        if not root.is_dir():
            raise ValueError("项目目录不存在或不是目录")
        if args.problem_count is not None and not 1 <= args.problem_count <= 20:
            raise ValueError("--problem-count 必须在 1 到 20 之间")
        if min(args.max_file_bytes, args.max_total_bytes, args.max_files) <= 0:
            raise ValueError("扫描预算必须为正整数")
        issues, summary, protected = audit(root, args.problem_count, max_file=args.max_file_bytes, max_total=args.max_total_bytes, max_files=args.max_files)
        output = render(issues, summary, args.format)
        if args.report:
            save_report(root, args.report, output, protected)
        print(output, end="")
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False) if args.format == "json" else f"检查失败：{exc}")
        return 3
    if args.strict:
        return 2 if summary["counts"]["BLOCKER"] else 1 if summary["counts"]["MAJOR"] else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
