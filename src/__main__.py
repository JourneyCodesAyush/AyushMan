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
    if validation.validate(package_name):
        result_obj: result.InstallResult = request_url.download_zip(
            str(package_name).lower()
        )
        if not result_obj.success:
            print(f"Download failed: {result_obj.error_message}")

        installed_version: str = registry.get_installed_version(
            str(package_name).lower()
        )

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
    package_list: list[str] = registry.list_package()
    for pkg in package_list:
        print(pkg)
    print(f"{len(package_list)} packages installed.")


def handle_uninstall(package_name: str) -> None:
    result_obj_uninstall: result.UninstallResult = uninstall.uninstall_package(
        str(package_name).lower()
    )
    removed: bool = registry.remove_package(result_obj_uninstall.package_name)
    if removed:
        print(f"Uninstalled {result_obj_uninstall.package_name}")
    else:
        print(f"{str(package_name).lower()} is not installed")


def handle_upgrade(package_name: str) -> None:
    package_installed = registry.get_package(package_name)
    if package_installed:
        handle_install(package_name)
    else:
        print(f"{package_name} does not exist.")


def main():
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="A simple package manager called 'ayuman' to install executables from github.com/journeycodesayush repos"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    install_parser = subparsers.add_parser("install", help="Install a package")
    install_parser.add_argument("pkg", help="Package to install")

    list_parser = subparsers.add_parser("list", help="List all the installed packages")

    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall a package")
    uninstall_parser.add_argument("pkg", help="Package to uninstall")

    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade a package")
    upgrade_parser.add_argument("pkg", help="Package to upgrade")

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
        case _:
            print("Invalid arguments")


if __name__ == "__main__":
    main()
