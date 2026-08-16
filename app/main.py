from threading import Lock
from time import perf_counter

from fastapi import FastAPI

from app.audit import write_access_event
from app.decision_engine import decide
from app.demo_ui import demo_page
from app.mock_vision import process_event
from app.schemas import AccessRequest, AccessResponse, QualityResult

app = FastAPI(title="FaceGate PoC", version="0.1.0")
processed_events: dict[str, AccessResponse] = {}
_processing_lock = Lock()


@app.get("/", include_in_schema=False)
def root():
    return demo_page()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/access/verify", response_model=AccessResponse)
def verify_access(request: AccessRequest) -> AccessResponse:
    # The lock makes the in-memory check-and-create atomic for concurrent retries.
    with _processing_lock:
        previous = processed_events.get(request.event_id)
        if previous is not None:
            return previous

        started_at = perf_counter()
        vision = process_event(request.event_id)
        result = decide(vision, request.metadata)
        margin = round(vision.match_score - vision.second_best_score, 4)
        response = AccessResponse(
            event_id=request.event_id,
            decision_id=f"d-{request.event_id}",
            decision=result.name,
            employee_id=vision.employee_id,
            match_score=vision.match_score,
            margin_to_second_best=margin,
            quality=QualityResult(
                face_detected=vision.face_detected,
                quality_score=vision.quality_score,
                liveness_score=vision.liveness_score,
            ),
            reasons=result.reasons,
            turnstile_command="open" if result.name == "allow" else "keep_closed",
            requires_human_review=result.name == "manual_review",
            degraded_mode=result.degraded_mode,
            audit_id=f"a-{request.event_id}",
            latency_ms=max(1, int((perf_counter() - started_at) * 1000)),
        )

        audit_record = response.model_dump(exclude={"quality"})
        audit_record.update({"gate_id": request.gate_id, "camera_id": request.camera_id})
        write_access_event(audit_record)
        processed_events[request.event_id] = response
        return response
