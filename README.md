# ⚡ pytrackio

**The fastest way to add performance tracking to any Python project.**  
One decorator. Zero dependencies. No servers. No config. Just answers.

[![Tests](https://github.com/danshu3007-lang/pytrackio/actions/workflows/tests.yml/badge.svg)](https://github.com/danshu3007-lang/pytrackio/actions)
[![PyPI version](https://img.shields.io/pypi/v/pytrackio?style=flat-square&color=blue)](https://pypi.org/project/pytrackio/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen?style=flat-square)](pyproject.toml)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)

---
```python
pip install pytrackio
```
```python
from pytrackio import track, timer, counter, report

@track
def process_order(order_id):
    ...

with timer("db_query"):
    results = db.execute(query)

counter("api_calls").increment()

report()
```
```
================================================================================
  pytrackio — Performance Report         uptime: 4.21s
================================================================================
  Name                         Calls      Avg      Min      Max      p95      p99  Errors
--------------------------------------------------------------------------------
  process_order                   42   120.34    98.10   310.50   290.10   308.40       —
  db_query                        18    45.20    40.10    89.30    87.20    89.10       —
--------------------------------------------------------------------------------
  Counters
--------------------------------------------------------------------------------
  api_calls: 42
================================================================================
```

---

## Why pytrackio?

Sometimes you just need to know how fast your code runs — without setting up servers, installing agents, or managing infrastructure.

pytrackio is different. It runs **inside your process**, with **zero setup**, and gives you real numbers in seconds.

| Feature | pytrackio |
|---|---|
| Setup time | 30 seconds |
| External server required | ❌ None |
| Dependencies | 0 |
| Works in scripts & notebooks | ✅ |
| p95 / p99 percentiles | ✅ |
| Async support | ✅ |
| Thread-safe | ✅ |

---

## Installation
```bash
pip install pytrackio
```

**Requirements:** Python 3.10+ · Zero external dependencies

---

## Usage

### `@track` — decorate any function
```python
from pytrackio import track

@track
def fetch_user(user_id: int):
    ...

# Works with async too
@track
async def send_notification(user_id: int):
    await mailer.send(...)

# Custom metric name
@track(name="payment_gateway")
def charge_card(amount: float):
    ...
```

Tracks: call count · avg / min / max / p95 / p99 latency · error count · error rate

---

### `timer()` — track any code block
```python
from pytrackio import timer

with timer("image_resize"):
    resized = resize_image(img, width=800)

# Async blocks too
async with timer("external_api"):
    result = await fetch_data()
```

---

### `counter()` — named event counters
```python
from pytrackio import counter

counter("cache_hits").increment()
counter("retries").increment(3)
counter("queue_size").decrement()
counter("requests").reset()

print(counter("cache_hits").value)
```

---

### `report()` — print everything
```python
from pytrackio import report

report()                       # full report to stdout
report(show_counters=False)    # hide counters
report(colour=False)           # plain text (good for log files)
```

Returns the report as a string for logging or alerting.

---

### Export data
```python
from pytrackio import export_json, export_csv, export_dict

export_json("metrics.json")   # write to file
export_csv("metrics.csv")     # write to file
data = export_dict()          # Python dict for custom dashboards
```

---

### Raw registry access
```python
from pytrackio import get_registry

registry = get_registry()

for s in registry.all_summaries():
    if s.error_rate > 5.0:
        alert(f"{s.name} error rate: {s.error_rate:.1f}%")

registry.reset()   # clear all metrics
```

---

## Real-world example
```python
from pytrackio import track, timer, counter, report

@track
def get_product(product_id: int) -> dict:
    counter("db_reads").increment()
    return db.query(Product).get(product_id)

@track
async def checkout(cart_id: int) -> str:
    with timer("payment"):
        result = await payment_gateway.charge(cart_id)
    counter("orders_placed").increment()
    return result["order_id"]

# After processing a batch:
report()
```

---

## How it works
```
Your code
   │
   ├── @track / timer()  ──▶  records duration + error per call
   │
   ├── counter()         ──▶  named integer counters
   │
   └── MetricsRegistry   ──▶  thread-safe, in-process dict
                                        │
                              report() / export_json() / export_csv()
```

| Concern | Approach |
|---|---|
| Thread safety | `threading.Lock` on every registry write |
| Memory | In-process only — no disk, no network |
| Exceptions | Always re-raised — pytrackio never hides errors |
| Async | Native `async with` and `async def` support |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) — PRs welcome.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

## Author

**Deepanshu** — Python Developer & Open Source Author.  
Creator of pytrackio. Building tools that solve real problems for real developers.

---

## License

[MIT](LICENSE) — free to use, modify, and distribute.
