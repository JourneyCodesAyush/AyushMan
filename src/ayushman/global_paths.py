"""
Centralized filesystem paths for ayushman.

This module defines the root installation directory inside LOCALAPPDATA and
provides derived paths for packages, binaries, and global metadata.

It serves as a single source of truth for all filesystem locations used by
ayushman, ensuring predictable, upgrade-safe installations and avoiding
repeated path computations across modules.
"""

import os
from pathlib import Path


def _get_local_app_data() -> Path:
    """
    Retrieve the LOCALAPPDATA directory as a Path object.

    Returns:
        Path: The path to the user's LOCALAPPDATA directory.

    Raises:
        ValueError: If the LOCALAPPDATA environment variable is not set.

    This function ensures that callers either receive a valid Path object
    pointing to LOCALAPPDATA or fail fast with a clear exception, avoiding
    undefined behavior elsewhere in ayushman.
    """

    value = os.getenv("LOCALAPPDATA")
    if not value:
        raise ValueError("LOCALAPPDATA is not set")
    return Path(value)


# Root directory for all ayushman data inside LOCALAPPDATA
AYUSHMAN_DIR = _get_local_app_data() / ".ayushman"

# Directory where all packages are installed
PACKAGE_DIR = AYUSHMAN_DIR / "packages"

# Directory where hardlinked executables are placed
BIN_DIR = AYUSHMAN_DIR / "bin"

# Path to the global metadata JSON file
GLOBAL_METADATA = AYUSHMAN_DIR / "metadata.json"
