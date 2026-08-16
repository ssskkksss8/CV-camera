from dataclasses import dataclass

from app.mock_vision import VisionResult
from app.schemas import EventMetadata

QUALITY_THRESHOLD = 0.60
LIVENESS_DENY_THRESHOLD = 0.50
LIVENESS_ALLOW_THRESHOLD = 0.75
MATCH_ALLOW_THRESHOLD = 0.80
MATCH_REVIEW_THRESHOLD = 0.65
MIN_MARGIN = 0.10
OFFLINE_CACHE_TTL_MINUTES = 15


@dataclass(frozen=True)
class Decision:
    name: str
    reasons: list[str]
    degraded_mode: bool = False


def decide(vision: VisionResult, metadata: EventMetadata) -> Decision:
    margin = vision.match_score - vision.second_best_score

    if metadata.network == "offline" and metadata.cache_age_minutes > OFFLINE_CACHE_TTL_MINUTES:
        return Decision("manual_review", ["offline_stale_cache"], degraded_mode=True)
    if not vision.face_detected:
        return Decision("manual_review", ["face_not_detected"])
    if vision.quality_score < QUALITY_THRESHOLD:
        return Decision("manual_review", ["quality_below_threshold"])
    if vision.liveness_score < LIVENESS_DENY_THRESHOLD:
        return Decision("deny", ["spoof_suspected"])
    if vision.liveness_score < LIVENESS_ALLOW_THRESHOLD:
        return Decision("manual_review", ["liveness_uncertain"])
    if vision.match_score >= MATCH_ALLOW_THRESHOLD and margin >= MIN_MARGIN:
        return Decision(
            "allow",
            ["quality_ok", "liveness_ok", "match_above_allow_threshold", "candidate_margin_ok"],
        )
    if vision.match_score >= MATCH_REVIEW_THRESHOLD:
        reasons = ["match_requires_review"]
        if margin < MIN_MARGIN:
            reasons.append("candidate_margin_too_small")
        return Decision("manual_review", reasons)
    return Decision("deny", ["match_below_review_threshold"])
