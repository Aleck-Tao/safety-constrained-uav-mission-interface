from __future__ import annotations

import hashlib
import re

from .models import MissionContract


PROTOCOL_VERSION = "1.0"


def parse_clearance(text: str) -> float:
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:m|meter|metre|meters|metres)\b", text, re.IGNORECASE)
    return float(match.group(1)) if match else float("nan")


def _mission_id(text: str) -> str:
    normalized = " ".join(text.strip().lower().split())
    return "mission-" + hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]


def parse_instruction(text: str) -> MissionContract:
    lower = text.lower()
    target_area = "unknown"
    if "corridor" in lower:
        target_area = "corridor"
    elif "target area" in lower:
        target_area = "target_area"
    elif "indoor" in lower or "test area" in lower:
        target_area = "indoor_test_area"

    mission_type = "unknown"
    if "search" in lower:
        mission_type = "search"
    elif "inspect" in lower:
        mission_type = "inspection"
    elif "move" in lower or "navigate" in lower:
        mission_type = "navigation"

    speed_mode = "normal"
    if "low speed" in lower or "slow" in lower:
        speed_mode = "low"
    elif "fast" in lower or "high speed" in lower:
        speed_mode = "high"

    return MissionContract(
        protocol_version=PROTOCOL_VERSION,
        mission_id=_mission_id(text),
        mission_type=mission_type,
        target_area=target_area,
        speed_mode=speed_mode,
        min_obstacle_clearance_m=parse_clearance(text),
        return_to_home_on_link_loss=(
            ("link" in lower or "communication" in lower or "starlink" in lower)
            and ("unstable" in lower or "loss" in lower or "lost" in lower)
        ),
        stop_on_low_lidar_confidence=(
            "low lidar confidence" in lower or "confidence is low" in lower
        ),
        report_required=("report" in lower or "describe" in lower or "generate" in lower),
        source_instruction=text,
    )
