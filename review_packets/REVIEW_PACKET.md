# Review Packet — Deterministic Composition Engine

## Architecture Summary

The engine is a linear pipeline of independent, pure stages: registration →
closure resolution → cycle detection → schema validation → version
compatibility → deterministic topological sort → runtime config generation.
Every stage returns a `Result` object rather than throwing, so failures are
structured and inspectable rather than exceptions bubbling up unpredictably.

## Entry Point

`composition_engine.Composer` is the sole public entry point.

```python
composer = Composer()
composer.register_module(module_definition)   # Result[None]
composer.compose(["module_id_a", "module_id_b"])  # Result[dict]
```

## Core Execution Flow (3 critical files)

1. **`composer.py`** — orchestrates the full pipeline; this is what an
   integrator calls and the only file that needs to be understood to use
   the engine.
2. **`resolver.py`** — implements the determinism guarantee via a
   min-heap-based Kahn's algorithm; this is the file to review if auditing
   "does identical input always give identical output."
3. **`graph.py`** — cycle detection; this is the file to review for
   correctness of invalid-graph rejection.

## Sample Input

See `samples/input/example_modules.json` — four modules (`database`,
`cache`, `auth`, `app`) with a real dependency chain and version
constraints.

## Sample Output

See `samples/output/example_output_success.json`. Verified output from
actual run:

```json
{
  "execution_order": ["cache", "database", "auth", "app"],
  ...
}
```

## Failure Cases (verified via `run_sample.py`)

1. **Circular dependency** — `samples/input/example_invalid_cycle.json`
   produces `CIRCULAR_DEPENDENCY` with the full cycle path in `details`.
2. **Missing dependency** — covered in `tests/test_composer.py::test_missing_dependency_detected`.
3. **Version incompatibility** — covered in `tests/test_composer.py::test_version_incompatibility_detected`.
4. **Schema validation failure** — covered in `tests/test_composer.py::test_schema_validation_failure_detected`.
5. **Unknown requested module** — covered in `tests/test_composer.py::test_unknown_requested_module`.

## Integration Notes

- Integrators interact only with `Composer.register_module()` and
  `Composer.compose()`. No other class in this package is part of the
  public contract.
- No assumptions are made about what calls `compose()` or what consumes its
  output — the returned dict is a plain, JSON-serializable structure with no
  engine-specific types leaking out.
- This engine does not execute anything; `generate_runtime_config`'s output
  is descriptive data only, safe to hand off to any downstream runtime.

## Validation Evidence

- [ ] Screenshot: `pytest -v` — 24/24 passing
- [ ] Screenshot: `python run_sample.py samples/input/example_modules.json` — success case
- [ ] Screenshot: `python run_sample.py samples/input/example_invalid_cycle.json` — failure case

*(Insert your terminal screenshots here before submission — you already have
the exact terminal output from this session to screenshot.)*