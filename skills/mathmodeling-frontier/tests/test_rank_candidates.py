from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "rank_candidates.py"
SKILL_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("rank_candidates", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def evidence(evidence_id: str = "E1", **overrides):
    item = {
        "id": evidence_id,
        "title": f"Verified paper {evidence_id}",
        "primary_url": f"https://example.org/papers/{evidence_id}",
        "publication_status": "PEER_REVIEWED",
        "verified_at": "2026-09-01T22:20:00+08:00",
        "code_status": "UNKNOWN",
        "compute_status": "UNREPORTED",
    }
    item.update(overrides)
    return item


def candidate(name: str, **overrides):
    item = {
        "name": name,
        "baseline_id": "B1",
        "evidence_ids": ["E1", "E2"],
        "delta": "add one structure-matched module",
        "fair_protocol": "same split, information, metrics, seeds, budget and solver limits",
        "ablation_plan": "B1 versus B1 plus the module",
        "reject_condition": "no decision-relevant gain or unacceptable cost",
        "feasibility_status": "PASS",
        "resource_status": "AVAILABLE",
        "mechanism_fit": 5,
        "data_fit": 5,
        "validation_strength": 5,
        "reproducibility": 5,
        "explainability": 4,
        "compute_fit": 4,
        "novelty": 4,
        "assumption_risk": 1,
        "implementation_risk": 1,
        "evidence_risk": 1,
    }
    item.update(overrides)
    return item


def matrix(*items, live: bool = True, contract: str = "FROZEN", evidence_items=None):
    return {
        "schema_version": 2,
        "problem_contract_status": contract,
        "live_search_verified": live,
        "search": {
            "searched_at": "2026-09-01T22:20:00+08:00",
            "timezone": "Asia/Shanghai",
            "cutoff": "2026-09-01T22:20:00+08:00",
            "sites": ["PMLR", "OpenReview"],
            "queries": ["mechanism candidate limitation"],
            "failures": [],
        },
        "baselines": [
            {"id": "B1", "name": "transparent baseline", "defect": "verified structural defect"}
        ],
        "evidence": list(evidence_items or [evidence("E1"), evidence("E2")]),
        "candidates": list(items),
    }


def legacy_matrix(*items):
    return {
        "schema_version": 1,
        "search_date": "2026-08-26",
        "live_search_verified": True,
        "candidates": list(items),
    }


class RankingTests(unittest.TestCase):
    def test_internal_markdown_links_and_single_active_delta(self):
        markdown_links = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
        skill_source = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(skill_source.count("](references/frontier-live-delta-"), 1)
        for markdown in sorted(SKILL_ROOT.rglob("*.md")):
            source = markdown.read_text(encoding="utf-8")
            for raw_target in markdown_links.findall(source):
                target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                target = unquote(target.split("#", 1)[0])
                if not target:
                    continue
                resolved = (markdown.parent / target).resolve()
                self.assertTrue(
                    resolved.exists(),
                    f"broken Markdown link in {markdown}: {raw_target}",
                )

    def test_hard_gate_overrides_high_novelty(self):
        result = MODULE.rank_matrix(
            matrix(
                candidate("mechanism-aligned"),
                candidate("fashionable but mismatched", mechanism_fit=2, novelty=5),
            )
        )
        by_name = {row["name"]: row for row in result["ranking"]}
        self.assertEqual(by_name["mechanism-aligned"]["status"], "PRIMARY")
        self.assertEqual(by_name["fashionable but mismatched"]["status"], "REJECT")
        self.assertIn("mechanism_fit < 3", by_name["fashionable but mismatched"]["hard_failures"])

    def test_legacy_schema_remains_executable_but_forces_watch(self):
        old = candidate("legacy")
        old["source_count"] = 3
        old["feasibility_check"] = True
        old["resources_available"] = True
        for field in (
            "baseline_id",
            "evidence_ids",
            "delta",
            "fair_protocol",
            "ablation_plan",
            "reject_condition",
            "feasibility_status",
            "resource_status",
        ):
            old.pop(field, None)
        result = MODULE.rank_matrix(legacy_matrix(old))
        self.assertTrue(result["migration_required"])
        self.assertEqual(result["ranking"][0]["status"], "WATCH")
        self.assertIn("legacy schema v1", result["ranking"][0]["watch_reasons"][0])

    def test_live_search_is_required(self):
        result = MODULE.rank_matrix(matrix(candidate("otherwise strong"), live=False))
        row = result["ranking"][0]
        self.assertEqual(row["status"], "REJECT")
        self.assertIn("live search not verified", row["hard_failures"])

    def test_provisional_contract_forces_watch(self):
        result = MODULE.rank_matrix(matrix(candidate("provisional"), contract="PROVISIONAL"))
        row = result["ranking"][0]
        self.assertEqual(row["status"], "WATCH")
        self.assertIn("problem contract is provisional", row["watch_reasons"])

    def test_unknown_resource_or_feasibility_forces_watch(self):
        result = MODULE.rank_matrix(
            matrix(candidate("unknown cost", feasibility_status="UNKNOWN", resource_status="UNKNOWN"))
        )
        row = result["ranking"][0]
        self.assertEqual(row["status"], "WATCH")
        self.assertIn("feasibility status unknown", row["watch_reasons"])
        self.assertIn("resource status unknown", row["watch_reasons"])

    def test_failed_feasibility_and_unavailable_resources_reject(self):
        result = MODULE.rank_matrix(
            matrix(candidate("not feasible", feasibility_status="FAIL", resource_status="UNAVAILABLE"))
        )
        row = result["ranking"][0]
        self.assertEqual(row["status"], "REJECT")
        self.assertIn("feasibility check failed", row["hard_failures"])
        self.assertIn("required resources unavailable", row["hard_failures"])

    def test_only_unreviewed_evidence_forces_watch(self):
        result = MODULE.rank_matrix(
            matrix(
                candidate("preprint only"),
                evidence_items=[
                    evidence("E1", publication_status="PREPRINT"),
                    evidence("E2", publication_status="UNDER_REVIEW"),
                ],
            )
        )
        row = result["ranking"][0]
        self.assertEqual(row["status"], "WATCH")
        self.assertIn("no peer-reviewed or accepted primary source", row["watch_reasons"])

    def test_other_status_without_formal_source_forces_watch(self):
        result = MODULE.rank_matrix(
            matrix(
                candidate("other evidence only"),
                evidence_items=[
                    evidence("E1", publication_status="OTHER"),
                    evidence("E2", publication_status="OTHER"),
                ],
            )
        )
        row = result["ranking"][0]
        self.assertEqual(row["status"], "WATCH")
        self.assertIn("no peer-reviewed or accepted primary source", row["watch_reasons"])

    def test_single_source_forces_watch(self):
        result = MODULE.rank_matrix(
            matrix(
                candidate("single source", evidence_ids=["E1"]),
                evidence_items=[evidence("E1")],
            )
        )
        row = result["ranking"][0]
        self.assertEqual(row["status"], "WATCH")
        self.assertIn("fewer than two evidence records", row["watch_reasons"])

    def test_unknown_evidence_reference_is_rejected(self):
        with self.assertRaises(MODULE.MatrixError):
            MODULE.rank_matrix(matrix(candidate("bad reference", evidence_ids=["E404"])))

    def test_duplicate_evidence_ids_are_rejected(self):
        with self.assertRaises(MODULE.MatrixError):
            MODULE.rank_matrix(matrix(candidate("duplicate evidence", evidence_ids=["E1", "E1"])))

    def test_unknown_baseline_is_rejected(self):
        with self.assertRaises(MODULE.MatrixError):
            MODULE.rank_matrix(matrix(candidate("bad baseline", baseline_id="B404")))

    def test_required_ablation_cannot_be_empty(self):
        with self.assertRaises(MODULE.MatrixError):
            MODULE.rank_matrix(matrix(candidate("missing ablation", ablation_plan="")))

    def test_required_protocol_and_reject_condition_cannot_be_empty(self):
        with self.assertRaises(MODULE.MatrixError):
            MODULE.rank_matrix(matrix(candidate("missing protocol", fair_protocol="")))
        with self.assertRaises(MODULE.MatrixError):
            MODULE.rank_matrix(matrix(candidate("missing reject condition", reject_condition="")))

    def test_search_time_must_not_exceed_cutoff(self):
        payload = matrix(candidate("bad search time"))
        payload["search"]["searched_at"] = "2026-09-01T22:21:00+08:00"
        payload["search"]["cutoff"] = "2026-09-01T22:20:00+08:00"
        with self.assertRaises(MODULE.MatrixError):
            MODULE.rank_matrix(payload)

    def test_evidence_verification_must_not_exceed_cutoff(self):
        payload = matrix(
            candidate("future evidence"),
            evidence_items=[
                evidence("E1", verified_at="2026-09-01T22:21:00+08:00"),
                evidence("E2"),
            ],
        )
        with self.assertRaises(MODULE.MatrixError):
            MODULE.rank_matrix(payload)

    def test_out_of_range_score_is_rejected(self):
        with self.assertRaises(MODULE.MatrixError):
            MODULE.rank_matrix(matrix(candidate("invalid", novelty=6)))

    def test_source_count_is_derived_from_evidence_ids(self):
        result = MODULE.rank_matrix(
            matrix(
                candidate("two sources", evidence_ids=["E1", "E2"]),
                evidence_items=[evidence("E1"), evidence("E2")],
            )
        )
        self.assertEqual(result["ranking"][0]["source_count"], 2)

    def test_cli_writes_utf8_json(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "matrix.json"
            output = root / "ranking.json"
            source.write_text(
                json.dumps(matrix(candidate("中文候选")), ensure_ascii=False),
                encoding="utf-8",
            )
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), str(source), "--format", "json", "--output", str(output)],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["ranking"][0]["name"], "中文候选")
            self.assertEqual(payload["ranking"][0]["status"], "PRIMARY")


if __name__ == "__main__":
    unittest.main()
