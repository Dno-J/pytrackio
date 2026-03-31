from __future__ import annotations
import time
from ._registry import _REGISTRY

class timer:
    def __init__(self, name: str) -> None:
        self._name = name; self._start = 0.0
    def __enter__(self):
        self._start = time.perf_counter(); return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        _REGISTRY.record(self._name, (time.perf_counter()-self._start)*1000, error=exc_type is not None)
        return False
    async def __aenter__(self):
        self._start = time.perf_counter(); return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        _REGISTRY.record(self._name, (time.perf_counter()-self._start)*1000, error=exc_type is not None)
        return False
