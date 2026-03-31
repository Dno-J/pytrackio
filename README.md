<div align="center">

# ⚡ pytrackio

**Zero-dependency Python performance tracker.**
Decorate, time, count — then report. No servers. No config. Just Python.

[![Tests](https://github.com/danshu3007-lang/pytrackio/actions/workflows/tests.yml/badge.svg)](https://github.com/danshu3007-lang/pytrackio/actions)
[![PyPI version](https://img.shields.io/pypi/v/pytrackio?style=flat-square&color=blue)](https://pypi.org/project/pytrackio/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen?style=flat-square)](pyproject.toml)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)

</div>

---

## 🤔 The Problem

Every Python metrics tool requires Prometheus, StatsD, Grafana, or some external server.
Setting them up takes hours and adds heavy dependencies.

**pytrackio works in 30 seconds — add one decorator and you're done.**

```python
from pytrackio import track, timer, counter, report

@track
def fetch_user(user_id: int):
    ...                          # your existing code, unchanged

with timer("database_query"):
    results = db.execute(query)

counter("api_calls").increment()

report()
```

**Output:**
```
╔════════════════════════════════════════════════════════════════════════╗
║                   pytrackio  —  Performance Report                     ║
║  uptime: 4.21s                                                         ║
╠════════════════════════════════════════════════════════════════════════╣
║ Function / Block             Calls  Avg (ms)   Min(ms)  Max (ms)  Errors ║
╠════════════════════════════════════════════════════════════════════════╣
║ fetch_user                      42    120.34     98.10    310.50  —      ║
║ database_query                  18     45.20     40.10     89.30  —      ║
╠════════════════════════════════════════════════════════════════════════╣
║ Counters                                                               ║
╠────────────────────────────────────────────────────────────────────────╣
║   api_calls:  42                                                       ║
╚════════════════════════════════════════════════════════════════════════╝
```

---

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
  - [@track decorator](#track-decorator)
  - [timer() context manager](#timer-context-manager)
  - [counter()](#counter)
  - [report()](#report)
  - [Raw data access](#raw-data-access)
- [Real-world example](#-real-world-example)
- [Why pytrackio?](#-why-pytrackio)
- [Contributing](#-contributing)
- [Changelog](#-changelog)

---

## 📦 Installation

```bash
pip install pytrackio
```

**Requirements:** Python 3.10+ · Zero external dependencies

---

## ⚡ Quick Start

```bash
pip install pytrackio
```

```python
from pytrackio import track, report

@track
def my_function(x):
    return x * 2

my_function(10)
my_function(20)

report()
```

That's it. No configuration. No servers. No signup.

---

## 💻 Usage

### `@track` decorator

Automatically tracks calls, duration, and errors for any function.

```python
from pytrackio import track

# Basic usage
@track
def process_order(order_id: int):
    ...

# Custom metric name
@track(name="payment_gateway")
def charge_card(amount: float):
    ...
```

Tracks automatically:
- Total call count
- Average / min / max duration in milliseconds
- Error count and error rate %
- Never swallows your exceptions — they always propagate

---

### `timer()` context manager

Track execution time of any block of code.

```python
from pytrackio import timer

with timer("image_resize"):
    resized = resize_image(img, width=800)

with timer("send_email"):
    mailer.send(to=user.email, body=html)
```

---

### `counter()`

Named event counters — create on first use, access anywhere.

```python
from pytrackio import counter

counter("cache_hits").increment()       # +1
counter("retries").increment(3)         # +3
counter("queue_size").decrement()       # -1
counter("requests").reset()             # → 0

# Read value
print(counter("cache_hits").value)
```

---

### `report()`

Print a formatted summary of all metrics.

```python
from pytrackio import report

report()                        # print to stdout
report(show_counters=False)     # hide counters section
report(colour=False)            # plain text output (for log files)
```

Returns the report as a string too — useful for logging.

---

### Raw data access

Access the underlying registry for custom dashboards or alerting.

```python
from pytrackio import get_registry

registry = get_registry()

# Get one metric
s = registry.summary("payment_gateway")
print(f"Calls: {s.calls}, Avg: {s.avg_ms}ms, Errors: {s.error_rate}%")

# Iterate all metrics and alert on high error rates
for s in registry.all_summaries():
    if s.error_rate > 5.0:
        send_alert(f"WARNING: {s.name} has {s.error_rate}% errors!")

# Reset between test runs
registry.reset()

# Check process uptime
print(f"Running for {registry.uptime_seconds()} seconds")
```

---

## 🌍 Real-world example

```python
from pytrackio import track, timer, counter, report
import requests as http

@track
def get_weather(city: str) -> dict:
    r = http.get(f"https://api.example.com/weather?city={city}", timeout=5)
    r.raise_for_status()
    counter("api_calls").increment()
    return r.json()

@track
def process_weather(data: dict) -> str:
    with timer("format_output"):
        return f"{data['city']}: {data['temp']}°C, {data['description']}"

# Run your app
cities = ["Delhi", "London", "Tokyo", "New York", "Sydney"]
for city in cities:
    data = get_weather(city)
    print(process_weather(data))

# See performance summary
report()
```

---

## 🏗 How it works

```
Your code
   │
   ├── @track / timer()  →  records duration + success/error
   │
   ├── counter()         →  named integer counters
   │
   └── MetricsRegistry   →  thread-safe in-memory store
                                     │
                                     └── report()  →  formatted table
```

| Concern | Approach |
|---|---|
| Thread safety | `threading.Lock` on all registry operations |
| HTTP reliability | Not needed — zero network calls |
| Memory | In-process dict — no disk, no network |
| Exceptions | Always re-raised — pytrackio never hides your errors |

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

**Good first issues:**
- Add `async def` support for `@track`
- Add JSON / CSV export for `report()`
- Add `p95` / `p99` percentile to summaries
- Add `@track` support for class methods

---

## 📋 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

## 👨‍💻 Author

**Deepanshu** — Data Analyst.

Building real tools to learn production-grade Python.

---

## 📄 License

[MIT](LICENSE) — free to use, modify, and distribute.
