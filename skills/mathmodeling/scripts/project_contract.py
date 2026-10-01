"""Shared, small filesystem/manifest contract for the contest helpers."""

from __future__ import annotations

import json
from pathlib import Path, PureWindowsPath


DEFAULT_PATHS = {
    "raw_data": "data/raw",
    "processed_data": "data/processed",
    "tables": "results/tables",
    "figures": "results/figures",
    "logs": "results/logs",
    "paper": "paper",
    "evidence": "docs/evidence_map.md",
}
DIRECTORIES = (
    "config", "data/raw", "data/processed", "src/common", "results/tables",
    "results/figures", "results/logs", "paper", "paper/build", "paper/output",
    "docs", "tests",
)
RUN_MANIFEST = "results/run_manifest.json"
REPORT_MARKER = "mathmodeling-structural-audit-v2"
BUILD_MARKER = "mathmodeling-paper-build-v1"


def validate_relative(value: object) -> str:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise ValueError("路径必须是非空的项目内相对路径")
    normalized = value.replace("\\", "/")
    windows = PureWindowsPath(value)
    if windows.drive or normalized.startswith("/") or any(
        part in {"..", ""} for part in normalized.split("/")
    ) or normalized in {".", "./"}:
        raise ValueError(f"路径不得越出项目或使用绝对路径：{value}")
    return normalized


def checked_path(root: Path, value: object) -> Path:
    relative = validate_relative(value)
    path = root / relative
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"路径经符号链接或 junction 指向项目外：{relative}")
    return path


def load_json(path: Path, limit: int = 2_000_000) -> object:
    if path.stat().st_size > limit:
        raise ValueError(f"JSON 超过读取上限 {limit} bytes：{path}")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def positive_count(value: object) -> int:
    if type(value) is not int or not 1 <= value <= 20:
        raise ValueError("题目数量必须是 1 到 20 的整数")
    return value


def validate_manifest(data: object, root: Path) -> dict:
    if not isinstance(data, dict):
        raise ValueError("mathmodeling.json 根节点必须为对象")
    version = data.get("schema_version", 1)
    if type(version) is not int or version not in {1, 2}:
        raise ValueError("支持 mathmodeling.json schema_version 1 或 2")
    count = positive_count(data.get("problem_count"))
    entries = data.get("entrypoints")
    if not isinstance(entries, list) or len(entries) != count:
        raise ValueError("problem_count 必须与 entrypoints 数量一致")
    resolved = [checked_path(root, entry) for entry in entries]
    if any(path.suffix.lower() != ".py" for path in resolved):
        raise ValueError("各问入口必须是 .py 文件")
    if len({str(path.resolve()).casefold() for path in resolved}) != count:
        raise ValueError("各问入口不得重复或指向同一个文件")
    paths = data.get("canonical_directories", {})
    if not isinstance(paths, dict):
        raise ValueError("canonical_directories 必须为对象")
    for value in paths.values():
        checked_path(root, value)
    sources = data.get("source_files", [])
    if not isinstance(sources, list):
        raise ValueError("source_files 必须为路径列表")
    for source in sources:
        checked_path(root, source)
    checked_path(root, data.get("run_manifest", RUN_MANIFEST))
    submission = data.get("submission", {})
    if not isinstance(submission, dict):
        raise ValueError("submission 必须为对象")
    for key, value in submission.items():
        if key in {"source", "pdf"}:
            expected = ".tex" if key == "source" else ".pdf"
            if checked_path(root, value).suffix.lower() != expected:
                raise ValueError(f"submission.{key} 必须使用 {expected} 文件")
        elif key == "page_limit":
            # Optional; absent means the contest page rule is not machine-checked.
            if type(value) is not int or not 1 <= value <= 500:
                raise ValueError("submission.page_limit 必须是 1 到 500 的整数正文页数上限")
        elif key == "anonymity":
            if type(value) is not bool:
                raise ValueError("submission.anonymity 必须是 true 或 false")
        else:
            raise ValueError(f"未知 submission 字段：{key}")
    return data


def project_paths(root: Path, manifest: dict) -> dict[str, Path]:
    names = DEFAULT_PATHS | manifest.get("canonical_directories", {})
    paths = {key: checked_path(root, value) for key, value in names.items()}
    paper = paths["paper"].relative_to(root).as_posix()
    submission = manifest.get("submission", {})
    paths["paper_source"] = checked_path(root, submission.get("source", f"{paper}/main.tex"))
    paths["paper_pdf"] = checked_path(root, submission.get("pdf", f"{paper}/output/main.pdf"))
    paths["build_receipt"] = paths["paper_pdf"].with_suffix(".build.json")
    paths["runs"] = checked_path(root, manifest.get("run_manifest", RUN_MANIFEST))
    return paths


def default_manifest(title: str, count: int) -> dict:
    positive_count(count)
    return {
        "schema_version": 2,
        "title": title,
        "problem_count": count,
        "entrypoints": [f"problem_{index}.py" for index in range(1, count + 1)],
        "canonical_directories": dict(DEFAULT_PATHS),
        "source_files": [],
        "run_manifest": RUN_MANIFEST,
        "submission": {"source": "paper/main.tex", "pdf": "paper/output/main.pdf"},
    }


def file_stamp(path: Path) -> dict:
    stat = path.stat()
    return {"size": stat.st_size, "mtime_ns": stat.st_mtime_ns}


def is_numeric(value: object) -> bool:
    import math
    try:
        return type(value) in {int, float} and math.isfinite(value)
    except OverflowError:
        return False


# Author-supplied document properties only. Creator/Producer name the toolchain
# (XeLaTeX writes them itself) and never identify the team, so they are not read.
IDENTITY_FIELDS = ("Author", "Title", "Subject", "Keywords")


def inspect_pdf(path: Path, with_identity: bool = False):
    """Parse a real PDF; a filename/header is not a successful compilation.

    Returns the page count, or `(pages, identity)` when `with_identity` is set.
    `identity` maps each non-empty author-supplied document property to its
    value; an anonymised contest PDF must leave all of them empty.
    """
    with path.open("rb") as stream:
        if not stream.read(8).startswith(b"%PDF-"):
            raise ValueError("PDF 文件头无效")
    identity: dict[str, str] = {}
    try:
        from pypdf import PdfReader
    except ImportError:
        import re
        import shutil
        import subprocess
        executable = shutil.which("pdfinfo")
        if not executable:
            raise RuntimeError("需要 pypdf 或 Poppler pdfinfo 才能验证 PDF，不能只按扩展名判定")
        process = subprocess.run(
            [executable, str(path)], capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=30,
        )
        match = re.search(r"^Pages:\s*(\d+)\s*$", process.stdout, re.MULTILINE)
        if process.returncode or not match or re.search(r"^Encrypted:\s+yes\b", process.stdout, re.MULTILINE | re.I):
            raise ValueError("pdfinfo 无法读取有效页数：" + process.stderr[:300])
        pages = int(match.group(1))
        for field in IDENTITY_FIELDS:
            # Horizontal space only. A bare \s* would span the newline, so a present
            # but blank field would capture the NEXT line as its value.
            found = re.search(rf"^{field}:[ \t]*(\S.*?)[ \t]*$", process.stdout, re.MULTILINE)
            if found and found.group(1).strip():
                identity[field] = found.group(1).strip()
    else:
        try:
            reader = PdfReader(path, strict=True)
            if reader.is_encrypted:
                raise ValueError("最终 PDF 不应加密")
            pages = len(reader.pages)
            for page in reader.pages:
                _ = page.mediabox
            metadata = reader.metadata or {}
            for field in IDENTITY_FIELDS:
                value = metadata.get(f"/{field}")
                if value is not None and str(value).strip():
                    identity[field] = str(value).strip()
        except Exception as exc:
            raise ValueError(f"PDF 解析失败：{exc}") from exc
    if pages < 1:
        raise ValueError("PDF 没有页面")
    return (pages, identity) if with_identity else pages
