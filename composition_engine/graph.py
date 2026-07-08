from typing import Dict, List, Optional

from .types import ModuleDefinition


class DependencyGraph:
    """
    Operates on an already-resolved closure of modules (i.e. every
    dependency id referenced is guaranteed to be a key in `modules`).
    Missing-dependency detection happens upstream in the composer.
    """

    def __init__(self, modules: Dict[str, ModuleDefinition]) -> None:
        self.modules = modules

    def detect_cycle(self, node_ids: List[str]) -> Optional[List[str]]:
        """DFS cycle detection with deterministic traversal order.
        Returns the cycle path if found, else None."""
        visited: set = set()
        in_stack: set = set()
        path: List[str] = []

        def visit(node: str) -> Optional[List[str]]:
            if node in in_stack:
                cycle_start = path.index(node)
                return path[cycle_start:] + [node]
            if node in visited:
                return None

            visited.add(node)
            in_stack.add(node)
            path.append(node)

            module = self.modules.get(node)
            dep_ids = sorted(d.module_id for d in module.dependencies) if module else []
            for dep_id in dep_ids:
                if dep_id not in self.modules:
                    continue
                found = visit(dep_id)
                if found:
                    return found

            path.pop()
            in_stack.remove(node)
            return None

        for nid in sorted(node_ids):
            if nid not in visited:
                cycle = visit(nid)
                if cycle:
                    return cycle
        return None