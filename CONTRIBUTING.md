# Contributing to pytrackio

Contributions are welcome — bug fixes, new features, docs improvements.

## Setup
```bash
git clone https://github.com/danshu3007-lang/pytrackio
cd pytrackio
python -m venv venv && source venv/bin/activate
pip install -e .
pip install pytest
python -m pytest tests/ -v
```

All 27 tests must pass before opening a PR.

## Open issues to work on

- Django / Flask middleware integration
- `@track` support for class methods
- `reset_after=N` parameter — auto-reset registry after N calls
- Structured logging output (JSON lines format)
- GitHub Actions badge for PyPI publish workflow

## Pull request checklist

- [ ] Tests pass: `python -m pytest tests/ -v`
- [ ] New feature has tests
- [ ] CHANGELOG.md updated

## Filing bugs

Open an issue with: Python version, OS, what you ran, what you expected, what happened.
