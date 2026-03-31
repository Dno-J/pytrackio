from __future__ import annotations
import asyncio, functools, inspect, time
from typing import Any, Callable, Optional
from ._registry import _REGISTRY

def track(func=None, *, name=None):
    if func is None:
        def decorator(fn): return _wrap(fn, name or fn.__qualname__)
        return decorator
    return _wrap(func, name or func.__qualname__)

def _wrap(fn, metric_name):
    if inspect.iscoroutinefunction(fn):
        @functools.wraps(fn)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter(); error = False
            try: return await fn(*args, **kwargs)
            except Exception: error = True; raise
            finally: _REGISTRY.record(metric_name, (time.perf_counter()-start)*1000, error=error)
        return async_wrapper
    else:
        @functools.wraps(fn)
        def sync_wrapper(*args, **kwargs):
            start = time.perf_counter(); error = False
            try: return fn(*args, **kwargs)
            except Exception: error = True; raise
            finally: _REGISTRY.record(metric_name, (time.perf_counter()-start)*1000, error=error)
        return sync_wrapper
