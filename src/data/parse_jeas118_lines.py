import os
import sys
import tempfile
from typing import Optional

import pandas as pd

sys.path.append(os.getcwd())

from src.utils.converters import doc_to_docx, docx_to_pandas


def parse_jeas118_lines(
    path_raw_data: str, path_parsed_data: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Parse raw data and load necessary parameters.

    Args:
        path_raw_data: Path to raw line data from JEAS-118 dataset.
        path_parsed_data: Path to save parsed data.

    Returns:
        Preprocessed line data or None if `path_to_save` is passed and the data
          were saved.
    """
    # To parse "doc", it is necessary to convert it into "docx"
    with tempfile.TemporaryDirectory() as temp_dir:
        path_docx = os.path.join(temp_dir, "jeas_118.docx")
        doc_to_docx(path_raw_data, path_docx)

        # Convert table with lines into dataframe
        lines = docx_to_pandas(path_docx, table_num=3, header_num=1)
        lines = lines[["Line No.", "From Bus", "To Bus", "Circuit ID", "B (pu)"]]

        # Unify variable names
        lines.rename(
            columns={
                "Line No.": "name",
                "From Bus": "from_bus",
                "To Bus": "to_bus",
                "Circuit ID": "parallel",
                "B (pu)": "b_pu",
            },
            inplace=True,
        )

        # Change line and bus names
        lines["name"] = lines["name"].astype(int)
        lines.sort_values(by="name", inplace=True, ignore_index=True)
        lines["name"] = "line__" + lines["name"].astype(str)
        lines["from_bus"] = "bus__" + lines["from_bus"]
        lines["to_bus"] = "bus__" + lines["to_bus"]

        # Return results
        if path_parsed_data:
            lines.to_csv(path_parsed_data, header=True, index=False)
        else:
            return lines


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "parse_jeas118_lines.py path_raw_data path_parsed_data\n"
        )

    # Run
    path_raw_data = sys.argv[1]
    path_parsed_data = sys.argv[2]
    parse_jeas118_lines(path_raw_data, path_parsed_data)
