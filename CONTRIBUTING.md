# Contributing to pytrackio

Thanks for your interest! Contributions are welcome.

## How to contribute

1. Fork the repo and create a feature branch
2. Make your changes with tests
3. Run `python -m pytest tests/ -v` — all 27 must pass
4. Open a pull request

## Good first issues

- Add a `reset_after` parameter to `@track` (auto-reset after N calls)
- Add `export_json()` / `export_csv()` to write reports to files
- Add Django / Flask middleware integration
- Add `p95` / `p99` to the report output columns
- Improve the report formatting with colour support

## Development setup
```bash
git clone https://github.com/danshu3007-lang/pytrackio
cd pytrackio
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
python -m pytest tests/ -v
```
