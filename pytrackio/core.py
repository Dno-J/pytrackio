from __future__ import annotations
import functools
import time
import inspect
from ._registry import _REGISTRY

def track(func=None, *, name=None): 
    """
    Universal decorator for tracking sync/async functions and methods.
    Supports: @track, @track(), and @track(name="custom_name")
    """
    def decorator(fn):
        metric_name = name or getattr(fn, "__qualname__", fn.__name__)
        
        if inspect.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(*args, **kwargs):
                start = time.perf_counter()
                err = False
                try:
                    return await fn(*args, **kwargs)
                except Exception as e:
                    err = True
                    raise e
                finally:
                    duration = (time.perf_counter() - start) * 1000
                    _REGISTRY.record(metric_name, duration, err)
            return async_wrapper

        @functools.wraps(fn)
        def sync_wrapper(*args, **kwargs):
            start = time.perf_counter()
            err = False
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                err = True
                raise e
            finally:
                duration = (time.perf_counter() - start) * 1000
                _REGISTRY.record(metric_name, duration, err)
        return sync_wrapper


    if func is None:
        return decorator
    return decorator(func)