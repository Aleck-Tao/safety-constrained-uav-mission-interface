from __future__ import annotations

import math
from dataclasses import asdict, dataclass, fields
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
        if not isinstance(value, dict):
            raise ValueError("Contract must be a JSON object")
        required = {field.name for field in fields(cls)}
        if set(value) != required:
            raise ValueError(f"Contract fields differ: missing={sorted(required - set(value))}, unexpected={sorted(set(value) - required)}")
        booleans = {"return_to_home_on_link_loss", "stop_on_low_lidar_confidence", "report_required"}
        for name in sorted(required):
            item = value[name]
            if name in booleans:
                if type(item) is not bool:
                    raise ValueError(f"{name} must be a JSON boolean")
            elif name == "min_obstacle_clearance_m":
                if type(item) not in (int, float) or not math.isfinite(item):
                    raise ValueError(f"{name} must be a finite JSON number")
            elif not isinstance(item, str) or not item.strip():
                raise ValueError(f"{name} must be a nonempty JSON string")
        return cls(**value)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class ValidationReport:
    accepted: bool
    contract: MissionContract | None
    issues: tuple[ValidationIssue, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "contract": self.contract.to_dict() if self.contract is not None else None,
            "issues": [issue.to_dict() for issue in self.issues],
        }
