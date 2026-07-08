from typing import List

import jsonschema

from .errors import CompositionError, ErrorCode
from .types import ModuleDefinition, Result


def validate_module_config(module: ModuleDefinition) -> Result[None]:
    """Validates module.config against module.config_schema (JSON Schema)."""
    if not module.config_schema:
        return Result.success(None)

    try:
        validator_cls = jsonschema.validators.validator_for(module.config_schema)
        validator_cls.check_schema(module.config_schema)
    except jsonschema.exceptions.SchemaError as e:
        return Result.failure([
            CompositionError(
                ErrorCode.SCHEMA_VALIDATION_FAILED,
                f"Module '{module.id}' has an invalid JSON Schema: {e.message}",
                module.id,
            )
        ])

    validator = validator_cls(module.config_schema)
    raw_errors = sorted(
        validator.iter_errors(module.config),
        key=lambda e: (list(map(str, e.path)), e.message),
    )

    if not raw_errors:
        return Result.success(None)

    comp_errors: List[CompositionError] = [
        CompositionError(
            ErrorCode.SCHEMA_VALIDATION_FAILED,
            e.message,
            module.id,
            {"path": list(map(str, e.path))},
        )
        for e in raw_errors
    ]
    return Result.failure(comp_errors)