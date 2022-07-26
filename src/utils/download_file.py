import os
import shutil

import requests


def download_file_by_url(url: str, path: str, unzip: bool = True) -> None:
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
