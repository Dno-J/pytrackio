# Changelog

All notable changes to pytrackio will be documented here.

---

## [0.1.0] - 2026-03-31

### Added
- `@track` decorator — automatically tracks calls, duration, and errors
- `timer()` context manager — tracks execution time of any code block
- `counter()` — named integer counters with increment/decrement/reset
- `report()` — formatted performance table with colour support
- `get_registry()` — programmatic access to raw metrics data
- Thread-safe `MetricsRegistry` using `threading.Lock`
- 29 unit tests covering all public APIs
- GitHub Actions CI — tests on Python 3.10, 3.11, 3.12
- Zero external dependencies — pure Python stdlib only

---

## Upcoming

- `async def` support for `@track`
- JSON and CSV export
- p95 / p99 percentile metrics
- Class method tracking
