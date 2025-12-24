"""
Minimal agent shim for test environment. Provides AgentContext with minimal API
used by ApiHandler.use_context to avoid importing the full Agent Zero runtime in tests.
"""
from __future__ import annotations

from typing import Dict, Optional
import threading


class AgentContext:
    _contexts: Dict[str, "AgentContext"] = {}
    _lock = threading.Lock()

    def __init__(self, config: Optional[dict] = None, id: Optional[str] = None, set_current: bool = False):
        self.id = id or "default"
        self.config = config or {}
        with AgentContext._lock:
            AgentContext._contexts[self.id] = self

    @classmethod
    def first(cls) -> Optional["AgentContext"]:
        with cls._lock:
            for c in cls._contexts.values():
                return c
        return None

    @classmethod
    def use(cls, ctxid: Optional[str] = None) -> Optional["AgentContext"]:
        with cls._lock:
            if ctxid is None:
                return cls.first()
            return cls._contexts.get(ctxid)

    @classmethod
    def create(cls, ctxid: str, config: Optional[dict] = None) -> "AgentContext":
        return AgentContext(config=config or {}, id=ctxid, set_current=True)
