from dataclasses import dataclass
from typing import Optional, Tuple

_OPERATORS = [">=", "<=", "==", "^", "~", ">", "<"]  # order matters: longest first


@dataclass(frozen=True)
class SemVer:
    major: int
    minor: int
    patch: int

    @staticmethod
    def parse(version_str: str) -> "SemVer":
        parts = version_str.strip().split(".")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            raise ValueError(f"Invalid semantic version: '{version_str}'")
        return SemVer(int(parts[0]), int(parts[1]), int(parts[2]))

    def as_tuple(self) -> Tuple[int, int, int]:
        return (self.major, self.minor, self.patch)

    def __lt__(self, other: "SemVer") -> bool:
        return self.as_tuple() < other.as_tuple()

    def __le__(self, other: "SemVer") -> bool:
        return self.as_tuple() <= other.as_tuple()

    def __gt__(self, other: "SemVer") -> bool:
        return self.as_tuple() > other.as_tuple()

    def __ge__(self, other: "SemVer") -> bool:
        return self.as_tuple() >= other.as_tuple()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, SemVer) and self.as_tuple() == other.as_tuple()


def _split_constraint(constraint: str) -> Tuple[str, str]:
    constraint = constraint.strip()
    for op in _OPERATORS:
        if constraint.startswith(op):
            return op, constraint[len(op):].strip()
    return "==", constraint  # bare version means exact match


def check_version_constraint(version: str, constraint: str) -> Tuple[bool, Optional[str]]:
    """
    Returns (satisfied, error_message). error_message is set for both
    'does not satisfy' cases and malformed-input cases.
    """
    try:
        actual = SemVer.parse(version)
    except ValueError as e:
        return False, str(e)

    op, raw = _split_constraint(constraint)

    try:
        target = SemVer.parse(raw)
    except ValueError:
        return False, f"Invalid constraint version in '{constraint}'"

    if op == "==":
        satisfied = actual == target
    elif op == ">=":
        satisfied = actual >= target
    elif op == "<=":
        satisfied = actual <= target
    elif op == ">":
        satisfied = actual > target
    elif op == "<":
        satisfied = actual < target
    elif op == "^":
        # Compatible within same major version, >= target
        satisfied = actual.major == target.major and actual >= target
    elif op == "~":
        # Compatible within same major.minor, >= target
        satisfied = (
            actual.major == target.major
            and actual.minor == target.minor
            and actual >= target
        )
    else:
        return False, f"Unsupported constraint operator: '{op}'"

    if not satisfied:
        return False, f"version '{version}' does not satisfy constraint '{constraint}'"
    return True, None