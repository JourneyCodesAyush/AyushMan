import json

from . import global_paths, result

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


def get_installed_version(package_name: str) -> str:
    data: dict = _read_metadata()
    for pkg in data["installed_packages"]:
        if pkg["name"] == package_name:
            return pkg["version"]
    return ""


def remove_package(package_name: str) -> bool:
    data: dict = _read_metadata()

    before: int = len(data["installed_packages"])

    data["installed_packages"] = [
        pkg for pkg in data["installed_packages"] if pkg["name"] != package_name
    ]

    removed: bool = before != len(data["installed_packages"])
    if removed:
        _write_metadata(data)
    return removed


def set_bin_in_path(value: bool) -> None:
    data: dict = _read_metadata()
    data["bin_in_path"] = value
    _write_metadata(data)


def get_bin_in_path() -> bool:
    data: dict = _read_metadata()
    return data.get("bin_in_path", False)
