"""
Registry management for ayushman.

This module manages the global metadata file that tracks installed packages
and system state. It provides functions to read, write, and update metadata,
query installed packages, and track whether the ayushman bin directory has
been added to the user PATH.

All modifications to installed packages should go through this module to
ensure consistency, maintain upgrade-safe installations, and keep metadata
in sync with the filesystem.
"""

import json

from . import global_paths, result

REGISTRY_PATH = global_paths.GLOBAL_METADATA


def _ensure_metadata_file() -> None:
    """
    Ensure that the global metadata file exists.

    Creates the parent directories if necessary and initializes the metadata
    file with an empty installed_packages list if it does not exist.
    """

    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not REGISTRY_PATH.exists():
        REGISTRY_PATH.write_text(json.dumps({"installed_packages": []}, indent=4))


def _read_metadata() -> dict:
    """
    Read and return the global metadata as a dictionary.

    Returns:
        dict: The contents of the global metadata file.

    Side effects:
        Ensures that the metadata file exists before reading.
    """

    _ensure_metadata_file()
    with open(REGISTRY_PATH, "r") as f:
        return json.load(f)


def _write_metadata(data: dict) -> None:
    """
    Write the given metadata dictionary to the global metadata file.

    Args:
        data (dict): The metadata to write.

    Side effects:
        Creates the metadata file and parent directories if they do not exist.
    """

    _ensure_metadata_file()
    with open(REGISTRY_PATH, "w") as f:
        json.dump(data, f, indent=4)


def add_package(install_result: result.InstallResult):
    """
    Add or update a package entry in the global metadata.

    Args:
        install_result (InstallResult): The result of a package installation.

    Behavior:
        Removes any existing entry for the same package/version before adding
        the new one, ensuring that the metadata reflects only the latest state.
    """

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
    """
    Return a list of installed packages in "name version" format.

    Returns:
        list[str]: List of installed packages with their versions.
    """

    data = _read_metadata()

    package_list: list[str] = []
    for pkg in data["installed_packages"]:
        package_list.append(f"{pkg['name']} {pkg['version']}")

    return package_list


def get_installed_version(package_name: str) -> str:
    """
    Get the currently installed version of a package.

    Args:
        package_name (str): Name of the package.

    Returns:
        str: Installed version if the package exists, otherwise an empty string.
    """

    data: dict = _read_metadata()
    for pkg in data["installed_packages"]:
        if pkg["name"] == package_name:
            return pkg["version"]
    return ""


def get_package(package_name: str) -> bool:
    """
    Check whether a package is installed.

    Args:
        package_name (str): Name of the package.

    Returns:
        bool: True if installed, False otherwise.
    """

    data: dict = _read_metadata()
    for pkg in data["installed_packages"]:
        if pkg["name"] == package_name:
            return True
    return False


def get_package_metadata(package_name: str) -> dict:
    """
    Retrieve the metadata dictionary for a specific package.

    Args:
        package_name (str): Name of the package.

    Returns:
        dict: Package metadata if found, otherwise an empty dict.
    """
    data: dict = _read_metadata()
    for pkg in data["installed_packages"]:
        if pkg["name"] == package_name:
            return pkg
    return {}


def remove_package(package_name: str) -> bool:
    """
    Remove a package entry from the global metadata.

    Args:
        package_name (str): Name of the package to remove.

    Returns:
        bool: True if a package was removed, False if it was not found.

    Behavior:
        Only removes the package entry from metadata; does not touch the filesystem.
    """

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
    """
    Set the flag indicating whether the ayushman bin directory is in the user PATH.

    Args:
        value (bool): True if the bin directory has been added to PATH, False otherwise.
    """

    data: dict = _read_metadata()
    data["bin_in_path"] = value
    _write_metadata(data)


def get_bin_in_path() -> bool:
    """
    Check whether the ayushman bin directory is in the user PATH.

    Returns:
        bool: True if the bin directory has been added to PATH, False otherwise.
    """

    data: dict = _read_metadata()
    return data.get("bin_in_path", False)
