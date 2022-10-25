import sys
from typing import Optional

import pandas as pd

from definitions import S_BASE_MVA
from src.utils.data_loaders import load_df_data


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
    nrel118_lines = load_df_data(
        data=parsed_nrel118_lines,
        dtypes={
            "branch_number": int,
            "from_bus": str,
            "to_bus": str,
            "max_p_mw": float,
            "x_pu": float,
            "r_pu": float,
        },
    )
    jeas118_lines = load_df_data(
        data=parsed_jeas118_lines,
        dtypes={"from_bus": str, "to_bus": str, "parallel": str, "b_pu": float},
    )
    jeas118_trafos = load_df_data(
        data=parsed_jeas118_trafos,
        dtypes={
            "from_bus": str,
            "to_bus": str,
            "parallel": str,
            "trafo_ratio_rel": float,
        },
    )
    buses = load_df_data(
        data=prepared_buses, dtypes={"bus_name": str, "v_rated_kv": float}
    )

    # Add parallel number to NREL-118 line data
    nrel118_lines["parallel"] = "1"
    parallel_mask = nrel118_lines["branch_number"].isin([67, 76, 86, 99, 124, 139, 142])
    nrel118_lines.loc[parallel_mask, "parallel"] = "2"

    # Combine data
    branches = pd.merge(
        nrel118_lines,
        jeas118_lines,
        on=["from_bus", "to_bus", "parallel"],
        how="left",
    )
    branches = branches.merge(
        jeas118_trafos, on=["from_bus", "to_bus", "parallel"], how="left"
    )

    # All branches are in service
    branches["in_service"] = True

    # Convert from pu to ohm
    # Consider from_bus is a high voltage level bus for transformers
    branches = branches.merge(
        buses[["bus_name", "v_rated_kv"]],
        left_on="from_bus",
        right_on="bus_name",
        how="left",
    )
    branches["r_ohm"] = branches["r_pu"] * branches["v_rated_kv"] ** 2 / S_BASE_MVA
    branches["x_ohm"] = branches["x_pu"] * branches["v_rated_kv"] ** 2 / S_BASE_MVA
    branches["b_µs"] = branches["b_pu"] * S_BASE_MVA * 1e6 / branches["v_rated_kv"] ** 2

    # Calculate max current
    branches["max_i_ka"] = branches["max_p_mw"] / (branches["v_rated_kv"] * 3**0.5)

    # Round values
    cols = ["r_ohm", "x_ohm", "b_µs", "max_i_ka", "trafo_ratio_rel"]
    branches.loc[:, cols] = branches.loc[:, cols].round(decimals=6)

    # Compose branch name
    branches["branch_name"] = (
        "branch"
        + "_"
        + branches["from_bus"].str.lstrip("bus_")
        + "_"
        + branches["to_bus"].str.lstrip("bus_")
        + "_"
        + branches["parallel"].astype(str)
    )

    # Return results
    cols = [
        "branch_name",
        "from_bus",
        "to_bus",
        "parallel",
        "in_service",
        "r_ohm",
        "x_ohm",
        "b_µs",
        "trafo_ratio_rel",
        "max_i_ka",
    ]
    branches.sort_values("branch_name", inplace=True, ignore_index=True)
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
