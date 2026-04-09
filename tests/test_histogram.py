import time
import unittest
import json
import os
from pytrackio import track, export_histogram, set_buckets
from pytrackio.core import _HISTOGRAM__REGISTRY

class TestHistogram(unittest.TestCase):
    def setUp(self):
        """Clear the registry before every test case."""
        _HISTOGRAM__REGISTRY.clear()

    def test_basic_bucket_logic(self):
        """Test if latencies fall into the correct boundaries."""
        @track(name="test_basic", histogram_buckets=[10, 50, 100])
        def fast_task():
            pass

        fast_task()
        stats = _HISTOGRAM__REGISTRY["test_basic"]
        
        self.assertEqual(stats[10], 1)
        self.assertEqual(stats[50], 0)

    def test_inf_bucket(self):
        """Test if latencies exceeding all buckets land in infinity."""
        @track(name="test_slow", histogram_buckets=[5, 10])
        def slow_task():
            time.sleep(0.02) 

        slow_task()
        stats = _HISTOGRAM__REGISTRY["test_slow"]
        self.assertEqual(stats[float('inf')], 1)
        self.assertEqual(stats[5], 0)
        self.assertEqual(stats[10], 0)

    def test_global_vs_local_buckets(self):
        """Test that local decorator buckets override global set_buckets."""
        set_buckets([1, 2, 3]) 
        
        @track(name="local_override", histogram_buckets=[100, 200])
        def task():
            time.sleep(0.05) 
            
        task()
        stats = _HISTOGRAM__REGISTRY["local_override"]
        self.assertIn(100, stats)
        self.assertNotIn(1, stats)
        self.assertEqual(stats[100], 1)

    def test_multiple_calls_accumulation(self):
        @track(name="multi_call", histogram_buckets=[20, 100]) 
        def task(duration):
            time.sleep(duration)

        task(0.001) 
        task(0.002) 
        task(0.050) 
        
        stats = _HISTOGRAM__REGISTRY["multi_call"]
        self.assertEqual(stats[20], 2)
        self.assertEqual(stats[100], 1)

    def test_json_export(self):
        """Test if the histogram correctly exports to a JSON file."""
        filename = "test_metrics.json"
        
        @track(name="json_test", histogram_buckets=[10])
        def task():
            pass
            
        task()
        export_histogram(filename)
        self.assertTrue(os.path.exists(filename))
        with open(filename, "r") as f:
            data = json.load(f)
            self.assertIn("json_test", data)
            self.assertEqual(data["json_test"]["10"], 1)
        
        os.remove(filename)

if __name__ == "__main__":
    unittest.main()