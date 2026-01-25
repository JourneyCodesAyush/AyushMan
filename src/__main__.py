import argparse

from . import extract_zip, registry, request_url, result, validation


def main():
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="A simple package manager called 'ayuman' to install executables from github.com/journeycodesayush repos"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    install_parser = subparsers.add_parser("install", help="Install a package")
    install_parser.add_argument("pkg", help="Package to install")

    args = parser.parse_args()

    match args.command:
        case "install":
            if validation.validate(args.pkg):
                result_obj: result.InstallResult = request_url.download_zip(
                    str(args.pkg).lower()
                )
                if not result_obj.success:
                    print(f"Download failed: {result_obj.error_message}")

                result_obj = extract_zip.extract_zip_file(install_result=result_obj)
                if result_obj.success:
                    print(
                        f"Installed {result_obj.package_name} {result_obj.version} to {result_obj.install_path}"
                    )
                    registry.add_package(result_obj)
                else:
                    print(f"Extraction failed: {result_obj.error_message}")

        case _:
            print("Invalid arguments")


if __name__ == "__main__":
    main()
