"""
Result objects for ayushman.

This module defines data structures that represent the outcomes of
package management operations in ayushman, specifically installations
and uninstallations.

Classes:
    - InstallResult: Captures the result of installing a package, including
      success status, downloaded ZIP, installation paths, and metadata.
    - UninstallResult: Captures the result of uninstalling a package,
      including removed versions, deleted binaries, directories, and any errors.

These classes are used to consistently communicate operation results across
the CLI and internal modules.
"""

__all__ = ["InstallResult", "UninstallResult"]


class InstallResult:
    """
    Represents the result of installing a package via ayushman.

    Attributes:
        package_name (str): Name of the installed package.
        version (str): Installed version.
        zip_file_name (str): Name of the downloaded ZIP file.
        install_path (str): Path where the package was extracted.
        success (bool): Whether the installation succeeded.
        error_message (str | None): Error message if installation failed.
        metadata (dict): Per-package metadata (author, license, etc.).
        local_sha256 (str): Locally calculated sha256 of the downloaded zip file.
        remote_sha256 (str | None): sha256 as received in response from Github.
        hash_verified (bool): Whether sha256 calculated locally and received from Github match or not.
        metadata_path (str): Path to the per-package metadata JSON file.
    """

    def __init__(
        self,
        package_name: str,
        version: str,
        zip_file_name: str,
        install_path: str,
        success: bool,
        error_message: str | None,
        metadata: dict,
        metadata_path: str,
        local_sha256: str = "",
        remote_sha256: str | None = None,
        hash_verified: bool = False,
    ) -> None:
        self.package_name = package_name
        self.version = version
        self.zip_file_name = zip_file_name
        self.local_sha256 = local_sha256 or None
        self.remote_sha256 = remote_sha256 or None
        self.hash_verified = hash_verified or False
        self.install_path = install_path
        self.success = success
        self.error_message = error_message
        self.metadata = metadata
        self.metadata_path = metadata_path


class UninstallResult:
    """
    Represents the result of uninstalling a package via ayushman.

    Attributes:
        package_name (str): Name of the uninstalled package.
        versions (list[str]): Versions that were removed.
        success (bool): Whether the uninstallation succeeded.
        removed_bins (list[str]): List of executable paths that were deleted.
        removed_packages (list[str]): List of package directories that were deleted.
        error_message (str): Error message if uninstallation failed.
    """

    def __init__(
        self,
        package_name: str,
        versions: list[str],
        success: bool,
        removed_bins: list[str] | None = None,
        removed_packages: list[str] | None = None,
        error_message: str = "",
    ):
        self.package_name = package_name
        self.versions = versions
        self.success = success
        self.removed_bins = removed_bins or []
        self.removed_packages = removed_packages or []
        self.error_message = error_message
