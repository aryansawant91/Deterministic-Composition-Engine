from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class ErrorCode(Enum):
    MISSING_DEPENDENCY = "MISSING_DEPENDENCY"
    CIRCULAR_DEPENDENCY = "CIRCULAR_DEPENDENCY"
    VERSION_INCOMPATIBLE = "VERSION_INCOMPATIBLE"
    SCHEMA_VALIDATION_FAILED = "SCHEMA_VALIDATION_FAILED"
    DUPLICATE_MODULE = "DUPLICATE_MODULE"
    UNKNOWN_MODULE_REQUESTED = "UNKNOWN_MODULE_REQUESTED"
    INVALID_VERSION_FORMAT = "INVALID_VERSION_FORMAT"


@dataclass(frozen=True)
class CompositionError:
    code: ErrorCode
    message: str
    module_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code.value,
            "message": self.message,
            "module_id": self.module_id,
            "details": self.details,
        }