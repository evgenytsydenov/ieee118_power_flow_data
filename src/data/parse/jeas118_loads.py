import os
import sys
import tempfile
from typing import Optional

import pandas as pd

from src.utils.converters import doc_to_docx, docx_to_pandas


def parse_jeas118_loads(
    raw_data: str | pd.DataFrame, path_parsed_data: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Parse raw load data from the JEAS-118 dataset.

    Args:
        raw_data: Path or dataframe with raw data.
        path_parsed_data: Path to save parsed data.

    Returns:
        Parsed data or None if `path_parsed_data` is passed and the data were saved.
    """
    dtypes = {"Bus No": str, "Pd\n   (MW)": float, "  Qd\n   (MVAR)": float}
    cols = dtypes.keys()
    if isinstance(raw_data, str):
        # To parse "doc", it is necessary to convert it into "docx"
        with tempfile.TemporaryDirectory() as temp_dir:
            path_docx = os.path.join(temp_dir, "jeas_118.docx")
            doc_to_docx(path_doc=raw_data, path_docx=path_docx)

            # Convert table into dataframe
            loads = docx_to_pandas(path_docx=path_docx, table_num=6, header_num=1)
            loads = loads[cols].astype(dtypes)
    else:
        loads = raw_data[cols].astype(dtypes)

    # Rename variables
    loads.rename(
        columns={
            "Bus No": "bus_name",
            "Pd\n   (MW)": "p_mw",
            "  Qd\n   (MVAR)": "q_mvar",
        },
        inplace=True,
    )

    # Change bus names
    loads["bus_name"] = "bus_" + loads["bus_name"].str.zfill(3)

    # Return results
    loads.sort_values(by="bus_name", inplace=True, ignore_index=True)
    if path_parsed_data:
        loads.to_csv(path_parsed_data, header=True, index=False)
    else:
        return loads


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "parse_jeas118_loads.py path_raw_jeas118 path_parsed_data\n"
        )

    # Run
    parse_jeas118_loads(raw_data=sys.argv[1], path_parsed_data=sys.argv[2])
