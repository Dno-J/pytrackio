"""
pytrackio
=========
Zero-dependency Python performance tracker.

    from pytrackio import track, timer, counter, report

    @track
    def my_function(): ...

    with timer("block"): do_something()

    counter("events").increment()
    report()
"""
from ._instruments import counter, timer, track
from ._report import report
from ._tracker import MetricSummary, get_registry

__version__ = "0.1.0"
__author__  = "Deepanshu"
__license__ = "MIT"

__all__ = ["track","timer","counter","report","get_registry","MetricSummary","__version__"]
