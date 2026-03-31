from __future__ import annotations
import time
from ._registry import _REGISTRY

class timer:
    def __init__(self, name):
        self._name=name; self._t=0.0
    def __enter__(self):
        self._t=time.perf_counter(); return self
    def __exit__(self, et, ev, tb):
        _REGISTRY.record(self._name,(time.perf_counter()-self._t)*1000,et is not None); return False
    async def __aenter__(self):
        self._t=time.perf_counter(); return self
    async def __aexit__(self, et, ev, tb):
        _REGISTRY.record(self._name,(time.perf_counter()-self._t)*1000,et is not None); return False
