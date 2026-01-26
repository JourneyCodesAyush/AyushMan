import json
import os
import zipfile
from pathlib import Path

from . import global_paths, result


def extract_zip_file(install_result: result.InstallResult):

    package_folder = (
        global_paths.PACKAGE_DIR / install_result.package_name / install_result.version
    )

    bin_folder = global_paths.BIN_DIR

    os.makedirs(package_folder, exist_ok=True)
    os.makedirs(bin_folder, exist_ok=True)

    metadata_json = package_folder / "metadata.json"
    try:
        with zipfile.ZipFile(install_result.zip_file_name, "r") as zip_ref:
            for file_info in zip_ref.infolist():
                if file_info.is_dir():
                    continue
                filename = Path(file_info.filename).name

                if not filename.lower().endswith(".exe"):
                    continue

                target_path = package_folder / filename
                hardlink_path = bin_folder / filename
                with zip_ref.open(file_info) as source, open(
                    target_path, "wb"
                ) as target:
                    target.write(source.read())

                # Delete old hard link if it exists, would be handy while implementing 'upgrade'
                if hardlink_path.exists():
                    hardlink_path.unlink()

                # Create new hard link
                os.link(src=target_path, dst=hardlink_path)

        with open(metadata_json, "w") as f:
            json.dump(install_result.metadata, f)

    except Exception as e:
        install_result.success = False
        install_result.error_message = str(e)
        return install_result

    install_result.install_path = str(package_folder)
    install_result.success = True
    install_result.error_message = None
    install_result.metadata_path = str(metadata_json)

    return install_result
