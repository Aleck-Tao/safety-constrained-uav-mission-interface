from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class MissionContract:
    protocol_version: str
    mission_id: str
    mission_type: str
    target_area: str
    speed_mode: str
    min_obstacle_clearance_m: float
    return_to_home_on_link_loss: bool
    stop_on_low_lidar_confidence: bool
    report_required: bool
    source_instruction: str

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        if not math.isfinite(self.min_obstacle_clearance_m):
            value["min_obstacle_clearance_m"] = None
        return value

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "MissionContract":
        return cls(
            protocol_version=str(value.get("protocol_version", "")),
            mission_id=str(value.get("mission_id", "")),
            mission_type=str(value.get("mission_type", "unknown")),
            target_area=str(value.get("target_area", "unknown")),
            speed_mode=str(value.get("speed_mode", "unknown")),
            min_obstacle_clearance_m=(
                float(value["min_obstacle_clearance_m"])
                if value.get("min_obstacle_clearance_m") is not None
                else float("nan")
            ),
            return_to_home_on_link_loss=bool(value.get("return_to_home_on_link_loss", False)),
            stop_on_low_lidar_confidence=bool(value.get("stop_on_low_lidar_confidence", False)),
            report_required=bool(value.get("report_required", False)),
            source_instruction=str(value.get("source_instruction", "")),
        )


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class ValidationReport:
    accepted: bool
    contract: MissionContract
    issues: tuple[ValidationIssue, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "contract": self.contract.to_dict(),
            "issues": [issue.to_dict() for issue in self.issues],
        }
