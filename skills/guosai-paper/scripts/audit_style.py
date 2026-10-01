#!/usr/bin/env python3
"""只读中文论文启发式审校；报告复核线索，不认证证据或结论。"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys

SEVERITY_RANK = {"BLOCKER": 0, "MAJOR": 1, "MINOR": 2}
MAX_BYTES = 5 * 1024 * 1024
PLACEHOLDER_PATTERN = re.compile(r"\[(?:待填|待补|待核验)[^\]]*\]|\b(?i:TODO|TBD)\b|\?{2,}|(?:图|表|式|章节)\s*[Xx?]+(?![A-Za-z])")
STRONG_CLAIM_PATTERN = re.compile(r"显著(?:提升|提高|降低|优于|改善|增加|减少)|精准(?:预测|识别|求解)?|精确无误|最优模型|充分证明|充分说明|普适性强|泛化能力强|科学性强|推广性(?:很|较)?强|鲁棒性(?:很|较)?强|优越性|高效的?(?:智能)?(?:优化)?算法"
                                  # Chinese also fronts the adjective: 较强的鲁棒性 / 很强的推广性.
                                  r"|(?:很|较)强的?(?:鲁棒性|推广性|泛化能力|适应性|稳定性)")
VAGUE_VALIDATION_PATTERN = re.compile(r"(?:验证|证明).{0,12}(?:科学性|合理性)|(?:科学|合理)(?:性)?(?:得到|得以)?验证")
CAUSAL_OVERCLAIM_PATTERN = re.compile(r"(?:证明|验证|表明|说明).{0,18}(?:因果关系|因果效应)")
CAUSAL_IDENTIFICATION_PATTERN = re.compile(r"随机(?:试验|分配|对照)|干预|工具变量|断点回归|双重差分|识别假设|混杂控制|倾向得分|do\s*\(", re.I)
CORRELATION_TO_CAUSATION_PATTERN = re.compile(
    # A correlational FINDING, never a bare 相关X noun phrase such as 相关参数/相关文献.
    r"(?:正相关|负相关|(?:显著|高度|线性|密切|强|弱)相关|相关系数|相关性(?:较|很)?(?:强|高|显著)|存在相关|拟合优度|趋势一致|变化一致)[^。！？；不未无非]{0,30}(?:因此|从而|可见|所以|说明|[，,]\s*故)[^。！？；不未无非]{0,30}(?:导致|引起|提升|提高|降低|减少|带来|使得|促进|因果关系|因果效应)")
INFERENCE_PATTERN = re.compile(r"结果表明|结果显示|由\s*(?:图|表|式)[0-9一二三四五六七八九十.\s（）()]*可知|由此可知|可以看出|这说明|这表明|验证了|说明了|表明了|证实了")
EVIDENCE_PATTERN = re.compile(r"\bREF\b|(?:图|表|式)\s*[（(]?\d|(?:误差|残差|目标值|间隙|置信区间|预测区间)[^。！？；]{0,16}\d|(?:由|为|至|降低|增加)\s*[-+]?\d+(?:\.\d+)?\s*(?:\\?%|％|元|万元|s\b|秒|米|m\b|个百分点)|p\s*[<=>]\s*\d|R\s*[²2^]+\s*[<=>]\s*\d|[\d一二三四五六七八九十百千两]+\s*(?:次|期|轮|个|条|组|类|种|台|站|例|篇|天|月|年)", re.I)
METRIC_PATTERN = re.compile(r"MAE|MAPE|RMSE|MSE|AUC|F1|准确率|准确性|误差|成本|目标值|覆盖率|运行时间|训练时间|收益|损失|间隙", re.I)
COMPARISON_PATTERN = re.compile(r"基线|对照|相比|比较|从.+到|由.+(?:至|为)")
IMPROVEMENT_CLAIM_PATTERN = re.compile(r"改进|优于|更快|更强|更好|提升")
# Guard: 提升 is also a physical lift and 改进 can describe notation, so an improvement
# claim only counts when the sentence is actually about a method or a metric.
IMPROVEMENT_SUBJECT_PATTERN = re.compile(r"算法|模型|方法|方案|策略|求解|性能|精度|效率|准确|误差|成本|收敛")
# Descriptive, not comparative: 改进之处在于…… states the change, claims no gain.
IMPROVEMENT_DESCRIPTIVE_PATTERN = re.compile(r"改进(?:之处|的地方)?在于|改动在于|区别在于|不同之处在于")
COLLOQUIAL_PATTERN = re.compile(r"我们可以看到|大家可以看到|很明显|显而易见|不难看出|搞清楚|弄清楚|效果非常好|非常优秀|效果(?:很|较)好|(?:采用|使用|运用|应用)了?多种(?:算法|方法|模型)")
METHOD_PATTERN = re.compile(r"(?:(?:[A-Za-z][A-Za-z0-9+\-]*)|(?:[\u4e00-\u9fff]{2,10}))(?:算法|模型|方法)")
SEQUENCE_PATTERN = re.compile(r"首先|其次|然后|接着|随后|最后")
NEGATION = re.compile(r"(?:(?:不能|无法|未能|不足以|尚未|并非|不应|不宜|没有|未进行|不代表|不支持|不构成).{0,12}|未(?!来)[^，,。；]{0,8}|[不未]\s*)$")
OPTIMALITY_PATTERN = re.compile(r"全局最优|精确最优")
TERM_QUESTION_PATTERNS = (re.compile(r"问题[一二三四五六七八九十0-9]+"), re.compile(r"第[一二三四五六七八九十0-9]+问(?!题)"))


@dataclass(frozen=True)
class Issue:
    severity: str
    rule: str
    line: int
    message: str
    excerpt: str


def _mask(match):
    return re.sub(r"[^\n]", " ", match.group(0))


def _without_comment(line: str) -> str:
    for match in re.finditer("%", line):
        before = line[:match.start()]
        slashes = len(before) - len(before.rstrip("\\"))
        if slashes % 2 == 0:
            return before + " " * (len(line) - match.start())
    return line


def clean_document(text: str, input_format: str = "markdown") -> str:
    # Mask excluded regions instead of deleting lines, preserving source locations.
    text = re.sub(r"(?ms)^[ \t]*(\x60{3,}|~{3,})[^\n]*\n.*?^[ \t]*\1[ \t]*$", _mask, text)
    text = re.sub(r"\\begin\{(verbatim\*?|lstlisting|minted|comment)\}[\s\S]*?\\end\{\1\}", _mask, text)
    text = re.sub(r"\x60[^\x60\n]+\x60", _mask, text)
    if input_format == "latex":
        text = "\n".join(_without_comment(line) for line in text.split("\n"))
    return text


def _strip_latex_and_markdown(text: str) -> str:
    text = re.sub(r"\$\$[\s\S]*?\$\$|\$(?:\\.|[^$])*\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)",
                  lambda m: " MATH " + " ".join(re.findall(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", m.group(0))) + " ", text)
    text = re.sub(r"\\(?:cite[pt]?|ref|eqref|autoref|cref|Cref)\*?(?:\[[^\]]*\])?\{[^{}]*\}", " REF ", text)
    text = re.sub(r"\\(?:label|input|include|includegraphics|bibliography)\*?(?:\[[^\]]*\])?\{[^{}]*\}", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", text)
    text = re.sub(r"[{}#*_>~]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _paragraphs(text: str) -> list[tuple[int, str]]:
    result, buffer = [], []
    start_line = 1

    def flush():
        if buffer:
            cleaned = _strip_latex_and_markdown(" ".join(buffer))
            if cleaned:
                result.append((start_line, cleaned))
            buffer.clear()

    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        heading = re.match(r"^(?:#{1,6}\s+|\\(?:part|chapter|section|subsection|subsubsection)\*?\{|[一二三四五六七八九十]+、)", line)
        if not line or heading:
            flush()
            if heading:
                result.append((line_no, _strip_latex_and_markdown(line)))
            continue
        if not buffer:
            start_line = line_no
        buffer.append(line)
    flush()
    return result


def _sentences(paragraph: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[。！？；])", paragraph) if part.strip()]


def _affirmed(pattern, sentence: str) -> bool:
    for match in pattern.finditer(sentence):
        prefix = re.split(r"[，,。！？；;]", sentence[:match.start()])[-1]
        if not NEGATION.search(prefix):
            return True
    return False


def _han_length(text):
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def _excerpt(text, limit=100):
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[:limit - 1] + "…"


def _add(issues, severity, rule, line, message, excerpt):
    item = Issue(severity, rule, line, message, _excerpt(excerpt))
    if item not in issues:
        issues.append(item)


# Off by default: a half-width mark directly touching a Chinese character is a real
# defect in a Chinese paper, but flagging it during drafting is noise. Parentheses are
# excluded on purpose — half-width parens around ASCII such as (MILP) are defensible.
HALFWIDTH_NEXT_TO_HAN = re.compile(r"[一-鿿][,;:?!]|[,;:?!][一-鿿]")


def audit_text(text: str, max_han: int = 80, input_format: str = "markdown",
               abstract_kind: str = "auto", check_punctuation: bool = False) -> list[Issue]:
    """Return review candidates. Nearby cues never certify evidence."""
    issues = []
    cleaned = clean_document(text, input_format)
    for match in PLACEHOLDER_PATTERN.finditer(cleaned):
        _add(issues, "BLOCKER", "unfinished-placeholder", cleaned[:match.start()].count("\n") + 1,
             "发现显式未完成标记；是否允许保留取决于草稿/终稿范围。", match.group(0))
    starts = []
    for line_no, paragraph in _paragraphs(cleaned):
        if len(METHOD_PATTERN.findall(paragraph)) >= 4:
            _add(issues, "MINOR", "method-stacking", line_no, "检查方法是否各有实际角色；不要按名称数量机械删改。", paragraph)
        if len(SEQUENCE_PATTERN.findall(paragraph)) >= 5:
            _add(issues, "MINOR", "sequence-marker-overuse", line_no, "流程词密集，检查能否改为必要的条件、目的或承接关系。", paragraph)
        for sentence in _sentences(paragraph):
            if _affirmed(VAGUE_VALIDATION_PATTERN, sentence):
                _add(issues, "MAJOR", "vague-validation", line_no, "核对该检验具体支持什么；科学性/合理性不是可直接检验的指标。", sentence)
            if _affirmed(CAUSAL_OVERCLAIM_PATTERN, sentence):
                design = _affirmed(CAUSAL_IDENTIFICATION_PATTERN, sentence)
                _add(issues, "MINOR" if design else "MAJOR",
                     "causal-identification-review" if design else "causal-overclaim", line_no,
                     "因果主张需人工追溯识别设计与假设；出现方法名不表示识别成立。", sentence)
            if _affirmed(CORRELATION_TO_CAUSATION_PATTERN, sentence) and not CAUSAL_IDENTIFICATION_PATTERN.search(sentence):
                _add(issues, "MAJOR", "correlation-to-causation", line_no,
                     "由相关直接推出因果；核对是否存在识别设计与假设，若没有则降格为关联或预测关系。", sentence)
            if _affirmed(STRONG_CLAIM_PATTERN, sentence):
                cue = bool(METRIC_PATTERN.search(sentence) and COMPARISON_PATTERN.search(sentence)
                           and re.search(r"\d|\bREF\b", sentence))
                _add(issues, "MINOR" if cue else "MAJOR",
                     "strong-claim-evidence-review" if cue else "unsupported-strong-claim", line_no,
                     "核对比较协议、主指标、波动与主张强度；数字或图表只能作为复核入口。", sentence)
            if _affirmed(OPTIMALITY_PATTERN, sentence):
                limited = bool(re.search(r"TIME.{0,4}LIMIT|达到时限|时限终止|未收敛", paragraph, re.I))
                _add(issues, "MAJOR" if limited else "MINOR", "optimality-claim-review", line_no,
                     "核对全局最优证书、求解状态和界；有可行解或目标值不等于已证明最优。", sentence)
            if _affirmed(INFERENCE_PATTERN, sentence) and not EVIDENCE_PATTERN.search(sentence):
                _add(issues, "MAJOR", "evidence-free-inference", line_no,
                     "本句未见可定位依据；先查上下文/原结果，不能靠另一句的任意数字免检。", sentence)
            if (_affirmed(IMPROVEMENT_CLAIM_PATTERN, sentence)
                    and IMPROVEMENT_SUBJECT_PATTERN.search(sentence)
                    and not IMPROVEMENT_DESCRIPTIVE_PATTERN.search(sentence)
                    and not re.search(r"\d|\bREF\b", sentence)
                    and not COMPARISON_PATTERN.search(sentence)):
                _add(issues, "MINOR", "unbaselined-improvement", line_no,
                     "改进主张未见比较对象与量化差异；补出基线、指标与数值，或改写为中性描述。", sentence)
            if _affirmed(COLLOQUIAL_PATTERN, sentence):
                _add(issues, "MINOR", "colloquial-or-vague", line_no, "直接写观察或判断，删去不携带信息的显然性措辞。", sentence)
            if check_punctuation:
                mixed = HALFWIDTH_NEXT_TO_HAN.search(sentence)
                if mixed:
                    _add(issues, "MINOR", "punctuation-mixing", line_no,
                         f"半角标点“{mixed.group(0)}”紧邻汉字；中文正文统一用全角，公式与纯英文片段除外。", sentence)
            if _han_length(sentence) > max_han:
                _add(issues, "MINOR", "long-sentence", line_no,
                     f"句子含 {_han_length(sentence)} 个汉字（阈值 {max_han}）；仅在层次不清时拆分。", sentence)
            han = "".join(re.findall(r"[\u4e00-\u9fff]", sentence))
            if len(han) >= 12:
                starts.append((line_no, han[:4], sentence))
        if paragraph.count("本文") >= 2 and paragraph.count("我们") >= 2:
            _add(issues, "MINOR", "voice-inconsistency", line_no, "同段主语多次切换，核对指代；不要求全篇禁用某个主语。", paragraph)

    counts = Counter(prefix for _, prefix, _ in starts if prefix != "针对问题")
    for prefix, count in counts.items():
        if count >= 5 and count / max(len(starts), 1) >= 0.08:
            line_no, _, sentence = next(item for item in starts if item[1] == prefix)
            _add(issues, "MINOR", "repeated-sentence-start", line_no, f"至少 {count} 句起始相同；检查是否存在无信息重复。", sentence)

    forms = [pattern.findall(cleaned) for pattern in TERM_QUESTION_PATTERNS]
    if all(len(form) >= 3 for form in forms):
        first = min((pattern.search(cleaned) for pattern in TERM_QUESTION_PATTERNS), key=lambda m: m.start())
        _add(issues, "MINOR", "terminology-inconsistency", cleaned[:first.start()].count("\n") + 1,
             f"同一对象混用两种称谓：“问题N”{len(forms[0])} 次，“第N问”{len(forms[1])} 次；全文统一其中一种。",
             cleaned[first.start():first.start() + 40])

    # Several official CUMCM templates set the abstract with \section*{摘要} rather than
    # an abstract environment; without this anchor the highest-weight section is skipped.
    match = re.search(
        r"\\begin\{abstract\}(?P<latex>[\s\S]*?)\\end\{abstract\}"
        r"|\\(?:sub)?section\*?\{\s*摘\s*要\s*\}(?P<heading>[\s\S]*?)(?:关\s*键\s*[词字]|\\(?:sub)?section)"
        r"|摘\s*要[:：]?(?P<plain>[\s\S]*?)(?:关\s*键\s*[词字])", cleaned)
    if match:
        abstract = _strip_latex_and_markdown(
            match.group("latex") or match.group("heading") or match.group("plain") or "")
        line = cleaned[:match.start()].count("\n") + 1
        result_text = re.sub(r"问题\s*(?:[一二三四五六七八九十]+|\d+)", "", abstract)
        if not re.search(r"\d", result_text) and abstract_kind != "qualitative":
            _add(issues, "MAJOR" if abstract_kind == "quantitative" else "MINOR",
                 "abstract-without-quantitative-result" if abstract_kind == "quantitative" else "abstract-result-review",
                 line, "检查是否遗漏决定性结果；定性、证明或反例任务不应为满足模板强加数字。", abstract)
    return sorted(issues, key=lambda i: (SEVERITY_RANK[i.severity], i.line, i.rule))


def render_markdown(path, text, issues, max_han):
    counts = Counter(i.severity for i in issues)
    lines = ["# 国赛论文语言审校线索", "",
             f"- 文件：{path}",
             f"- 待人工复核：BLOCKER {counts['BLOCKER']}，MAJOR {counts['MAJOR']}，MINOR {counts['MINOR']}",
             f"- 句长提醒阈值：{max_han} 个汉字",
             "- 零命中仅表示未触发这些规则；不证明表达优秀、证据充分或可以提交。",
             "- 位置通常为段落起始行；显式占位符给出其实际所在行。", "",
             "| 行 | 级别 | 规则 | 复核点 | 片段 |", "|---:|---|---|---|---|"]
    for issue in issues:
        values = [str(issue.line), issue.severity, issue.rule, issue.message, issue.excerpt]
        lines.append("| " + " | ".join(v.replace("|", r"\|") for v in values) + " |")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--input-format", choices=("auto", "markdown", "text", "latex"), default="auto")
    parser.add_argument("--abstract-kind", choices=("auto", "quantitative", "qualitative"), default="auto")
    parser.add_argument("--check-punctuation", action="store_true",
                        help="额外报告紧邻汉字的半角标点；默认关闭，起草阶段属噪声。")
    parser.add_argument("--max-han", type=int, default=80)
    parser.add_argument("--strict", action="store_true", help="存在 BLOCKER/MAJOR 候选时返回 2，不表示候选已经确认。")
    args = parser.parse_args(argv)
    if args.max_han < 20:
        parser.error("--max-han must be at least 20")
    try:
        with args.path.open("rb") as stream:
            data = stream.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError(f"file exceeds {MAX_BYTES} bytes")
        text = data.decode("utf-8-sig")
    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))
    input_format = args.input_format
    if input_format == "auto":
        input_format = "latex" if args.path.suffix.lower() == ".tex" else "markdown"
    issues = audit_text(text, args.max_han, input_format, args.abstract_kind, args.check_punctuation)
    if args.format == "json":
        print(json.dumps({"file": str(args.path), "max_han": args.max_han, "input_format": input_format,
                          "counts": dict(Counter(i.severity for i in issues)),
                          "issues": [asdict(i) for i in issues],
                          "verification_boundary": "Heuristic review candidates only; evidence, mathematics, code and claim truth were not verified."},
                         ensure_ascii=False, indent=2))
    else:
        print(render_markdown(args.path, text, issues, args.max_han), end="")
    return 2 if args.strict and any(i.severity in {"BLOCKER", "MAJOR"} for i in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
