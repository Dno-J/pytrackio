"""
pytrackio
=========
Zero-dependency Python performance tracker.

Track function calls, timings, and errors with a single decorator.
No external servers. No configuration. Just import and use.

Basic usage::

    from pytrackio import track, timer, counter, report

    @track
    def my_function():
        ...

    with timer("block_name"):
        do_something()

    counter("events").increment()

    report()   # print summary table

"""

from ._instruments import counter, timer, track
from ._report import report
from ._tracker import MetricSummary, get_registry

__version__ = "0.1.0"
__author__  = "Deepanshu"
__license__ = "MIT"

__all__ = [
    # Instrumentation
    "track",
    "timer",
    "counter",
    # Reporting
    "report",
    # Advanced / programmatic access
    "get_registry",
    "MetricSummary",
    # Meta
    "__version__",
]
