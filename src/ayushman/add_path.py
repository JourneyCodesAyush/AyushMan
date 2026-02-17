"""
Windows PATH management for ayushman.

This module provides utilities to manage the user's PATH environment
variable on Windows. It ensures that the ayushman bin directory is
added to the user PATH in a safe, idempotent manner and notifies the
system of the change so that new terminals pick up the updated PATH.

All modifications are limited to the current user's environment and
do not require administrator privileges.
"""

import ctypes
import os
import winreg

from . import global_paths


def get_user_path():
    """
    Get the current user's PATH environment variable from the Windows registry.

    Returns:
        str: The user's PATH value.
    """
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ
    ) as key:
        value, _ = winreg.QueryValueEx(key, "PATH")
        return value


def set_user_path(new_path: str):
    """
    Set the user's PATH environment variable in the Windows registry.

    Args:
        new_path (str): The new PATH value to set.
    """

    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE
    ) as key:
        winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)


def normalize(p: str) -> str:
    """
    Normalize a filesystem path for consistent comparison.

    Args:
        p (str): Path string to normalize.

    Returns:
        str: Normalized path (case-insensitive and standardized separators).
    """

    return os.path.normcase(os.path.normpath(p))


def add_to_path():
    """
    Add ayushman's bin directory to the user's PATH if it is not already present.

    Side effects:
        - Updates the Windows registry for the current user's PATH.
        - Broadcasts a system message to notify open applications of the change.
        - Prints messages indicating whether the path was added or already present.

    Behavior:
        - Checks the current PATH and avoids adding duplicates.
        - Uses ctypes to send WM_SETTINGCHANGE after updating the registry.
    """

    bin_path = str(global_paths.BIN_DIR)

    path_value = get_user_path()
    paths = path_value.split(";")

    normalized = [normalize(p) for p in paths]

    if normalize(bin_path) in normalized:
        print("BIN already in PATH")
        return

    paths.append(bin_path)
    new_path = ";".join(paths)

    set_user_path(new_path)
    print("Added BIN to PATH (open a new terminal)")

    # After updating PATH in registry
    HWND_BROADCAST = 0xFFFF
    WM_SETTINGCHANGE = 0x1A
    SMTO_ABORTIFHUNG = 0x0002

    ctypes.windll.user32.SendMessageTimeoutW(
        HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", SMTO_ABORTIFHUNG, 5000, None
    )
