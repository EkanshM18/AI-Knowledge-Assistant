from __future__ import annotations

from collections import defaultdict
from threading import Lock
from uuid import uuid4


class MemoryService:
    def __init__(self) -> None:
        self._messages: dict[str, list[dict[str, str]]] = defaultdict(list)
        self._lock = Lock()

    def ensure_session(self, session_id: str | None) -> str:
        return session_id or uuid4().hex

    def append(self, session_id: str, role: str, content: str) -> None:
        with self._lock:
            self._messages[session_id].append({"role": role, "content": content})

    def get_history(self, session_id: str, limit: int = 8) -> list[dict[str, str]]:
        with self._lock:
            return list(self._messages.get(session_id, [])[-limit:])

    def render_history(self, session_id: str, limit: int = 8) -> str:
        messages = self.get_history(session_id, limit=limit)
        return "\n".join(f"{item['role']}: {item['content']}" for item in messages)

