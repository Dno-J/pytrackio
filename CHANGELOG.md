# Changelog

All notable changes to pytrackio will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [0.2.0] — 2026-03-31

### Added
- **Async support** — `@track` now works transparently on `async def` functions
- **Async `timer()`** — `async with timer("name")` context manager support
- **p95 and p99 percentile latency** — shown in `report()` and all export formats
- **`export_json()`** — serialize all metrics and counters to JSON string
- **`export_csv()`** — serialize metrics to CSV format (p95/p99 included)
- **`export_dict()`** — return metrics as a plain Python dictionary
- `Summary.percentile(p)` — compute arbitrary percentile from raw durations
- `Summary.p95_ms` and `Summary.p99_ms` properties
- `report(output=False)` — return report as string without printing

### Changed
- `report()` table now includes `p95 ms` and `p99 ms` columns
- `pyproject.toml` updated to v0.2.0 with expanded classifiers
- README fully rewritten with async examples, export docs, comparison table
- Author bio updated to reflect production-grade open source work

### Fixed
- `timer()` now correctly records errors when exceptions occur inside the block

---

## [0.1.0] — 2026-01-01

### Added
- `@track` decorator for sync functions
- `timer()` synchronous context manager
- `counter()` named integer counters
- `report()` formatted terminal output
- `get_registry()` for raw metric access
- Zero external dependencies
- Thread-safe `MetricsRegistry` with `threading.Lock`
- MIT License, CONTRIBUTING, CODE_OF_CONDUCT
- CI/CD via GitHub Actions
- Published to PyPI
