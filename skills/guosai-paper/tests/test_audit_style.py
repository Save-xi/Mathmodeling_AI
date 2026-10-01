from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_style.py"
SPEC = importlib.util.spec_from_file_location("audit_style", SCRIPT)
assert SPEC and SPEC.loader
AUDIT_STYLE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT_STYLE
SPEC.loader.exec_module(AUDIT_STYLE)

# references/results-and-style.md 的“常见空泛表达”表列出的写法，逐条要求工具自身能够命中。
DOCUMENTED_VAGUE_PHRASINGS = (
    "模型显著提高准确性",
    "验证了模型的科学性",
    "由图可知效果很好",
    "由图3可知，模型效果很好",
    "该模型推广性很强，可以广泛应用于其他实际问题",
    "本文采用多种算法对该问题进行求解",
    "两者高度相关，因此存在因果关系",
    "投资额与产出显著正相关，因此增加投资能够有效提升产出",
    "本文方法准确性有较大提升，充分说明了模型的优越性",
    "本文改进的遗传算法收敛更快，寻优能力更强",
)


class AuditStyleTests(unittest.TestCase):
    def rules(self, text: str, max_han: int = 80) -> set[str]:
        return {issue.rule for issue in AUDIT_STYLE.audit_text(text, max_han=max_han)}

    def test_metric_qualified_comparison_is_not_unsupported(self) -> None:
        text = (
            "在相同时间划分与评价指标下，与周期朴素基线相比，"
            "模型的MAPE由12.4%降至9.8%，改善幅度为2.6个百分点。"
        )
        rules = self.rules(text)
        self.assertNotIn("unsupported-strong-claim", rules)
        self.assertNotIn("evidence-free-inference", rules)

    def test_vague_strong_claim_is_flagged(self) -> None:
        text = "结果表明，该最优模型显著提高了准确性，并充分证明了模型的科学性。"
        rules = self.rules(text)
        self.assertIn("unsupported-strong-claim", rules)
        self.assertIn("evidence-free-inference", rules)
        self.assertIn("vague-validation", rules)

    def test_causal_overclaim_without_identification_is_flagged(self) -> None:
        text = "相关系数为0.61，因此结果表明价格变化与销量之间存在因果关系。"
        self.assertIn("causal-overclaim", self.rules(text))

    def test_placeholder_is_blocker(self) -> None:
        issues = AUDIT_STYLE.audit_text("结果见[待填：表号与指标]。")
        self.assertTrue(
            any(
                issue.rule == "unfinished-placeholder" and issue.severity == "BLOCKER"
                for issue in issues
            )
        )

    def test_domain_xx_and_normal_figure_sentence_are_not_placeholders(self) -> None:
        text = (
            "女胎的性染色体为XX。为了展示结果，得到如下三维视觉图。"
            "完整结果保存在问题二结果表.xlsx中。"
        )
        self.assertNotIn("unfinished-placeholder", self.rules(text))

    def test_long_sentence_threshold_is_configurable(self) -> None:
        text = "在给定条件下，" + "模型用于描述系统状态并输出决策结果" * 8 + "。"
        self.assertIn("long-sentence", self.rules(text, max_han=40))

    def test_cli_json_and_strict_exit_code(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.md"
            path.write_text(
                "结果表明，该最优模型显著提高了准确性。\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "-X",
                    "utf8",
                    str(SCRIPT),
                    str(path),
                    "--format",
                    "json",
                    "--strict",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(completed.returncode, 2)
            payload = json.loads(completed.stdout)
            self.assertTrue(payload["issues"])
            self.assertIn("verification_boundary", payload)

    def test_documented_vague_phrasings_are_all_detected(self) -> None:
        for phrase in DOCUMENTED_VAGUE_PHRASINGS:
            with self.subTest(phrase=phrase):
                self.assertTrue(
                    AUDIT_STYLE.audit_text(phrase),
                    "参考文档列出的空泛写法未被任何规则命中",
                )

    def test_numbered_reference_is_not_an_inference_loophole(self) -> None:
        self.assertIn("evidence-free-inference", self.rules("由图三可知，模型效果符合预期。"))

    def test_correlation_to_causation_needs_an_identification_design(self) -> None:
        rules = self.rules("投资额与产出显著正相关，因此增加投资能够有效提升产出。")
        self.assertIn("correlation-to-causation", rules)
        self.assertNotIn(
            "correlation-to-causation",
            self.rules("在双重差分设定下，投资额与产出显著正相关，因此增加投资能够提升产出。"),
        )
        self.assertNotIn(
            "correlation-to-causation",
            self.rules("两者虽然高度相关，但不能因此断定增加投资能够提升产出。"),
        )

    def test_improvement_claim_without_baseline_is_flagged(self) -> None:
        self.assertIn("unbaselined-improvement", self.rules("本文改进的遗传算法收敛更快，寻优能力更强。"))
        self.assertNotIn(
            "unbaselined-improvement",
            self.rules("与遗传算法基线相比，改进后的收敛步数由120降至85。"),
        )

    def test_terminology_inconsistency_is_reported_once_per_document(self) -> None:
        text = (
            "问题一给出模型。问题2给出求解。问题三给出结论。"
            "第一问结果稳定。第二问误差较小。第三问给出建议。"
        )
        found = [issue for issue in AUDIT_STYLE.audit_text(text) if issue.rule == "terminology-inconsistency"]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].severity, "MINOR")
        self.assertIn("3", found[0].message)
        self.assertNotIn(
            "terminology-inconsistency",
            self.rules("问题一给出模型。问题二给出求解。第一问结果稳定。"),
        )


    def test_section_star_abstract_heading_is_detected(self):
        r"""Several official CUMCM templates use \section*{摘要} instead of an environment."""
        tex = "\n".join([
            r"\section*{摘要}",
            "本文针对供水调度问题建立模型，并给出定性判断与反例。",
            r"\textbf{关键词：}调度",
            "",
        ])
        rules = {issue.rule for issue in AUDIT_STYLE.audit_text(tex, input_format="latex")}
        self.assertIn("abstract-result-review", rules)

    def test_punctuation_check_is_opt_in_and_precise(self):
        mixed = "本文建立模型,并给出结果;结论如下:"
        self.assertNotIn("punctuation-mixing", {i.rule for i in AUDIT_STYLE.audit_text(mixed)})
        self.assertIn("punctuation-mixing",
                      {i.rule for i in AUDIT_STYLE.audit_text(mixed, check_punctuation=True)})
        for clean in ("本文建立模型，并给出结果；结论如下：",
                      "求解器状态为 OPTIMAL, gap = 0.4%。",
                      "在同一划分下，MAPE 由 12.4% 降至 9.8%。"):
            with self.subTest(text=clean):
                self.assertNotIn("punctuation-mixing",
                                 {i.rule for i in AUDIT_STYLE.audit_text(clean, check_punctuation=True)})


if __name__ == "__main__":
    unittest.main()

