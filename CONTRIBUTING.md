# Contributing to pytrackio

Thank you for your interest! pytrackio welcomes contributions from everyone —
from fixing typos to adding major features.

---

## Getting started

```bash
git clone https://github.com/danshu3007-lang/pytrackio.git
cd pytrackio
pip install -e .
pip install pytest
pytest tests/ -v
```

All 29 tests should pass before you start.

---

## How to contribute

1. Fork the repo on GitHub
2. Create a branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Commit: `git commit -m "Add: description of change"`
6. Push: `git push origin feature/my-feature`
7. Open a Pull Request

---

## Good first contributions

These are great for newcomers:

| Issue | Difficulty |
|---|---|
| Add `@track` support for `async def` functions | Medium |
| Add `report(format="json")` JSON export | Easy |
| Add `report(format="csv")` CSV export | Easy |
| Add `p95` / `p99` percentile to MetricSummary | Medium |
| Improve colour support on Windows terminals | Easy |
| Add `@track` for class methods | Medium |

---

## Code standards

- Pure Python stdlib only — no new dependencies
- Type hints on all public functions
- Docstrings on all public functions
- New features need new tests

---

## Questions?

Open a GitHub issue — no question is too small.
