import heapq
from typing import Dict, List, Optional, Set, Tuple

from .types import ModuleDefinition


def topological_sort(
    closure: Set[str], modules: Dict[str, ModuleDefinition]
) -> Tuple[Optional[List[str]], Optional[List[str]]]:
    """
    Deterministic Kahn's algorithm: uses a min-heap over module ids so that
    whenever multiple modules become 'ready' at once, the alphabetically
    smallest is always chosen first. This guarantees identical output order
    for identical input, independent of dict/set iteration order.

    Returns (order, unresolved). If a cycle exists, order is None and
    unresolved contains the leftover (stuck) node ids.
    """
    in_degree: Dict[str, int] = {mid: 0 for mid in closure}
    dependents: Dict[str, List[str]] = {mid: [] for mid in closure}

    for mid in closure:
        module = modules[mid]
        for dep in module.dependencies:
            if dep.module_id in closure:
                in_degree[mid] += 1
                dependents[dep.module_id].append(mid)

    heap: List[str] = sorted(mid for mid in closure if in_degree[mid] == 0)
    heapq.heapify(heap)

    order: List[str] = []
    while heap:
        node = heapq.heappop(heap)
        order.append(node)
        for dependent in sorted(dependents[node]):
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                heapq.heappush(heap, dependent)

    if len(order) != len(closure):
        unresolved = sorted(closure - set(order))
        return None, unresolved

    return order, None