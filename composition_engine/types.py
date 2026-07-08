from dataclasses import dataclass, field
from typing import Any, Dict, Generic, List, Optional, TypeVar

from .errors import CompositionError

T = TypeVar("T")


@dataclass(frozen=True)
class Dependency:
    module_id: str
    version_constraint: str  # e.g. "^1.2.0", ">=2.0.0", "1.0.0"


@dataclass(frozen=True)
class ModuleDefinition:
    id: str
    version: str
    dependencies: List[Dependency] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Result(Generic[T]):
    ok: bool
    value: Optional[T] = None
    errors: List[CompositionError] = field(default_factory=list)

    @staticmethod
    def success(value: T) -> "Result[T]":
        return Result(ok=True, value=value, errors=[])

    @staticmethod
    def failure(errors: List[CompositionError]) -> "Result[T]":
        return Result(ok=False, value=None, errors=errors)