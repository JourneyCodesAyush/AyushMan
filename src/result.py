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
    ):
        self.package_name = package_name
        self.version = version
        self.zip_file_name = zip_file_name
        self.install_path = install_path
        self.success = success
        self.error_message = error_message
        self.metadata = metadata
        self.metadata_path = metadata_path
