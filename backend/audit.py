"""Append-only audit trail of agent-loop activity.

Every chat turn records one entry per loop step to output/audit_trail.json:
each tool call (with short args + result) and the final structured answer, tagged
with a timestamp, a per-run id, and a stop reason. The file is never wiped — new
runs are appended to whatever is already there.
"""

from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from pydantic_ai.messages import ModelRequest, ModelResponse, ToolCallPart, ToolReturnPart

ROOT = Path(__file__).resolve().parent.parent
AUDIT_PATH = ROOT / "output" / "audit_trail.json"
_LOCK = threading.Lock()
MAX_LEN = 400  # truncate long args/results so the trail stays readable

# pydantic-ai delivers the structured answer through this internal tool call; it marks
# the agent finishing, not a real tool step.
OUTPUT_TOOL = "final_result"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _short(value: object, limit: int = MAX_LEN) -> str:
    if value is None:
        return ""
    text = value if isinstance(value, str) else json.dumps(value, default=str)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit] + "…"


def _load() -> list:
    if not AUDIT_PATH.exists():
        return []
    try:
        data = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _append(entries: list[dict]) -> None:
    if not entries:
        return
    with _LOCK:
        data = _load()
        data.extend(entries)
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        AUDIT_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def record_run(result, *, subject: str, mode: str) -> None:
    """Append one entry per loop step from a completed agent run.

    `result` is a pydantic-ai (Streamed)RunResult exposing new_messages().
    """
    run_id = uuid.uuid4().hex[:12]
    try:
        messages = result.new_messages()
    except Exception:  # noqa: BLE001 — never let auditing break a chat reply
        return

    # tool_call_id -> returned content, gathered from the request that follows a call
    returns: dict[str, object] = {}
    for msg in messages:
        if isinstance(msg, ModelRequest):
            for part in msg.parts:
                if isinstance(part, ToolReturnPart):
                    returns[part.tool_call_id] = part.content

    entries: list[dict] = []
    step = 0
    for msg in messages:
        if not isinstance(msg, ModelResponse):
            continue
        for part in msg.parts:
            if not isinstance(part, ToolCallPart):
                continue
            step += 1
            is_output = part.tool_name == OUTPUT_TOOL
            entries.append(
                {
                    "time": _now(),
                    "run_id": run_id,
                    "step": step,
                    "mode": mode,
                    "subject": _short(subject, 160),
                    "tool": None if is_output else part.tool_name,
                    "args": _short(part.args),
                    "result": _short(returns.get(part.tool_call_id)) if not is_output else _short(part.args),
                    "stop_reason": "final_output" if is_output else "tool_call",
                }
            )

    if not entries:  # a plain-text answer with no output tool (rare)
        entries.append(
            {
                "time": _now(), "run_id": run_id, "step": 1, "mode": mode,
                "subject": _short(subject, 160), "tool": None, "args": "",
                "result": "", "stop_reason": "final_output",
            }
        )
    _append(entries)


def record_error(subject: str, mode: str, error: str) -> None:
    _append(
        [
            {
                "time": _now(), "run_id": uuid.uuid4().hex[:12], "step": 0, "mode": mode,
                "subject": _short(subject, 160), "tool": None, "args": "",
                "result": _short(error), "stop_reason": "error",
            }
        ]
    )
