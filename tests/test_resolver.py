from composition_engine.resolver import topological_sort
from composition_engine.types import Dependency, ModuleDefinition


def make_module(mid, deps=None):
    return ModuleDefinition(
        id=mid,
        version="1.0.0",
        dependencies=[Dependency(d, "*") for d in (deps or [])],
    )


def test_simple_ordering_respects_dependencies():
    modules = {
        "app": make_module("app", ["db", "cache"]),
        "db": make_module("db"),
        "cache": make_module("cache"),
    }
    order, unresolved = topological_sort(set(modules.keys()), modules)
    assert unresolved is None
    assert order.index("db") < order.index("app")
    assert order.index("cache") < order.index("app")


def test_deterministic_tiebreak_is_alphabetical():
    # b and c both have no deps and become ready simultaneously
    modules = {
        "a": make_module("a", ["b", "c"]),
        "b": make_module("b"),
        "c": make_module("c"),
    }
    order, _ = topological_sort(set(modules.keys()), modules)
    assert order == ["b", "c", "a"]


def test_repeated_calls_produce_identical_order():
    modules = {
        "x": make_module("x", ["y", "z", "w"]),
        "y": make_module("y"),
        "z": make_module("z"),
        "w": make_module("w"),
    }
    results = [topological_sort(set(modules.keys()), modules)[0] for _ in range(20)]
    assert all(r == results[0] for r in results)


def test_cycle_returns_unresolved():
    modules = {
        "a": make_module("a", ["b"]),
        "b": make_module("b", ["a"]),
    }
    order, unresolved = topological_sort(set(modules.keys()), modules)
    assert order is None
    assert unresolved == ["a", "b"]