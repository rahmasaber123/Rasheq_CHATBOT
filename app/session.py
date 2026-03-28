from __future__ import annotations
import re
import uuid
from dataclasses import dataclass, field
from typing import Any

from app.config import MAX_HISTORY_MESSAGES


@dataclass
class Session:
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    user_profile: dict[str, Any] = field(default_factory=dict)
    messages: list[dict[str, str]] = field(default_factory=list)
    greeted: bool = False

    # ── helpers ──────────────────────────────────────────────

    def add(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        # keep window bounded
        if len(self.messages) > MAX_HISTORY_MESSAGES:
            self.messages = self.messages[-MAX_HISTORY_MESSAGES:]

    def history_for_api(self, last_n: int = 16) -> list[dict[str, str]]:
        """Return the most recent messages for the API call."""
        return self.messages[-last_n:]

    # ── body-metric extraction ──────────────────────────────

    def try_extract_metrics(self, text: str) -> bool:

        numbers = re.findall(r"\d{2,3}", text)
        if len(numbers) < 2:
            return False

        candidates = [int(n) for n in numbers]
        height = weight = None

        for n in candidates:
            if 140 <= n <= 220 and height is None:
                height = n
            elif 40 <= n <= 200 and weight is None:
                weight = n

        if height and weight:
            bmi = round(weight / (height / 100) ** 2, 1)
            self.user_profile.update(
                height_cm=height, weight_kg=weight, bmi=bmi
            )
            return True
        return False


# ── in-memory store (swap for Redis in production) ──────────

_store: dict[str, Session] = {}


def get_session(sid: str) -> Session:
    if sid not in _store:
        _store[sid] = Session(session_id=sid)
    return _store[sid]


def delete_session(sid: str) -> None:
    _store.pop(sid, None)
