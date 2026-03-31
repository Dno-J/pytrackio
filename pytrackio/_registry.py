"""
MetricsRegistry — thread-safe, in-process metrics store.
Supports sync and async tracking, percentiles, counters, and export.
"""

from __future__ import annotations

import math
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Optional


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Summary:
    """Immutable snapshot of a single tracked metric."""
    name: str
    calls: int
    errors: int
    total_ms: float
    durations_ms: List[float]  # kept for percentile calculation

    @property
    def avg_ms(self) -> float:
        return self.total_ms / self.calls if self.calls else 0.0

    @property
    def min_ms(self) -> float:
        return min(self.durations_ms) if self.durations_ms else 0.0

    @property
    def max_ms(self) -> float:
        return max(self.durations_ms) if self.durations_ms else 0.0

    @property
    def error_rate(self) -> float:
        return (self.errors / self.calls * 100) if self.calls else 0.0

    def percentile(self, p: float) -> float:
        """Return the p-th percentile latency (0–100)."""
        if not self.durations_ms:
            return 0.0
        sorted_d = sorted(self.durations_ms)
        k = (len(sorted_d) - 1) * p / 100
        lo, hi = int(math.floor(k)), int(math.ceil(k))
        if lo == hi:
            return sorted_d[lo]
        return sorted_d[lo] + (sorted_d[hi] - sorted_d[lo]) * (k - lo)

    @property
    def p95_ms(self) -> float:
        return self.percentile(95)

    @property
    def p99_ms(self) -> float:
        return self.percentile(99)


@dataclass
class _MetricData:
    """Mutable internal record for a tracked function/block."""
    name: str
    calls: int = 0
    errors: int = 0
    total_ms: float = 0.0
    durations_ms: List[float] = field(default_factory=list)

    def record(self, duration_ms: float, error: bool = False) -> None:
        self.calls += 1
        self.total_ms += duration_ms
        self.durations_ms.append(duration_ms)
        if error:
            self.errors += 1

    def to_summary(self) -> Summary:
        return Summary(
            name=self.name,
            calls=self.calls,
            errors=self.errors,
            total_ms=self.total_ms,
            durations_ms=list(self.durations_ms),
        )


# ---------------------------------------------------------------------------
# Counter
# ---------------------------------------------------------------------------

class Counter:
    """A named integer counter, safe for concurrent use."""

    def __init__(self, name: str) -> None:
        self._name = name
        self._value = 0
        self._lock = threading.Lock()

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> int:
        with self._lock:
            return self._value

    def increment(self, by: int = 1) -> "Counter":
        with self._lock:
            self._value += by
        return self

    def decrement(self, by: int = 1) -> "Counter":
        with self._lock:
            self._value -= by
        return self

    def reset(self) -> "Counter":
        with self._lock:
            self._value = 0
        return self


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class MetricsRegistry:
    """
    Central, thread-safe store for all pytrackio metrics.

    One global instance is created at import time; you can also
    instantiate isolated registries for testing.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._metrics: Dict[str, _MetricData] = {}
        self._counters: Dict[str, Counter] = {}
        self._start_time: float = time.monotonic()

    # ------------------------------------------------------------------
    # Metrics (timings)
    # ------------------------------------------------------------------

    def record(self, name: str, duration_ms: float, error: bool = False) -> None:
        """Record a single timing observation."""
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = _MetricData(name=name)
            self._metrics[name].record(duration_ms, error)

    def summary(self, name: str) -> Optional[Summary]:
        """Return a snapshot for a single metric, or None if not found."""
        with self._lock:
            data = self._metrics.get(name)
            return data.to_summary() if data else None

    def all_summaries(self) -> List[Summary]:
        """Return snapshots for every tracked metric."""
        with self._lock:
            return [d.to_summary() for d in self._metrics.values()]

    # ------------------------------------------------------------------
    # Counters
    # ------------------------------------------------------------------

    def counter(self, name: str) -> Counter:
        """Retrieve (or create) a named counter."""
        with self._lock:
            if name not in self._counters:
                self._counters[name] = Counter(name)
            return self._counters[name]

    def all_counters(self) -> List[Counter]:
        with self._lock:
            return list(self._counters.values())

    # ------------------------------------------------------------------
    # Housekeeping
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Clear all metrics and counters (useful between test runs)."""
        with self._lock:
            self._metrics.clear()
            self._counters.clear()
            self._start_time = time.monotonic()

    def uptime_seconds(self) -> float:
        return time.monotonic() - self._start_time


# Singleton used by all public API functions
_GLOBAL_REGISTRY = MetricsRegistry()


def get_registry() -> MetricsRegistry:
    """Return the global MetricsRegistry instance."""
    return _GLOBAL_REGISTRY
