import os
import sys
from typing import Optional

import pandas as pd

sys.path.append(os.getcwd())

from src.utils.common_names import gen_types
from src.utils.data_loader import load_df_data


def parse_nrel118_gens(
    raw_data: str | pd.DataFrame, path_parsed_data: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Parse raw generation data from the NREL-118 dataset.

    Args:
        raw_data: Path or dataframe with raw data.
        path_parsed_data: Path to save parsed data.

    Returns:
        Parsed data or None if `path_parsed_data` is passed and the data were saved.
    """
    dtypes = {
        "Generator Name": str,
        "Node of connection": str,
        "Max Capacity (MW)": float,
    }
    gens = load_df_data(data=raw_data, dtypes=dtypes, sep=";", decimal=",")

    # Drop empty rows
    gens.dropna(how="all", inplace=True)

    # Rename variables
    gens.rename(
        columns={
            "Generator Name": "name",
            "Node of connection": "bus_name",
            "Max Capacity (MW)": "max_p__mw",
        },
        inplace=True,
    )
    gens.sort_values(by="name", inplace=True, ignore_index=True)

    # Unify generator names
    name_pattern = r"^(?P<plant_type>[\w\s]+)\s(?P<plant_number>\d+)$"
    names = gens["name"].str.extract(pat=name_pattern, expand=True)
    names["plant_type"].replace(gen_types, inplace=True)
    gens["name"] = names["plant_type"] + "_" + names["plant_number"].str.lstrip("0")
    gens["bus_name"] = "bus_" + gens["bus_name"].str.lstrip("node0")

    # Return results
    if path_parsed_data:
        gens.to_csv(path_parsed_data, header=True, index=False)
    else:
        return gens


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "parse_nrel118_gens.py path_raw_data path_parsed_data\n"
        )

    # Run
    parse_nrel118_gens(raw_data=sys.argv[1], path_parsed_data=sys.argv[2])
