import json
import tempfile
import unittest
from pathlib import Path

from mission_interface.cli import main
from mission_interface.parser import parse_instruction
from mission_interface.policy import compile_instruction


SAFE = ("Inspect the corridor at low speed, keep 1.5 metres from obstacles, "
        "return if the link is lost, stop if LiDAR confidence is low, and generate a report.")


class InputBoundaryTests(unittest.TestCase):
    def test_negated_conflicting_and_unrelated_clauses_are_blocked(self):
        cases = [
            SAFE.replace("return if", "do not return if"),
            SAFE.replace("stop if", "do not stop if"),
            SAFE.replace("return if", "continue if"),
            SAFE.replace("stop if", "continue if"),
            SAFE.replace("Inspect", "Do not inspect"),
            SAFE.replace("low speed", "low speed or high speed"),
            SAFE.replace("keep 1.5 metres", "move 1.5 metres"),
            SAFE.replace("keep 1.5 metres", "travel 10 metres and keep 1.5 metres"),
            SAFE.replace("keep 1.5 metres from obstacles", "keep 1.5 metres from obstacles and keep 0.4 m clearance"),
            SAFE + " Do not return home.",
        ]
        for instruction in cases:
            with self.subTest(instruction=instruction):
                report = compile_instruction(instruction)
                self.assertFalse(report.accepted)
                self.assertEqual(report.issues[0].code, "INSTRUCTION_SYNTAX")

    def test_signed_clearance_is_not_made_positive(self):
        report = compile_instruction(SAFE.replace("1.5", "-1.5"))
        self.assertFalse(report.accepted)
        self.assertEqual(report.contract.min_obstacle_clearance_m, -1.5)
        self.assertIn("CLEARANCE_LOW", {issue.code for issue in report.issues})

    def test_validate_cli_rejects_bad_types_and_malformed_json(self):
        contract = parse_instruction(SAFE).to_dict()
        cases = []
        for field in ("return_to_home_on_link_loss", "stop_on_low_lidar_confidence", "report_required"):
            for value in ("false", "true", 1, 0, None, [], {}):
                cases.append(json.dumps({**contract, field: value}))
        for value in ("1.5", True, None, float("nan"), float("inf"), 10**1000, -(10**1000)):
            cases.append(json.dumps({**contract, "min_obstacle_clearance_m": value}))
        cases.extend(["[]", "null", "{", json.dumps({**contract, "unknown": 1}), "{}"])
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "contract.json", Path(directory) / "report.json"
            for payload in cases:
                with self.subTest(payload=payload):
                    source.write_text(payload, encoding="utf-8")
                    self.assertEqual(main(["validate", str(source), "--out", str(output)]), 2)
                    report = json.loads(output.read_text(encoding="utf-8"))
                    self.assertFalse(report["accepted"])
                    self.assertIsNone(report["contract"])
                    self.assertEqual(report["issues"][0]["code"], "CONTRACT_INPUT")

    def test_compile_cli_returns_structured_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            self.assertEqual(main(["compile", SAFE.replace("return if", "never return if"), "--out", str(output)]), 2)
            self.assertEqual(json.loads(output.read_text())["issues"][0]["code"], "INSTRUCTION_SYNTAX")

    def test_actual_false_remains_false_and_policy_rejects(self):
        contract = parse_instruction(SAFE).to_dict()
        contract["return_to_home_on_link_loss"] = False
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "contract.json", Path(directory) / "report.json"
            source.write_text(json.dumps(contract), encoding="utf-8")
            self.assertEqual(main(["validate", str(source), "--out", str(output)]), 2)
            report = json.loads(output.read_text())
            self.assertIs(report["contract"]["return_to_home_on_link_loss"], False)
            self.assertEqual(report["issues"][0]["code"], "LINK_LOSS_BEHAVIOR")
