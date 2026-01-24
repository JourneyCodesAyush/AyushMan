import requests

from . import result


def download_zip(package: str) -> result.InstallResult:

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
