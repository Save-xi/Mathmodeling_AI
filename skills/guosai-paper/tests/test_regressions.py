from __future__ import annotations
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location("regression_" + name, ROOT / "scripts" / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = result
    spec.loader.exec_module(result)
    return result


A = module("audit_style")
C = module("corpus_lookup")

# 写法规范的样例：含基线比较、百分点、保留代价与否定式边界，任何规则都不得命中。
WELL_WRITTEN_SAMPLE = """图~2 给出了在同一滚动划分下两种方法的预测误差分布。与季节性朴素基线相比，动态回归的 MAPE 由 12.4% 降至 9.8%，即下降 2.6 个百分点；同时单次求解时间由 3.2 s 增至 8.1 s。该结果支持动态回归在本题划分与指标下误差更低，但不能推出其在其他区域或更长预测期上同样有效。

将单位缺水成本在 3.0 至 5.0 元/吨范围内扰动，最优调度方案的取值未发生变化，目标值变化幅度不超过 1.8%。该检验支持模型在所测范围内对该参数较稳定，不能说明模型在所有工况下均可靠，因为扰动范围与分布未覆盖极端枯水情形。
"""


class AuditRegressionTests(unittest.TestCase):
    def rules(self, text, **kwargs):
        return {i.rule for i in A.audit_text(text, **kwargs)}

    def test_markdown_percent_does_not_hide_rest_of_line(self):
        self.assertIn("unfinished-placeholder", self.rules("误差为2.1%。结果为[待填：指标]。"))

    def test_tex_comments_and_escaped_percent_are_distinct(self):
        text = "% TODO 不属于正文\n误差为2.1\\%，结果为[待填：指标]。% TBD 注释\n"
        issues = A.audit_text(text, input_format="latex")
        self.assertEqual([(i.rule, i.line) for i in issues if i.rule == "unfinished-placeholder"],
                         [("unfinished-placeholder", 2)])
        self.assertNotIn("unfinished-placeholder", self.rules(r"误差为2.1\%。% TODO", input_format="latex"))

    def test_equation_or_figure_reference_stays_a_visible_cue(self):
        self.assertNotIn("evidence-free-inference", self.rules(r"图\ref{fig:trend}中的结果表明波峰逐步降低。"))
        self.assertNotIn("evidence-free-inference", self.rules(r"根据\eqref{eq:balance}，结果表明收支相等。"))

    def test_unrelated_number_no_longer_exempts_a_later_claim(self):
        rules = self.rules("本文处理3个问题。结果表明，该最优模型显著提高准确性。")
        self.assertIn("unsupported-strong-claim", rules)
        self.assertIn("evidence-free-inference", rules)
        self.assertIn("evidence-free-inference", self.rules("结果表明模型误差很小。"))

    def test_identification_keyword_is_never_a_truth_certificate(self):
        self.assertIn("causal-overclaim", self.rules("本文未进行干预试验。相关系数为0.61，证明存在因果关系。"))
        self.assertIn("causal-identification-review", self.rules("采用双重差分，结果证明存在因果效应。"))

    def test_explicit_negation_is_not_an_affirmative_overclaim(self):
        for text in ("现有结果不能证明因果关系。", "该结果不能证明模型的科学性。", "数据不表明存在因果关系。"):
            self.assertFalse({"causal-overclaim", "vague-validation"} & self.rules(text))
        self.assertIn("unsupported-strong-claim", self.rules("样本不多仍充分证明模型具有普适性。"))

    def test_code_is_excluded_but_prose_line_numbers_survive(self):
        text = "\x60\x60\x60python\n# TODO\n\x60\x60\x60\n\n结论为[待填：结果]。"
        found = [i for i in A.audit_text(text) if i.rule == "unfinished-placeholder"]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].line, 5)

    def test_qualitative_abstract_and_tex_math_result(self):
        text = "摘要\n问题一给出反例，问题二证明成立条件。\n关键词：约束"
        self.assertFalse([i for i in A.audit_text(text, abstract_kind="qualitative") if i.severity == "MAJOR"])
        tex = r"\begin{abstract}问题1得到误差$e=0.2$。\end{abstract}"
        self.assertNotIn("abstract-without-quantitative-result", self.rules(tex, abstract_kind="quantitative"))
        self.assertIn("abstract-without-quantitative-result", self.rules("摘要\n问题1报告结果。\n关键词：预测", abstract_kind="quantitative"))

    def test_visible_comparison_remains_manual_review(self):
        self.assertIn("strong-claim-evidence-review", self.rules("与基线相比，MAPE由12.4%降至9.8%，显著提高准确性。"))

    def test_time_limit_and_global_optimality_need_review(self):
        found = A.audit_text("TIME_LIMIT时返回可行方案。结果达到全局最优。")
        self.assertTrue(any(i.rule == "optimality-claim-review" and i.severity == "MAJOR" for i in found))

    def test_well_written_prose_stays_free_of_false_positives(self):
        self.assertEqual(A.audit_text(WELL_WRITTEN_SAMPLE), [])

    def test_bad_encoding_and_large_input_fail_without_replacement(self):
        with tempfile.TemporaryDirectory(prefix="审校 中文 ") as folder:
            p = Path(folder) / "稿件.md"
            for content in (b"\xff\xfe", b"a" * (A.MAX_BYTES + 1)):
                p.write_bytes(content)
                result = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "scripts/audit_style.py"), str(p)],
                                        capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(result.returncode, 2)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(p.read_bytes(), content)


class CorpusRegressionTests(unittest.TestCase):
    def test_no_action_and_list_do_not_extract(self):
        with tempfile.TemporaryDirectory(prefix="语料 中文 ") as folder:
            root = Path(folder)
            (root / "A.PDF").write_bytes(b"metadata-only")
            with patch.object(C, "load_papers", side_effect=AssertionError("must not extract")), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(C.main(["--corpus", str(root)]), 0)
                self.assertEqual(C.main(["--corpus", str(root), "--list"]), 0)
            self.assertEqual(C.inventory(root), [root / "A.PDF"])

    def test_ambiguous_selection_fails_before_any_extraction(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ("B1.pdf", "B2.pdf"):
                (root / name).touch()
            with patch.object(C, "load_papers", side_effect=AssertionError("must not extract")), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as caught:
                    C.main(["--corpus", str(root), "--abstract", "B"])
                self.assertEqual(caught.exception.code, 2)

    def test_abstract_filters_before_loading_and_keeps_boundary(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / "B1.pdf"
            target.touch()
            (root / "B2.pdf").touch()
            paper = {"file":"B1.pdf", "year":"2023", "backend":"pdftotext", "usable":True,
                     "text":"标题\n摘要\n这里的摘要结果为1.2%。\n关键词\n优化\n正文"}
            out = io.StringIO()
            with patch.object(C, "load_papers", return_value=[paper]) as loader, contextlib.redirect_stdout(out):
                self.assertEqual(C.main(["--corpus", str(root), "--abstract", "B1"]), 0)
            self.assertEqual(loader.call_args.args[2], [target])
            self.assertNotIn("正文", out.getvalue())

    def test_missing_corpus_is_not_a_false_zero_count(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(RuntimeError):
                C.inventory(Path(folder) / "missing")
            with self.assertRaises(RuntimeError):
                C.inventory(Path(folder))

    def test_loading_preserves_raw_lines_and_pdf_pages(self):
        raw = "标题\n摘要\n结果1.2%。\n关键词\n预测\f第二页结果。"
        path = Path("2023国赛优秀论文/B1.pdf")
        with patch.object(C, "resolve_backends", return_value=["pdftotext"]), patch.object(C, "cached_extract", return_value=raw):
            with tempfile.TemporaryDirectory() as folder:
                papers = C.load_papers(Path(folder), "pdftotext", [path])
        self.assertEqual(papers[0]["text"], raw)
        self.assertEqual(len(papers[0]["pages"]), 2)
        self.assertNotIn("关键词", C.abstract_of(papers[0]["text"]))

    def test_grep_reports_correct_page_and_keeps_late_match_in_excerpt(self):
        sentence = "背景" * 200 + "触发位置显示变化明显且仍须结合原图解释。"
        paper = {"file":"样本.pdf", "year":"2025", "backend":"pdftotext", "usable":True,
                 "text":"第一页\f"+sentence, "pages":["第一页",sentence]}
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            C.cmd_grep([paper], "触发位置", 1, "full")
        self.assertIn("PDF p.2", out.getvalue())
        self.assertIn("触发位置", out.getvalue())

    def test_failed_primary_backend_is_recorded_with_fallback(self):
        raw = "模型用于描述系统状态并输出结果。" * 1200
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(C, "resolve_backends", return_value=["pdftotext", "pypdf"]), patch.object(C, "cached_extract", side_effect=[subprocess.TimeoutExpired("pdftotext",30),raw]):
                paper = C.load_papers(Path(folder), "auto", [Path("2025/A.pdf")])[0]
        self.assertEqual(paper["backend"], "pypdf")
        self.assertTrue(paper["extraction_errors"])
        self.assertTrue(paper["usable"])

    def test_pypdf_worker_is_bounded_and_preserves_page_separator(self):
        result = subprocess.CompletedProcess([],0,stdout="第一页\f第二页".encode(),stderr=b"")
        with patch.object(C.subprocess, "run", return_value=result) as call:
            self.assertEqual(C.extract_pypdf(Path("样本.pdf")), "第一页\f第二页")
        self.assertEqual(call.call_args.kwargs["timeout"], 30)

    def test_corrupt_cache_is_rebuilt_without_changing_pdf(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pdf = root / "资料.pdf"
            pdf.write_bytes(b"source")
            cache = root / (C._cache_key(pdf, "pdftotext") + ".json")
            cache.write_text(json.dumps({"schema":C.CACHE_SCHEMA,"backend":"pdftotext","text":4}),encoding="utf-8")
            with patch.object(C, "extract_pdftotext", return_value="recovered"):
                self.assertEqual(C.cached_extract(pdf,"pdftotext",root),"recovered")
            self.assertEqual(pdf.read_bytes(), b"source")


if __name__ == "__main__":
    unittest.main()
