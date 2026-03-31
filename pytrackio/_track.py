from __future__ import annotations
import functools, inspect, time
from ._registry import _REGISTRY

def track(func=None, *, name=None):
    if func is None:
        def decorator(fn): return _wrap(fn, name or fn.__qualname__)
        return decorator
    return _wrap(func, name or func.__qualname__)

def _wrap(fn, metric_name):
    if inspect.iscoroutinefunction(fn):
        @functools.wraps(fn)
        async def aw(*a, **kw):
            t=time.perf_counter(); err=False
            try: return await fn(*a, **kw)
            except: err=True; raise
            finally: _REGISTRY.record(metric_name,(time.perf_counter()-t)*1000,err)
        return aw
    @functools.wraps(fn)
    def sw(*a, **kw):
        t=time.perf_counter(); err=False
        try: return fn(*a, **kw)
        except: err=True; raise
        finally: _REGISTRY.record(metric_name,(time.perf_counter()-t)*1000,err)
    return sw
