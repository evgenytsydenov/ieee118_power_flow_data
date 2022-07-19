import datetime
import os
import shutil

import requests


def download_file(url: str, path: str, unzip: bool = True) -> None:
    """Download file by URL.

    Args:
        url: Link to the file.
        path: Path to folder where the file should be saved.
        unzip: Unzip file if it is an archive.
    """
    file_name = os.path.split(url)[1]
    file_path = os.path.join(path, file_name)
    with open(file_path, "wb") as out_file:
        content = requests.get(url, stream=True).content
        out_file.write(content)
    if unzip:
        try:
            shutil.unpack_archive(file_path, extract_dir=path)
            os.remove(file_path)
        except shutil.ReadError:
            pass


if __name__ == "__main__":
    url_root = "https://www.nrel.gov/esif/assets/docs/"
    files = [
        "input-files.zip",
        "additional-files-mti-118.zip",
        "plexos-export.xls",
        "mti-118-mt-da-rt-da-rt-reserves-all-generators.xml",
    ]
    path_folder = os.path.join("..", "data", "raw", "nrel118")
    os.makedirs(path_folder, exist_ok=True)
    for file in files:
        url = os.path.join(url_root, file)
        download_file(url, path_folder)

    # Save download timestamp
    with open(os.path.join(path_folder, "timestamp.txt"), "w") as file:
        timestamp = datetime.datetime.now(tz=datetime.timezone.utc)
        file.write(timestamp.strftime("%m/%d/%Y %H:%M:%S %Z"))
