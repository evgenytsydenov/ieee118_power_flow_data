import datetime
import logging
import os

from src.utils.converters import doc_to_docx
from src.utils.download_file import download_file_by_url

logger = logging.getLogger(__name__)

text = """# JEAS-118 Dataset

The dataset contains the information about the IEEE-118 test system
 prepared by Illinois Institute of Technology (version of 2004).

## Source

The data were downloaded {timestamp} from the following URLs:

- [http://motor.ece.iit.edu/data/JEAS_IEEE118.doc](
http://motor.ece.iit.edu/data/JEAS_IEEE118.doc)

## Reference

IIT, “Index of data Illinois Institute of Technology,”
 Illinois Inst. Technol., Chicago, IL, USA, [Online].
 Available: http://motor.ece.iit.edu/data/
"""

if __name__ == "__main__":

    # Download files
    url_root = "http://motor.ece.iit.edu/data/"
    file = "JEAS_IEEE118.doc"
    path_folder = os.path.join("..", "data", "raw", "jeas118")
    os.makedirs(path_folder, exist_ok=True)
    url = os.path.join(url_root, file)
    download_file_by_url(url, path_folder)

    # Add reference
    timestamp = datetime.datetime.now(tz=datetime.timezone.utc)
    timestamp = timestamp.strftime("%m/%d/%Y %H:%M:%S %Z")
    with open(os.path.join(path_folder, "README.md"), "w", encoding="utf-8") as file:
        file.write(text.format(timestamp=timestamp))

    # Convert doc to docx
    path_doc = os.path.join(path_folder, "JEAS_IEEE118.doc")
    path_docx = os.path.join(path_folder, "JEAS_IEEE118.docx")
    try:
        doc_to_docx(path_doc=path_doc, path_docx=path_docx)
    except RuntimeError:
        logger.warning(
            "Conversion from doc to docx failed. "
            f'Please convert file "{path_doc}" into "{path_docx}" manually.'
        )
