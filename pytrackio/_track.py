"""
@track decorator — works on both regular and async functions.
"""

from __future__ import annotations

import asyncio
import functools
import time
from typing import Any, Callable, Optional, Union

from ._registry import get_registry


def track(
    func: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
) -> Any:
    """
    Decorator that tracks call count, latency, and errors for a function.

    Works transparently on both ``def`` and ``async def`` functions.

    Usage::

        @track
        def process(x): ...

        @track(name="custom_label")
        async def fetch(url): ...
    """
    # Allow bare @track or @track(name="...")
    if func is None:
        # Called as @track(...) — return the real decorator
        def decorator(fn: Callable) -> Callable:
            return _wrap(fn, name)
        return decorator

    # Called as @track directly
    return _wrap(func, name)


def _wrap(func: Callable, label: Optional[str]) -> Callable:
    metric_name = label or func.__qualname__

    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            error = False
            try:
                return await func(*args, **kwargs)
            except Exception:
                error = True
                raise
            finally:
                elapsed_ms = (time.perf_counter() - start) * 1000
                get_registry().record(metric_name, elapsed_ms, error)

        return async_wrapper

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        error = False
        try:
            return func(*args, **kwargs)
        except Exception:
            error = True
            raise
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            get_registry().record(metric_name, elapsed_ms, error)

    return sync_wrapper
