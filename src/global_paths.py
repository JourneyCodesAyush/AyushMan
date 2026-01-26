import os

from pathlib import Path


def _get_local_app_data():
    value = os.getenv("LOCALAPPDATA")
    if not value:
        raise ValueError("LOCALAPPDATA is not set")
    return Path(value)


AYUMAN_DIR = _get_local_app_data() / ".ayuman"

PACKAGE_DIR = AYUMAN_DIR / "packages"
BIN_DIR = AYUMAN_DIR / "bin"
GLOBAL_METADATA = AYUMAN_DIR / "metadata.json"
