from ._registry import _REGISTRY, MetricSummary, MetricsRegistry
from ._track import track
from ._timer import timer
from ._report import report, export_json, export_csv, export_dict

def counter(name):
    return _REGISTRY.counter(name)

def get_registry():
    return _REGISTRY

__version__ = "0.7.0"
__author__ = "Deepanshu"
__license__ = "MIT"
__all__ = ["track","timer","counter","report","export_json","export_csv","export_dict","get_registry","MetricSummary","MetricsRegistry","__version__"]
