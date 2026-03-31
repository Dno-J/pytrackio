"""
timer() — context manager for timing arbitrary code blocks.
Supports both synchronous (with timer(...)) and
asynchronous (async with timer(...)) usage.
"""

from __future__ import annotations

import time
from types import TracebackType
from typing import Optional, Type

from ._registry import get_registry


class timer:
    """
    Context manager that records the wall-clock duration of a code block.

    Sync usage::

        with timer("db_query"):
            rows = db.execute(sql)

    Async usage::

        async with timer("external_api"):
            data = await client.get(url)
    """

    def __init__(self, name: str) -> None:
        self._name = name
        self._start: float = 0.0

    # ------------------------------------------------------------------
    # Synchronous context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> "timer":
        self._start = time.perf_counter()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        elapsed_ms = (time.perf_counter() - self._start) * 1000
        error = exc_type is not None
        get_registry().record(self._name, elapsed_ms, error)
        return False  # never suppress exceptions

    # ------------------------------------------------------------------
    # Asynchronous context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "timer":
        self._start = time.perf_counter()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        elapsed_ms = (time.perf_counter() - self._start) * 1000
        error = exc_type is not None
        get_registry().record(self._name, elapsed_ms, error)
        return False
