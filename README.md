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
    ...  # your existing code, unchanged

with timer("database_query"):
    results = db.execute(query)

counter("api_calls").increment()

report()
```

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

## Why pytrackio?

Every other Python metrics tool requires Prometheus, StatsD, Grafana, or some external server. Setting them up takes hours.

**pytrackio works in 30 seconds:**
- ✅ Zero dependencies — pure Python stdlib only
- ✅ Zero configuration — no config files, no servers
- ✅ Zero changes to your logic — just add one decorator
- ✅ Thread-safe — works in concurrent applications
- ✅ Production-ready — proper error tracking, not just happy-path

---

## Installation

```bash
pip install pytrackio
```

---

## Usage

### Track a function automatically

```python
from pytrackio import track

@track
def process_order(order_id: int):
    # your code here — nothing else changes
    ...

# Call it normally
process_order(123)
process_order(456)
```

### Custom metric name

```python
@track(name="payment_gateway")
def charge_card(amount: float):
    ...
```

### Time any block of code

```python
from pytrackio import timer

with timer("image_resize"):
    resized = resize_image(img, width=800)

with timer("send_email"):
    mailer.send(to=user.email, body=html)
```

### Count events

```python
from pytrackio import counter

counter("cache_hits").increment()
counter("cache_misses").increment()
counter("retries").increment(3)    # increment by N
counter("queue_size").decrement()  # decrement

# Read the value anywhere
print(counter("cache_hits").value)
```

### Print the report

```python
from pytrackio import report

report()                        # print to stdout
report(show_counters=False)     # hide counters section
```

### Access raw data programmatically

```python
from pytrackio import get_registry

registry = get_registry()

# Get summary for one metric
s = registry.summary("payment_gateway")
print(s.calls, s.avg_ms, s.error_rate)

# Get all summaries
for s in registry.all_summaries():
    if s.error_rate > 5.0:
        alert(f"{s.name} has {s.error_rate}% errors!")

# Reset between test runs
registry.reset()
```

---

## Real-world example

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
        return f"{data['city']}: {data['temp']}°C"

# Run your app...
for city in ["Delhi", "London", "Tokyo"]:
    data = get_weather(city)
    print(process_weather(data))

# See how everything performed
report()
```

---

## API Reference

### `@track`

```python
@track
def my_func(): ...

@track(name="custom_name")
def my_func(): ...
```

Tracks: call count, duration (min/max/avg), errors and error rate.
Never swallows exceptions — your original errors always propagate.

---

### `timer(name)`

```python
with timer("block_name"):
    ...
```

Context manager. Records duration and any exceptions raised inside the block.

---

### `counter(name)`

```python
counter("name").increment()       # +1
counter("name").increment(n)      # +n
counter("name").decrement()       # -1
counter("name").reset()           # → 0
counter("name").value             # read current value
```

---

### `report(stream, colour, show_counters)`

```python
report()
report(show_counters=False)
report(colour=False)              # force plain text
```

Prints to stdout and returns the output as a string.

---

### `get_registry()`

Returns the global `MetricsRegistry` instance for programmatic access.

```python
registry = get_registry()
registry.all_summaries()          # List[MetricSummary]
registry.all_counters()           # List[CounterState]
registry.summary("name")          # Optional[MetricSummary]
registry.reset()                  # clear everything
registry.uptime_seconds()         # float
```

---

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

**Ideas for contributions:**
- Async support (`@track` for `async def` functions)
- Export to JSON / CSV
- Histogram bucketing
- `@track` for class methods
- Minimum call threshold filter in report

---

## Built by

**Deepanshu** — BCA Student at Chandigarh University, aspiring Data Analyst.

---

## License

[MIT](LICENSE)
