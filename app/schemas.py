from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class EventMetadata(BaseModel):
    direction: Literal["in", "out"]
    illumination: str
    edge_node: str
    network: Literal["online", "offline"]
    cache_age_minutes: int = Field(default=0, ge=0)
    occlusion_hint: str | None = None
    head_pose_hint: str | None = None
    note: str | None = None


class AccessRequest(BaseModel):
    event_id: str = Field(min_length=1)
    gate_id: str = Field(min_length=1)
    camera_id: str = Field(min_length=1)
    captured_at: datetime
    frame_uri: str
    metadata: EventMetadata


class QualityResult(BaseModel):
    face_detected: bool
    quality_score: float
    liveness_score: float


class AccessResponse(BaseModel):
    event_id: str
    decision_id: str
    decision: Literal["allow", "manual_review", "deny"]
    employee_id: str | None = None
    match_score: float
    margin_to_second_best: float
    quality: QualityResult
    reasons: list[str]
    turnstile_command: Literal["open", "keep_closed"]
    requires_human_review: bool
    degraded_mode: bool
    audit_id: str
    latency_ms: int
