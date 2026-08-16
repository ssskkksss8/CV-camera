import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.audit as audit
from app.main import app, processed_events

client = TestClient(app)
DEMO_DIR = Path(__file__).parents[1] / "demo"


@pytest.fixture(autouse=True)
def isolated_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    processed_events.clear()
    monkeypatch.setattr(audit, "LOG_PATH", tmp_path / "access_events.jsonl")
    # main imports the function, whose globals still resolve LOG_PATH in app.audit.
    yield
    processed_events.clear()


def request_demo(name: str):
    payload = json.loads((DEMO_DIR / name).read_text(encoding="utf-8"))
    return client.post("/v1/access/verify", json=payload)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_root_serves_demo_ui():
    result = client.get("/")
    assert result.status_code == 200
    assert "FaceGate PoC" in result.text
    assert "/v1/access/verify" in result.text


def test_online_event_does_not_require_cache_age():
    payload = json.loads((DEMO_DIR / "happy_path.json").read_text(encoding="utf-8"))
    payload["metadata"].pop("cache_age_minutes")
    result = client.post("/v1/access/verify", json=payload)
    assert result.status_code == 200
    assert result.json()["decision"] == "allow"


@pytest.mark.parametrize(
    ("filename", "decision", "command"),
    [
        ("happy_path.json", "allow", "open"),
        ("ambiguous_match.json", "manual_review", "keep_closed"),
        ("spoof_attempt.json", "deny", "keep_closed"),
        ("offline_stale_cache.json", "manual_review", "keep_closed"),
    ],
)
def test_demo_scenarios(filename: str, decision: str, command: str):
    result = request_demo(filename)
    assert result.status_code == 200
    assert result.json()["decision"] == decision
    assert result.json()["turnstile_command"] == command


def test_risky_paths_never_open():
    for filename in ("ambiguous_match.json", "spoof_attempt.json", "offline_stale_cache.json"):
        processed_events.clear()
        assert request_demo(filename).json()["turnstile_command"] != "open"


def test_repeated_event_is_idempotent():
    first = request_demo("happy_path.json")
    second = request_demo("happy_path.json")
    assert second.json() == first.json()
    assert len(audit.LOG_PATH.read_text(encoding="utf-8").splitlines()) == 1
