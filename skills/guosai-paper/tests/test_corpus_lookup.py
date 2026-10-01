from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "corpus_lookup.py"
SPEC = importlib.util.spec_from_file_location("corpus_lookup", SCRIPT)
assert SPEC and SPEC.loader
CORPUS_LOOKUP = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CORPUS_LOOKUP
SPEC.loader.exec_module(CORPUS_LOOKUP)


class CorpusLookupTests(unittest.TestCase):
    def test_quality_gate_accepts_full_chinese_text(self) -> None:
        text = "模型用于描述系统状态并输出决策结果。" * 1200
        quality = CORPUS_LOOKUP.text_quality(text)
        self.assertTrue(quality["usable"])
        self.assertGreaterEqual(quality["han"], 5000)

    def test_quality_gate_rejects_watermark_text(self) -> None:
        text = ("数模加油站" * 20) + ("模型用于描述系统状态。" * 1200)
        quality = CORPUS_LOOKUP.text_quality(text)
        self.assertFalse(quality["usable"])
        self.assertGreaterEqual(quality["watermark"], 8)

    def test_abstract_extraction_stops_at_keywords(self) -> None:
        text = (
            "题目\n摘要：以单品编码为关键字，通过统计得到误差为2.1%。"
            "关键词：优化；检验\n正文"
        )
        abstract = CORPUS_LOOKUP.abstract_of(text)
        self.assertIn("2.1%", abstract)
        self.assertIn("关键字", abstract)
        self.assertNotIn("优化；检验", abstract)
        self.assertNotIn("正文", abstract)

    def test_abstract_extraction_accepts_colonless_keyword_header(self) -> None:
        text = "题目\n摘要\n得到误差为1.8%。\n关键词\n优化；检验\n正文"
        abstract = CORPUS_LOOKUP.abstract_of(text)
        self.assertIn("1.8%", abstract)
        self.assertNotIn("优化；检验", abstract)
        self.assertNotIn("正文", abstract)

    def test_candidate_selection_prefers_usable_text(self) -> None:
        bad = {
            "backend": "pdftotext",
            "text": "短文本",
            "quality": CORPUS_LOOKUP.text_quality("短文本"),
        }
        good_text = "模型用于描述系统状态并输出决策结果。" * 1200
        good = {
            "backend": "pypdf",
            "text": good_text,
            "quality": CORPUS_LOOKUP.text_quality(good_text),
        }
        chosen = CORPUS_LOOKUP.choose_candidate([bad, good])
        self.assertEqual(chosen["backend"], "pypdf")

    def test_auto_backend_order_is_poppler_then_pypdf(self) -> None:
        with (
            patch.object(CORPUS_LOOKUP.shutil, "which", return_value="pdftotext"),
            patch.object(CORPUS_LOOKUP, "_pypdf_available", return_value=True),
        ):
            self.assertEqual(
                CORPUS_LOOKUP.resolve_backends("auto"),
                ["pdftotext", "pypdf"],
            )

    def test_grep_reports_backend_and_source(self) -> None:
        text = (
            "模型用于描述系统状态并输出决策结果。" * 1200
            + "灵敏度分析显示该指标在测试范围内保持稳定。"
        )
        paper = {
            "year": "2025",
            "file": "sample.pdf",
            "backend": "pdftotext",
            "text": text,
            "usable": True,
        }
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            CORPUS_LOOKUP.cmd_grep([paper], "灵敏度", 2, "full")
        rendered = output.getvalue()
        self.assertIn("sample.pdf", rendered)
        self.assertIn("pdftotext", rendered)


if __name__ == "__main__":
    unittest.main()
