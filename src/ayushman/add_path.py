import ctypes
import os
import winreg
from pathlib import Path


def get_local_app_data():
    value = os.getenv("LOCALAPPDATA")
    if not value:
        raise ValueError("LOCALAPPDATA is not set")
    return Path(value)


AYUSHMAN_DIR = get_local_app_data() / ".ayushman"
BIN_DIR = AYUSHMAN_DIR / "bin"


def get_user_path():
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ
    ) as key:
        value, _ = winreg.QueryValueEx(key, "PATH")
        return value


def set_user_path(new_path: str):
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE
    ) as key:
        winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)


def normalize(p: str) -> str:
    return os.path.normcase(os.path.normpath(p))


def add_to_path():
    bin_path = str(BIN_DIR)

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
