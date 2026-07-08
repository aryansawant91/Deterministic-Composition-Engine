from typing import Any, Dict, List

from .types import ModuleDefinition


def generate_runtime_config(
    order: List[str], modules: Dict[str, ModuleDefinition]
) -> Dict[str, Any]:
    """Pure function: identical (order, modules) always produces an
    identical output. No mutation, no external state, no timestamps."""
    return {
        "execution_order": order,
        "modules": {
            mid: {
                "version": modules[mid].version,
                "config": modules[mid].config,
                "dependencies": sorted(d.module_id for d in modules[mid].dependencies),
            }
            for mid in order
        },
    }