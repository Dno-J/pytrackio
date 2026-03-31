# pytrackio

> Zero-dependency Python performance tracker. Decorate, time, count — then report.

[![Tests](https://github.com/danshu3007-lang/pytrackio/actions/workflows/tests.yml/badge.svg)](https://github.com/danshu3007-lang/pytrackio/actions)
[![PyPI version](https://img.shields.io/pypi/v/pytrackio?style=flat-square&color=blue)](https://pypi.org/project/pytrackio/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen?style=flat-square)](pyproject.toml)
```python
from pytrackio import track, timer, counter, report

@track
def fetch_user(user_id: int):
    ...

with timer("database_query"):
    results = db.execute(query)

counter("api_calls").increment()
report()
```

## Why pytrackio?

Every other Python metrics tool requires Prometheus, StatsD, Grafana, or some external server.

**pytrackio works in 30 seconds — zero config, zero dependencies, just pip install and decorate.**

## Installation
```bash
pip install pytrackio
```

## Usage
```python
from pytrackio import track, timer, counter, report

# Track any function automatically
@track
def process_order(order_id: int):
    ...

# Custom metric name
@track(name="payment_gateway")
def charge_card(amount: float):
    ...

# Time any block of code
with timer("image_resize"):
    resized = resize_image(img, width=800)

# Count events
counter("api_calls").increment()
counter("cache_hits").increment(5)
print(counter("api_calls").value)

# Print the report
report()
```

## Access raw data
```python
from pytrackio import get_registry

registry = get_registry()
for s in registry.all_summaries():
    if s.error_rate > 5.0:
        print(f"WARNING: {s.name} has {s.error_rate}% errors")

registry.reset()  # clear between test runs
```

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

Ideas: async support, JSON export, histogram bucketing, class method tracking.

## Built by

**Deepanshu** — BCA Student at Chandigarh University, aspiring Data Analyst.

## License

[MIT](LICENSE)
