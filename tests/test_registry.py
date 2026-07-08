from composition_engine.errors import ErrorCode
from composition_engine.registry import ModuleRegistry
from composition_engine.types import ModuleDefinition


def test_register_and_get():
    registry = ModuleRegistry()
    module = ModuleDefinition(id="a", version="1.0.0")
    result = registry.register(module)
    assert result.ok is True
    assert registry.get("a") is module


def test_duplicate_registration_fails():
    registry = ModuleRegistry()
    module = ModuleDefinition(id="a", version="1.0.0")
    registry.register(module)
    result = registry.register(module)
    assert result.ok is False
    assert result.errors[0].code == ErrorCode.DUPLICATE_MODULE


def test_all_ids_is_sorted():
    registry = ModuleRegistry()
    registry.register(ModuleDefinition(id="zeta", version="1.0.0"))
    registry.register(ModuleDefinition(id="alpha", version="1.0.0"))
    assert registry.all_ids() == ["alpha", "zeta"]