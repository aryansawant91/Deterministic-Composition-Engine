from typing import Dict, List, Optional

from .errors import CompositionError, ErrorCode
from .types import ModuleDefinition, Result


class ModuleRegistry:
    """Holds registered module definitions. No hidden state beyond this dict."""

    def __init__(self) -> None:
        self._modules: Dict[str, ModuleDefinition] = {}

    def register(self, module: ModuleDefinition) -> Result[None]:
        if module.id in self._modules:
            return Result.failure([
                CompositionError(
                    ErrorCode.DUPLICATE_MODULE,
                    f"Module '{module.id}' is already registered",
                    module.id,
                )
            ])
        self._modules[module.id] = module
        return Result.success(None)

    def get(self, module_id: str) -> Optional[ModuleDefinition]:
        return self._modules.get(module_id)

    def all_ids(self) -> List[str]:
        return sorted(self._modules.keys())

    def as_map(self) -> Dict[str, ModuleDefinition]:
        return dict(self._modules)