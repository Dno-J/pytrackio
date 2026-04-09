import pytest
from pytrackio import _REGISTRY, track

class TestClass:
    @track
    def instance_method(self):
        return "instance"
    
    @classmethod
    @track
    def class_method(cls):
        return "class"
    
    @staticmethod
    @track
    def static_method():
        return "static"

def test_all_method_types_tracked():
    _REGISTRY.reset()
    obj = TestClass()

    obj.instance_method()
    TestClass.class_method()
    TestClass.static_method()

    summaries = {s.name: s for s in _REGISTRY.all_summaries()}

    assert "TestClass.instance_method" in summaries
    assert "TestClass.class_method" in summaries
    assert "TestClass.static_method" in summaries

    for name in summaries:
        assert summaries[name].calls == 1
