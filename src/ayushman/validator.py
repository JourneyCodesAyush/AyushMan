"""
Package validation for ayushman.

This module provides utilities to verify whether a given package
is officially supported by ayushman. It ensures that only recognized
packages from the trusted repository (github.com/journeycodesayush)
can be installed, maintaining predictable and safe package management.

Currently supported packages:
    - cpp-cloc
    - c-utils
    - pdf-toolkit

This list may be extended as new packages are added.
"""

import ayushman.registry_supported as registry_supported

__all__ = ["validate_package"]


def validate_package(package: str) -> bool:
    """
    Check whether a given package is supported by ayushman.

    Args:
        package (str): The name of the package to validate.

    Returns:
        bool: True if the package is supported, False otherwise.

    Notes:
        Currently, the supported packages are:
        ["cpp-cloc", "c-utils", "pdf-toolkit"].
        This list may be extended in the future as new packages are added.
    """

    # PACKAGES: list[str] = ["cpp-cloc", "c-utils", "pdf-toolkit"]
    if package in registry_supported.SUPPORTED_PACKAGES:
        return True
    return False
