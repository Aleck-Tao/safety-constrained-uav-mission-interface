from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .models import MissionContract
from .policy import DEFAULT_POLICY, compile_instruction, load_policy, validate_contract


def _write_json(value: dict[str, Any], path: Path | None) -> None:
    content = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    else:
        print(content, end="")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compile and validate safety-constrained UAV mission contracts")
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    subparsers = parser.add_subparsers(dest="command", required=True)

    compile_command = subparsers.add_parser("compile", help="parse and validate one instruction")
    compile_command.add_argument("instruction")
    compile_command.add_argument("--out", type=Path)

    validate_command = subparsers.add_parser("validate", help="validate a JSON contract")
    validate_command.add_argument("contract", type=Path)
    validate_command.add_argument("--out", type=Path)

    batch_command = subparsers.add_parser("batch", help="compile non-empty instruction lines")
    batch_command.add_argument("instructions", type=Path)
    batch_command.add_argument("--out", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    policy = load_policy(args.policy)
    if args.command == "compile":
        report = compile_instruction(args.instruction, policy)
        _write_json(report.to_dict(), args.out)
        return 0 if report.accepted else 2
    if args.command == "validate":
        contract = MissionContract.from_dict(json.loads(args.contract.read_text(encoding="utf-8")))
        report = validate_contract(contract, policy)
        _write_json(report.to_dict(), args.out)
        return 0 if report.accepted else 2

    instructions = [
        line.strip()
        for line in args.instructions.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    reports = [compile_instruction(instruction, policy) for instruction in instructions]
    payload = {
        "summary": {
            "total": len(reports),
            "accepted": sum(report.accepted for report in reports),
            "blocked": sum(not report.accepted for report in reports),
        },
        "reports": [report.to_dict() for report in reports],
    }
    _write_json(payload, args.out)
    return 0
