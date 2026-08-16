import json
from pathlib import Path
from typing import Any

LOG_PATH = Path("logs/access_events.jsonl")


def write_access_event(record: dict[str, Any]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(record, ensure_ascii=False) + "\n")
