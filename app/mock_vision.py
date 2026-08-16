from dataclasses import dataclass


@dataclass(frozen=True)
class VisionResult:
    face_detected: bool
    quality_score: float
    liveness_score: float
    employee_id: str | None
    match_score: float
    second_best_score: float


SCENARIOS = {
    "e-1001": VisionResult(True, 0.91, 0.96, "emp-4821", 0.88, 0.65),
    "e-1002": VisionResult(True, 0.42, 0.90, None, 0.76, 0.59),
    "e-1003": VisionResult(True, 0.88, 0.21, None, 0.91, 0.51),
    "e-1004": VisionResult(True, 0.78, 0.94, "emp-1021", 0.82, 0.79),
    "e-1005": VisionResult(True, 0.92, 0.97, "emp-9001", 0.90, 0.61),
}

UNKNOWN_RESULT = VisionResult(False, 0.0, 0.0, None, 0.0, 0.0)


def process_event(event_id: str) -> VisionResult:
    """Imitate detection, quality, liveness, embedding and ANN search."""
    return SCENARIOS.get(event_id, UNKNOWN_RESULT)
