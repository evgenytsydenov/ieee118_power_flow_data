import datetime
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

    # Save download timestamp
    with open(os.path.join(path_folder, "timestamp.txt"), "w") as file:
        timestamp = datetime.datetime.now(tz=datetime.timezone.utc)
        file.write(timestamp.strftime("%m/%d/%Y %H:%M:%S %Z"))
