import os
import shutil

from . import global_paths, result


def uninstall_package(package_name: str):
    package_folder = global_paths.PACKAGE_DIR / package_name
    bin_folder = global_paths.BIN_DIR

    if not package_folder.exists():
        return result.UninstallResult(
            package_name=package_name,
            versions=[],
            removed_bins=[],
            removed_packages=[],
            success=False,
            error_message=f"{package_name} does not exist",
        )

    versions_installed = [d.name for d in package_folder.iterdir() if d.is_dir()]
    removed_bins = []
    removed_packages = []

    try:
        # Remove hardlinks
        for version_folder in package_folder.iterdir():
            if not version_folder.is_dir():
                continue
            for exe_file in version_folder.glob("*.exe"):
                bin_link = bin_folder / exe_file.name
                if bin_link.exists():
                    os.unlink(bin_link)
                    removed_bins.append(str(bin_link))

        # Remove entire package folder
        shutil.rmtree(package_folder)
        removed_packages.append(str(package_folder))

        return result.UninstallResult(
            package_name=package_name,
            versions=versions_installed,
            removed_bins=removed_bins,
            removed_packages=removed_packages,
            success=True,
            error_message="",
        )

    except Exception as e:
        return result.UninstallResult(
            package_name=package_name,
            versions=versions_installed,
            removed_bins=removed_bins,
            removed_packages=removed_packages,
            success=False,
            error_message=str(e),
        )
