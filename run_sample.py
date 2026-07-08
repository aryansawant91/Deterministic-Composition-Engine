import json
import sys

from composition_engine import Composer, Dependency, ModuleDefinition


def load_and_compose(input_path: str):
    with open(input_path, "r") as f:
        data = json.load(f)

    composer = Composer()

    for m in data["modules"]:
        deps = [
            Dependency(d["module_id"], d["version_constraint"])
            for d in m.get("dependencies", [])
        ]
        module = ModuleDefinition(
            id=m["id"],
            version=m["version"],
            dependencies=deps,
            config_schema=m.get("config_schema", {}),
            config=m.get("config", {}),
        )
        reg_result = composer.register_module(module)
        if not reg_result.ok:
            print("Registration failed:")
            print(json.dumps([e.to_dict() for e in reg_result.errors], indent=2))
            sys.exit(1)

    result = composer.compose(data["compose_request"])

    if result.ok:
        print("Composition succeeded:")
        print(json.dumps(result.value, indent=2))
    else:
        print("Composition failed:")
        print(json.dumps({"ok": False, "errors": [e.to_dict() for e in result.errors]}, indent=2))


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "samples/input/example_modules.json"
    load_and_compose(path)