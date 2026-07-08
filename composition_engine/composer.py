from typing import Any, Dict, List, Set

from .compatibility import check_version_constraint
from .config_generator import generate_runtime_config
from .errors import CompositionError, ErrorCode
from .graph import DependencyGraph
from .registry import ModuleRegistry
from .resolver import topological_sort
from .types import ModuleDefinition, Result
from .validator import validate_module_config


def _sort_errors(errors: List[CompositionError]) -> List[CompositionError]:
    return sorted(errors, key=lambda e: (e.module_id or "", e.code.value, e.message))


class Composer:
    def __init__(self) -> None:
        self.registry = ModuleRegistry()

    def register_module(self, module: ModuleDefinition) -> Result[None]:
        return self.registry.register(module)

    def compose(self, requested_ids: List[str]) -> Result[Dict[str, Any]]:
        modules_map = self.registry.as_map()
        errors: List[CompositionError] = []

        # Step 1: compute transitive closure, catch unknown/missing deps
        closure: Set[str] = set()
        unknown_requested: Set[str] = set()
        queue: List[str] = list(requested_ids)
        seen: Set[str] = set()

        while queue:
            mid = queue.pop(0)
            if mid in seen:
                continue
            seen.add(mid)

            module = modules_map.get(mid)
            if module is None:
                unknown_requested.add(mid)
                continue

            closure.add(mid)
            for dep in module.dependencies:
                if dep.module_id not in modules_map:
                    errors.append(CompositionError(
                        ErrorCode.MISSING_DEPENDENCY,
                        f"Module '{mid}' depends on unregistered module '{dep.module_id}'",
                        mid,
                        {"dependency": dep.module_id},
                    ))
                else:
                    queue.append(dep.module_id)

        for mid in unknown_requested:
            errors.append(CompositionError(
                ErrorCode.UNKNOWN_MODULE_REQUESTED,
                f"Requested module '{mid}' is not registered",
                mid,
            ))

        if errors:
            return Result.failure(_sort_errors(errors))

        # Step 2: cycle detection (before we try to schema/compat validate,
        # since a cyclic graph has no meaningful execution order anyway)
        closure_modules = {mid: modules_map[mid] for mid in closure}
        graph = DependencyGraph(closure_modules)
        cycle = graph.detect_cycle(list(closure))
        if cycle:
            return Result.failure([CompositionError(
                ErrorCode.CIRCULAR_DEPENDENCY,
                f"Circular dependency detected: {' -> '.join(cycle)}",
                None,
                {"cycle": cycle},
            )])

        # Step 3: per-module schema validation
        for mid in sorted(closure):
            result = validate_module_config(closure_modules[mid])
            if not result.ok:
                errors.extend(result.errors)

        # Step 4: dependency version compatibility
        for mid in sorted(closure):
            module = closure_modules[mid]
            for dep in module.dependencies:
                dep_module = modules_map.get(dep.module_id)
                if dep_module is None:
                    continue
                ok, msg = check_version_constraint(dep_module.version, dep.version_constraint)
                if not ok:
                    errors.append(CompositionError(
                        ErrorCode.VERSION_INCOMPATIBLE,
                        f"Module '{mid}' requires '{dep.module_id}' "
                        f"{dep.version_constraint}, but found {dep_module.version} ({msg})",
                        mid,
                        {
                            "dependency": dep.module_id,
                            "constraint": dep.version_constraint,
                            "found_version": dep_module.version,
                        },
                    ))

        if errors:
            return Result.failure(_sort_errors(errors))

        # Step 5: deterministic topological ordering
        order, unresolved = topological_sort(closure, closure_modules)
        if order is None:
            return Result.failure([CompositionError(
                ErrorCode.CIRCULAR_DEPENDENCY,
                "Cycle detected during topological sort",
                None,
                {"unresolved": unresolved},
            )])

        # Step 6: generate runtime config
        config = generate_runtime_config(order, closure_modules)
        return Result.success(config)