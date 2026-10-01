#!/usr/bin/env python3
"""Build declared LaTeX in a fresh directory; never publish a stale failed build."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from project_contract import (
    BUILD_MARKER, checked_path, file_stamp, inspect_pdf, load_json,
    project_paths, validate_manifest,
)


# A missing glyph or an unresolved reference corrupts the delivered content, so it
# must stop the build. Overfull/Underfull boxes are layout defects that a person has
# to look at: an ordinary five-column Chinese table overflows by tens of points, and
# failing the whole build on that pushed teams off the tool exactly when the receipt
# linking source to PDF matters most. Layout warnings are therefore recorded, and
# separated by measured magnitude, instead of aborting the build.
FATAL_WARNING_RE = re.compile(
    r"Missing character:|"
    r"undefined references|undefined citations|multiply[ -]defined|"
    r"(?:Reference|Citation) .{0,160} undefined|"
    r"LaTeX Font Warning: Font shape|fontspec (?:Warning|Error)", re.I,
)
LAYOUT_WARNING_RE = re.compile(r"Overfull \\[hv]box|Underfull \\[hv]box|Float too large", re.I)
OVERFLOW_SIZE_RE = re.compile(r"\(([\d.]+)pt too (?:wide|high)\)", re.I)
DEFAULT_LAYOUT_THRESHOLD_PT = 5.0


def classify_warnings(log: str, threshold: float = DEFAULT_LAYOUT_THRESHOLD_PT) -> dict[str, list[str]]:
    """Split build-log warnings into fatal, material-layout and minor-layout."""
    fatal: list[str] = []
    material: list[str] = []
    minor: list[str] = []
    for raw in log.splitlines():
        line = raw.strip()
        if FATAL_WARNING_RE.search(line):
            fatal.append(line)
        elif LAYOUT_WARNING_RE.search(line):
            if re.search(r"Float too large", line, re.I):
                material.append(line)
            elif re.search(r"Underfull", line, re.I):
                minor.append(line)  # Underfull is spacing badness, never lost content.
            else:
                size = OVERFLOW_SIZE_RE.search(line)
                # An unmeasurable overfull box stays material rather than silently passing.
                (minor if size and float(size.group(1)) < threshold else material).append(line)
    return {key: list(dict.fromkeys(value))
            for key, value in (("fatal", fatal), ("material", material), ("minor", minor))}


def atomic_write(path: Path, content: bytes) -> None:
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".paper-", suffix=".tmp", delete=False) as stream:
            temporary = stream.name
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if temporary and Path(temporary).exists():
            Path(temporary).unlink()


def bibliography_inputs(build_dir: Path, source_dir: Path) -> set[Path]:
    """TeX's .fls does not record the .bib files read by BibTeX/Biber."""
    values: set[str] = set()
    for aux in build_dir.rglob("*.aux"):
        content = aux.read_text(encoding="utf-8", errors="replace")
        for group in re.findall(r"\\bibdata\{([^}]+)\}", content):
            values.update(name.strip() + ("" if name.strip().endswith(".bib") else ".bib")
                          for name in group.split(",") if name.strip())
        for name in re.findall(r"\\bibstyle\{([^}]+)\}", content):
            values.add(name.strip() + ".bst")
    for bcf in build_dir.rglob("*.bcf"):
        for element in ET.parse(bcf).iter():
            if element.tag.rsplit("}", 1)[-1] == "datasource" and element.text:
                values.add(element.text.strip())
    candidates = {Path(value) if Path(value).is_absolute() else source_dir / value for value in values}
    return {path.resolve() for path in candidates if path.is_file()}


def stage_bibtex_inputs(aux: Path, source_dir: Path) -> set[Path]:
    """Alias local bibliography files in the disposable build, preserving originals.

    On Windows, BibTeX can open its Unicode argv but misread UTF-8 filenames
    inside an .aux file. Only compiler-generated .aux and new build files change.
    """
    aliases: dict[Path, str] = {}
    content = aux.read_text(encoding="utf-8")
    for command, suffix in (("bibdata", ".bib"), ("bibstyle", ".bst")):
        def replace(match: re.Match) -> str:
            names = []
            for name in match.group(1).split(","):
                name = name.strip()
                path = source_dir / (name if name.endswith(suffix) else name + suffix)
                if path.is_file():
                    path = path.resolve()
                    if path not in aliases:
                        alias = f"mm-bib-input-{len(aliases)+1:03d}"
                        with (aux.parent / (alias + suffix)).open("xb") as output:
                            output.write(path.read_bytes())
                        aliases[path] = alias
                    names.append(aliases[path])
                else:
                    names.append(name)
            return "\\" + command + "{" + ",".join(names) + "}"
        content = re.sub(r"\\" + command + r"\{([^}]+)\}", replace, content)
    aux.write_text(content, encoding="utf-8")
    return set(aliases)


def prune_builds(build_root: Path, keep: int = 5) -> None:
    """Keep only the newest disposable build directories; never touch anything else."""
    runs = sorted((path for path in build_root.glob("run-*")
                   if path.is_dir() and not path.is_symlink()
                   and not getattr(path, "is_junction", lambda: False)()),
                  key=lambda path: path.stat().st_mtime, reverse=True)
    for stale in runs[keep:]:
        shutil.rmtree(stale, ignore_errors=True)


def build(root: Path, timeout: int = 300, engine: str = "auto", *,
          strict_layout: bool = False, replace_unowned: bool = False,
          layout_threshold: float = DEFAULT_LAYOUT_THRESHOLD_PT, keep_builds: int = 5) -> dict:
    manifest_file = root / "mathmodeling.json"
    manifest = validate_manifest(load_json(manifest_file), root) if manifest_file.exists() else {}
    paths = project_paths(root, manifest)
    source, destination, receipt = (paths[key] for key in ("paper_source", "paper_pdf", "build_receipt"))
    if not source.is_file():
        raise ValueError(f"声明的 LaTeX 源稿不存在：{source}")
    if destination.resolve() in {checked_path(root, value).resolve() for value in manifest.get("source_files", [])}:
        raise ValueError("目标 PDF 同时是声明的原始输入，拒绝覆盖")
    build_root = source.parent / "build"
    for target in (destination, receipt, build_root):
        checked_path(root, target.relative_to(root).as_posix())
        for component in (target, *target.parents):
            if component == root:
                break
            if component.is_symlink() or getattr(component, "is_junction", lambda: False)():
                raise ValueError(f"构建目标包含链接/junction：{component}")
    latexmk = shutil.which("latexmk")
    xelatex = shutil.which("xelatex")
    if engine == "latexmk" and not latexmk or engine == "xelatex" and not xelatex:
        raise RuntimeError(f"未找到指定编译器 {engine}")
    # Direct XeLaTeX also lets us alias UTF-8 BibTeX database names on Windows.
    use_latexmk = bool(latexmk) and engine != "xelatex" and not (engine == "auto" and os.name == "nt")
    if not use_latexmk and not xelatex:
        raise RuntimeError("需要 latexmk 或 XeLaTeX；未编译，不更改现有 PDF")
    # Generated output locations may update only their own previous products.
    old_receipt = None
    if receipt.exists():
        old_receipt = load_json(receipt)
        if not isinstance(old_receipt, dict) or old_receipt.get("tool") != BUILD_MARKER:
            raise ValueError("构建收据位置已有其他文件，已保留")
        if old_receipt.get("pdf") != destination.relative_to(root).as_posix() or (
            destination.exists() and old_receipt.get("pdf_stamp") != file_stamp(destination)
        ):
            raise ValueError("已有 PDF 与构建收据不一致，可能含人工修改；请使用新目标保留它")
    backup: Path | None = None
    if destination.exists() and not old_receipt:
        # A hand-published PDF used to lock this path for the rest of the contest.
        # It is still refused by default, but an explicit opt-in can take it over
        # after preserving the original bytes beside it.
        if not replace_unowned:
            raise ValueError(
                "目标 PDF 已存在且没有本工具收据；确认可以接管请加 --replace-unowned（旧文件会另存备份），"
                "或在 submission.pdf 指定新路径保留旧交付物"
            )
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = destination.with_name(f"{destination.stem}.bak-{stamp}{destination.suffix}")
        if backup.exists():
            raise ValueError(f"备份目标已存在，未覆盖：{backup}")
        shutil.copy2(destination, backup)
    build_root.mkdir(parents=True, exist_ok=True)
    prune_builds(build_root, keep_builds)
    build_dir = Path(tempfile.mkdtemp(prefix="run-", dir=build_root))
    start = time.time()
    before_source = file_stamp(source)
    commands: list[list[str]] = []
    stdout: list[str] = []
    extra_inputs: set[Path] = set()
    common = ["-interaction=nonstopmode", "-halt-on-error", "-file-line-error", "-recorder", "-no-shell-escape"]
    output_argument = build_dir.relative_to(source.parent).as_posix()

    def run(command: list[str], *, cwd: Path | None = None, env: dict | None = None) -> None:
        remaining = timeout - (time.time() - start)
        if remaining <= 0:
            raise TimeoutError("整个构建流程超过时限")
        commands.append(command)
        working_dir = cwd or source.parent
        stdout.append(f"cwd: {working_dir}\nargv: {json.dumps(command, ensure_ascii=False)}\n")
        process = subprocess.run(command, cwd=working_dir, env=env, capture_output=True, text=True,
                                 encoding="utf-8", errors="replace", timeout=remaining)
        stdout.append(process.stdout + process.stderr)
        if process.returncode:
            raise RuntimeError(f"编译命令退出 {process.returncode}；本次目录：{build_dir}\n" + (process.stdout + process.stderr)[-2500:])

    try:
        if use_latexmk:
            run([latexmk, "-xelatex", *common, f"-outdir={output_argument}", "./" + source.name])
        else:
            # An ASCII relative output option avoids Windows TeX putenv failures
            # with particular UTF-8 byte sequences in otherwise valid paths.
            command = [xelatex, *common, f"-output-directory={output_argument}", "./" + source.name]
            run(command)
            bcf = build_dir / f"{source.stem}.bcf"
            aux = build_dir / f"{source.stem}.aux"
            if bcf.exists():
                biber = shutil.which("biber")
                if not biber:
                    raise RuntimeError("当前文献配置需要 biber；未完成构建，不交付旧 PDF")
                run([biber, "--input-directory", output_argument, "--output-directory", output_argument, source.stem])
            elif aux.exists() and "\\bibdata" in aux.read_text(encoding="utf-8", errors="replace"):
                bibtex = shutil.which("bibtex")
                if not bibtex:
                    raise RuntimeError("当前文献配置需要 BibTeX；未完成构建")
                environment = os.environ.copy()
                for key in ("BIBINPUTS", "BSTINPUTS"):
                    environment[key] = str(source.parent) + os.pathsep + environment.get(key, "")
                if os.name == "nt":
                    extra_inputs.update(stage_bibtex_inputs(aux, source.parent))
                # BibTeX must write inside its working directory under openout_any=p.
                run([bibtex, source.stem], cwd=build_dir, env=environment)
            run(command)
            run(command)
        generated = build_dir / (source.stem + ".pdf")
        log = build_dir / (source.stem + ".log")
        if not generated.is_file() or not log.is_file():
            raise RuntimeError(f"本次构建没有生成 PDF/log：{build_dir}")
        pages = inspect_pdf(generated)
        found = classify_warnings(log.read_text(encoding="utf-8", errors="replace"), layout_threshold)
        if found["fatal"]:
            raise RuntimeError(f"本次 PDF 有内容级错误（缺字形/未解析引用），未替换交付物；检查 {generated}\n"
                               + "\n".join(found["fatal"][:12]))
        if strict_layout and (found["material"] or found["minor"]):
            raise RuntimeError(f"--strict-layout：本次 PDF 仍有版面警告，未替换交付物；检查 {generated}\n"
                               + "\n".join((found["material"] + found["minor"])[:12]))
        if file_stamp(source) != before_source:
            raise RuntimeError("编译期间源稿发生变化，请重新构建")
        inputs = {source.relative_to(root).as_posix(): file_stamp(source)}
        fls = build_dir / (source.stem + ".fls")
        if not fls.is_file():
            raise RuntimeError("缺少 recorder .fls，无法关联实际论文依赖")
        dependencies = bibliography_inputs(build_dir, source.parent) | extra_inputs
        for line in fls.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.startswith("INPUT "):
                continue
            value = line[6:].strip().strip('"')
            path = Path(value)
            if not path.is_absolute():
                path = source.parent / path
            dependencies.add(path.resolve())
        for path in sorted(dependencies):
            if not path.is_relative_to(root) or path.is_relative_to(build_root.resolve()) or not path.is_file():
                continue
            if path in {destination.resolve(), receipt.resolve()}:
                raise ValueError("目标交付物同时是编译输入，拒绝覆盖")
            if path.stat().st_mtime > start:
                raise RuntimeError(f"构建期间依赖发生变化：{path}")
            inputs[path.relative_to(root).as_posix()] = file_stamp(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(destination, generated.read_bytes())
        record = {
            "tool": BUILD_MARKER, "status": "compiled", "source": source.relative_to(root).as_posix(),
            "pdf": destination.relative_to(root).as_posix(), "pdf_stamp": file_stamp(destination),
            "inputs": inputs, "pages": pages,
            "warnings": found["material"], "minor_warnings": found["minor"],
            "layout_threshold_pt": layout_threshold,
            "commands": commands, "log": log.relative_to(root).as_posix(),
            "built_at": datetime.now(timezone.utc).isoformat(), "visual_review": "pending",
        }
        if backup is not None:
            record["replaced_unowned_backup"] = backup.relative_to(root).as_posix()
        atomic_write(receipt, (json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        return record
    finally:
        (build_dir / "command-output.txt").write_text("\n".join(stdout), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="在独立目录编译并验证 PDF；成功后才更新声明的交付物")
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--timeout", type=int, default=300, help="整个构建流程总秒数")
    parser.add_argument("--engine", choices=("auto", "latexmk", "xelatex"), default="auto")
    parser.add_argument("--strict-layout", action="store_true",
                        help="任何 Overfull/Underfull/浮动体过大都判为失败；默认只记录并按幅度分级")
    parser.add_argument("--layout-threshold", type=float, default=DEFAULT_LAYOUT_THRESHOLD_PT,
                        help="溢出多少 pt 起算实质版面警告（默认 5.0）")
    parser.add_argument("--replace-unowned", action="store_true",
                        help="接管一个没有本工具收据的已有 PDF；旧文件先另存为 .bak-<UTC 时间戳>.pdf")
    parser.add_argument("--keep-builds", type=int, default=5, help="保留最近多少个一次性构建目录")
    args = parser.parse_args()
    try:
        root = args.project_dir.expanduser().resolve()
        if not root.is_dir() or args.timeout <= 0:
            raise ValueError("项目目录必须存在，timeout 必须为正数")
        if args.layout_threshold < 0 or args.keep_builds < 1:
            raise ValueError("--layout-threshold 不得为负，--keep-builds 至少为 1")
        record = build(root, args.timeout, args.engine, strict_layout=args.strict_layout,
                       replace_unowned=args.replace_unowned, layout_threshold=args.layout_threshold,
                       keep_builds=args.keep_builds)
        print(json.dumps(record, ensure_ascii=False, indent=2))
        print("编译与 PDF 解析通过；仍需逐页视觉检查和数字一致性核验，记录在 docs/qa_report.md。")
        if record["warnings"]:
            print(f"注意：{len(record['warnings'])} 条实质版面警告已写入收据，结构审计会报 MAJOR，请逐条查看渲染页。")
        return 0
    except (OSError, ValueError, RuntimeError, TimeoutError, subprocess.TimeoutExpired, ET.ParseError) as exc:
        print(f"构建失败，未授权使用旧 PDF 代替本次结果：{exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
