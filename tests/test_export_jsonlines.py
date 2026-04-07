import os
import json
import pytest
from pytrackio import _REGISTRY, export_jsonlines, track, counter

def test_export_jsonlines_format():
    _REGISTRY.reset()
    @track(name="test_func")
    def func(): pass
    func()
    counter("test_count").increment(5)
    
    output = export_jsonlines()
    lines = output.strip().split('\n')
    assert len(lines) == 2
    
    data = [json.loads(l) for l in lines]
    names = [d["name"] for d in data]
    assert "test_func" in names
    assert "test_count" in names

def test_export_jsonlines_file_writing(tmp_path):
    _REGISTRY.reset()
    counter("file_metric").increment(1)
    
    path = tmp_path / "metrics.jsonl"
    export_jsonlines(str(path))
    
    assert os.path.exists(path)
    with open(path, "r") as f:
        line = f.readline()
        assert '"name": "file_metric"' in line