#!/usr/bin/env python3
"""Validate and rank literature-backed frontier candidates.

The script enforces the schema-v2 links between a frozen/provisional problem
contract, baselines, evidence records, and candidate deltas. It never searches
the web or decides whether a paper, model, equation, or experiment is correct.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


BENEFIT_WEIGHTS = {
    "mechanism_fit": 0.23,
    "data_fit": 0.16,
    "validation_strength": 0.17,
    "reproducibility": 0.13,
    "explainability": 0.11,
    "compute_fit": 0.10,
    "novelty": 0.10,
}

RISK_WEIGHTS = {
    "assumption_risk": 0.40,
    "implementation_risk": 0.30,
    "evidence_risk": 0.30,
}

STATUS_ORDER = {"PRIMARY": 0, "BACKUP": 1, "WATCH": 2, "REJECT": 3}
CONTRACT_STATUSES = {"FROZEN", "PROVISIONAL"}
PUBLICATION_STATUSES = {
    "PEER_REVIEWED",
    "ACCEPTED",
    "PREPRINT",
    "WORKSHOP",
    "UNDER_REVIEW",
    "OTHER",
}
CODE_STATUSES = {"AVAILABLE", "UNAVAILABLE", "UNKNOWN"}
COMPUTE_STATUSES = {"REPORTED", "PARTIAL", "UNREPORTED", "UNKNOWN"}
FEASIBILITY_STATUSES = {"PASS", "FAIL", "UNKNOWN"}
RESOURCE_STATUSES = {"AVAILABLE", "UNAVAILABLE", "UNKNOWN"}
FORMAL_PUBLICATION_STATUSES = {"PEER_REVIEWED", "ACCEPTED"}


class MatrixError(ValueError):
    """Raised when the candidate matrix violates the documented schema."""


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MatrixError(f"{field} must be a non-empty string")
    return value.strip()


def _text_list(value: Any, field: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list):
        raise MatrixError(f"{field} must be a list of strings")
    items = [_text(item, f"{field}[{index}]") for index, item in enumerate(value)]
    if not allow_empty and not items:
        raise MatrixError(f"{field} must not be empty")
    if len(set(items)) != len(items):
        raise MatrixError(f"{field} contains duplicate values")
    return items


def _choice(value: Any, field: str, allowed: set[str]) -> str:
    selected = _text(value, field)
    if selected not in allowed:
        raise MatrixError(f"{field} must be one of: {', '.join(sorted(allowed))}")
    return selected


def _iso_datetime(value: Any, field: str) -> str:
    timestamp = _text(value, field)
    try:
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise MatrixError(f"{field} must be an ISO-8601 datetime with UTC offset") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise MatrixError(f"{field} must include a UTC offset")
    return timestamp


def _datetime_value(timestamp: str) -> datetime:
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


def _https_url(value: Any, field: str) -> str:
    url = _text(value, field)
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise MatrixError(f"{field} must be a stable https URL")
    return url


def _score_0_to_5(value: Any, field: str, candidate: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MatrixError(f"{candidate}: {field} must be a number from 0 to 5")
    number = float(value)
    if not math.isfinite(number) or not 0 <= number <= 5:
        raise MatrixError(f"{candidate}: {field} must be a finite number from 0 to 5")
    return number


def _legacy_source_count(value: Any, candidate: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise MatrixError(f"{candidate}: source_count must be a non-negative integer")
    return value


def _validate_search(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise MatrixError("search must be an object")
    searched_at = _iso_datetime(value.get("searched_at"), "search.searched_at")
    cutoff = _iso_datetime(value.get("cutoff"), "search.cutoff")
    if _datetime_value(searched_at) > _datetime_value(cutoff):
        raise MatrixError("search.searched_at must be earlier than or equal to search.cutoff")
    return {
        "searched_at": searched_at,
        "timezone": _text(value.get("timezone"), "search.timezone"),
        "cutoff": cutoff,
        "sites": _text_list(value.get("sites"), "search.sites"),
        "queries": _text_list(value.get("queries"), "search.queries"),
        "failures": _text_list(value.get("failures"), "search.failures", allow_empty=True),
    }


def _validate_baselines(value: Any) -> dict[str, dict[str, str]]:
    if not isinstance(value, list) or not value:
        raise MatrixError("baselines must be a non-empty list")
    baselines: dict[str, dict[str, str]] = {}
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            raise MatrixError(f"baseline {index} must be an object")
        baseline_id = _text(item.get("id"), f"baseline {index}.id")
        if baseline_id in baselines:
            raise MatrixError(f"duplicate baseline id: {baseline_id}")
        baselines[baseline_id] = {
            "id": baseline_id,
            "name": _text(item.get("name"), f"baseline {baseline_id}.name"),
            "defect": _text(item.get("defect"), f"baseline {baseline_id}.defect"),
        }
    return baselines


def _validate_evidence(value: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise MatrixError("evidence must be a non-empty list")
    evidence: dict[str, dict[str, Any]] = {}
    seen_urls: set[str] = set()
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            raise MatrixError(f"evidence {index} must be an object")
        evidence_id = _text(item.get("id"), f"evidence {index}.id")
        if evidence_id in evidence:
            raise MatrixError(f"duplicate evidence id: {evidence_id}")
        primary_url = _https_url(item.get("primary_url"), f"evidence {evidence_id}.primary_url")
        if primary_url in seen_urls:
            raise MatrixError(f"duplicate evidence primary_url: {primary_url}")
        seen_urls.add(primary_url)
        code_status = _choice(
            item.get("code_status"),
            f"evidence {evidence_id}.code_status",
            CODE_STATUSES,
        )
        code_url = item.get("code_url")
        if code_status == "AVAILABLE":
            code_url = _https_url(code_url, f"evidence {evidence_id}.code_url")
        elif code_url is not None:
            code_url = _https_url(code_url, f"evidence {evidence_id}.code_url")
        evidence[evidence_id] = {
            "id": evidence_id,
            "title": _text(item.get("title"), f"evidence {evidence_id}.title"),
            "primary_url": primary_url,
            "publication_status": _choice(
                item.get("publication_status"),
                f"evidence {evidence_id}.publication_status",
                PUBLICATION_STATUSES,
            ),
            "verified_at": _iso_datetime(
                item.get("verified_at"),
                f"evidence {evidence_id}.verified_at",
            ),
            "code_status": code_status,
            "code_url": code_url,
            "compute_status": _choice(
                item.get("compute_status"),
                f"evidence {evidence_id}.compute_status",
                COMPUTE_STATUSES,
            ),
        }
    return evidence


def _hard_failures(
    scores: dict[str, float],
    live_search_verified: bool,
    feasibility_status: str,
    resource_status: str,
) -> list[str]:
    failures: list[str] = []
    if not live_search_verified:
        failures.append("live search not verified")
    if scores["mechanism_fit"] < 3:
        failures.append("mechanism_fit < 3")
    if scores["data_fit"] < 2:
        failures.append("data_fit < 2")
    if scores["validation_strength"] < 2:
        failures.append("validation_strength < 2")
    if scores["evidence_risk"] >= 4:
        failures.append("evidence_risk >= 4")
    if feasibility_status == "FAIL":
        failures.append("feasibility check failed")
    if resource_status == "UNAVAILABLE":
        failures.append("required resources unavailable")
    return failures


def _watch_reasons(
    problem_contract_status: str,
    feasibility_status: str,
    resource_status: str,
    evidence_ids: list[str],
    evidence: dict[str, dict[str, Any]],
) -> list[str]:
    reasons: list[str] = []
    if problem_contract_status == "PROVISIONAL":
        reasons.append("problem contract is provisional")
    if feasibility_status == "UNKNOWN":
        reasons.append("feasibility status unknown")
    if resource_status == "UNKNOWN":
        reasons.append("resource status unknown")
    if len(evidence_ids) < 2:
        reasons.append("fewer than two evidence records")
    if not any(
        evidence[evidence_id]["publication_status"] in FORMAL_PUBLICATION_STATUSES
        for evidence_id in evidence_ids
    ):
        reasons.append("no peer-reviewed or accepted primary source")
    return reasons


def _rank_legacy_matrix(document: dict[str, Any]) -> dict[str, Any]:
    """Keep schema-v1 files executable while forcing an auditable migration."""
    search_date = _text(document.get("search_date"), "search_date")
    try:
        datetime.strptime(search_date, "%Y-%m-%d")
    except ValueError as exc:
        raise MatrixError("search_date must be an ISO date such as 2026-08-26") from exc
    live_search_verified = document.get("live_search_verified")
    if not isinstance(live_search_verified, bool):
        raise MatrixError("live_search_verified must be true or false")
    candidates = document.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise MatrixError("candidates must be a non-empty list")

    ranked: list[dict[str, Any]] = []
    seen_names: set[str] = set()
    for index, candidate in enumerate(candidates, start=1):
        if not isinstance(candidate, dict):
            raise MatrixError(f"candidate {index} must be an object")
        name = _text(candidate.get("name"), f"candidate {index}.name")
        normalized_name = name.casefold()
        if normalized_name in seen_names:
            raise MatrixError(f"duplicate candidate name: {name}")
        seen_names.add(normalized_name)
        scores = {
            field: _score_0_to_5(candidate.get(field), field, name)
            for field in (*BENEFIT_WEIGHTS, *RISK_WEIGHTS)
        }
        source_count = _legacy_source_count(candidate.get("source_count", 0), name)
        benefit = sum(scores[field] * weight for field, weight in BENEFIT_WEIGHTS.items()) / 5 * 100
        risk_penalty = sum(scores[field] * weight for field, weight in RISK_WEIGHTS.items()) / 5 * 30
        total = max(0.0, min(100.0, benefit - risk_penalty))
        feasibility_status = (
            "FAIL" if candidate.get("feasibility_check") is False
            else "PASS" if candidate.get("feasibility_check") is True
            else "UNKNOWN"
        )
        resource_status = (
            "UNAVAILABLE" if candidate.get("resources_available") is False
            else "AVAILABLE" if candidate.get("resources_available") is True
            else "UNKNOWN"
        )
        failures = _hard_failures(
            scores,
            live_search_verified,
            feasibility_status,
            resource_status,
        )
        if source_count < 1:
            failures.append("no primary source recorded")
        ranked.append(
            {
                "name": name,
                "baseline_id": "UNRECORDED",
                "evidence_ids": [],
                "source_count": source_count,
                "delta": "UNRECORDED",
                "fair_protocol": "UNRECORDED",
                "ablation_plan": "UNRECORDED",
                "reject_condition": "MIGRATE_TO_SCHEMA_V2",
                "feasibility_status": feasibility_status,
                "resource_status": resource_status,
                "status": "REJECT" if failures else "WATCH",
                "total_score": round(total, 2),
                "benefit_score": round(benefit, 2),
                "risk_penalty": round(risk_penalty, 2),
                "watch_reasons": ["legacy schema v1 lacks auditable baseline and evidence links"],
                "hard_failures": failures,
            }
        )

    ranked.sort(key=lambda row: (STATUS_ORDER[row["status"]], -row["total_score"], row["name"].casefold()))
    for position, row in enumerate(ranked, start=1):
        row["rank"] = position
    return {
        "schema_version": 1,
        "migration_required": True,
        "problem_contract_status": "PROVISIONAL",
        "live_search_verified": live_search_verified,
        "search": {
            "searched_at": search_date,
            "timezone": "UNRECORDED",
            "cutoff": search_date,
            "sites": [],
            "queries": [],
            "failures": ["legacy schema v1 did not record structured search metadata"],
        },
        "ranking": ranked,
        "verification_boundary": (
            "Legacy schema v1 was accepted for command compatibility only. All otherwise viable candidates "
            "were forced to WATCH until baseline, evidence, protocol, ablation, and resource links are migrated "
            "to schema v2."
        ),
    }


def rank_matrix(document: dict[str, Any]) -> dict[str, Any]:
    """Validate and rank one schema-v2 evidence matrix."""
    if not isinstance(document, dict):
        raise MatrixError("input must be a JSON object")
    if document.get("schema_version") == 1:
        return _rank_legacy_matrix(document)
    if document.get("schema_version") != 2:
        raise MatrixError("schema_version must equal 2")

    problem_contract_status = _choice(
        document.get("problem_contract_status"),
        "problem_contract_status",
        CONTRACT_STATUSES,
    )
    live_search_verified = document.get("live_search_verified")
    if not isinstance(live_search_verified, bool):
        raise MatrixError("live_search_verified must be true or false")
    search = _validate_search(document.get("search"))
    baselines = _validate_baselines(document.get("baselines"))
    evidence = _validate_evidence(document.get("evidence"))
    cutoff_time = _datetime_value(search["cutoff"])
    for evidence_id, record in evidence.items():
        if _datetime_value(record["verified_at"]) > cutoff_time:
            raise MatrixError(f"evidence {evidence_id}.verified_at must not be later than search.cutoff")

    candidates = document.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise MatrixError("candidates must be a non-empty list")

    ranked: list[dict[str, Any]] = []
    seen_names: set[str] = set()
    for index, candidate in enumerate(candidates, start=1):
        if not isinstance(candidate, dict):
            raise MatrixError(f"candidate {index} must be an object")
        name = _text(candidate.get("name"), f"candidate {index}.name")
        normalized_name = name.casefold()
        if normalized_name in seen_names:
            raise MatrixError(f"duplicate candidate name: {name}")
        seen_names.add(normalized_name)

        baseline_id = _text(candidate.get("baseline_id"), f"{name}.baseline_id")
        if baseline_id not in baselines:
            raise MatrixError(f"{name}: unknown baseline_id {baseline_id}")
        evidence_ids = _text_list(candidate.get("evidence_ids"), f"{name}.evidence_ids")
        missing_evidence = [item for item in evidence_ids if item not in evidence]
        if missing_evidence:
            raise MatrixError(f"{name}: unknown evidence_ids: {', '.join(missing_evidence)}")

        delta = _text(candidate.get("delta"), f"{name}.delta")
        fair_protocol = _text(candidate.get("fair_protocol"), f"{name}.fair_protocol")
        ablation_plan = _text(candidate.get("ablation_plan"), f"{name}.ablation_plan")
        reject_condition = _text(candidate.get("reject_condition"), f"{name}.reject_condition")
        feasibility_status = _choice(
            candidate.get("feasibility_status"),
            f"{name}.feasibility_status",
            FEASIBILITY_STATUSES,
        )
        resource_status = _choice(
            candidate.get("resource_status"),
            f"{name}.resource_status",
            RESOURCE_STATUSES,
        )

        scores = {
            field: _score_0_to_5(candidate.get(field), field, name)
            for field in (*BENEFIT_WEIGHTS, *RISK_WEIGHTS)
        }
        benefit = sum(scores[field] * weight for field, weight in BENEFIT_WEIGHTS.items()) / 5 * 100
        risk_penalty = sum(scores[field] * weight for field, weight in RISK_WEIGHTS.items()) / 5 * 30
        total = max(0.0, min(100.0, benefit - risk_penalty))
        failures = _hard_failures(
            scores,
            live_search_verified,
            feasibility_status,
            resource_status,
        )
        watch_reasons = _watch_reasons(
            problem_contract_status,
            feasibility_status,
            resource_status,
            evidence_ids,
            evidence,
        )

        if failures:
            status = "REJECT"
        elif watch_reasons:
            status = "WATCH"
        elif total >= 72:
            status = "PRIMARY"
        elif total >= 56:
            status = "BACKUP"
        else:
            status = "WATCH"

        ranked.append(
            {
                "name": name,
                "baseline_id": baseline_id,
                "evidence_ids": evidence_ids,
                "source_count": len(evidence_ids),
                "delta": delta,
                "fair_protocol": fair_protocol,
                "ablation_plan": ablation_plan,
                "reject_condition": reject_condition,
                "feasibility_status": feasibility_status,
                "resource_status": resource_status,
                "status": status,
                "total_score": round(total, 2),
                "benefit_score": round(benefit, 2),
                "risk_penalty": round(risk_penalty, 2),
                "watch_reasons": watch_reasons,
                "hard_failures": failures,
            }
        )

    ranked.sort(key=lambda row: (STATUS_ORDER[row["status"]], -row["total_score"], row["name"].casefold()))
    for position, row in enumerate(ranked, start=1):
        row["rank"] = position

    return {
        "schema_version": 2,
        "problem_contract_status": problem_contract_status,
        "live_search_verified": live_search_verified,
        "search": search,
        "ranking": ranked,
        "verification_boundary": (
            "The tool validated supplied schema links and self-reported gates only; it did not search the web "
            "or prove source authenticity, literature completeness, mathematical correctness, feasibility, "
            "reproducibility, novelty, or superiority on the target problem."
        ),
    }


def to_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Frontier Candidate Ranking",
        "",
        f"- Search cutoff: {result['search']['cutoff']}",
        f"- Search timezone: {result['search']['timezone']}",
        f"- Problem contract: {result['problem_contract_status']}",
        f"- Live search verified: {str(result['live_search_verified']).lower()}",
        "",
        "| Rank | Candidate | Status | Baseline | Evidence | Total | Watch reasons | Hard failures |",
        "|---:|---|---|---|---|---:|---|---|",
    ]
    for row in result["ranking"]:
        safe_name = row["name"].replace("|", "\\|").replace("\n", " ")
        evidence_ids = ", ".join(row["evidence_ids"])
        watch_reasons = "; ".join(row["watch_reasons"]) or "--"
        failures = "; ".join(row["hard_failures"]) or "--"
        lines.append(
            f"| {row['rank']} | {safe_name} | {row['status']} | {row['baseline_id']} | "
            f"{evidence_ids} | {row['total_score']:.2f} | {watch_reasons} | {failures} |"
        )
    lines.extend(["", f"> Verification boundary: {result['verification_boundary']}", ""])
    return "\n".join(lines)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise MatrixError(f"input file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise MatrixError(f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise MatrixError("input must be a JSON object")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="UTF-8 JSON schema-v2 candidate matrix")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", type=Path, help="write output to this path instead of stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = rank_matrix(_read_json(args.input))
    except MatrixError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    else:
        rendered = to_markdown(result)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
