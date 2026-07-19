from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path

from mission_interface.cli import main
from mission_interface.models import MissionContract
from mission_interface.parser import parse_clearance, parse_instruction
from mission_interface.policy import compile_instruction, load_policy, validate_contract


SAFE = (
    "Inspect the corridor at low speed, keep 1.5 metres from obstacles, "
    "return if the link is lost, stop if LiDAR confidence is low, and generate a report."
)


class MissionInterfaceTests(unittest.TestCase):
    def test_safe_instruction_is_accepted(self) -> None:
        report = compile_instruction(SAFE)
        self.assertTrue(report.accepted)
        self.assertEqual(report.issues, ())
        self.assertEqual(report.contract.target_area, "corridor")

    def test_unsafe_instruction_is_blocked_for_four_reasons(self) -> None:
        report = compile_instruction("Move fast through the corridor and keep 0.4 m from obstacles.")
        codes = {issue.code for issue in report.issues}
        self.assertEqual(
            codes,
            {"CLEARANCE_LOW", "SPEED_MODE", "LINK_LOSS_BEHAVIOR", "LOW_CONFIDENCE_BEHAVIOR"},
        )

    def test_missing_clearance_fails_closed(self) -> None:
        report = compile_instruction(
            "Inspect the corridor slowly, return if the link is lost, and stop if LiDAR confidence is low."
        )
        self.assertTrue(math.isnan(report.contract.min_obstacle_clearance_m))
        self.assertIn("CLEARANCE_MISSING", {issue.code for issue in report.issues})

    def test_mission_id_is_stable_for_whitespace_and_case(self) -> None:
        first = parse_instruction(SAFE).mission_id
        second = parse_instruction("  " + SAFE.upper().replace(" ", "   ") + "  ").mission_id
        self.assertEqual(first, second)

    def test_metric_clearance_variants(self) -> None:
        self.assertEqual(parse_clearance("keep 2 metres clearance"), 2.0)
        self.assertEqual(parse_clearance("keep 0.75 m clearance"), 0.75)

    def test_contract_round_trip(self) -> None:
        contract = parse_instruction(SAFE)
        self.assertEqual(MissionContract.from_dict(contract.to_dict()), contract)
        self.assertTrue(validate_contract(contract, load_policy()).accepted)

    def test_batch_cli_writes_stable_summary(self) -> None:
        commands = Path(__file__).resolve().parents[1] / "examples" / "mission_commands.txt"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "batch.json"
            self.assertEqual(main(["batch", str(commands), "--out", str(output)]), 0)
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result["summary"], {"total": 3, "accepted": 2, "blocked": 1})


if __name__ == "__main__":
    unittest.main()
