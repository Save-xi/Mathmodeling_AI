"""只读离线锚点索引：不联网、不安装、不写文件、不评分。"""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

DEFAULT_CATALOG = Path(__file__).resolve().parents[1] / "references" / "algorithm-anchors.json"
MAX_BYTES = 512 * 1024
PUBLICATION_STATES = {"PEER_REVIEWED", "ACCEPTED", "PREPRINT", "WORKSHOP", "UNDER_REVIEW", "SOFTWARE_RELEASE", "OFFICIAL_DOCS"}


class CatalogError(ValueError):
    pass


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise CatalogError(f"{label}: expected non-empty text")
    return value


def text_list(value, label):
    if not isinstance(value, list) or not value:
        raise CatalogError(f"{label}: expected non-empty list")
    for item in value:
        nonempty(item, label)
    return value


def check_date(value, label):
    try:
        return date.fromisoformat(nonempty(value, label))
    except ValueError as error:
        raise CatalogError(f"{label}: invalid ISO date") from error


def check_url(value, label):
    try:
        parsed = urlsplit(nonempty(value, label))
    except ValueError as error:
        raise CatalogError(f"{label}: malformed source URL") from error
    if parsed.scheme != "https" or not parsed.netloc:
        raise CatalogError(f"{label}: expected HTTPS source URL")


def index(items, label):
    if not isinstance(items, list) or not items:
        raise CatalogError(f"{label}: expected non-empty list")
    result = {}
    for item in items:
        if not isinstance(item, dict):
            raise CatalogError(f"{label}: entry must be an object")
        key = nonempty(item.get("id"), f"{label}.id")
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", key):
            raise CatalogError(f"{label}: invalid ID {key!r}")
        if key in result:
            raise CatalogError(f"{label}: duplicate ID {key!r}")
        result[key] = item
    return result


def validate_catalog(document):
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        raise CatalogError("catalog schema_version must equal 1")
    nonempty(document.get("release_id"), "release_id")
    prepared = check_date(document.get("prepared_on"), "prepared_on")
    if document.get("status") != "PREPARED":
        raise CatalogError("catalog status must be PREPARED, not a task ranking")
    for field in ("evidence_basis", "coverage_boundary", "resource_boundary", "reuse_rule"):
        nonempty(document.get(field), field)
    sources = index(document.get("evidence"), "evidence")
    for key, item in sources.items():
        for field in ("title", "author_label", "venue", "read_scope", "source_finding", "license_note"):
            nonempty(item.get(field), f"{key}.{field}")
        if type(item.get("year")) is not int or not 1600 <= item["year"] <= prepared.year:
            raise CatalogError(f"{key}: invalid year")
        verified = check_date(item.get("verified_on"), f"{key}.verified_on")
        if verified > prepared:
            raise CatalogError(f"{key}: verification later than release")
        if item.get("publication_status") not in PUBLICATION_STATES:
            raise CatalogError(f"{key}: invalid publication status")
        check_url(item.get("primary_url"), f"{key}.primary_url")
        if not isinstance(item.get("supporting_urls"), list):
            raise CatalogError(f"{key}: supporting_urls must be a list")
        for url in item["supporting_urls"]:
            check_url(url, f"{key}.supporting_urls")
        if item.get("implementation_url") is not None:
            check_url(item["implementation_url"], f"{key}.implementation_url")
        if item.get("implementation_status") not in {"PAGE_CHECKED", "NOT_CHECKED"}:
            raise CatalogError(f"{key}: invalid implementation status")
        if item["implementation_status"] == "PAGE_CHECKED" and not item.get("implementation_url"):
            raise CatalogError(f"{key}: checked implementation has no URL")
        # The catalog stores literature readiness only. Actual run evidence belongs to a project/experiment.
        if item.get("local_smoke") != "NOT_RUN" or item.get("task_validation") != "NOT_RUN":
            raise CatalogError(f"{key}: use a separate evidenced run record for local/task readiness")
    routes = index(document.get("routes"), "routes")
    aliases = {}
    for key, item in routes.items():
        for field in ("title", "signals", "baseline", "module_contract", "minimal_validation", "implementation_caution"):
            nonempty(item.get(field), f"{key}.{field}")
        for field in ("aliases", "conditional_upgrades", "reject_conditions", "evidence_ids", "gap_queries"):
            text_list(item.get(field), f"{key}.{field}")
        if len(set(item["evidence_ids"])) != len(item["evidence_ids"]):
            raise CatalogError(f"{key}: duplicate evidence reference")
        missing = set(item["evidence_ids"]) - sources.keys()
        if missing:
            raise CatalogError(f"{key}: unknown evidence IDs {sorted(missing)}")
        if item.get("family_status") != "PREPARED" or item.get("task_fit") != "NOT_EVALUATED":
            raise CatalogError(f"{key}: family preparation must not assert task fit")
        for alias in [key, *item["aliases"]]:
            normalized = alias.strip().casefold()
            if normalized in aliases and aliases[normalized] != key:
                raise CatalogError(f"ambiguous task alias {alias!r}")
            aliases[normalized] = key
    return document


def load_catalog(path=DEFAULT_CATALOG):
    try:
        with Path(path).open("rb") as stream:
            data = stream.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise CatalogError(f"catalog exceeds {MAX_BYTES} bytes")
        document = json.loads(data.decode("utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise CatalogError(f"Cannot read catalog {path}: {error}") from error
    return validate_catalog(document)


def select_routes(document, tasks):
    if not 1 <= len(tasks) <= 3:
        raise CatalogError("Select one to three task routes; use --list to inspect the index")
    aliases = {alias.strip().casefold(): item for item in document["routes"] for alias in [item["id"], *item["aliases"]]}
    selected = {}
    for task in tasks:
        normalized = task.strip().casefold()
        if normalized not in aliases:
            raise CatalogError(f"Unknown task {task!r}; use --list. No all-catalog fallback was performed")
        route = aliases[normalized]
        selected[route["id"]] = route
    needed = {key for route in selected.values() for key in route["evidence_ids"]}
    return {**{key: document[key] for key in ("release_id", "prepared_on", "status", "coverage_boundary", "resource_boundary", "reuse_rule")},
            "retrieval_mode": "OFFLINE_ANCHOR_MATCH", "network_performed": False,
            "routes": list(selected.values()),
            "evidence": [item for item in document["evidence"] if item["id"] in needed]}


def render_markdown(result):
    lines = [f"# {result['release_id']}：离线锚点匹配", "",
             f"资料核验截止：{result['prepared_on']}；本次未联网。PREPARED 是资料准备，不是本机/本题验证。", ""]
    for item in result["routes"]:
        lines += [f"## {item['id']} — {item['title']}", "", f"适配信号：{item['signals']}", "",
                  f"基线：{item['baseline']}", "", f"接口：{item['module_contract']}", "", "条件升级：", ""]
        lines += [f"- {value}" for value in item["conditional_upgrades"]]
        lines += ["", "淘汰/降级条件：", ""] + [f"- {value}" for value in item["reject_conditions"]]
        lines += ["", f"最小验证：{item['minimal_validation']}", "", f"实现准备：{item['implementation_caution']}", "", "只在有缺口时使用：", ""]
        lines += [f"- `{query}`" for query in item["gap_queries"]]
        lines += ["", "证据 IDs：" + ", ".join(item["evidence_ids"]), ""]
    lines += ["## 仅所选路线的证据", ""]
    for item in result["evidence"]:
        lines += [f"- **{item['id']}** — [{item['title']}]({item['primary_url']})，{item['year']}，{item['publication_status']}。",
                  f"  {item['author_label']}；{item['venue']}。核验 {item['verified_on']}；阅读：{item['read_scope']}。",
                  f"  资料内容：{item['source_finding']}"]
        if item.get("version_note"):
            lines += [f"  版本边界：{item['version_note']}"]
        lines += [f"  本机试跑/本题验证：{item['local_smoke']}/{item['task_validation']}；实现页：{item['implementation_status']}；许可：{item['license_note']}"]
        if item.get("implementation_url"):
            lines += [f"  [实现入口]({item['implementation_url']})"]
        if item["supporting_urls"]:
            lines += ["  补充核验：" + "、".join(f"[来源 {i}]({url})" for i, url in enumerate(item["supporting_urls"], 1))]
        lines += [""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--list", action="store_true", help="只列任务路线")
    choice.add_argument("--check", action="store_true", help="检查目录内部一致性")
    choice.add_argument("--task", action="append", help="route ID 或确切别名；最多三个，可重复参数")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args(argv)
    try:
        document = load_catalog(args.catalog)
        if args.check:
            result = dict(check="CATALOG_CONSISTENCY_ONLY", release_id=document["release_id"],
                          routes=len(document["routes"]), evidence=len(document["evidence"]), network_performed=False)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.list:
            items = [{key: item[key] for key in ("id", "title", "aliases")} for item in document["routes"]]
            if args.format == "json":
                print(json.dumps(dict(release_id=document["release_id"], prepared_on=document["prepared_on"], routes=items), ensure_ascii=False, indent=2))
            else:
                print(f"资料库 {document['release_id']}；先按原题条件选择路线。\n\n| ID | 任务 |\n|---|---|")
                for item in items:
                    print(f"| {item['id']} | {item['title']} |")
        else:
            result = select_routes(document, args.task)
            print(json.dumps(result, ensure_ascii=False, indent=2) if args.format == "json" else render_markdown(result))
    except CatalogError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
