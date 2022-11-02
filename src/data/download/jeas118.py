import os
import sys

from src.data.download.utils.downloader import download_file_by_url


def download_jeas118(path_raw_data: str) -> None:
    """Download the JEAS-118 dataset.

    Args:
        path_raw_data: path to save dataset.
    """
    url_root = "http://motor.ece.iit.edu/data/"
    files = ["JEAS_IEEE118.doc"]
    os.makedirs(path_raw_data, exist_ok=True)
    for file in files:
        url = os.path.join(url_root, file)
        download_file_by_url(url, path_raw_data)


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 2:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "download_jeas118.py path_raw_data\n"
        )

    # Download
    download_jeas118(path_raw_data=sys.argv[1])
