import json
import os
from pathlib import Path

from . import result

if PATH := os.getenv("LOCALAPPDATA"):
    METADATA_JSON = Path(PATH) / ".ayuman" / "metadata.json"


def _ensure_metadata_file() -> None:
    METADATA_JSON.parent.mkdir(parents=True, exist_ok=True)
    if not METADATA_JSON.exists():
        METADATA_JSON.write_text(json.dumps({"installed_packages": []}, indent=4))


def read_metadata() -> dict:
    _ensure_metadata_file()
    with open(METADATA_JSON, "r") as f:
        return json.load(f)


def write_metadata(data: dict) -> None:
    _ensure_metadata_file()
    with open(METADATA_JSON, "w") as f:
        json.dump(data, f, indent=4)


def add_package(install_result: result.InstallResult):
    data = read_metadata()

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
    write_metadata(data)
