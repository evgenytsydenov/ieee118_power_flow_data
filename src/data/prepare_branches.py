import sys
from typing import Optional

import pandas as pd


def load_data(data: str | pd.DataFrame) -> pd.DataFrame:
    """Auxiliary function to load branch data.

    Args:
        data: path or dataframe with data.

    Returns:
        Loaded data as a dataframe.
    """
    return pd.read_csv(data, header=0) if isinstance(data, str) else data


def prepare_branches(
    parsed_nrel118_lines: str | pd.DataFrame,
    parsed_jeas118_lines: str | pd.DataFrame,
    parsed_jeas118_trafos: str | pd.DataFrame,
    path_prepared_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Combine information about branches into final dataset.

    Args:
        parsed_nrel118_lines: path or dataframe with line data from NREL-118 dataset.
        parsed_jeas118_lines: path or dataframe with line data from JEAS-118 dataset.
        parsed_jeas118_trafos: path or dataframe with trafo data from JEAS-118 dataset.
        path_prepared_data: Path to save prepared data.

    Returns:
        Prepared bus data or None if `path_prepared_data` is passed and the data
          were saved.
    """
    # Load data
    nrel118_lines = load_data(parsed_nrel118_lines)
    jeas118_lines = load_data(parsed_jeas118_lines)
    jeas118_trafos = load_data(parsed_jeas118_trafos)

    # Combine data
    branches = pd.merge(
        nrel118_lines,
        jeas118_lines[["name", "parallel", "b__pu"]],
        on="name",
        how="left",
    )
    branches = branches.merge(
        jeas118_trafos[["from_bus", "to_bus", "parallel", "ratio"]],
        on=["from_bus", "to_bus", "parallel"],
        how="left",
    )

    # All branches are in service
    branches["in_service"] = True

    # Return results
    if path_prepared_data:
        branches.to_csv(path_prepared_data, header=True, index=False)
    else:
        return branches


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 5:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "prepare_branches.py path_parsed_nrel118_lines path_parsed_jeas118_lines "
            "path_parsed_jeas118_trafos path_prepared_data\n"
        )

    # Run
    path_parsed_nrel118_lines = sys.argv[1]
    path_parsed_jeas118_lines = sys.argv[2]
    path_parsed_jeas118_trafos = sys.argv[3]
    path_prepared_data = sys.argv[4]
    prepare_branches(
        path_parsed_nrel118_lines,
        path_parsed_jeas118_lines,
        path_parsed_jeas118_trafos,
        path_prepared_data,
    )
