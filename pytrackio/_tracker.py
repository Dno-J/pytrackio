from __future__ import annotations
import threading, time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class CallRecord:
    duration_ms: float
    success: bool
    error_type: Optional[str] = None

@dataclass
class MetricSummary:
    name: str
    calls: int
    success: int
    errors: int
    total_ms: float
    min_ms: float
    max_ms: float
    avg_ms: float
    error_rate: float

@dataclass
class CounterState:
    name: str
    value: int = 0
    def increment(self, by: int = 1) -> "CounterState":
        self.value += by; return self
    def decrement(self, by: int = 1) -> "CounterState":
        self.value -= by; return self
    def reset(self) -> "CounterState":
        self.value = 0; return self

class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._timings: Dict[str, List[CallRecord]] = {}
        self._counters: Dict[str, CounterState] = {}
        self._start_time: float = time.time()

    def record(self, name: str, duration_ms: float, success: bool, error_type: Optional[str] = None) -> None:
        with self._lock:
            if name not in self._timings:
                self._timings[name] = []
            self._timings[name].append(CallRecord(duration_ms=duration_ms, success=success, error_type=error_type))

    def summary(self, name: str) -> Optional[MetricSummary]:
        with self._lock:
            records = self._timings.get(name)
            if not records: return None
            return self._compute_summary(name, records)

    def all_summaries(self) -> List[MetricSummary]:
        with self._lock:
            return [self._compute_summary(n, r) for n, r in self._timings.items()]

    @staticmethod
    def _compute_summary(name: str, records: List[CallRecord]) -> MetricSummary:
        durations = [r.duration_ms for r in records]
        errors    = [r for r in records if not r.success]
        return MetricSummary(
            name=name, calls=len(records),
            success=len(records)-len(errors), errors=len(errors),
            total_ms=round(sum(durations),3), min_ms=round(min(durations),3),
            max_ms=round(max(durations),3), avg_ms=round(sum(durations)/len(durations),3),
            error_rate=round(len(errors)/len(records)*100,1),
        )

    def get_counter(self, name: str) -> CounterState:
        with self._lock:
            if name not in self._counters:
                self._counters[name] = CounterState(name=name)
            return self._counters[name]

    def all_counters(self) -> List[CounterState]:
        with self._lock: return list(self._counters.values())

    def reset(self) -> None:
        with self._lock:
            self._timings.clear(); self._counters.clear()
            self._start_time = time.time()

    def uptime_seconds(self) -> float:
        return round(time.time() - self._start_time, 2)

_registry = MetricsRegistry()
def get_registry() -> MetricsRegistry: return _registry
