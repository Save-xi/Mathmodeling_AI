from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/lookup_anchors.py"
SPEC = importlib.util.spec_from_file_location("lookup_anchors", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class LookupTests(unittest.TestCase):
    def setUp(self):
        self.catalog = MODULE.load_catalog()

    def cli(self, *args):
        return subprocess.run([sys.executable, "-X", "utf8", str(SCRIPT), *map(str, args)],
                              capture_output=True, text=True, encoding="utf-8")

    def test_selected_route_loads_only_referenced_evidence(self):
        with patch.object(socket, "socket", side_effect=AssertionError("network forbidden")):
            selected = MODULE.select_routes(self.catalog, ["forecast"])
        self.assertEqual([r["id"] for r in selected["routes"]], ["forecast"])
        wanted = set(selected["routes"][0]["evidence_ids"])
        self.assertEqual({e["id"] for e in selected["evidence"]}, wanted)
        self.assertNotIn("cadsr2026", wanted)
        self.assertFalse(selected["network_performed"])

    def test_alias_combination_is_deduplicated_without_date_refresh(self):
        selected = MODULE.select_routes(self.catalog, ["预测", "FORECAST", "predict-optimize"])
        self.assertEqual([r["id"] for r in selected["routes"]], ["forecast", "predict-optimize"])
        original = {e["id"]: e["verified_on"] for e in self.catalog["evidence"]}
        self.assertTrue(all(e["verified_on"] == original[e["id"]] for e in selected["evidence"]))
        self.assertTrue(all(e["task_validation"] == "NOT_RUN" for e in selected["evidence"]))

    def test_unknown_task_is_atomic_and_does_not_dump_catalog(self):
        completed = self.cli("--task", "forecast", "--task", "not-a-task")
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertNotIn("Traceback", completed.stderr)

    def test_missing_file_and_invalid_json_are_controlled(self):
        with tempfile.TemporaryDirectory(prefix="锚点测试 ") as tmp:
            path = Path(tmp) / "目录.json"
            self.assertEqual(self.cli("--catalog", path, "--check").returncode, 2)
            path.write_text("{invalid", encoding="utf-8")
            result = self.cli("--catalog", path, "--check")
            self.assertEqual(result.returncode, 2)
            self.assertNotIn("Traceback", result.stderr)

    def test_unicode_path_repeated_lookup_is_read_only(self):
        with tempfile.TemporaryDirectory(prefix="中文 锚点 ") as tmp:
            path = Path(tmp) / "资料目录.json"
            data = json.dumps(self.catalog, ensure_ascii=False).encode("utf-8")
            path.write_bytes(data)
            before = path.stat()
            first = self.cli("--catalog", path, "--task", "鲁棒", "--format", "json")
            second = self.cli("--catalog", path, "--task", "robust", "--format", "json")
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(first.stdout, second.stdout)
            self.assertEqual(path.read_bytes(), data)
            self.assertEqual(path.stat().st_mtime_ns, before.st_mtime_ns)
            self.assertEqual(list(Path(tmp).iterdir()), [path])

    def test_duplicate_source_and_route_are_rejected(self):
        for field in ("evidence", "routes"):
            bad = copy.deepcopy(self.catalog)
            bad[field].append(copy.deepcopy(bad[field][0]))
            with self.assertRaises(MODULE.CatalogError):
                MODULE.validate_catalog(bad)

    def test_unknown_source_link_is_rejected(self):
        bad = copy.deepcopy(self.catalog)
        bad["routes"][0]["evidence_ids"].append("not-a-source")
        with self.assertRaises(MODULE.CatalogError):
            MODULE.validate_catalog(bad)

    def test_malformed_url_is_a_controlled_catalog_error(self):
        bad = copy.deepcopy(self.catalog)
        bad["evidence"][0]["primary_url"] = "https://[broken"
        with self.assertRaises(MODULE.CatalogError):
            MODULE.validate_catalog(bad)

    def test_future_verification_and_ambiguous_alias_are_rejected(self):
        bad = copy.deepcopy(self.catalog)
        bad["evidence"][0]["verified_on"] = "2099-01-01"
        with self.assertRaises(MODULE.CatalogError):
            MODULE.validate_catalog(bad)
        bad = copy.deepcopy(self.catalog)
        bad["routes"][1]["aliases"].append(bad["routes"][0]["id"])
        with self.assertRaises(MODULE.CatalogError):
            MODULE.validate_catalog(bad)

    def test_preparation_cannot_be_promoted_to_task_validation(self):
        bad = copy.deepcopy(self.catalog)
        bad["evidence"][0]["task_validation"] = "VERIFIED"
        with self.assertRaises(MODULE.CatalogError):
            MODULE.validate_catalog(bad)

    def test_paper_and_software_release_remain_distinct(self):
        result = MODULE.select_routes(self.catalog, ["forecast"])
        by_id = {e["id"]: e for e in result["evidence"]}
        self.assertEqual(by_id["timesfm2024"]["publication_status"], "PEER_REVIEWED")
        self.assertEqual(by_id["timesfm3_2026"]["publication_status"], "SOFTWARE_RELEASE")
        self.assertNotEqual(by_id["timesfm2024"]["primary_url"], by_id["timesfm3_2026"]["primary_url"])

    def test_invalid_encoding_and_oversized_catalog_are_controlled(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "catalog.json"
            for data in (b"\xff\xfe", b" " * (MODULE.MAX_BYTES + 1)):
                path.write_bytes(data)
                result = self.cli("--catalog", path, "--check")
                self.assertEqual(result.returncode, 2)
                self.assertNotIn("Traceback", result.stderr)

    def test_consistency_check_does_not_claim_model_validation(self):
        result = self.cli("--check")
        self.assertEqual(result.returncode, 0, result.stderr)
        parsed = json.loads(result.stdout)
        self.assertEqual(parsed["check"], "CATALOG_CONSISTENCY_ONLY")
        self.assertEqual(parsed["routes"], len(self.catalog["routes"]))
        self.assertFalse(parsed["network_performed"])


if __name__ == "__main__":
    unittest.main()
