#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Search the local CUMCM excellent-paper corpus for language patterns.

The script extracts only text for prose analysis. It does not validate or
transfer any paper's algorithms, results, or claims.

Extraction backends:
- pdftotext (Poppler): preferred when available because it recovers more PDFs.
- pypdf: portable fallback.

Use --backend to make a run protocol explicit. The auto mode records which
backend supplied each paper and never changes the source PDFs.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path


# The excellent-paper corpus is user-supplied and is not bundled here.
# Point --corpus or the GUOSAI_CORPUS environment variable at your own local
# directory of PDFs; this default only needs to exist when neither is given.
DEFAULT_CORPUS = Path.home() / "guosai-corpus"
CACHE_SCHEMA = 3
CACHE_DIR_NAME = "guosai-corpus-cache-v3"

PHRASES = [
    "针对问题",
    "问题一",
    "问题二",
    "问题三",
    "问题四",
    "首先",
    "其次",
    "再次",
    "最后",
    "然后",
    "接着",
    "进一步",
    "在此基础上",
    "基础上",
    "综上",
    "综上所述",
    "因此",
    "从而",
    "进而",
    "如图",
    "由图",
    "见表",
    "由表",
    "从图",
    "从表",
    "建立",
    "采用",
    "利用",
    "引入",
    "提出",
    "构造",
    "结合",
    "本文",
    "我们",
    "笔者",
    "显著",
    "明显",
    "灵敏度",
    "敏感性",
    "稳定性",
    "检验",
    "验证",
    "误差",
    "对比",
    "相比",
    "结果表明",
    "可得",
    "随着",
    "考虑到",
]

SECTION_PATTERNS = {
    "问题重述": r"问题重述",
    "问题分析": r"问题分析",
    "模型假设": r"模型(?:的)?假设|问题假设",
    "符号说明": r"符号说明|符号定义",
    "数据处理": r"数据预处理|数据处理|数据分析",
    "模型建立": r"模型(?:的)?建立|建立模型",
    "模型求解": r"模型(?:的)?求解|求解模型",
    "检验与稳健性": r"模型检验|敏感性分析|灵敏度分析|稳健性分析|误差分析",
    "评价与改进": r"模型(?:的)?评价|模型优缺点|模型(?:的)?优缺点|模型改进|模型推广",
    "结论与建议": r"结论|总结|建议",
    "参考文献": r"参考文献",
    "附录": r"附录",
}


def ensure_utf8() -> None:
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def normalize(text: str) -> str:
    text = text.replace("\u3000", " ").replace("\x0c", "\n")
    text = re.sub(
        r"(?<=[\u4e00-\u9fff，。；：、（）])\s+(?=[\u4e00-\u9fff，。；：、（）])",
        "",
        text,
    )
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def text_quality(text: str | None) -> dict[str, int | float | bool]:
    raw = text or ""
    han = len(re.findall(r"[\u4e00-\u9fff]", raw))
    watermark = raw.count("数模加油站")
    chars = len(raw)
    ratio = han / max(chars, 1)
    usable = chars >= 10_000 and han >= 5_000 and watermark < 8
    return {
        "chars": chars,
        "han": han,
        "watermark": watermark,
        "han_ratio": round(ratio, 6),
        "usable": usable,
    }


def abstract_of(text: str) -> str:
    match = re.search(r"摘\s*要[:：]?", text)
    if not match:
        return ""
    tail = text[match.end() :]
    # Accept a colon-bearing header anywhere, or a colonless header occupying
    # its own line.  Do not truncate prose such as “以单品编码为关键字”.
    keyword = re.search(
        r"关\s*键\s*[词字]\s*[:：]|^[ \t]*关\s*键\s*[词字][ \t]*(?=\r?$)",
        tail,
        flags=re.MULTILINE,
    )
    end = keyword.start() if keyword else min(1800, len(tail))
    return normalize(tail[:end])


def _pypdf_available() -> bool:
    return importlib.util.find_spec("pypdf") is not None


def resolve_backends(requested: str) -> list[str]:
    has_poppler = shutil.which("pdftotext") is not None
    has_pypdf = _pypdf_available()

    if requested == "pdftotext":
        if not has_poppler:
            raise RuntimeError("未找到 pdftotext；请安装 Poppler，或改用 --backend pypdf。")
        return ["pdftotext"]
    if requested == "pypdf":
        if not has_pypdf:
            raise RuntimeError("未安装 pypdf；请运行 python -m pip install pypdf。")
        return ["pypdf"]

    backends: list[str] = []
    if has_poppler:
        backends.append("pdftotext")
    if has_pypdf:
        backends.append("pypdf")
    if not backends:
        raise RuntimeError("没有可用 PDF 文本后端；需要 Poppler/pdftotext 或 pypdf。")
    return backends


def extract_pdftotext(path: Path) -> str | None:
    executable = shutil.which("pdftotext")
    if not executable:
        return None
    completed = subprocess.run(
        [
            executable,
            "-layout",
            "-enc",
            "UTF-8",
            "--",
            str(path),
            "-",
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
    )
    if completed.returncode != 0 or not completed.stdout:
        raise RuntimeError("pdftotext failed: " + completed.stderr.decode("utf-8", errors="replace")[:240])
    return completed.stdout.decode("utf-8", errors="replace")


def extract_pypdf(path: Path) -> str | None:
    # Keep malformed PDF parsing bounded even in the portable fallback.
    worker = (
        "import sys\n"
        "from pypdf import PdfReader\n"
        "r=PdfReader(sys.argv[1],strict=False)\n"
        "parts=[]\n"
        "for i,p in enumerate(r.pages,1):\n"
        " try: parts.append(p.extract_text() or '')\n"
        " except Exception as e:\n"
        "  parts.append(''); print('page '+str(i)+': '+str(e),file=sys.stderr)\n"
        "sys.stdout.buffer.write(chr(12).join(parts).encode('utf-8',errors='replace'))\n"
    )
    completed = subprocess.run([sys.executable, "-X", "utf8", "-c", worker, str(path)],
                               capture_output=True, timeout=30)
    if completed.returncode:
        raise RuntimeError("pypdf failed: " + completed.stderr.decode("utf-8", errors="replace")[-240:])
    if completed.stderr:
        print(f"[pypdf 提示 {path.name}] " + completed.stderr.decode("utf-8", errors="replace")[-500:], file=sys.stderr)
    return completed.stdout.decode("utf-8", errors="replace")


def _cache_key(path: Path, backend: str) -> str:
    stat = path.stat()
    payload = (
        f"{CACHE_SCHEMA}|{backend}|{path.resolve()}|"
        f"{stat.st_mtime_ns}|{stat.st_size}"
    )
    return hashlib.sha256(payload.encode("utf-8", errors="replace")).hexdigest()


def cached_extract(path: Path, backend: str, cache_dir: Path) -> str | None:
    cache_file = cache_dir / f"{_cache_key(path, backend)}.json"
    if cache_file.is_file():
        try:
            payload = json.loads(cache_file.read_text(encoding="utf-8"))
            if payload.get("schema") == CACHE_SCHEMA and payload.get("backend") == backend:
                if isinstance(payload.get("text"), str):
                    return payload["text"]
        except Exception:
            pass

    extractor = extract_pdftotext if backend == "pdftotext" else extract_pypdf
    text = extractor(path)
    if text is not None:
        try:
            cache_file.write_text(
                json.dumps({"schema": CACHE_SCHEMA, "backend": backend, "text": text}, ensure_ascii=False),
                encoding="utf-8",
            )
        except OSError as error:
            print(f"缓存未写入，使用本次抽取结果：{error}", file=sys.stderr)
    return text


def choose_candidate(candidates: list[dict[str, object]]) -> dict[str, object]:
    if not candidates:
        return {
            "backend": "none",
            "text": "",
            "quality": text_quality(""),
        }

    def score(candidate: dict[str, object]) -> tuple[int, int, int, int]:
        quality = candidate["quality"]
        assert isinstance(quality, dict)
        return (
            int(bool(quality["usable"])),
            int(quality["han"]),
            -int(quality["watermark"]),
            int(quality["chars"]),
        )

    return max(candidates, key=score)


def inventory(corpus: Path) -> list[Path]:
    if not corpus.is_dir():
        raise RuntimeError(f"语料文件夹不存在：{corpus}；可用 --corpus 或 GUOSAI_CORPUS 指定。")
    paths = sorted(p for p in corpus.rglob("*") if p.is_file() and p.suffix.lower() == ".pdf")
    if not paths:
        raise RuntimeError(f"语料目录没有 PDF：{corpus}")
    return paths


def select_paths(paths: list[Path], selectors: list[str], corpus: Path) -> list[Path]:
    selected = []
    for selector in selectors:
        key = selector.replace("\\", "/").casefold()
        exact = [p for p in paths if key in {p.name.casefold(), p.stem.casefold(), p.relative_to(corpus).as_posix().casefold()}]
        matches = exact or [p for p in paths if key in p.relative_to(corpus).as_posix().casefold()]
        if len(matches) != 1:
            names = ", ".join(p.relative_to(corpus).as_posix() for p in matches[:8])
            raise RuntimeError(f"论文选择必须唯一：{selector!r}；命中 {len(matches)} 篇。{names}")
        if matches[0] not in selected:
            selected.append(matches[0])
    return selected


def load_papers(corpus: Path, requested_backend: str = "auto", paths: list[Path] | None = None) -> list[dict[str, object]]:
    if not corpus.is_dir():
        raise RuntimeError(
            f"语料文件夹不存在：{corpus}\n可用 --corpus 或环境变量 GUOSAI_CORPUS 指定。"
        )

    backends = resolve_backends(requested_backend)
    cache_dir = Path(tempfile.gettempdir()) / CACHE_DIR_NAME
    cache_dir.mkdir(parents=True, exist_ok=True)

    papers: list[dict[str, object]] = []
    for path in inventory(corpus) if paths is None else paths:
        candidates: list[dict[str, object]] = []
        errors = []
        for backend in backends:
            try:
                raw = cached_extract(path, backend, cache_dir)
                if raw is None:
                    errors.append(f"{backend}: extraction returned no text")
            except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
                raw = None
                errors.append(f"{backend}: {str(error)[:240]}")
            quality = text_quality(raw)
            candidates.append(
                {
                    "backend": backend,
                    "text": raw or "",
                    "quality": quality,
                }
            )
            # In auto mode Poppler is preferred and already passes the strict gate.
            if requested_backend == "auto" and backend == "pdftotext" and quality["usable"]:
                break

        chosen = choose_candidate(candidates)
        quality = chosen["quality"]
        assert isinstance(quality, dict)
        year_match = re.search(r"20\d{2}", path.parent.name)
        papers.append(
            {
                "year": year_match.group(0) if year_match else "unknown",
                "file": path.name,
                "path": str(path),
                "backend": chosen["backend"],
                # Preserve page/line boundaries for abstract parsing and provenance.
                "text": str(chosen["text"]),
                "pages": str(chosen["text"]).rstrip("\f").split("\f"),
                "extraction_errors": errors,
                **quality,
            }
        )
    return papers


def usable_papers(papers: list[dict[str, object]]) -> list[dict[str, object]]:
    return [paper for paper in papers if paper["usable"]]


def cmd_list(papers: list[dict[str, object]]) -> None:
    for paper in papers:
        mark = "OK" if paper["usable"] else "--"
        print(
            f"{paper['year']:<4} {mark:<2} {paper['backend']:<9} "
            f"han={paper['han']:>7} chars={paper['chars']:>7}  {paper['file']}"
        )
    ok = usable_papers(papers)
    print(f"共 {len(papers)} 篇；可解析 {len(ok)} 篇。")
    print("口径：chars>=10000、汉字>=5000、水印命中<8；汉字占比仅作诊断。")


def _percentile(values: list[int], fraction: float) -> int:
    if not values:
        return 0
    values = sorted(values)
    return values[min(len(values) - 1, int(len(values) * fraction))]


def cmd_stats(papers: list[dict[str, object]], requested_backend: str) -> None:
    usable = usable_papers(papers)
    print("== 语料概况 ==")
    print(f"  请求后端：{requested_backend}")
    print(
        "  实际后端："
        + ", ".join(
            f"{name}={count}"
            for name, count in sorted(Counter(str(p["backend"]) for p in papers).items())
        )
    )
    for year in sorted({str(p["year"]) for p in papers}):
        group = [p for p in papers if p["year"] == year]
        print(
            f"  {year}: {len(group)} 篇，可解析 "
            f"{sum(bool(p['usable']) for p in group)} 篇"
        )
    print(f"  合计 {len(papers)} 篇，可解析 {len(usable)} 篇\n")

    print(f"== 章节出现（按篇，{len(usable)} 篇）==")
    for label, pattern in SECTION_PATTERNS.items():
        count = sum(bool(re.search(pattern, str(p["text"]))) for p in usable)
        print(f"  {label:<8} {count}/{len(usable)}")

    abstracts = [abstract_of(str(p["text"])) for p in usable]
    abstracts = [abstract for abstract in abstracts if abstract]
    print("\n== 摘要画像 ==")
    if abstracts:
        lengths = sorted(len(abstract) for abstract in abstracts)
        digits = sum(bool(re.search(r"\d", abstract)) for abstract in abstracts)
        taskwise = sum("针对问题" in abstract for abstract in abstracts)
        checks = sum(
            bool(re.search(r"检验|验证|灵敏度|敏感性|误差|对比|稳健|稳定", abstract))
            for abstract in abstracts
        )
        print(
            f"  摘要数 {len(abstracts)}，长度中位 {_percentile(lengths, 0.5)}，"
            f"范围 {lengths[0]}–{lengths[-1]}"
        )
        print(
            f"  含阿拉伯数字 {digits}/{len(abstracts)}；含“针对问题” "
            f"{taskwise}/{len(abstracts)}；含检验词 {checks}/{len(abstracts)}（均为词面统计）"
        )

    print(f"\n== 全文本高频词（前 25，{len(usable)} 篇合计）==")
    frequencies: Counter[str] = Counter()
    for paper in usable:
        text = str(paper["text"])
        for phrase in PHRASES:
            frequencies[phrase] += text.count(phrase)
    for phrase, count in frequencies.most_common(25):
        if count:
            print(f"  {phrase:<8} {count}")

    sentence_lengths: list[int] = []
    for paper in usable:
        for sentence in re.split(r"[。！？；]", str(paper["text"])):
            length = len(re.findall(r"[\u4e00-\u9fff]", sentence))
            if length >= 8:
                sentence_lengths.append(length)
    print("\n== 句长（汉字，按。！？；切分）==")
    if sentence_lengths:
        print(
            f"  句子数 {len(sentence_lengths)}；中位 "
            f"{_percentile(sentence_lengths, 0.5)}；75分位 "
            f"{_percentile(sentence_lengths, 0.75)}；90分位 "
            f"{_percentile(sentence_lengths, 0.9)}"
        )


def cmd_grep(
    papers: list[dict[str, object]],
    pattern: str,
    limit: int,
    where: str,
) -> None:
    matched = 0
    for paper in usable_papers(papers):
        pages = paper.get("pages", str(paper["text"]).split("\f"))
        if where == "abstract":
            raw = str(paper["text"])
            start = re.search(r"摘\s*要", raw)
            page_no = raw[:start.start()].count("\f") + 1 if start else 1
            segments = [(page_no, abstract_of(raw))]
        else:
            segments = list(enumerate(pages, 1))
        for page_no, source in segments:
            for sentence in re.split(r"[。！？；]", str(source)):
                sentence = normalize(sentence)
                if len(sentence) < 12 or pattern not in sentence:
                    continue
                at = sentence.find(pattern)
                begin = max(0, at - 80)
                excerpt = ("…" if begin else "") + sentence[begin:begin + 220]
                location = f"PDF abstract start p.{page_no}" if where == "abstract" else f"PDF p.{page_no}"
                print(f"[{paper['year']} {paper['file']} | {paper['backend']} | {location}] {excerpt}")
                matched += 1
                if matched >= limit:
                    return
    if matched == 0:
        print("无匹配。")


def cmd_abstract(papers: list[dict[str, object]], substring: str) -> None:
    matches = [p for p in papers if substring.casefold() in str(p["file"]).casefold()]
    if len(matches) != 1:
        raise RuntimeError(f"摘要选择必须唯一，命中 {len(matches)} 篇：{substring}")
    for paper in matches:
            abstract = abstract_of(str(paper["text"]))
            if not abstract:
                abstract = "（未提取到摘要：可能为扫描版或损坏 PDF。）"
            raw = str(paper["text"])
            start = re.search(r"摘\s*要", raw)
            page_no = raw[:start.start()].count("\f") + 1 if start else None
            bounded = bool(start and re.search(r"关\s*键\s*[词字]\s*[:：]|^[ \t]*关\s*键\s*[词字][ \t]*$", raw[start.end():], re.M))
            print(f"[{paper['year']} {paper['file']} | {paper['backend']} | PDF start p.{page_no} | full-text-gate={paper.get('usable', 'UNKNOWN')}]")
            if not bounded:
                print("未定位关键词结束边界；以下可能只是截取片段，不能当作完整摘要。")
            print(abstract)
            return
    print(f"未找到文件名包含“{substring}”的论文。先用 --list 查看文件名。")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="国赛优秀论文语言语料检索")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--list", action="store_true", help="列出语料与解析状态")
    actions.add_argument("--stats", action="store_true", help="输出语言画像统计")
    actions.add_argument("--grep", metavar="文本", help="检索包含该文本的句子")
    actions.add_argument("--abstract", metavar="文件名片段", help="打印某篇摘要")
    parser.add_argument(
        "--backend",
        choices=("auto", "pdftotext", "pypdf"),
        default="auto",
        help="抽取后端；auto 优先 Poppler 并回退到 pypdf",
    )
    parser.add_argument(
        "--corpus",
        type=Path,
        help="语料目录；优先本参数，其次 GUOSAI_CORPUS，最后 ~/guosai-corpus",
    )
    parser.add_argument(
        "--where",
        choices=("full", "abstract"),
        default="full",
        help="grep 范围",
    )
    parser.add_argument("--limit", type=int, default=10, help="grep 最多输出条数")
    parser.add_argument("--paper", action="append", default=[], help="先按唯一文件名/相对路径选择论文再抽取，可重复")
    return parser


def main(argv: list[str] | None = None) -> int:
    ensure_utf8()
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.limit < 1:
        parser.error("--limit 必须大于 0")
    if not any((args.list, args.stats, args.grep, args.abstract)):
        parser.print_help()
        return 0
    if args.abstract and args.paper:
        parser.error("--abstract 已选择论文，不同时使用 --paper")

    corpus = args.corpus
    if corpus is None:
        corpus = Path(os.environ.get("GUOSAI_CORPUS", str(DEFAULT_CORPUS)))
    try:
        paths = inventory(corpus)
        selectors = [args.abstract] if args.abstract else args.paper
        if selectors:
            paths = select_paths(paths, selectors, corpus)
        if args.list:
            for path in paths:
                print(path.relative_to(corpus).as_posix())
            print(f"共 {len(paths)} 篇；仅文件清单，未抽取/核验文本。解析统计请用 --stats。")
            return 0
        papers = load_papers(corpus, args.backend, paths)
        for paper in papers:
            for error in paper.get("extraction_errors", []):
                print(f"[抽取提示 {paper['file']}] {error}", file=sys.stderr)
    except (RuntimeError, OSError) as error:
        parser.error(str(error))

    if args.list:
        cmd_list(papers)
    elif args.stats:
        cmd_stats(papers, args.backend)
    elif args.grep:
        cmd_grep(papers, args.grep, args.limit, args.where)
    elif args.abstract:
        cmd_abstract(papers, str(papers[0]["file"]))
    else:
        parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
