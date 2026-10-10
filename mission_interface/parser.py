from __future__ import annotations

import hashlib
import re

from .models import MissionContract


PROTOCOL_VERSION = "1.0"
NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)"
CLEARANCE = re.compile(
    rf"(?:keep|maintain) ({NUMBER}) (?:m|meters?|metres?) "
    r"(?:from obstacles|(?:obstacle )?clearance)"
)
MISSION = re.compile(
    r"(inspect|search|move|navigate)(?: (slowly|fast))? "
    r"(?:(?:to|through) )?(?:the )?"
    r"(corridor|target area|indoor test area|test area|indoor area)"
    r"(?: (slowly|fast|at (?:low|normal|high) speed))?"
)
RETURN = re.compile(
    r"return(?: home| to home)? (?:if (?:the )?(?:link|communication) is lost|"
    r"on (?:link|communication) loss)"
)
STOP = re.compile(r"stop (?:if lidar confidence is low|on low lidar confidence)")
REPORT = re.compile(r"(?:generate|provide|write) (?:a )?report")


def _clauses(text: str) -> list[str]:
    normalized = " ".join(text.strip().lower().split()).rstrip(".")
    # Decimal points are not sentence delimiters. Unknown/negated clauses fail below.
    return re.split(r",\s*(?:and\s+)?|\s+and\s+|;\s*", normalized)


def parse_clearance(text: str) -> float:
    matches = [CLEARANCE.fullmatch(clause) for clause in _clauses(text)]
    values = [float(match.group(1)) for match in matches if match]
    if len(values) > 1:
        raise ValueError("Specify obstacle clearance exactly once")
    return values[0] if values else float("nan")


def _mission_id(text: str) -> str:
    normalized = " ".join(text.strip().lower().split())
    return "mission-" + hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]


def parse_instruction(text: str) -> MissionContract:
    """Parse complete supported clauses; reject unmatched or duplicate clauses."""
    found: dict[str, object] = {}
    for clause in _clauses(text):
        mission = MISSION.fullmatch(clause)
        clearance = CLEARANCE.fullmatch(clause)
        if mission:
            kind, value = "mission", mission
        elif clearance:
            kind, value = "clearance", float(clearance.group(1))
        elif RETURN.fullmatch(clause):
            kind, value = "return", True
        elif STOP.fullmatch(clause):
            kind, value = "stop", True
        elif REPORT.fullmatch(clause):
            kind, value = "report", True
        else:
            raise ValueError(f"Unsupported or ambiguous clause: {clause!r}")
        if kind in found:
            raise ValueError(f"Specify {kind} exactly once")
        found[kind] = value
    mission = found.get("mission")
    if mission is None:
        raise ValueError("An explicit supported mission clause is required")
    verb, before_speed, target, after_speed = mission.groups()
    if before_speed and after_speed:
        raise ValueError("Specify speed exactly once")
    speed = before_speed or after_speed or "at normal speed"
    speed_mode = "low" if speed in ("slowly", "at low speed") else (
        "high" if speed in ("fast", "at high speed") else "normal"
    )
    return MissionContract(
        protocol_version=PROTOCOL_VERSION,
        mission_id=_mission_id(text),
        mission_type={"inspect": "inspection", "search": "search", "move": "navigation", "navigate": "navigation"}[verb],
        target_area={"corridor": "corridor", "target area": "target_area"}.get(target, "indoor_test_area"),
        speed_mode=speed_mode,
        min_obstacle_clearance_m=found.get("clearance", float("nan")),
        return_to_home_on_link_loss="return" in found,
        stop_on_low_lidar_confidence="stop" in found,
        report_required="report" in found,
        source_instruction=text,
    )
