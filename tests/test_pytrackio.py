import time, threading, unittest
from pytrackio import track, timer, counter, report
from pytrackio._registry import _REGISTRY

def fresh():
    _REGISTRY.reset()

class TestTrack(unittest.TestCase):
    def setUp(self): fresh()

    def test_basic_call(self):
        @track
        def add(a, b): return a + b
        self.assertEqual(add(1, 2), 3)
        s = _REGISTRY.all_summaries()
        self.assertEqual(len(s), 1)
        self.assertEqual(s[0].calls, 1)

    def test_multiple_calls(self):
        @track
        def noop(): pass
        for _ in range(5): noop()
        self.assertEqual(_REGISTRY.all_summaries()[0].calls, 5)

    def test_records_error(self):
        @track
        def boom(): raise ValueError("fail")
        with self.assertRaises(ValueError): boom()
        self.assertEqual(_REGISTRY.all_summaries()[0].errors, 1)

    def test_exception_propagates(self):
        @track
        def explode(): raise RuntimeError("x")
        with self.assertRaises(RuntimeError): explode()

    def test_custom_name(self):
        @track(name="custom")
        def f(): pass
        f()
        names = [s.name for s in _REGISTRY.all_summaries()]
        self.assertIn("custom", names)

    def test_preserves_metadata(self):
        @track
        def documented():
            """My docstring."""
        self.assertEqual(documented.__name__, "documented")

    def test_duration_positive(self):
        @track
        def slow(): time.sleep(0.01)
        slow()
        self.assertGreater(_REGISTRY.all_summaries()[0].avg_ms, 0)

    def test_error_rate(self):
        @track
        def flaky(fail=False):
            if fail: raise Exception("err")
        flaky(); flaky()
        with self.assertRaises(Exception): flaky(fail=True)
        s = _REGISTRY.all_summaries()[0]
        self.assertEqual(s.calls, 3)
        self.assertEqual(s.errors, 1)
        self.assertAlmostEqual(s.error_rate, 33.3, delta=0.1)

    def test_multiple_functions(self):
        @track
        def fa(): pass
        @track
        def fb(): pass
        fa(); fa(); fb()
        summaries = {s.name.split(".")[-1]: s for s in _REGISTRY.all_summaries()}
        self.assertEqual(summaries["fa"].calls, 2)
        self.assertEqual(summaries["fb"].calls, 1)

class TestTimer(unittest.TestCase):
    def setUp(self): fresh()

    def test_records_block(self):
        with timer("block"): time.sleep(0.01)
        s = _REGISTRY.summary("block")
        self.assertIsNotNone(s)
        self.assertGreater(s.avg_ms, 0)

    def test_records_error(self):
        with self.assertRaises(ZeroDivisionError):
            with timer("bad"): _ = 1/0
        self.assertEqual(_REGISTRY.summary("bad").errors, 1)

    def test_exception_propagates(self):
        with self.assertRaises(KeyError):
            with timer("t"): raise KeyError("x")

    def test_multiple_uses(self):
        for _ in range(3):
            with timer("loop"): pass
        self.assertEqual(_REGISTRY.summary("loop").calls, 3)

    def test_min_max(self):
        with timer("t"): time.sleep(0.01)
        with timer("t"): time.sleep(0.02)
        s = _REGISTRY.summary("t")
        self.assertLessEqual(s.min_ms, s.max_ms)

class TestCounter(unittest.TestCase):
    def setUp(self): fresh()

    def test_increment(self):
        counter("hits").increment()
        counter("hits").increment()
        self.assertEqual(counter("hits").value, 2)

    def test_increment_by(self):
        counter("x").increment(10)
        self.assertEqual(counter("x").value, 10)

    def test_decrement(self):
        counter("x").increment(5)
        counter("x").decrement(2)
        self.assertEqual(counter("x").value, 3)

    def test_reset(self):
        counter("x").increment(100)
        counter("x").reset()
        self.assertEqual(counter("x").value, 0)

    def test_starts_at_zero(self):
        self.assertEqual(counter("new").value, 0)

class TestRegistry(unittest.TestCase):
    def setUp(self): fresh()

    def test_reset_clears(self):
        @track
        def f(): pass
        f(); counter("x").increment()
        _REGISTRY.reset()
        self.assertEqual(_REGISTRY.all_summaries(), [])
        self.assertEqual(_REGISTRY.all_counters(), {})

    def test_summary_none_for_unknown(self):
        self.assertIsNone(_REGISTRY.summary("nope"))

    def test_uptime_increases(self):
        t1 = _REGISTRY.uptime_seconds()
        time.sleep(0.05)
        self.assertGreater(_REGISTRY.uptime_seconds(), t1)

    def test_thread_safety(self):
        @track
        def worker(): time.sleep(0.001)
        threads = [threading.Thread(target=worker) for _ in range(20)]
        for t in threads: t.start()
        for t in threads: t.join()
        self.assertEqual(_REGISTRY.all_summaries()[0].calls, 20)

class TestReport(unittest.TestCase):
    def setUp(self): fresh()

    def test_runs_with_no_data(self):
        out = report()
        self.assertIn("pytrackio", out)

    def test_shows_function_name(self):
        @track(name="my_func")
        def f(): pass
        f()
        self.assertIn("my_func", report())

    def test_shows_counter(self):
        counter("views").increment(42)
        out = report()
        self.assertIn("views", out)
        self.assertIn("42", out)

    def test_hides_counters(self):
        counter("hidden").increment(5)
        self.assertNotIn("hidden", report(show_counters=False))

if __name__ == "__main__":
    unittest.main(verbosity=2)
