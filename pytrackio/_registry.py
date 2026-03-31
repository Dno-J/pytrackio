from __future__ import annotations
import threading
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class MetricSummary:
    name: str
    calls: int
    errors: int
    avg_ms: float
    min_ms: float
    max_ms: float
    p95_ms: float
    p99_ms: float
    error_rate: float

class Counter:
    def __init__(self, name: str) -> None:
        self.name = name
        self._value = 0
        self._lock = threading.Lock()
    @property
    def value(self) -> int:
        with self._lock: return self._value
    def increment(self, n: int = 1) -> None:
        with self._lock: self._value += n
    def decrement(self, n: int = 1) -> None:
        with self._lock: self._value -= n
    def reset(self) -> None:
        with self._lock: self._value = 0

def _percentile(s: List[float], p: float) -> float:
    if not s: return 0.0
    n = len(s)
    if n == 1: return s[0]
    idx = (p / 100.0) * (n - 1)
    lo = int(idx)
    hi = lo + 1
    if hi >= n: return s[-1]
    return s[lo] + (idx - lo) * (s[hi] - s[lo])

class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._samples: Dict[str, List[float]] = {}
        self._errors: Dict[str, int] = {}
        self._counters: Dict[str, Counter] = {}
        self._start = time.monotonic()
    def record(self, name: str, duration_ms: float, error: bool = False) -> None:
        with self._lock:
            if name not in self._samples:
                self._samples[name] = []
                self._errors[name] = 0
            self._samples[name].append(duration_ms)
            if error: self._errors[name] += 1
    def counter(self, name: str) -> Counter:
        with self._lock:
            if name not in self._counters:
                self._counters[name] = Counter(name)
            return self._counters[name]
    def summary(self, name: str) -> Optional[MetricSummary]:
        with self._lock:
            samples = self._samples.get(name)
            if not samples: return None
            return self._build(name, list(samples), self._errors.get(name, 0))
    def all_summaries(self) -> List[MetricSummary]:
        with self._lock:
            return [self._build(n, list(s), self._errors.get(n, 0))
                    for n, s in self._samples.items()]
    def all_counters(self) -> Dict[str, int]:
        with self._lock:
            return {n: c.value for n, c in self._counters.items()}
    def _build(self, name, samples, errors) -> MetricSummary:
        s = sorted(samples)
        c = len(s)
        return MetricSummary(name=name, calls=c, errors=errors,
            avg_ms=sum(s)/c, min_ms=s[0], max_ms=s[-1],
            p95_ms=_percentile(s, 95), p99_ms=_percentile(s, 99),
            error_rate=100.0*errors/c if c else 0.0)
    def reset(self) -> None:
        with self._lock:
            self._samples.clear(); self._errors.clear()
            self._counters.clear(); self._start = time.monotonic()
    def uptime_seconds(self) -> float:
        return time.monotonic() - self._start

_REGISTRY = MetricsRegistry()
