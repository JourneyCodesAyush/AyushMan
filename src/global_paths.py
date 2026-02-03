import os
from pathlib import Path


def _get_local_app_data():
    value = os.getenv("LOCALAPPDATA")
    if not value:
        raise ValueError("LOCALAPPDATA is not set")
    return Path(value)


AYUSHMAN_DIR = _get_local_app_data() / ".ayushman"

PACKAGE_DIR = AYUSHMAN_DIR / "packages"
BIN_DIR = AYUSHMAN_DIR / "bin"
GLOBAL_METADATA = AYUSHMAN_DIR / "metadata.json"
