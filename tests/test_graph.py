from composition_engine.graph import DependencyGraph
from composition_engine.types import Dependency, ModuleDefinition


def make_module(mid, deps=None):
    return ModuleDefinition(
        id=mid,
        version="1.0.0",
        dependencies=[Dependency(d, "*") for d in (deps or [])],
    )


def test_no_cycle_in_linear_chain():
    modules = {
        "a": make_module("a", ["b"]),
        "b": make_module("b", ["c"]),
        "c": make_module("c"),
    }
    graph = DependencyGraph(modules)
    assert graph.detect_cycle(list(modules.keys())) is None


def test_detects_direct_cycle():
    modules = {
        "a": make_module("a", ["b"]),
        "b": make_module("b", ["a"]),
    }
    graph = DependencyGraph(modules)
    cycle = graph.detect_cycle(list(modules.keys()))
    assert cycle is not None
    assert set(cycle) == {"a", "b"}


def test_detects_indirect_cycle():
    modules = {
        "a": make_module("a", ["b"]),
        "b": make_module("b", ["c"]),
        "c": make_module("c", ["a"]),
    }
    graph = DependencyGraph(modules)
    cycle = graph.detect_cycle(list(modules.keys()))
    assert cycle is not None
    assert {"a", "b", "c"}.issubset(set(cycle))