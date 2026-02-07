class InstallResult:
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
    ) -> None:
        self.package_name = package_name
        self.version = version
        self.zip_file_name = zip_file_name
        self.install_path = install_path
        self.success = success
        self.error_message = error_message
        self.metadata = metadata
        self.metadata_path = metadata_path


class UninstallResult:
    def __init__(
        self,
        package_name: str,
        versions: list[str],
        success: bool,
        removed_bins: list[str] = [],
        removed_packages: list[str] = [],
        error_message: str = "",
    ):
        self.package_name = package_name
        self.versions = versions
        self.success = success
        self.removed_bins = removed_bins or []
        self.removed_packages = removed_packages or []
        self.error_message = error_message
