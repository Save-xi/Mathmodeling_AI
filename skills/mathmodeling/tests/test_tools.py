from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import unquote


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
import audit_project as auditor
import build_paper as builder
from project_contract import BUILD_MARKER, file_stamp, is_numeric


def run_tool(name: str, *args: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-B", "-X", "utf8", str(SCRIPTS / name), *(str(x) for x in args)],
                          capture_output=True, text=True, encoding="utf-8", timeout=45)


def put(root: Path, relative: str, content: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return path


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def snapshot(root: Path) -> dict:
    return {str(path.relative_to(root)): (path.read_bytes(), path.stat().st_mtime_ns)
            for path in root.rglob("*") if path.is_file()}


def make_directory_link(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=True)
        return
    except OSError:
        if os.name != "nt":
            raise
    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if not powershell:
        raise OSError("No PowerShell available for a non-admin Windows junction")
    environment = os.environ.copy()
    environment.update(MODELING_TEST_LINK=str(link), MODELING_TEST_TARGET=str(target))
    process = subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-Command",
         "New-Item -ItemType Junction -Path $env:MODELING_TEST_LINK -Target $env:MODELING_TEST_TARGET -ErrorAction Stop | Out-Null"],
        env=environment, capture_output=True, timeout=20,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if process.returncode:
        raise OSError("Could not create test junction")


def cleanup_temporary(temporary) -> None:
    path = Path(temporary.name).resolve()
    allowed = Path(tempfile.gettempdir()).resolve()
    if path == allowed or not path.is_relative_to(allowed):
        raise AssertionError(f"Refusing recursive cleanup outside the dedicated temp directory: {path}")
    temporary.cleanup()


def complete_fixture(root: Path, *, parser_fixture: bool = True) -> None:
    """Actually run small calculations; PDF/receipt are schema fixtures, not TeX evidence."""
    initialized = run_tool("init_project.py", root, "--problems", 2, "--title", "中文测试 & 骨架")
    if initialized.returncode:
        raise AssertionError(initialized.stdout + initialized.stderr)
    put(root, "data/raw/原始题目.txt", "合成测试题：第一问计算 2,4,6 的均值；第二问 max 2x+3y，x+y<=3，y<=2，x,y 为非负整数。\n")
    put(root, "data/raw/观测.csv", "value\n2\n4\n6\n")
    put(root, "src/common/calculation.py", "def mean(values):\n    return sum(values) / len(values)\n")
    put(root, "problem_1.py", '''from pathlib import Path
import csv, json, math
from src.common.calculation import mean
root = Path(__file__).resolve().parent
with (root/'data/raw/观测.csv').open(encoding='utf-8') as stream:
    values = [float(row['value']) for row in csv.DictReader(stream)]
result = mean(values)
assert math.isfinite(result) and result == 4.0
table = root/'results/tables'
summary = {'mean': result, 'n': len(values)}
check = {'hand_sum': 12, 'hand_n': 3, 'mean_check': result == 12/3}
(table/'q1.json').write_text(json.dumps(summary), encoding='utf-8')
(table/'q1_check.json').write_text(json.dumps(check), encoding='utf-8')
print(result)
''')
    put(root, "problem_2.py", '''from pathlib import Path
import json
root = Path(__file__).resolve().parent
feasible = []
for x in range(4):
    for y in range(3):
        if x+y <= 3:
            feasible.append((2*x+3*y, x, y))
objective,x,y = max(feasible)
assert objective == 8 and x+y <= 3 and y <= 2
table = root/'results/tables'
summary = {'objective': objective, 'x': x, 'y': y}
check = {'feasible': True, 'bound': 2*3+2, 'gap': 0}
(table/'q2.json').write_text(json.dumps(summary), encoding='utf-8')
(table/'q2_check.json').write_text(json.dumps(check), encoding='utf-8')
print(objective)
''')
    manifest = read_json(root / "mathmodeling.json")
    manifest["source_files"] = ["data/raw/原始题目.txt", "data/raw/观测.csv"]
    write_json(root / "mathmodeling.json", manifest)
    for name in auditor.DOCS:
        put(root, "docs/" + name, "# 结构测试记录\n\n本夹具使用合成题与已执行的小型计算；真实比赛仍需核对原题、协议和规则。\n")
    put(root, "docs/qa_report.md", "人工 QA 记录应保留，不能被结构报告覆盖。\n")
    runs = []
    for question in (1, 2):
        start = datetime.now(timezone.utc)
        process = subprocess.run([sys.executable, "-B", "-X", "utf8", str(root / f"problem_{question}.py")],
                                 capture_output=True, text=True, encoding="utf-8", timeout=20)
        if process.returncode:
            raise AssertionError(process.stderr)
        finish = datetime.now(timezone.utc)
        record = {
            "question": question, "run_id": f"q{question}-selected", "status": "completed",
            "model_kind": "regression" if question == 1 else "optimization",
            "command": f"python -B -X utf8 problem_{question}.py", "environment": "Python " + sys.version.split()[0] + "; stdlib",
            "started_at": start.isoformat(), "finished_at": finish.isoformat(), "runtime_seconds": (finish-start).total_seconds(),
            "inputs": ["data/raw/原始题目.txt", "data/raw/观测.csv"],
            "code": [f"problem_{question}.py", "config/parameters.yaml"] + (["src/common/calculation.py"] if question == 1 else []),
            "artifacts": [f"results/tables/q{question}.json"],
            "validation": {"status": "passed", "protocol": "explicit hand-checkable arithmetic/bound; baseline equals selected solution", "baseline_artifact": f"results/tables/q{question}.json", "artifacts": [f"results/tables/q{question}_check.json"]},
            "randomness": {"mode": "deterministic"},
        }
        if question == 2:
            record["solver"] = {"name": "finite enumeration", "version": "fixture-v1", "status": "optimal", "problem_type": "mip", "has_incumbent": True, "feasibility_verified": True, "objective": 8, "bound": 8, "gap": 0}
        tracked = record["inputs"] + record["code"] + record["artifacts"] + record["validation"]["artifacts"]
        record["file_stamps"] = {relative: file_stamp(root/relative) for relative in tracked}
        runs.append(record)
    write_json(root / "results/run_manifest.json", {"schema_version": 1, "runs": runs})
    put(root, "docs/evidence_map.md", """| Claim ID | Question | Run ID | Paper claim | Source artifact | Metric/value | Conditions | Paper location | Verification |
|---|---|---|---|---|---|---|---|---|
| C-01 | 1 | q1-selected | 三数均值 | `results/tables/q1.json` | mean=4 | 2,4,6 | 第一问 | verified |
| C-02 | 2 | q2-selected | 小型整数规划目标 | `results/tables/q2.json` | objective=8 | x+y<=3,y<=2 | 第二问 | 已核验 |
""")
    if not parser_fixture:
        return
    # A valid parser fixture. Real XeLaTeX rendering is tested separately during release QA.
    from pypdf import PdfWriter
    pdf = root / "paper/output/main.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=595.276, height=841.89)
    writer.write(pdf)
    source = put(root, "paper/main.tex", "\\documentclass[UTF8]{ctexart}\n\\begin{document}\n均值为4，枚举目标为8。\\end{document}\n")
    write_json(pdf.with_suffix(".build.json"), {"tool": BUILD_MARKER, "status": "compiled", "source": "paper/main.tex", "pdf": "paper/output/main.pdf", "pdf_stamp": file_stamp(pdf), "inputs": {"paper/main.tex": file_stamp(source)}, "pages": 1, "warnings": [], "visual_review": "pending"})


class InitializationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "中文 空格项目"

    def tearDown(self):
        cleanup_temporary(self.temp)

    def test_dry_run_has_no_side_effects(self):
        result = run_tool("init_project.py", self.root, "--problems", 2, "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.root.exists())

    def test_actual_count_is_required_and_invalid_counts_rejected(self):
        for arguments in [[], ["--problems", "0"], ["--problems", "21"], ["--problems", "abc"]]:
            with self.subTest(arguments=arguments):
                result = run_tool("init_project.py", self.root, *arguments)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Traceback", result.stderr)
                self.assertFalse(self.root.exists())

    def test_rerun_preserves_all_existing_files(self):
        self.assertEqual(run_tool("init_project.py", self.root, "--problems", 2).returncode, 0)
        put(self.root, "problem_1.py", "# USER SENTINEL\n")
        before = snapshot(self.root)
        result = run_tool("init_project.py", self.root, "--problems", 2, "--title", "不同标题")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(before, snapshot(self.root))

    def test_count_change_is_rejected_before_writes(self):
        self.assertEqual(run_tool("init_project.py", self.root, "--problems", 1).returncode, 0)
        before = snapshot(self.root)
        result = run_tool("init_project.py", self.root, "--problems", 2)
        self.assertEqual(result.returncode, 3)
        self.assertEqual(before, snapshot(self.root))

    def test_file_directory_collision_does_not_partially_initialize(self):
        put(self.root, "config", "not a directory")
        before = snapshot(self.root)
        result = run_tool("init_project.py", self.root, "--problems", 2)
        self.assertEqual(result.returncode, 3)
        self.assertEqual(before, snapshot(self.root))

    def test_missing_latex_asset_fails_before_project_creation(self):
        import init_project
        with patch.object(init_project, "LATEX_TEMPLATE", Path(self.temp.name)/"missing.tex"), patch.object(sys, "argv", ["init_project.py", str(self.root), "--problems", "1"]):
            self.assertEqual(init_project.main(), 3)
        self.assertFalse(self.root.exists())

    def test_linked_destination_cannot_redirect_initialization(self):
        outside = Path(self.temp.name)/"outside"
        outside.mkdir()
        self.root.mkdir()
        try:
            make_directory_link(self.root/"data", outside)
        except OSError as exc:
            self.skipTest(f"OS does not permit symlink creation: {exc}")
        result = run_tool("init_project.py", self.root, "--problems", 1)
        self.assertEqual(result.returncode, 3)
        self.assertEqual(list(outside.iterdir()), [])
        (self.root/"data").rmdir() if getattr(self.root/"data", "is_junction", lambda: False)() else (self.root/"data").unlink()

    def test_fresh_project_cannot_pass_submission_checks(self):
        run_tool("init_project.py", self.root, "--problems", 2)
        result = run_tool("audit_project.py", self.root, "--strict", "--format", "json")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["summary"]["status"], "NOT_READY")


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)/"中文 空格项目"
        complete_fixture(self.root)

    def tearDown(self):
        cleanup_temporary(self.temp)

    def audit(self):
        result = run_tool("audit_project.py", self.root, "--strict", "--format", "json")
        self.assertNotIn("Traceback", result.stderr)
        return result, json.loads(result.stdout)

    def assert_issue(self, code: str):
        process, result = self.audit()
        self.assertNotEqual(process.returncode, 0, result)
        self.assertIn(code, [issue["code"] for issue in result["issues"]], result)

    def mutate_runs(self, operation):
        path = self.root/"results/run_manifest.json"
        data = read_json(path)
        operation(data["runs"])
        write_json(path, data)

    def test_actual_small_calculations_and_read_only_audit(self):
        self.assertEqual(read_json(self.root/"results/tables/q1.json")["mean"], 4)
        self.assertEqual(read_json(self.root/"results/tables/q2.json")["objective"], 8)
        before = snapshot(self.root)
        process, result = self.audit()
        self.assertEqual(process.returncode, 0, result)
        self.assertEqual(result["summary"]["status"], "STRUCTURE_CHECKS_PASSED")
        self.assertTrue(result["summary"]["review_required"])
        self.assertEqual(before, snapshot(self.root))

    def test_unverified_substrings_and_negation_never_pass(self):
        path = self.root/"docs/evidence_map.md"
        original = path.read_text(encoding="utf-8")
        for status in ["unverified", "not verified", "未核验", "partially verified", "verified later"]:
            with self.subTest(status=status):
                path.write_text(original.replace("| verified |", f"| {status} |"), encoding="utf-8")
                self.assert_issue("EVIDENCE_INVALID")

    def test_nonexistent_evidence_path_fails(self):
        path = self.root/"docs/evidence_map.md"
        path.write_text(path.read_text(encoding="utf-8").replace("q1.json", "missing.json"), encoding="utf-8")
        self.assert_issue("EVIDENCE_INVALID")

    def test_missing_actual_result_is_not_replaced_by_logs(self):
        (self.root/"results/tables/q1.json").unlink()
        put(self.root, "results/logs/run.log", "status=completed; validation passed; verified")
        self.assert_issue("RUN_INVALID")

    def test_logs_cannot_be_declared_as_result(self):
        put(self.root, "results/logs/run.log", "status=completed; verified")
        self.mutate_runs(lambda runs: runs[0].update(artifacts=["results/logs/run.log"]))
        self.assert_issue("RUN_INVALID")

    def test_failed_solver_and_missing_incumbent_are_rejected(self):
        path = self.root/"results/run_manifest.json"
        original = read_json(path)
        for status in ["infeasible", "unbounded", "unknown", "failed"]:
            with self.subTest(status=status):
                data = json.loads(json.dumps(original))
                data["runs"][1]["solver"]["status"] = status
                write_json(path, data)
                self.assert_issue("RUN_INVALID")
        data = json.loads(json.dumps(original))
        data["runs"][1]["solver"].update(status="time_limit", has_incumbent=False)
        write_json(path, data)
        self.assert_issue("RUN_INVALID")

    def test_time_limit_with_usable_verified_incumbent_is_allowed(self):
        self.mutate_runs(lambda runs: runs[1]["solver"].update(status="time_limit"))
        result, body = self.audit()
        self.assertEqual(result.returncode, 0, body)

    def test_nonfinite_objective_and_missing_gap_are_rejected(self):
        self.mutate_runs(lambda runs: runs[1]["solver"].update(objective=float("nan")))
        self.assert_issue("RUN_INVALID")
        self.mutate_runs(lambda runs: (runs[1]["solver"].update(objective=8), runs[1]["solver"].pop("gap")))
        self.assert_issue("RUN_INVALID")

    def test_missing_seed_or_validation_protocol_is_rejected(self):
        self.mutate_runs(lambda runs: runs[0].update(randomness={"mode":"stochastic","seeds":[],"repetitions":3}))
        self.assert_issue("RUN_INVALID")
        self.mutate_runs(lambda runs: (runs[0].update(randomness={"mode":"deterministic"}), runs[0]["validation"].pop("protocol")))
        self.assert_issue("RUN_INVALID")

    def test_shared_unimplemented_code_is_detected(self):
        put(self.root, "src/common/calculation.py", "def mean(values):\n    raise NotImplementedError('pending')\n")
        self.assert_issue("CODE_PLACEHOLDER")

    def test_rapid_input_or_result_change_breaks_run_link(self):
        put(self.root, "data/raw/观测.csv", "value\n200\n400\n600\n")
        self.assert_issue("RUN_INVALID")

    def test_previous_output_cannot_be_reused_as_current_run(self):
        def move_start(runs):
            runs[0]["started_at"] = "2099-01-01T00:00:00+00:00"
            runs[0]["finished_at"] = "2099-01-01T00:01:00+00:00"
        self.mutate_runs(move_start)
        self.assert_issue("RUN_INVALID")

    def test_claim_must_use_same_question_run(self):
        path = self.root/"docs/evidence_map.md"
        path.write_text(path.read_text(encoding="utf-8").replace("q1-selected", "q2-selected"), encoding="utf-8")
        self.assert_issue("EVIDENCE_INVALID")

    def test_causal_uq_and_decision_subtypes_have_matching_contracts(self):
        for first, second in (("causal", "multi_objective"), ("uncertainty_quantification", "robust_optimization")):
            self.mutate_runs(lambda runs: (runs[0].update(model_kind=first), runs[1].update(model_kind=second)))
            process, result = self.audit()
            self.assertEqual(process.returncode, 0, result)
        self.mutate_runs(lambda runs: runs[1].pop("solver"))
        self.assert_issue("RUN_INVALID")

    def test_optional_verified_by_column_names_the_actual_checker(self):
        table = (self.root/"docs/evidence_map.md").read_text(encoding="utf-8")
        # Absent column: unchanged behaviour.
        process, result = self.audit()
        self.assertEqual(process.returncode, 0, result)
        for actor, expected_pass in (("independent-rerun", True), ("队员核验", True),
                                     ("looks fine", False), ("", False)):
            with self.subTest(actor=actor):
                # Each row already ends in "|", so the new cell is appended after it.
                rows = [line.rstrip() for line in table.splitlines() if line.strip()]
                widened = [rows[0] + " Verified by |", rows[1] + "---|"]
                widened += [row + f" {actor} |" for row in rows[2:]]
                put(self.root, "docs/evidence_map.md", "\n".join(widened) + "\n")
                process, result = self.audit()
                if expected_pass:
                    self.assertEqual(process.returncode, 0, result)
                else:
                    self.assertIn("EVIDENCE_INVALID", [x["code"] for x in result["issues"]], result)

    def test_each_question_needs_its_selected_run(self):
        self.mutate_runs(lambda runs: runs.pop())
        self.assert_issue("QUESTION_RUN_MISSING")

    def test_bad_manifest_count_duplicates_and_escape_are_rejected(self):
        path = self.root/"mathmodeling.json"
        original = read_json(path)
        cases = [{"problem_count":3}, {"problem_count":True}, {"entrypoints":["problem_1.py","problem_1.py"]}, {"entrypoints":["../outside.py","problem_2.py"]}, {"entrypoints":["C:\\outside.py","problem_2.py"]}]
        for mutation in cases:
            with self.subTest(mutation=mutation):
                write_json(path, original | mutation)
                self.assert_issue("MANIFEST_INVALID")

    def test_broken_json_has_controlled_diagnostic(self):
        put(self.root, "mathmodeling.json", "{broken")
        self.assert_issue("MANIFEST_INVALID")

    def test_original_source_under_data_raw_is_found_for_legacy_layout(self):
        path = self.root/"mathmodeling.json"
        data = read_json(path)
        data["schema_version"] = 1
        data.pop("source_files")
        write_json(path, data)
        process, result = self.audit()
        self.assertEqual(process.returncode, 0, result)

    def test_legacy_missing_execution_is_not_silently_upgraded(self):
        (self.root/"results/run_manifest.json").unlink()
        before = snapshot(self.root)
        self.assert_issue("RUN_MANIFEST_MISSING")
        self.assertEqual(before, snapshot(self.root))

    def test_scan_encoding_and_size_failures_are_visible(self):
        (self.root/"src/common/bad.py").write_bytes("# 中文注释\nx=1\n".encode("gbk"))
        self.assert_issue("SCAN_INCOMPLETE")
        process = run_tool("audit_project.py", self.root, "--strict", "--format", "json", "--max-file-bytes", 20)
        self.assertNotEqual(process.returncode, 0)
        self.assertTrue(json.loads(process.stdout)["summary"]["scan"]["skipped"])

    def test_declared_paths_accept_windows_separators(self):
        path = self.root/"mathmodeling.json"
        data = read_json(path)
        data["source_files"] = [value.replace("/", "\\") for value in data["source_files"]]
        write_json(path, data)
        process, body = self.audit()
        self.assertEqual(process.returncode, 0, body)

    def test_build_source_edit_and_invalid_pdf_are_detected(self):
        with (self.root/"paper/main.tex").open("a",encoding="utf-8") as stream:
            stream.write("\n新结果\n")
        self.assert_issue("BUILD_STALE_OR_INVALID")
        put(self.root, "paper/output/main.pdf", "%PDF-1.4\n% not a valid PDF\n%%EOF\n")
        self.assert_issue("PDF_UNVERIFIED")

    def test_unreferenced_draft_does_not_block_final_paper(self):
        put(self.root, "paper/drafts/old.tex", "TODO abandoned draft\n")
        process, result = self.audit()
        self.assertEqual(process.returncode, 0, result)

    def test_reports_never_overwrite_protected_inputs_or_manual_notes(self):
        for relative in ["problem_1.py", "data/raw/观测.csv", "paper/main.tex", "paper/output/main.pdf", "docs/qa_report.md", "docs/evidence_map.md", "results/run_manifest.json", "docs/source_inventory.md"]:
            with self.subTest(path=relative):
                before = snapshot(self.root)
                result = run_tool("audit_project.py", self.root, "--report", relative)
                self.assertEqual(result.returncode, 3, result.stdout)
                self.assertEqual(before, snapshot(self.root))

    def test_report_refuses_unowned_existing_file_and_path_escape(self):
        put(self.root, "docs/manual.md", "hand reviewed notes\n")
        for relative in ["docs/manual.md", "../outside.md", str(Path(self.temp.name)/"outside.md")]:
            result = run_tool("audit_project.py", self.root, "--report", relative)
            self.assertEqual(result.returncode, 3, result.stdout)
        self.assertEqual((self.root/"docs/manual.md").read_text(), "hand reviewed notes\n")
        self.assertFalse((Path(self.temp.name)/"outside.md").exists())

    def test_junction_cannot_redirect_report_writes(self):
        outside = Path(self.temp.name)/"external-reports"
        outside.mkdir()
        link = self.root/"reports"
        try:
            make_directory_link(link, outside)
        except OSError as exc:
            self.skipTest(str(exc))
        result = run_tool("audit_project.py", self.root, "--report", "reports/report.md")
        self.assertEqual(result.returncode, 3, result.stdout)
        self.assertEqual(list(outside.iterdir()), [])
        link.rmdir() if getattr(link, "is_junction", lambda: False)() else link.unlink()

    def test_machine_report_is_repeatable_and_does_not_replace_manual_qa(self):
        manual = (self.root/"docs/qa_report.md").read_bytes()
        for _ in range(2):
            result = run_tool("audit_project.py", self.root, "--strict", "--format", "markdown", "--report", "docs/structural_audit.md")
            self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(manual, (self.root/"docs/qa_report.md").read_bytes())

    def test_builder_failure_preserves_previous_pdf_and_receipt(self):
        pdf = self.root/"paper/output/main.pdf"
        receipt = pdf.with_suffix(".build.json")
        before = (pdf.read_bytes(), receipt.read_bytes())
        with patch.object(builder.shutil, "which", side_effect=lambda name: name), patch.object(builder.subprocess, "run", return_value=SimpleNamespace(returncode=1, stdout="deliberate compiler failure", stderr="")):
            with self.assertRaises(RuntimeError):
                builder.build(self.root)
        self.assertEqual(before, (pdf.read_bytes(), receipt.read_bytes()))

    def test_zero_exit_without_new_pdf_cannot_publish_old_build(self):
        put(self.root, "paper/build/stale/main.pdf", "%PDF old file")
        pdf = self.root/"paper/output/main.pdf"
        before = pdf.read_bytes()
        with patch.object(builder.shutil, "which", side_effect=lambda name: name), patch.object(builder.subprocess, "run", return_value=SimpleNamespace(returncode=0, stdout="no new output", stderr="")):
            with self.assertRaises(RuntimeError):
                builder.build(self.root)
        self.assertEqual(before, pdf.read_bytes())


    def test_bibliography_files_are_tracked_for_both_backends(self):
        bibliography = put(self.root, "paper/中文文献.bib", "@misc{q,title={Synthetic test}}\n")
        build_dir = self.root / "paper/build/bibliography-fixture"
        put(self.root, "paper/build/bibliography-fixture/main.aux", "\\bibdata{中文文献}\n\\bibstyle{plain}\n")
        self.assertIn(bibliography.resolve(), builder.bibliography_inputs(build_dir, self.root/"paper"))
        (build_dir/"main.aux").unlink()
        put(self.root, "paper/build/bibliography-fixture/main.bcf", '<bcf:controlfile xmlns:bcf="https://example.invalid/bcf"><bcf:datasource>中文文献.bib</bcf:datasource></bcf:controlfile>')
        self.assertIn(bibliography.resolve(), builder.bibliography_inputs(build_dir, self.root/"paper"))

    def test_bibtex_aliases_preserve_original_unicode_inputs(self):
        bibliography = put(self.root, "paper/中文文献.bib", "@misc{q,title={中文测试}}\n")
        style = put(self.root, "paper/中文样式.bst", "ENTRY {} {} {}\n")
        aux = put(self.root, "paper/build/alias-fixture/main.aux", "\\bibdata{中文文献}\n\\bibstyle{中文样式}\n")
        before = {path: (path.read_bytes(), file_stamp(path)) for path in (bibliography, style)}
        tracked = builder.stage_bibtex_inputs(aux, self.root/"paper")
        self.assertEqual(tracked, {bibliography.resolve(), style.resolve()})
        self.assertEqual(before, {path: (path.read_bytes(), file_stamp(path)) for path in before})
        self.assertTrue(aux.read_text(encoding="utf-8").isascii())
        self.assertEqual((aux.parent/"mm-bib-input-001.bib").read_bytes(), bibliography.read_bytes())


class SubmissionLimitTests(unittest.TestCase):
    """Page limit and PDF identity metadata are disqualification-class contest rules."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)/"提交限制项目"
        complete_fixture(self.root)

    def tearDown(self):
        cleanup_temporary(self.temp)

    def declare(self, **extra):
        path = self.root/"mathmodeling.json"
        data = read_json(path)
        data["submission"].update(extra)
        write_json(path, data)

    def publish_pdf(self, pages: int, metadata: dict | None = None):
        from pypdf import PdfWriter
        writer = PdfWriter()
        for _ in range(pages):
            writer.add_blank_page(width=595.276, height=841.89)
        if metadata:
            writer.add_metadata(metadata)
        writer.write(self.root/"paper/output/main.pdf")

    def codes(self):
        result = run_tool("audit_project.py", self.root, "--format", "json")
        self.assertNotIn("Traceback", result.stderr)
        return [issue["code"] for issue in json.loads(result.stdout)["issues"]]

    def test_page_limit_and_identity_metadata_block_submission(self):
        self.declare(page_limit=30, anonymity=True)
        self.publish_pdf(33, {"/Author": "张三（某某大学 第0001队）", "/Title": "2026 国赛 B 题"})
        codes = self.codes()
        self.assertIn("PAGE_LIMIT_EXCEEDED", codes)
        self.assertIn("PDF_IDENTITY_METADATA", codes)
        strict = run_tool("audit_project.py", self.root, "--strict")
        self.assertEqual(strict.returncode, 2, strict.stdout)

    def test_compliant_pdf_triggers_neither_check(self):
        self.declare(page_limit=30, anonymity=True)
        self.publish_pdf(1)
        codes = self.codes()
        self.assertNotIn("PAGE_LIMIT_EXCEEDED", codes)
        self.assertNotIn("PDF_IDENTITY_METADATA", codes)
        self.assertNotIn("SUBMISSION_LIMITS_UNDECLARED", codes)

    def test_undeclared_limits_are_visible_but_do_not_block(self):
        codes = self.codes()
        self.assertIn("SUBMISSION_LIMITS_UNDECLARED", codes)
        result = run_tool("audit_project.py", self.root, "--strict")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_declaring_only_one_limit_still_reports_the_other(self):
        """Declaring one silently disables the other; that must stay visible."""
        for declared, missing in (({"page_limit": 30}, "anonymity"),
                                  ({"anonymity": True}, "page_limit")):
            with self.subTest(declared=declared):
                data = read_json(self.root/"mathmodeling.json")
                data["submission"] = {"source": "paper/main.tex", "pdf": "paper/output/main.pdf", **declared}
                write_json(self.root/"mathmodeling.json", data)
                result = run_tool("audit_project.py", self.root, "--format", "json")
                issues = [x for x in json.loads(result.stdout)["issues"]
                          if x["code"] == "SUBMISSION_LIMITS_UNDECLARED"]
                self.assertTrue(issues, result.stdout)
                self.assertIn(missing, issues[0]["evidence"][0])

    def test_unparsable_pdf_blocks_when_limits_were_declared(self):
        self.declare(page_limit=30, anonymity=True)
        put(self.root, "paper/output/main.pdf", "%PDF-1.4\ntruncated, unparsable\n")
        issues = {x["code"]: x["severity"] for x in json.loads(
            run_tool("audit_project.py", self.root, "--format", "json").stdout)["issues"]}
        # The declared disqualification checks could not run at all, so this is not
        # a lesser finding than an actual page overrun.
        self.assertEqual(issues.get("PDF_UNVERIFIED"), "BLOCKER", issues)

    def test_pdfinfo_fallback_matches_pypdf_including_blank_fields(self):
        from pypdf import PdfWriter
        import builtins
        from project_contract import inspect_pdf
        blank, dirty = self.root/"blank.pdf", self.root/"dirty.pdf"
        for target, metadata in ((blank, {"/Author": "   "}),
                                 (dirty, {"/Author": "张三（某某大学）", "/Title": "A题"})):
            writer = PdfWriter()
            writer.add_blank_page(width=595.276, height=841.89)
            writer.add_metadata(metadata)
            writer.write(target)
        real = builtins.__import__

        def blocked(name, *args, **kwargs):
            if name == "pypdf":
                raise ImportError("pypdf blocked for this test")
            return real(name, *args, **kwargs)

        for target in (blank, dirty):
            with self.subTest(pdf=target.name):
                expected = inspect_pdf(target, with_identity=True)
                builtins.__import__ = blocked
                try:
                    if not shutil.which("pdfinfo"):
                        self.skipTest("Poppler pdfinfo not installed")
                    # A blank field must stay absent, not swallow the next output line.
                    self.assertEqual(inspect_pdf(target, with_identity=True), expected)
                finally:
                    builtins.__import__ = real
        self.assertEqual(inspect_pdf(blank, with_identity=True)[1], {})

    def test_manifest_accepts_optional_limits_and_rejects_bad_values(self):
        from project_contract import default_manifest, validate_manifest
        manifest = default_manifest("t", 1)
        self.assertNotIn("page_limit", manifest["submission"],
                         "default_manifest must stay unchanged or reruns reject existing projects")
        (self.root/"problem_only.py").write_text("x = 1\n", encoding="utf-8")
        manifest["entrypoints"] = ["problem_only.py"]
        manifest["submission"].update(page_limit=30, anonymity=True)
        validate_manifest(manifest, self.root)
        for bad in ({"page_limit": 0}, {"page_limit": "30"}, {"anonymity": "yes"}, {"unknown": 1}):
            broken = default_manifest("t", 1)
            broken["entrypoints"] = ["problem_only.py"]
            broken["submission"].update(bad)
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                validate_manifest(broken, self.root)

    def test_declared_limits_do_not_block_an_initializer_rerun(self):
        self.declare(page_limit=30, anonymity=True)
        before = snapshot(self.root)
        result = run_tool("init_project.py", self.root, "--problems", 2, "--title", "中文测试 & 骨架")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, snapshot(self.root))
        # A genuinely different path layout must still be refused.
        path = self.root/"mathmodeling.json"
        data = read_json(path)
        data["submission"]["pdf"] = "paper/output/other.pdf"
        write_json(path, data)
        refused = run_tool("init_project.py", self.root, "--problems", 2, "--title", "中文测试 & 骨架")
        self.assertEqual(refused.returncode, 3, refused.stdout)

    def test_placeholder_and_unchecked_item_are_separate_findings(self):
        put(self.root, "docs/data_audit.md", "# 数据审计\n\n待补：字段与单位。\n")
        put(self.root, "docs/source_inventory.md", "# 清单\n\n| 状态 | 文件 |\n|---|---|\n| [ ] | 附件一 |\n")
        codes = self.codes()
        self.assertIn("DOC_PLACEHOLDER", codes)
        self.assertIn("DOC_UNCHECKED_ITEM", codes)


class LayoutWarningTests(unittest.TestCase):
    """Overfull boxes are ordinary in Chinese papers; only content loss may abort a build."""

    def test_warnings_are_classified_by_kind_and_magnitude(self):
        log = "\n".join([
            r"Missing character: There is no 中 in font [lmroman10-regular]!",
            r"LaTeX Warning: Reference `fig:one' on page 3 undefined on input line 42.",
            r"Overfull \hbox (45.77441pt too wide) in paragraph at lines 12--19",
            r"Overfull \hbox (0.51234pt too wide) in paragraph at lines 30--31",
            r"Underfull \hbox (badness 10000) in paragraph at lines 50--52",
            r"Float too large for page by 12.0pt on input line 60.",
        ])
        found = builder.classify_warnings(log)
        self.assertEqual(len(found["fatal"]), 2, found)
        self.assertTrue(any("45.77441pt" in x for x in found["material"]), found)
        self.assertTrue(any("Float too large" in x for x in found["material"]), found)
        self.assertTrue(any("0.51234pt" in x for x in found["minor"]), found)
        self.assertTrue(any("Underfull" in x for x in found["minor"]), found)
        self.assertFalse(any("Overfull" in x for x in found["fatal"]), found)

    def test_unmeasurable_overflow_stays_material(self):
        found = builder.classify_warnings(r"Overfull \vbox (too high) detected at line 7")
        self.assertTrue(found["material"], found)
        self.assertFalse(found["minor"], found)


@unittest.skipUnless(shutil.which("xelatex"), "XeLaTeX not installed")
class RealCompilationTests(unittest.TestCase):
    """The bundled template and a realistically overfull paper must both deliver a PDF."""

    WIDE_TABLE = "\n".join([
        r"\documentclass[UTF8,zihao=-4]{ctexart}",
        r"\usepackage[a4paper,top=2.5cm,bottom=2.5cm,left=2.5cm,right=2.5cm]{geometry}",
        r"\usepackage{amsmath,booktabs,array}",
        r"\begin{document}",
        r"\section{模型检验}",
        r"\begin{table}[htbp]\centering\caption{敏感性分析}",
        r"\begin{tabular}{p{3.1cm}p{3.1cm}p{3.1cm}p{3.1cm}p{3.1cm}}",
        r"\toprule",
        r"参数 & 基准值 & 下界 & 上界 & 结论 \\",
        r"\midrule",
        r"单位缺水成本 & 4.0 & 3.0 & 5.0 & 决策不变 \\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
        r"\end{document}",
        "",
    ])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)/"layout"
        if run_tool("init_project.py", self.root, "--problems", 1, "--title", "版面回归").returncode:
            self.skipTest("initializer unavailable")

    def tearDown(self):
        cleanup_temporary(self.temp)

    def test_bundled_template_compiles_without_layout_warnings(self):
        record = builder.build(self.root, timeout=300)
        self.assertEqual(record["status"], "compiled")
        self.assertGreaterEqual(record["pages"], 1)
        self.assertEqual(record["warnings"], [], "the shipped template must not overflow")
        self.assertEqual(record["minor_warnings"], [], record)

    def test_overfull_paper_still_delivers_a_pdf_and_records_the_warning(self):
        put(self.root, "paper/main.tex", self.WIDE_TABLE)
        record = builder.build(self.root, timeout=300)
        self.assertEqual(record["status"], "compiled")
        self.assertTrue((self.root/"paper/output/main.pdf").is_file())
        self.assertTrue(any("Overfull" in x for x in record["warnings"]), record)
        # The audit surfaces it as MAJOR, so the defect stays visible without
        # costing the team the source-to-PDF receipt.
        result = run_tool("audit_project.py", self.root, "--format", "json")
        self.assertIn("BUILD_WARNINGS", [x["code"] for x in json.loads(result.stdout)["issues"]])

    def test_strict_layout_restores_the_blocking_behaviour(self):
        put(self.root, "paper/main.tex", self.WIDE_TABLE)
        with self.assertRaises(RuntimeError):
            builder.build(self.root, timeout=300, strict_layout=True)
        self.assertFalse((self.root/"paper/output/main.pdf").exists())

    def test_replace_unowned_preserves_the_hand_published_pdf(self):
        destination = self.root/"paper/output/main.pdf"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"%PDF-1.4 hand published\n")
        with self.assertRaises(ValueError):
            builder.build(self.root, timeout=300)
        record = builder.build(self.root, timeout=300, replace_unowned=True)
        backup = self.root/record["replaced_unowned_backup"]
        self.assertEqual(backup.read_bytes(), b"%PDF-1.4 hand published\n")
        self.assertNotEqual(destination.read_bytes(), backup.read_bytes())

    def test_old_build_directories_are_pruned(self):
        builder.build(self.root, timeout=300, keep_builds=1)
        for index in range(3):
            (self.root/f"paper/build/run-stale{index}").mkdir(parents=True)
        builder.prune_builds(self.root/"paper/build", keep=1)
        self.assertEqual(len(list((self.root/"paper/build").glob("run-*"))), 1)


class ReferenceTests(unittest.TestCase):
    def test_invalid_numeric_metadata_is_not_finite(self):
        for value in (True, None, "1", float("inf"), float("nan"), 10**1000):
            self.assertFalse(is_numeric(value))
        self.assertTrue(is_numeric(0))
        self.assertTrue(is_numeric(1.25))

    def test_local_markdown_links_resolve_without_optional_specialists(self):
        for markdown in SKILL_ROOT.rglob("*.md"):
            for raw in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", markdown.read_text(encoding="utf-8")):
                target = raw.strip().split(maxsplit=1)[0].strip("<>")
                if target.startswith(("https://", "http://", "mailto:", "#")):
                    continue
                relative = unquote(target.split("#",1)[0])
                if relative:
                    self.assertTrue((markdown.parent/relative).resolve().exists(), f"{markdown}: {raw}")

    def test_unknown_project_and_invalid_audit_limits_are_controlled(self):
        with tempfile.TemporaryDirectory() as temporary:
            for extra in [["--problem-count", "0"], ["--max-files", "0"]]:
                result = run_tool("audit_project.py", temporary, *extra)
                self.assertEqual(result.returncode, 3)
                self.assertNotIn("Traceback", result.stderr)
            result = run_tool("audit_project.py", Path(temporary)/"missing")
            self.assertEqual(result.returncode, 3)


if __name__ == "__main__":
    unittest.main()
