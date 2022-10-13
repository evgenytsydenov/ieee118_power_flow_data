import os
import sys
import tempfile
from typing import Optional

import pandas as pd

from src.utils.converters import doc_to_docx, docx_to_pandas


def parse_jeas118_lines(
    raw_data: str | pd.DataFrame, path_parsed_data: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Parse raw line data from the JEAS-118 dataset.

    Args:
        raw_data: Path or dataframe with raw data.
        path_parsed_data: Path to save parsed data.

    Returns:
        Parsed data or None if `path_parsed_data` is passed and the data were saved.
    """
    dtypes = {
        "Line No.": int,
        "From Bus": str,
        "To Bus": str,
        "Circuit ID": int,
        "B (pu)": float,
    }
    cols = dtypes.keys()
    if isinstance(raw_data, str):
        # To parse "doc", it is necessary to convert it into "docx"
        with tempfile.TemporaryDirectory() as temp_dir:
            path_docx = os.path.join(temp_dir, "jeas_118.docx")
            doc_to_docx(path_doc=raw_data, path_docx=path_docx)

            # Convert table into dataframe
            lines = docx_to_pandas(path_docx=path_docx, table_num=3, header_num=1)
            lines = lines[cols].astype(dtypes)
    else:
        lines = raw_data[cols].astype(dtypes)

    # Rename variables
    lines.rename(
        columns={
            "Line No.": "branch_name",
            "From Bus": "from_bus",
            "To Bus": "to_bus",
            "Circuit ID": "parallel",
            "B (pu)": "b_pu",
        },
        inplace=True,
    )

    # Change line and bus names
    lines.sort_values(by="branch_name", inplace=True, ignore_index=True)
    lines["branch_name"] = "branch_" + lines["branch_name"].astype(str)
    lines["from_bus"] = "bus_" + lines["from_bus"]
    lines["to_bus"] = "bus_" + lines["to_bus"]

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
            "parse_jeas118_lines.py path_raw_jeas118 path_parsed_data\n"
        )

    # Run
    parse_jeas118_lines(raw_data=sys.argv[1], path_parsed_data=sys.argv[2])
