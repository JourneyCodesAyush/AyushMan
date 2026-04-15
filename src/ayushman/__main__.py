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
import shutil
import sys
from pathlib import Path

from . import (
    colors,
    extract_zip,
    global_paths,
    path,
    registry,
    registry_supported,
    request_url,
    result,
    uninstall,
    validator,
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

    if not validator.validate_package(package_name):
        print(
            colors.Color.BOLD
            + colors.Color.RED
            + f"{package_name} not found in github.com/journeycodesayush"
            + colors.Color.RESET
        )
        return

    result_obj: result.InstallResult = request_url.download_zip(
        str(package_name).lower()
    )
    if not result_obj.success:
        print(
            colors.Color.RED
            + colors.Color.BOLD
            + f"Download failed: {result_obj.error_message}"
            + colors.Color.RESET
        )

    installed_version: str | None = registry.get_installed_version(
        str(package_name).lower()
    )

    if installed_version is not None and installed_version == result_obj.version:
        print(
            colors.Color.YELLOW
            + f"{package_name} is already up to date."
            + colors.Color.RESET
        )
        if Path(result_obj.zip_file_name).exists():
            os.remove(result_obj.zip_file_name)
            return

    if installed_version:
        print(
            colors.Color.YELLOW
            + f"Upgrading {package_name} from {installed_version} → {result_obj.version}"
            + colors.Color.RESET
        )
    else:
        print(
            colors.Color.YELLOW
            + f"Installing {package_name} {result_obj.version}"
            + colors.Color.RESET
        )

    result_obj = extract_zip.extract_zip_file(install_result=result_obj)

    if result_obj.success:
        print(
            colors.Color.GREEN
            + f"Installed {result_obj.package_name} {result_obj.version} to {result_obj.install_path}"
            + colors.Color.RESET
        )
        print(
            colors.Color.GREEN
            + f"Executable available as: {result_obj.package_name}.exe in ~/.ayushman/bin"
            + colors.Color.RESET
        )
        registry.add_package(result_obj)
    else:
        print(
            colors.Color.RED
            + colors.Color.BOLD
            + f"Extraction failed: {result_obj.error_message}"
            + colors.Color.RESET
        )
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
    print(
        colors.Color.GREEN
        + f"{len(package_list)} packages installed."
        + colors.Color.RESET
    )


def handle_available() -> None:
    packages = registry_supported.SUPPORTED_PACKAGES
    print(colors.Color.YELLOW + "\nAvailable packages:\n" + colors.Color.RESET)
    max_len = max(len(name) for name in packages)
    for name, data in packages.items():
        print(
            colors.Color.GREEN
            + f"  {name:<{max_len}}"
            + colors.Color.RESET
            + f"  -  {data['description']}"
        )


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
        print(
            colors.Color.GREEN
            + f"Uninstalled {result_obj_uninstall.package_name}"
            + colors.Color.RESET
        )
    else:
        print(
            colors.Color.RED
            + colors.Color.BOLD
            + f"{str(package_name).lower()} is not installed"
            + colors.Color.RESET
        )


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

    package_installed = registry.is_package_installed(package_name)
    if package_installed:
        handle_install(package_name)
    else:
        print(
            colors.Color.BOLD
            + colors.Color.RED
            + f"{package_name} does not exist."
            + colors.Color.RESET
        )


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
        print(
            colors.Color.RED
            + colors.Color.BOLD
            + f"No package named '{package_name}'"
            + colors.Color.RESET
        )
        return
    for key, value in package_info.items():
        print(colors.Color.GREEN + f"{key}:" + colors.Color.RESET + f" {value}")


def handle_purge(force: bool = False, dry_run: bool = False) -> None:
    root = global_paths.AYUSHMAN_DIR
    if not root.exists():
        print(
            colors.Color.YELLOW
            + "Ayushman is already fully removed."
            + colors.Color.RESET
        )
        return

    # DRY RUN
    if dry_run:
        print(
            colors.Color.YELLOW + "\n[DRY RUN] Purge simulation:\n" + colors.Color.RESET
        )
        print(
            colors.Color.YELLOW
            + f"Would remove PATH entry:\n  {global_paths.BIN_DIR}"
            + colors.Color.RESET
        )
        print(
            colors.Color.YELLOW
            + f"\nWould delete directory:\n  {root}"
            + colors.Color.RESET
        )
        print(colors.Color.YELLOW + "\nWould remove:" + colors.Color.RESET)
        print("  - all installed packages")
        print("  - all metadata")
        print("  - all binaries")
        print(colors.Color.GREEN + "\nNo changes were made." + colors.Color.RESET)
        return

    if not force:
        print(colors.Color.RED + colors.Color.BOLD + f"""
This will remove ALL ayushman data:

  {root}

This action CANNOT be undone.
""" + colors.Color.RESET)
        confirm = input("Type 'DELETE' to continue: ").strip()
        if confirm != "DELETE":
            print(colors.Color.YELLOW + "Aborted." + colors.Color.RESET)
            return

    try:
        path.remove_from_path()
    except Exception as e:
        print(
            colors.Color.YELLOW
            + f"Warning: failed to update PATH: {e}"
            + colors.Color.RESET
        )

    try:
        shutil.rmtree(root)
        print(
            colors.Color.GREEN + "Ayushman has been fully removed." + colors.Color.RESET
        )
    except PermissionError as e:
        print(
            colors.Color.RED
            + colors.Color.BOLD
            + f"Permission denied: {e}"
            + colors.Color.RESET
        )
    except Exception as e:
        print(
            colors.Color.RED
            + f"\nError: failed to delete some files. {e}\nYou may need to remove them manually."
            + colors.Color.RESET
        )


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

    if sys.platform != "win32":
        print("ayushman only supports Windows.")
        sys.exit(1)

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="A simple package manager called 'ayushman' to install executables from github.com/journeycodesayush repos"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    install_parser = subparsers.add_parser("install", help="Install a package")
    install_parser.add_argument("pkg", help="Package to install")

    list_parser = subparsers.add_parser("list", help="List all the installed packages")

    available_parser = subparsers.add_parser(
        "available", help="List all the available packages that can be installed"
    )

    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall a package")
    uninstall_parser.add_argument("pkg", help="Package to uninstall")

    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade a package")
    upgrade_parser.add_argument("pkg", help="Package to upgrade")

    info_parser = subparsers.add_parser("info", help="Get info of a package")
    info_parser.add_argument("pkg", help="Package to get info of")

    purge_parser = subparsers.add_parser(
        "purge",
        help="Remove all ayushman data and configuration",
    )
    purge_parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompt",
    )
    purge_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate purge without making changes",
    )

    args = parser.parse_args()

    match args.command:
        case "install":
            handle_install(args.pkg)
            if not registry.get_bin_in_path():
                path.add_to_path()
                registry.set_bin_in_path(True)
        case "list":
            handle_list()
        case "available":
            handle_available()
        case "uninstall":
            handle_uninstall(args.pkg)
        case "upgrade":
            handle_upgrade(args.pkg)
        case "info":
            handle_info(args.pkg)
        case "purge":
            handle_purge(force=args.force, dry_run=args.dry_run)
        case _:
            print("Invalid arguments")


if __name__ == "__main__":
    main()
