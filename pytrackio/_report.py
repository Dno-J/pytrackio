from __future__ import annotations
import csv, json, io
from typing import Any, Dict, Optional
from ._registry import _REGISTRY

def report(*, show_counters=True, colour=True):
    summaries = _REGISTRY.all_summaries()
    counters = _REGISTRY.all_counters() if show_counters else {}
    lines = []
    W = "═" * 80
    lines.append(W)
    lines.append(f"  pytrackio — Performance Report    uptime: {_REGISTRY.uptime_seconds():.2f}s")
    lines.append(W)
    if not summaries:
        lines.append("  No metrics recorded yet.")
        lines.append(W)
        out = "\n".join(lines); print(out); return out
    lines.append(f"  {'Function/Block':<30} {'Calls':>6} {'Avg(ms)':>9} {'Min(ms)':>9} {'Max(ms)':>9} {'p95(ms)':>9} {'p99(ms)':>9} {'Errors':>8}")
    lines.append("─" * 80)
    for s in sorted(summaries, key=lambda x: x.avg_ms, reverse=True):
        err = f"{s.errors}({s.error_rate:.0f}%)" if s.errors else "—"
        lines.append(f"  {s.name:<30} {s.calls:>6} {s.avg_ms:>9.2f} {s.min_ms:>9.2f} {s.max_ms:>9.2f} {s.p95_ms:>9.2f} {s.p99_ms:>9.2f} {err:>8}")
    if counters:
        lines.append("─" * 80)
        lines.append("  Counters")
        lines.append("─" * 80)
        for n, v in sorted(counters.items()):
            lines.append(f"  {n}: {v}")
    lines.append(W)
    out = "\n".join(lines); print(out); return out

def export_dict():
    return {"uptime_seconds": _REGISTRY.uptime_seconds(),
            "metrics": [{"name":s.name,"calls":s.calls,"errors":s.errors,
                "error_rate":round(s.error_rate,4),"avg_ms":round(s.avg_ms,4),
                "min_ms":round(s.min_ms,4),"max_ms":round(s.max_ms,4),
                "p95_ms":round(s.p95_ms,4),"p99_ms":round(s.p99_ms,4)}
               for s in _REGISTRY.all_summaries()],
            "counters": _REGISTRY.all_counters()}

def export_json(path=None, *, indent=2):
    data = json.dumps(export_dict(), indent=indent)
    if path:
        with open(path, "w") as f: f.write(data)
    return data

def export_csv(path=None):
    buf = io.StringIO()
    fields = ["name","calls","errors","error_rate","avg_ms","min_ms","max_ms","p95_ms","p99_ms"]
    w = csv.DictWriter(buf, fieldnames=fields)
    w.writeheader()
    for s in _REGISTRY.all_summaries():
        w.writerow({"name":s.name,"calls":s.calls,"errors":s.errors,
            "error_rate":round(s.error_rate,4),"avg_ms":round(s.avg_ms,4),
            "min_ms":round(s.min_ms,4),"max_ms":round(s.max_ms,4),
            "p95_ms":round(s.p95_ms,4),"p99_ms":round(s.p99_ms,4)})
    csv_str = buf.getvalue()
    if path:
        with open(path, "w") as f: f.write(csv_str)
    return csv_str
