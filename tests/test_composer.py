from composition_engine.composer import Composer
from composition_engine.errors import ErrorCode
from composition_engine.types import Dependency, ModuleDefinition


def build_valid_composer():
    composer = Composer()
    composer.register_module(ModuleDefinition(
        id="database",
        version="1.4.0",
        config_schema={
            "type": "object",
            "properties": {"host": {"type": "string"}},
            "required": ["host"],
        },
        config={"host": "localhost"},
    ))
    composer.register_module(ModuleDefinition(
        id="cache",
        version="2.0.0",
        config={"ttl": 300},
    ))
    composer.register_module(ModuleDefinition(
        id="app",
        version="1.0.0",
        dependencies=[
            Dependency("database", "^1.0.0"),
            Dependency("cache", ">=1.0.0"),
        ],
        config={"port": 8080},
    ))
    return composer


def test_successful_composition():
    composer = build_valid_composer()
    result = composer.compose(["app"])
    assert result.ok is True
    assert result.value["execution_order"].index("database") < result.value["execution_order"].index("app")
    assert result.value["execution_order"].index("cache") < result.value["execution_order"].index("app")


def test_determinism_across_repeated_calls():
    composer = build_valid_composer()
    results = [composer.compose(["app"]) for _ in range(10)]
    assert all(r.value == results[0].value for r in results)


def test_missing_dependency_detected():
    composer = Composer()
    composer.register_module(ModuleDefinition(
        id="app",
        version="1.0.0",
        dependencies=[Dependency("ghost", "^1.0.0")],
    ))
    result = composer.compose(["app"])
    assert result.ok is False
    assert result.errors[0].code == ErrorCode.MISSING_DEPENDENCY


def test_circular_dependency_detected():
    composer = Composer()
    composer.register_module(ModuleDefinition(id="a", version="1.0.0", dependencies=[Dependency("b", "*")]))
    composer.register_module(ModuleDefinition(id="b", version="1.0.0", dependencies=[Dependency("a", "*")]))
    result = composer.compose(["a"])
    assert result.ok is False
    assert result.errors[0].code == ErrorCode.CIRCULAR_DEPENDENCY


def test_version_incompatibility_detected():
    composer = Composer()
    composer.register_module(ModuleDefinition(id="database", version="2.0.0"))
    composer.register_module(ModuleDefinition(
        id="app", version="1.0.0",
        dependencies=[Dependency("database", "^1.0.0")],
    ))
    result = composer.compose(["app"])
    assert result.ok is False
    assert result.errors[0].code == ErrorCode.VERSION_INCOMPATIBLE


def test_schema_validation_failure_detected():
    composer = Composer()
    composer.register_module(ModuleDefinition(
        id="database",
        version="1.0.0",
        config_schema={"type": "object", "required": ["host"]},
        config={},  # missing required field
    ))
    result = composer.compose(["database"])
    assert result.ok is False
    assert result.errors[0].code == ErrorCode.SCHEMA_VALIDATION_FAILED


def test_unknown_requested_module():
    composer = Composer()
    result = composer.compose(["does-not-exist"])
    assert result.ok is False
    assert result.errors[0].code == ErrorCode.UNKNOWN_MODULE_REQUESTED