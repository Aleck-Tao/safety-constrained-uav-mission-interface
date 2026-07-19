from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from .models import MissionContract, ValidationIssue, ValidationReport
from .parser import parse_instruction


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = PROJECT_ROOT / "config" / "safety_policy.json"


def load_policy(path: Path = DEFAULT_POLICY) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_contract(contract: MissionContract, policy: dict[str, Any]) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if contract.protocol_version != str(policy["protocol_version"]):
        issues.append(ValidationIssue("PROTOCOL_VERSION", "Unsupported or missing protocol version"))
    if not contract.mission_id:
        issues.append(ValidationIssue("MISSION_ID", "Mission ID is required"))
    if contract.mission_type not in policy["allowed_mission_types"]:
        issues.append(ValidationIssue("MISSION_TYPE", f"Unsupported mission type: {contract.mission_type}"))
    if contract.target_area in policy["blocked_target_values"]:
        issues.append(ValidationIssue("TARGET_AREA", "Target area is missing or ambiguous"))
    if contract.speed_mode not in policy["allowed_speed_modes"]:
        issues.append(ValidationIssue("SPEED_MODE", f"Unsupported speed mode: {contract.speed_mode}"))

    clearance = contract.min_obstacle_clearance_m
    if not math.isfinite(clearance):
        issues.append(ValidationIssue("CLEARANCE_MISSING", "Explicit obstacle clearance is required"))
    else:
        if clearance < float(policy["min_clearance_m"]):
            issues.append(ValidationIssue("CLEARANCE_LOW", f"Obstacle clearance too low: {clearance:.2f} m"))
        if clearance > float(policy["max_clearance_m"]):
            issues.append(ValidationIssue("CLEARANCE_HIGH", f"Obstacle clearance is outside the supported range: {clearance:.2f} m"))

    if policy["require_link_loss_return"] and not contract.return_to_home_on_link_loss:
        issues.append(ValidationIssue("LINK_LOSS_BEHAVIOR", "Return-to-home behavior is required for link loss"))
    if policy["require_low_confidence_stop"] and not contract.stop_on_low_lidar_confidence:
        issues.append(ValidationIssue("LOW_CONFIDENCE_BEHAVIOR", "Stop behavior is required for low LiDAR confidence"))

    return ValidationReport(accepted=not issues, contract=contract, issues=tuple(issues))


def compile_instruction(text: str, policy: dict[str, Any] | None = None) -> ValidationReport:
    return validate_contract(parse_instruction(text), policy or load_policy())
