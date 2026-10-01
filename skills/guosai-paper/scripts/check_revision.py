#!/usr/bin/env python3
"""只读比较原稿/改稿的保护项；差异须复核，零差异不证明语义相同。"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

MAX_BYTES = 5 * 1024 * 1024
MATH = re.compile(r"\$\$[\s\S]*?\$\$|\$(?:\\.|[^$])*\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|\\begin\{(equation\*?|align\*?|gather\*?)\}[\s\S]*?\\end\{\1\}")
REFERENCE = re.compile(r"\\(?:cite[pt]?|ref|eqref|autoref|[cC]ref|label)\*?(?:\[[^\]]*\])?\{[^{}]*\}")
NUMBER = re.compile(r"(?<![A-Za-z0-9_])[-+−]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][-+]?\d+)?(?:\\?[%％])?(?![A-Za-z0-9_])")
QUANTITY = re.compile(r"(?<![A-Za-z0-9_])[-+−]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][-+]?\d+)?\s*(?:\\[,;!:]|\s)*\s*(?:个百分点|万元|千米|小时|分钟|摄氏度|km|kg|ms|元|米|秒|吨|℃|s|m|g)(?![A-Za-z])")
IDENTIFIER = re.compile(r"\b(?:TIME(?:\\_|\s+|_)?LIMIT|OPTIMAL|INFEASIBLE|UNBOUNDED)\b|[\w\u4e00-\u9fff.\\/-]+\.(?:csv|xlsx|json|pdf|png|tex|py)\b")
SYMBOL = re.compile(r"<=|>=|!=|≤|≥|≠|<|>|=")


def compact(token: str) -> str:
    token = token.replace("−", "-").replace("％", "%").replace(r"\%", "%").replace(r"\_", "_")
    token = re.sub(r"\\[,;!:]", "", token)
    return re.sub(r"\s+", "", token)


def protected_items(text: str) -> dict[str, Counter]:
    # A conservative token screen: all differences stay visible, including harmless edits.
    return {
        "math": Counter(compact(m.group(0)) for m in MATH.finditer(text)),
        "references": Counter(compact(m.group(0)) for m in REFERENCE.finditer(text)),
        "numbers": Counter(compact(m.group(0)) for m in NUMBER.finditer(text)),
        "quantities": Counter(compact(m.group(0)) for m in QUANTITY.finditer(text)),
        "identifiers": Counter(compact(m.group(0)) for m in IDENTIFIER.finditer(text)),
        "relation_symbols": Counter(m.group(0) for m in SYMBOL.finditer(text)),
    }


def compare_texts(before: str, after: str) -> dict:
    left, right = protected_items(before), protected_items(after)
    changes = {}
    for kind in left:
        removed, added = left[kind] - right[kind], right[kind] - left[kind]
        if removed or added:
            changes[kind] = {"removed": dict(removed), "added": dict(added)}
    return {
        "status": "REVIEW_CHANGES" if changes else "NO_TOKEN_DIFFERENCE",
        "changes": changes,
        "verification_boundary": "Token multisets only. Same tokens can have swapped subjects, directions, conditions or negation. No mathematical or semantic verification.",
    }


def read_text(path: Path) -> str:
    with path.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError(f"file exceeds {MAX_BYTES} bytes: {path}")
    return data.decode("utf-8-sig")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--strict", action="store_true", help="有保护项差异时返回 2，差异仍须人工裁决。")
    args = parser.parse_args(argv)
    try:
        result = compare_texts(read_text(args.before), read_text(args.after))
    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if args.strict and result["changes"] else 0


if __name__ == "__main__":
    sys.exit(main())
