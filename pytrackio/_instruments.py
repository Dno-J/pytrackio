from __future__ import annotations
import functools, time
from contextlib import contextmanager
from typing import Any, Callable, Generator, Optional, TypeVar
from ._tracker import CounterState, get_registry

F = TypeVar("F", bound=Callable[..., Any])

def track(func=None, *, name=None):
    """Decorator: track calls, duration and errors for any function.

    Usage::

        @track
        def my_func(): ...

        @track(name="custom")
        def my_func(): ...
    """
    if func is None:
        def decorator(f): return _wrap(f, name)
        return decorator
    return _wrap(func, name)

def _wrap(func, custom_name):
    metric_name = custom_name or f"{func.__module__}.{func.__qualname__}"
    registry    = get_registry()
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            registry.record(metric_name, (time.perf_counter()-start)*1000, True)
            return result
        except Exception as exc:
            registry.record(metric_name, (time.perf_counter()-start)*1000, False, type(exc).__name__)
            raise
    return wrapper

@contextmanager
def timer(name: str) -> Generator[None, None, None]:
    """Context manager: track duration of any code block.

    Usage::

        with timer("db_query"):
            results = db.execute(query)
    """
    registry = get_registry()
    start    = time.perf_counter()
    try:
        yield
        registry.record(name, (time.perf_counter()-start)*1000, True)
    except Exception as exc:
        registry.record(name, (time.perf_counter()-start)*1000, False, type(exc).__name__)
        raise

def counter(name: str) -> CounterState:
    """Get a named counter (created on first access).

    Usage::

        counter("hits").increment()
        counter("hits").value
    """
    return get_registry().get_counter(name)
