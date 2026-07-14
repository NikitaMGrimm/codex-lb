import json
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).parents[2]

ARM64_NATIVE_OPTIONAL_DEPENDENCIES = {
    "@oxc-parser/binding-linux-arm64-gnu": "0.138.0",
    "@oxc-parser/binding-linux-arm64-musl": "0.138.0",
    "@oxc-resolver/binding-linux-arm64-gnu": "11.24.2",
    "@oxc-resolver/binding-linux-arm64-musl": "11.24.2",
    "@oxlint/binding-linux-arm64-gnu": "1.66.0",
    "@oxlint/binding-linux-arm64-musl": "1.66.0",
    "@rolldown/binding-linux-arm64-gnu": "1.1.5",
    "@rolldown/binding-linux-arm64-musl": "1.1.5",
    "@tailwindcss/oxide-linux-arm64-gnu": "4.3.2",
    "@tailwindcss/oxide-linux-arm64-musl": "4.3.2",
    "@typescript/typescript-linux-arm64": "7.0.2",
    "lightningcss-linux-arm64-gnu": "1.32.0",
    "lightningcss-linux-arm64-musl": "1.32.0",
}

NESTED_ARM64_NATIVE_LOCK_ENTRIES = {
    "node_modules/vitest/node_modules/@rolldown/binding-linux-arm64-gnu": "1.1.3",
    "node_modules/vitest/node_modules/@rolldown/binding-linux-arm64-musl": "1.1.3",
}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_arm64_native_packages_are_locked_as_exact_optional_dependencies() -> None:
    package_json = _read_json(REPOSITORY_ROOT / "frontend" / "package.json")
    package_lock = _read_json(REPOSITORY_ROOT / "frontend" / "package-lock.json")
    root_lock_record = package_lock["packages"][""]

    assert package_json["optionalDependencies"] == ARM64_NATIVE_OPTIONAL_DEPENDENCIES
    assert root_lock_record["optionalDependencies"] == ARM64_NATIVE_OPTIONAL_DEPENDENCIES

    lock_entries = {
        **{
            f"node_modules/{package_name}": version
            for package_name, version in ARM64_NATIVE_OPTIONAL_DEPENDENCIES.items()
        },
        **NESTED_ARM64_NATIVE_LOCK_ENTRIES,
    }
    for lock_path, version in lock_entries.items():
        lock_record = package_lock["packages"][lock_path]

        assert lock_record["version"] == version
        assert lock_record["optional"] is True
        assert lock_record["os"] == ["linux"]
        assert lock_record["cpu"] == ["arm64"]
        assert "libc" not in lock_record
        assert lock_record["resolved"].startswith("https://registry.npmjs.org/")
        assert lock_record["integrity"].startswith("sha512-")
