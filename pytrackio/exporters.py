import json
from ._registry import _REGISTRY

def export_jsonlines(path=None):
    """
    Exports metrics (summaries + counters) in JSON Lines format.
    Each line is a valid standalone JSON object.
    """
    output = []
    summaries = _REGISTRY.all_summaries()
    counters = _REGISTRY.all_counters()
    for s in summaries:
        obj = {
            "name": s.name,
            "calls": s.calls,
            "avg": round(s.avg_ms, 2),
            "min": round(s.min_ms, 2),
            "max": round(s.max_ms, 2),
            "p95": round(s.p95_ms, 2),
            "p99": round(s.p99_ms, 2),
            "errors": s.errors
        }
        output.append(json.dumps(obj)) 

    for name, value in counters.items():
        obj = {"name": name, "type": "counter", "value": value}
        output.append(json.dumps(obj))
    result = "\n".join(output)
    if path:
        with open(path, "w") as f:
            f.write(result + "\n")
    return result