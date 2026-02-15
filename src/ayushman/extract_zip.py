"""
ZIP extraction utilities for ayushman.

This module provides functionality to extract .exe files from a downloaded
package ZIP and place them in versioned package directories. It also creates
hard links in the ayushman bin directory to enable upgrade-safe installations
without duplicating binaries.

The module updates per-package metadata and the InstallResult object to
reflect installation success, paths, and any errors.

Key behaviors:
    - Extracts only .exe files from a ZIP archive.
    - Creates versioned package directories and a global bin directory if needed.
    - Writes per-package metadata to metadata.json.
    - Creates or updates hard links in the bin directory.
    - Updates the InstallResult object with installation status and paths.
"""

import json
import os
import zipfile
from pathlib import Path

from . import global_paths, result


def extract_zip_file(install_result: result.InstallResult):
    """
    Extract .exe files from a package ZIP and set up upgrade-safe binaries.

    Args:
        install_result (InstallResult): The result object from downloading
            a package. Must include zip_file_name and metadata.

    Returns:
        InstallResult: The same object, updated with:
            - install_path: Path to the versioned package folder
            - metadata_path: Path to the saved per-package metadata JSON
            - success: True if extraction succeeded, False otherwise
            - error_message: Error message if extraction failed, None otherwise

    Side effects:
        - Creates package and bin directories if they don't exist.
        - Extracts only .exe files from the ZIP.
        - Writes a per-package metadata.json.
        - Creates hard links in the bin folder, replacing old links if necessary.

    Failure modes:
        Any exception during extraction, file writing, or link creation
        will set success to False and populate error_message.
    """

    package_folder = (
        global_paths.PACKAGE_DIR / install_result.package_name / install_result.version
    )

    bin_folder = global_paths.BIN_DIR

    os.makedirs(package_folder, exist_ok=True)
    os.makedirs(bin_folder, exist_ok=True)

    metadata_json = package_folder / "metadata.json"
    try:
        with zipfile.ZipFile(install_result.zip_file_name, "r") as zip_ref:
            for file_info in zip_ref.infolist():
                if file_info.is_dir():
                    continue
                filename = Path(file_info.filename).name

                if not filename.lower().endswith(".exe"):
                    continue

                target_path = package_folder / filename
                hardlink_path = bin_folder / filename
                with (
                    zip_ref.open(file_info) as source,
                    open(target_path, "wb") as target,
                ):
                    target.write(source.read())

                # Delete old hard link if it exists, would be handy while implementing 'upgrade'
                if hardlink_path.exists():
                    hardlink_path.unlink()

                # Create new hard link
                os.link(src=target_path, dst=hardlink_path)

        with open(metadata_json, "w") as f:
            json.dump(install_result.metadata, f)

    except Exception as e:
        install_result.success = False
        install_result.error_message = str(e)
        return install_result

    install_result.install_path = str(package_folder)
    install_result.success = True
    install_result.error_message = None
    install_result.metadata_path = str(metadata_json)

    return install_result
