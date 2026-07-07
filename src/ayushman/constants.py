"""
Project-wide configuration constants for ayushman.

This module contains configurable values that define ayushman's identity
and default filesystem naming conventions.

Forks can modify these constants to point to a different GitHub owner or
use a different local installation layout without changing the core logic.

Constants:
    GITHUB_OWNER:
        GitHub account or organization that hosts ayushman packages.

    INSTALL_DIR_NAME:
        Name of the root ayushman data directory inside LOCALAPPDATA.

    PACKAGE_DIR_NAME:
        Name of the directory containing installed package versions.

    BIN_DIR_NAME:
        Name of the directory containing active executable links.

    METADATA_FILE_NAME:
        Base name of the metadata JSON file.
"""

__all__ = [
    "GITHUB_OWNER",
    "INSTALL_DIR_NAME",
    "PACKAGE_DIR_NAME",
    "BIN_DIR_NAME",
    "METADATA_FILE_NAME",
]

GITHUB_OWNER: str = "JourneyCodesAyush"

INSTALL_DIR_NAME: str = "ayushman"
PACKAGE_DIR_NAME: str = "packages"
BIN_DIR_NAME: str = "bin"
METADATA_FILE_NAME: str = "metadata"
