import datetime
import os

from src.utils.download_file import download_file_by_url

text = """# NREL-118 Dataset

The dataset contains the information about the IEEE-118 power system with
 several modifications (aka "NREL-118"), which are presented and described
 [in the paper "An Extended IEEE 118-Bus Test System With High Renewable
 Penetration"](https://ieeexplore.ieee.org/document/7904729).

## Source

The data were downloaded {timestamp} from the following URLs:

- [https://www.nrel.gov/esif/assets/docs/input-files.zip](
https://www.nrel.gov/esif/assets/docs/input-files.zip)
- [https://www.nrel.gov/esif/assets/docs/additional-files-mti-118.zip](
https://www.nrel.gov/esif/assets/docs/additional-files-mti-118.zip)
- [https://www.nrel.gov/esif/assets/docs/plexos-export.xls](
https://www.nrel.gov/esif/assets/docs/plexos-export.xls)
- [https://www.nrel.gov/esif/assets/docs/mti-118-mt-da-rt-reserves-all-generators.xml](
https://www.nrel.gov/esif/assets/docs/mti-118-mt-da-rt-reserves-all-generators.xml)

## Reference

I. Peña, C. B. Martinez-Anido and B. -M. Hodge,
 "An Extended IEEE 118-Bus Test System With High Renewable Penetration,"
 in IEEE Transactions on Power Systems, vol. 33, no. 1, pp. 281-289, Jan. 2018,
 doi: 10.1109/TPWRS.2017.2695963.
"""

if __name__ == "__main__":

    # Download files
    url_root = "https://www.nrel.gov/esif/assets/docs/"
    files = [
        "input-files.zip",
        "additional-files-mti-118.zip",
        "plexos-export.xls",
        "mti-118-mt-da-rt-reserves-all-generators.xml",
    ]
    path_folder = os.path.join("..", "data", "raw", "nrel118")
    os.makedirs(path_folder, exist_ok=True)
    for file in files:
        url = os.path.join(url_root, file)
        download_file_by_url(url, path_folder)

    # Add reference
    timestamp = datetime.datetime.now(tz=datetime.timezone.utc)
    timestamp = timestamp.strftime("%m/%d/%Y %H:%M:%S %Z")
    with open(os.path.join(path_folder, "README.md"), "w", encoding="utf-8") as file:
        file.write(text.format(timestamp=timestamp))
