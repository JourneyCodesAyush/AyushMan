import json
import os
from pathlib import Path

from . import result, global_paths


REGISTRY_PATH = global_paths.GLOBAL_METADATA


def _ensure_metadata_file() -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not REGISTRY_PATH.exists():
        REGISTRY_PATH.write_text(json.dumps({"installed_packages": []}, indent=4))


def _read_metadata() -> dict:
    _ensure_metadata_file()
    with open(REGISTRY_PATH, "r") as f:
        return json.load(f)


def _write_metadata(data: dict) -> None:
    _ensure_metadata_file()
    with open(REGISTRY_PATH, "w") as f:
        json.dump(data, f, indent=4)


def add_package(install_result: result.InstallResult):
    data = _read_metadata()

    data["installed_packages"] = [
        pkg
        for pkg in data["installed_packages"]
        if pkg["name"] != install_result.package_name
        or pkg["version"] != install_result.version
    ]
    data["installed_packages"].append(
        {
            "name": install_result.package_name,
            "version": install_result.version,
            "install_path": install_result.install_path,
            "zip_file_name": install_result.zip_file_name,
            "metadata_path": install_result.metadata_path,
        }
    )
    _write_metadata(data)


def list_package() -> list[str]:
    data = _read_metadata()

    package_list: list[str] = []
    for pkg in data["installed_packages"]:
        package_list.append(f"{pkg['name']} {pkg['version']}")

    return package_list
