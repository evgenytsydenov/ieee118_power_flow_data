import os

from src.utils.download_file import download_file_by_url

if __name__ == "__main__":
    url_root = "http://motor.ece.iit.edu/data/"
    files = ["JEAS_IEEE118.doc"]
    path_folder = os.path.join("..", "data", "raw", "jeas118")
    os.makedirs(path_folder, exist_ok=True)
    for file in files:
        url = os.path.join(url_root, file)
        download_file_by_url(url, path_folder)
