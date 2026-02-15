"""
Uninstallation utilities for ayushman.

This module provides functions to safely remove installed packages
and their associated binaries from the system. It handles:

    - Deletion of versioned package folders.
    - Removal of hard links in the ayushman bin directory.
    - Reporting of operation results via the UninstallResult object.

Note:
    - This module focuses only on filesystem cleanup.
    - Updates to registry or global metadata should be handled separately
      via the registry module.
"""

import os
import shutil

from . import global_paths, result


def uninstall_package(package_name: str):
    """
    Uninstall a package and remove its binaries from the system.

    Args:
        package_name (str): Name of the package to uninstall.

    Returns:
        UninstallResult: Object containing:
            - package_name: Name of the package uninstalled
            - versions: List of versions that were removed
            - removed_bins: List of executable paths deleted from the bin folder
            - removed_packages: List of package folders deleted
            - success: True if uninstallation succeeded, False otherwise
            - error_message: Error message if uninstallation failed

    Side effects:
        - Deletes all versioned folders of the package from the package directory.
        - Deletes associated hard links in the bin directory.
        - Creates no side effects outside of ayushman's directories.

    Failure modes:
        Any exception during file deletion or folder removal will set success
        to False and populate error_message.
    """

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
