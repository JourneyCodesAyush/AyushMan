"""
Download helpers for ayushman.

This module provides functions to fetch the latest release ZIP files for
packages hosted on the JourneyCodesAyush GitHub repository. It handles
network requests, error handling, and populates InstallResult objects
with metadata, file paths, and download status.

All downloads are saved to the current working directory. Any failures
are reported via the InstallResult.error_message field, and the InstallResult
object is always returned to capture success/failure and relevant data.
"""

import requests

from . import result


def download_zip(package: str) -> result.InstallResult:
    """
    Download the latest release ZIP of a package from GitHub.

    This function queries the GitHub API for the latest release of the specified
    package, finds a ZIP asset, downloads it to the current working directory,
    and returns an InstallResult containing all relevant information.

    Args:
        package (str): The name of the package to download from the JourneyCodesAyush GitHub repository.

    Returns:
        InstallResult: An object containing package information, the local ZIP file name,
        download success status, error messages (if any), and package metadata.

    Side effects:
        - Performs HTTP requests to GitHub API and asset URLs.
        - Writes the ZIP file to the current working directory if found.

    Failure modes:
        - Network issues or bad HTTP status codes.
        - No ZIP asset found in the latest release.
        - Failed to download the ZIP due to I/O or network errors.
        In these cases, `success` will be False and `error_message` populated.
    """

    url = f"https://api.github.com/repos/JourneyCodesAyush/{package}/releases/latest"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        # Network error or bad status code
        return result.InstallResult(
            package_name=package,
            version="",
            zip_file_name="",
            install_path="",
            success=False,
            error_message=str(e),
            metadata={},
            metadata_path="",
        )

    data = response.json()
    assets = data.get("assets", [])
    zip_asset = next((a for a in assets if a["name"].endswith(".zip")), None)

    if not zip_asset:
        # Zip asset not found in releases
        return result.InstallResult(
            package_name=package,
            version=data.get("tag_name", ""),
            zip_file_name="",
            install_path="",
            success=False,
            error_message="No zip asset found in latest release",
            metadata=data,
            metadata_path="",
        )

    zip_url = zip_asset.get("browser_download_url")
    local_zip_file_name = zip_asset.get("name")
    version = data.get("tag_name", "")

    # Download the zip
    try:
        with requests.get(zip_url, stream=True) as r:
            r.raise_for_status()
            with open(local_zip_file_name, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    except requests.RequestException as e:
        return result.InstallResult(
            package_name=package,
            version=version,
            zip_file_name=local_zip_file_name,
            install_path="",
            success=False,
            error_message=f"Failed to download ZIP: {e}",
            metadata=data,
            metadata_path="",
        )

    package_metadata = {
        "author": data.get("author", {}).get("login", ""),
        "license": "MIT",
        "published_at": data.get("published_at", ""),
    }

    # Success! Return a fully populated InstallResult
    return result.InstallResult(
        package_name=package,
        version=version,
        zip_file_name=local_zip_file_name,
        install_path="",  # Will be filled after extraction
        success=True,
        error_message=None,
        metadata=package_metadata,
        metadata_path="",  # Will be filled after extraction
    )


if __name__ == "__main__":
    result_obj = download_zip("PDF-Toolkit")
    if result_obj.success:
        # print(
        #     f"Downloaded {result_obj.zip_file_name} for {result_obj.package_name} v{result_obj.version}"
        # )
        print(result_obj)
    else:
        print(f"Download failed: {result_obj.error_message}")
