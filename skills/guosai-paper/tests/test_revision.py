from __future__ import annotations
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check_revision.py"
spec = importlib.util.spec_from_file_location("revision", SCRIPT)
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)


class RevisionTests(unittest.TestCase):
    def test_safe_word_order_and_spacing(self):
        a = r"由图\ref{f}可知，误差为2.1\%，时间为3.2\,s。"
        b = r"误差为2.1%，时间为3.2 s（见图\ref{f}）。"
        self.assertEqual(R.compare_texts(a,b)["status"], "NO_TOKEN_DIFFERENCE")

    def test_changed_math_reference_and_sign_are_visible(self):
        a = r"$g(x)\ge0$，值为-3.2，见表\ref{t1}。"
        b = r"$g(x)\le0$，值为3.2，见表\ref{t2}。"
        changes = R.compare_texts(a,b)["changes"]
        self.assertTrue({"math","references","numbers"} <= changes.keys())

    def test_unit_and_solver_status_change_are_visible(self):
        changes = R.compare_texts("TIME_LIMIT，成本3.2万元。","OPTIMAL，成本3.2元。")["changes"]
        self.assertTrue({"quantities","identifiers"} <= changes.keys())

    def test_percentage_points_are_not_silently_normalized(self):
        self.assertEqual(R.compare_texts("降低2.6%。","降低2.6个百分点。")["status"],"REVIEW_CHANGES")

    def test_semantic_swap_is_an_explicit_tool_limit(self):
        result = R.compare_texts("A=3，B=5。","A=5，B=3。")
        self.assertEqual(result["status"],"NO_TOKEN_DIFFERENCE")
        self.assertIn("swapped subjects",result["verification_boundary"])

    def test_unicode_cli_strict_is_read_only(self):
        with tempfile.TemporaryDirectory(prefix="改写 中文 ") as folder:
            before, after = Path(folder)/"原稿.tex",Path(folder)/"改稿.tex"
            before.write_text("结果为1.2%。",encoding="utf-8")
            after.write_text("结果为2.1%。",encoding="utf-8")
            saved = [p.read_bytes() for p in (before,after)]
            result = subprocess.run([sys.executable,"-X","utf8",str(SCRIPT),str(before),str(after),"--strict"],
                                    capture_output=True,text=True,encoding="utf-8")
            self.assertEqual(result.returncode,2)
            self.assertEqual([p.read_bytes() for p in (before,after)],saved)
            self.assertEqual(len(list(Path(folder).iterdir())),2)


if __name__ == "__main__":
    unittest.main()
