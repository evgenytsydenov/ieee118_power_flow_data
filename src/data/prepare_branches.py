import sys
from typing import Optional

import pandas as pd

# Base power
S_BASE__MVA = 100


def load_data(data: str | pd.DataFrame, dtypes: dict) -> pd.DataFrame:
    """Auxiliary function to load data.

    Args:
        dtypes: Path for each column/
        data: Path or dataframe with data.

    Returns:
        Loaded data as a dataframe.
    """
    cols = dtypes.keys()
    if isinstance(data, str):
        return pd.read_csv(data, header=0, usecols=cols, dtype=dtypes)
    else:
        return data[cols].astype(dtypes)


def prepare_branches(
    parsed_nrel118_lines: str | pd.DataFrame,
    parsed_jeas118_lines: str | pd.DataFrame,
    parsed_jeas118_trafos: str | pd.DataFrame,
    prepared_buses: str | pd.DataFrame,
    path_prepared_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Prepare final branch data.

    Args:
        prepared_buses: Path or dataframe to prepared bus data.
        parsed_nrel118_lines: Path or dataframe with line data from NREL-118 dataset.
        parsed_jeas118_lines: Path or dataframe with line data from JEAS-118 dataset.
        parsed_jeas118_trafos: Path or dataframe with trafo data from JEAS-118 dataset.
        path_prepared_data: Path to save prepared data.

    Returns:
        Prepared data or None if `path_prepared_data` is passed and the data were saved.
    """
    # Load data
    nrel118_lines = load_data(
        parsed_nrel118_lines,
        {
            "name": str,
            "from_bus": str,
            "to_bus": str,
            "max_p__mw": float,
            "x__pu": float,
            "r__pu": float,
        },
    )
    jeas118_lines = load_data(
        parsed_jeas118_lines, {"name": str, "parallel": str, "b__pu": float}
    )
    jeas118_trafos = load_data(
        parsed_jeas118_trafos,
        {
            "from_bus": str,
            "to_bus": str,
            "parallel": str,
            "trafo_ratio": float,
        },
    )
    buses = load_data(prepared_buses, {"name": str, "v_rated__kv": float})

    # Combine data
    branches = pd.merge(nrel118_lines, jeas118_lines, on="name", how="left")
    branches = branches.merge(
        jeas118_trafos, on=["from_bus", "to_bus", "parallel"], how="left"
    )

    # All branches are in service
    branches["in_service"] = True

    # Convert from pu to ohm
    buses.rename(columns={"name": "bus_name"}, inplace=True)
    branches = branches.merge(
        buses[["bus_name", "v_rated__kv"]],
        left_on="from_bus",
        right_on="bus_name",
        how="left",
    )
    branches["r__ohm"] = branches["r__pu"] * branches["v_rated__kv"] ** 2 / S_BASE__MVA
    branches["x__ohm"] = branches["x__pu"] * branches["v_rated__kv"] ** 2 / S_BASE__MVA
    branches["b__µs"] = (
        branches["b__pu"] * S_BASE__MVA * 1e6 / branches["v_rated__kv"] ** 2
    )

    # Calculate max current
    branches["max_i__ka"] = branches["max_p__mw"] / (branches["v_rated__kv"] * 3**0.5)

    # Return results
    cols = [
        "name",
        "from_bus",
        "to_bus",
        "parallel",
        "in_service",
        "r__ohm",
        "x__ohm",
        "b__µs",
        "trafo_ratio",
        "max_i__ka",
    ]
    if path_prepared_data:
        branches[cols].to_csv(path_prepared_data, header=True, index=False)
    else:
        return branches[cols]


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 6:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "prepare_branches.py path_parsed_nrel118_lines path_parsed_jeas118_lines "
            "path_parsed_jeas118_trafos path_prepared_buses path_prepared_data\n"
        )

    # Run
    prepare_branches(
        parsed_nrel118_lines=sys.argv[1],
        parsed_jeas118_lines=sys.argv[2],
        parsed_jeas118_trafos=sys.argv[3],
        prepared_buses=sys.argv[4],
        path_prepared_data=sys.argv[5],
    )
