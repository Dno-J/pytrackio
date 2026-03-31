"""
tests/test_pytrackio.py
-----------------------
Full test suite — 25 tests covering every public API.
Run: python -m pytest tests/ -v
"""

import io
import threading
import time
import unittest

from pytrackio import counter, report, timer, track
from pytrackio._tracker import MetricsRegistry, get_registry


def fresh() -> MetricsRegistry:
    """Return a fresh registry for each test."""
    r = get_registry()
    r.reset()
    return r


# ===========================================================================
# @track decorator
# ===========================================================================

class TestTrackDecorator(unittest.TestCase):

    def setUp(self):
        fresh()

    def test_records_successful_call(self):
        @track
        def add(a, b): return a + b

        result = add(1, 2)
        self.assertEqual(result, 3)
        s = get_registry().all_summaries()
        self.assertEqual(len(s), 1)
        self.assertEqual(s[0].calls, 1)
        self.assertEqual(s[0].success, 1)
        self.assertEqual(s[0].errors, 0)

    def test_records_multiple_calls(self):
        @track
        def noop(): pass

        for _ in range(5):
            noop()

        s = get_registry().all_summaries()[0]
        self.assertEqual(s.calls, 5)

    def test_records_error(self):
        @track
        def boom(): raise ValueError("fail")

        with self.assertRaises(ValueError):
            boom()

        s = get_registry().all_summaries()[0]
        self.assertEqual(s.errors, 1)
        self.assertEqual(s.success, 0)

    def test_does_not_swallow_exception(self):
        @track
        def explode(): raise RuntimeError("must propagate")

        with self.assertRaises(RuntimeError):
            explode()

    def test_custom_name(self):
        @track(name="my_custom_metric")
        def some_func(): pass

        some_func()
        names = [s.name for s in get_registry().all_summaries()]
        self.assertIn("my_custom_metric", names)

    def test_preserves_function_metadata(self):
        @track
        def documented():
            """My docstring."""
            pass

        self.assertEqual(documented.__name__, "documented")
        self.assertEqual(documented.__doc__, "My docstring.")

    def test_records_duration_is_positive(self):
        @track
        def slow():
            time.sleep(0.01)

        slow()
        s = get_registry().all_summaries()[0]
        self.assertGreater(s.avg_ms, 0)

    def test_error_rate_calculation(self):
        @track
        def flaky(fail=False):
            if fail: raise Exception("err")

        flaky(fail=False)
        flaky(fail=False)
        with self.assertRaises(Exception):
            flaky(fail=True)

        s = get_registry().all_summaries()[0]
        self.assertEqual(s.calls, 3)
        self.assertEqual(s.errors, 1)
        self.assertAlmostEqual(s.error_rate, 33.3, delta=0.1)

    def test_multiple_functions_tracked_separately(self):
        @track
        def func_a(): pass

        @track
        def func_b(): pass

        func_a()
        func_a()
        func_b()

        summaries = {s.name.split(".")[-1]: s for s in get_registry().all_summaries()}
        self.assertEqual(summaries["func_a"].calls, 2)
        self.assertEqual(summaries["func_b"].calls, 1)


# ===========================================================================
# timer() context manager
# ===========================================================================

class TestTimer(unittest.TestCase):

    def setUp(self):
        fresh()

    def test_records_block(self):
        with timer("my_block"):
            time.sleep(0.01)

        s = get_registry().summary("my_block")
        self.assertIsNotNone(s)
        self.assertEqual(s.calls, 1)
        self.assertGreater(s.avg_ms, 0)

    def test_records_error_in_block(self):
        with self.assertRaises(ZeroDivisionError):
            with timer("bad_block"):
                _ = 1 / 0

        s = get_registry().summary("bad_block")
        self.assertEqual(s.errors, 1)

    def test_does_not_swallow_exception(self):
        with self.assertRaises(KeyError):
            with timer("block"):
                raise KeyError("propagate me")

    def test_multiple_uses_same_name(self):
        for _ in range(3):
            with timer("loop"):
                pass

        s = get_registry().summary("loop")
        self.assertEqual(s.calls, 3)

    def test_min_max_avg(self):
        with timer("t"):
            time.sleep(0.01)
        with timer("t"):
            time.sleep(0.02)

        s = get_registry().summary("t")
        self.assertLessEqual(s.min_ms, s.avg_ms)
        self.assertGreaterEqual(s.max_ms, s.avg_ms)


# ===========================================================================
# counter()
# ===========================================================================

class TestCounter(unittest.TestCase):

    def setUp(self):
        fresh()

    def test_increment(self):
        counter("hits").increment()
        counter("hits").increment()
        self.assertEqual(counter("hits").value, 2)

    def test_increment_by(self):
        counter("events").increment(10)
        self.assertEqual(counter("events").value, 10)

    def test_decrement(self):
        counter("stock").increment(5)
        counter("stock").decrement(2)
        self.assertEqual(counter("stock").value, 3)

    def test_reset(self):
        counter("x").increment(100)
        counter("x").reset()
        self.assertEqual(counter("x").value, 0)

    def test_multiple_counters(self):
        counter("a").increment()
        counter("b").increment(3)
        counters = {c.name: c.value for c in get_registry().all_counters()}
        self.assertEqual(counters["a"], 1)
        self.assertEqual(counters["b"], 3)

    def test_counter_starts_at_zero(self):
        self.assertEqual(counter("brand_new").value, 0)


# ===========================================================================
# Registry
# ===========================================================================

class TestRegistry(unittest.TestCase):

    def setUp(self):
        fresh()

    def test_reset_clears_all(self):
        @track
        def f(): pass
        f()
        counter("x").increment()

        get_registry().reset()
        self.assertEqual(get_registry().all_summaries(), [])
        self.assertEqual(get_registry().all_counters(), [])

    def test_summary_returns_none_for_unknown(self):
        self.assertIsNone(get_registry().summary("does_not_exist"))

    def test_uptime_increases(self):
        t1 = get_registry().uptime_seconds()
        time.sleep(0.05)
        t2 = get_registry().uptime_seconds()
        self.assertGreater(t2, t1)

    def test_thread_safety(self):
        """Multiple threads recording simultaneously should not corrupt state."""
        @track
        def worker(): time.sleep(0.001)

        threads = [threading.Thread(target=worker) for _ in range(20)]
        for t in threads: t.start()
        for t in threads: t.join()

        s = get_registry().all_summaries()
        self.assertEqual(len(s), 1)
        self.assertEqual(s[0].calls, 20)


# ===========================================================================
# report()
# ===========================================================================

class TestReport(unittest.TestCase):

    def setUp(self):
        fresh()

    def _capture(self, **kwargs) -> str:
        buf = io.StringIO()
        report(stream=buf, colour=False, **kwargs)
        return buf.getvalue()

    def test_report_runs_with_no_data(self):
        output = self._capture()
        self.assertIn("pytrackio", output)

    def test_report_shows_function_name(self):
        @track(name="test_func")
        def f(): pass
        f()

        output = self._capture()
        self.assertIn("test_func", output)

    def test_report_shows_counter(self):
        counter("page_views").increment(42)
        output = self._capture()
        self.assertIn("page_views", output)
        self.assertIn("42", output)

    def test_report_returns_string(self):
        result = self._capture()
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_report_hides_counters_when_disabled(self):
        counter("hidden").increment(5)
        output = self._capture(show_counters=False)
        self.assertNotIn("hidden", output)


# ===========================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
