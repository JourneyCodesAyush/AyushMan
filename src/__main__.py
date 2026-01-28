import argparse
import os
from pathlib import Path

from . import extract_zip, registry, request_url, result, uninstall, validation


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

    args = parser.parse_args()

    match args.command:
        case "install":
            if validation.validate(args.pkg):
                result_obj: result.InstallResult = request_url.download_zip(
                    str(args.pkg).lower()
                )
                if not result_obj.success:
                    print(f"Download failed: {result_obj.error_message}")

                installed_version: str = registry.get_installed_version(
                    str(args.pkg).lower()
                )

                if installed_version == result_obj.version:
                    print(f"{args.pkg} is already up to date.")

                    if Path(result_obj.zip_file_name).exists():
                        os.remove(result_obj.zip_file_name)
                    return

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
        case "list":
            package_list: list[str] = registry.list_package()
            for pkg in package_list:
                print(pkg)
            print(f"{len(package_list)} packages installed.")
        case "uninstall":
            result_obj_uninstall: result.UninstallResult = uninstall.uninstall_package(
                str(args.pkg).lower()
            )
            removed: bool = registry.remove_package(
                result_obj_uninstall.package_name
            )
            if removed:
                print(f"Uninstalled {result_obj_uninstall.package_name}")
            else:
                print(f"{str(args.pkg).lower()} is not installed")
        case _:
            print("Invalid arguments")


if __name__ == "__main__":
    main()
