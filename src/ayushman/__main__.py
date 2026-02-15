"""
Command-line interface for ayushman.

This module implements the CLI for ayushman, a minimal Windows-only
package manager that installs prebuilt executables from
github.com/journeycodesayush repositories.

Available commands:
    - install <pkg>: Downloads and installs a package
    - list: Lists all installed packages
    - uninstall <pkg>: Uninstalls a package
    - upgrade <pkg>: Upgrades a package to the latest version
    - info <pkg>: Shows metadata for a package

Each command delegates functionality to appropriate modules, ensuring
installations are upgrade-safe, paths are updated, and metadata is tracked.
"""

import argparse
import os
from pathlib import Path

from . import (
    add_path,
    extract_zip,
    registry,
    request_url,
    result,
    uninstall,
    validation,
)


def handle_install(package_name: str) -> None:
    """
    Install or upgrade a package.

    Args:
        package_name (str): Name of the package to install or upgrade.

    Behavior:
        - Validates the package exists in the trusted repository.
        - Downloads the latest release ZIP.
        - Skips installation if the latest version is already installed.
        - Extracts `.exe` files to versioned package folder and creates hard links.
        - Updates global metadata.
        - Cleans up the downloaded ZIP file.

    Raises:
        None
    """

    if not validation.validate(package_name):
        print(f"{package_name} not found in github.com/journeycodesayush")
        return

    result_obj: result.InstallResult = request_url.download_zip(
        str(package_name).lower()
    )
    if not result_obj.success:
        print(f"Download failed: {result_obj.error_message}")

    installed_version: str = registry.get_installed_version(str(package_name).lower())

    if installed_version == result_obj.version:
        print(f"{package_name} is already up to date.")
        if Path(result_obj.zip_file_name).exists():
            os.remove(result_obj.zip_file_name)
            return

    if installed_version:
        print(
            f"Upgrading {package_name} from {installed_version} → {result_obj.version}"
        )
    else:
        print(f"Installing {package_name} {result_obj.version}")

    result_obj = extract_zip.extract_zip_file(install_result=result_obj)

    if result_obj.success:
        print(
            f"Installed {result_obj.package_name} {result_obj.version} to {result_obj.install_path}"
        )
        registry.add_package(result_obj)
    else:
        print(f"Extraction failed: {result_obj.error_message}")
    if Path(result_obj.zip_file_name).exists():
        os.remove(result_obj.zip_file_name)


def handle_list() -> None:
    """
    List all installed packages.

    Prints each installed package in 'name version' format and
    the total count of installed packages.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """

    package_list: list[str] = registry.list_package()
    for pkg in package_list:
        print(pkg)
    print(f"{len(package_list)} packages installed.")


def handle_uninstall(package_name: str) -> None:
    """
    Uninstall a package.

    Args:
        package_name (str): Name of the package to uninstall.

    Behavior:
        - Removes the package's binaries and folders using uninstall module.
        - Updates global metadata.
        - Prints success or failure messages.
    """

    result_obj_uninstall: result.UninstallResult = uninstall.uninstall_package(
        str(package_name).lower()
    )
    removed: bool = registry.remove_package(result_obj_uninstall.package_name)
    if removed:
        print(f"Uninstalled {result_obj_uninstall.package_name}")
    else:
        print(f"{str(package_name).lower()} is not installed")


def handle_upgrade(package_name: str) -> None:
    """
    Upgrade a package to the latest version.

    Args:
        package_name (str): Name of the package to upgrade.

    Behavior:
        - Checks if the package is installed.
        - Calls handle_install to download and install the latest version.
        - Prints a message if the package does not exist.

    Returns:
        None

    Raises:
        None
    """

    package_installed = registry.get_package(package_name)
    if package_installed:
        handle_install(package_name)
    else:
        print(f"{package_name} does not exist.")


def handle_info(package_name: str) -> None:
    """
    Display metadata for a specific package.

    Args:
        package_name (str): Name of the package.

    Behavior:
        - Retrieves metadata from global registry.
        - Prints key-value pairs.
        - Prints a message if the package does not exist.

    Returns:
        None

    Raises:
        None
    """

    package_info = registry.get_package_metadata(package_name)
    # print(package_info)
    if not package_info:
        print(f"No package named '{package_name}'")
        return
    for key, value in package_info.items():
        print(f"{key}: {value}")


def main():
    """
    Entry point for the ayushman CLI.

    Behavior:
        - Parses command-line arguments using argparse.
        - Dispatches to corresponding handle_* functions.
        - Adds ayushman bin directory to PATH on first install.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="A simple package manager called 'ayushman' to install executables from github.com/journeycodesayush repos"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    install_parser = subparsers.add_parser("install", help="Install a package")
    install_parser.add_argument("pkg", help="Package to install")

    list_parser = subparsers.add_parser("list", help="List all the installed packages")

    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall a package")
    uninstall_parser.add_argument("pkg", help="Package to uninstall")

    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade a package")
    upgrade_parser.add_argument("pkg", help="Package to upgrade")

    info_parser = subparsers.add_parser("info", help="Get info of a package")
    info_parser.add_argument("pkg", help="Package to get info of")

    args = parser.parse_args()

    match args.command:
        case "install":
            handle_install(args.pkg)
            if not registry.get_bin_in_path():
                add_path.add_to_path()
                registry.set_bin_in_path(True)
        case "list":
            handle_list()
        case "uninstall":
            handle_uninstall(args.pkg)
        case "upgrade":
            handle_upgrade(args.pkg)
        case "info":
            handle_info(args.pkg)
        case _:
            print("Invalid arguments")


if __name__ == "__main__":
    main()
