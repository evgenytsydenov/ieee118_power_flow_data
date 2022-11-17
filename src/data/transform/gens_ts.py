import sys
from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd

from definitions import DATE_FORMAT
from src.utils.data_loaders import load_df_data


def transform_gens_ts(
    transformed_gens: str | pd.DataFrame,
    parsed_nrel118_winds_ts: str | pd.DataFrame,
    parsed_nrel118_solars_ts: str | pd.DataFrame,
    parsed_nrel118_hydros_ts: str | pd.DataFrame,
    parsed_nrel118_hydros_nondisp_ts: str | pd.DataFrame,
    path_transformed_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Concat time-series data about generators output.

    Args:
        transformed_gens: Path or dataframe with transformed generation data.
        parsed_nrel118_winds_ts: Path or dataframe with time-series wind data
          from the NREL-118 dataset.
        parsed_nrel118_solars_ts: Path or dataframe with time-series solar data
          from the NREL-118 dataset.
        parsed_nrel118_hydros_ts: Path or dataframe with time-series hydro data
          from the NREL-118 dataset.
        parsed_nrel118_hydros_nondisp_ts: Path or dataframe with time-series data
          of non-dispatchable hydro plants from the NREL-118 dataset.
        path_transformed_data: Path to save transformed data.

    Returns:
        Transformed data or None if `path_transformed_data` is passed
          and the data were saved.
    """
    # Load gens data
    gens = load_df_data(
        data=transformed_gens,
        dtypes={"gen_name": str, "opt_category": str},
    )

    # Load gens time-series data
    gens_ts = []
    for data in [
        parsed_nrel118_winds_ts,
        parsed_nrel118_solars_ts,
        parsed_nrel118_hydros_ts,
        parsed_nrel118_hydros_nondisp_ts,
    ]:
        gen_data = load_df_data(
            data=data,
            dtypes={"datetime": str, "gen_name": str, "p_mw": float},
        )
        gens_ts.append(gen_data)

    # Generators whose outputs will be optimized
    optimized = gens["opt_category"] != "non_optimized"
    gens_optimized = pd.DataFrame(
        data={
            "gen_name": gens.loc[optimized, "gen_name"].values,
            "datetime": datetime(2024, 1, 1, 0, 0, 0).strftime(DATE_FORMAT),
            "p_mw": np.nan,
        }
    )
    gens_ts.append(gens_optimized)
    gens_ts = pd.concat(gens_ts, ignore_index=True)

    # Return results
    gens_ts.sort_values(["datetime", "gen_name"], inplace=True, ignore_index=True)
    cols = ["datetime", "gen_name", "p_mw"]
    if path_transformed_data:
        gens_ts[cols].to_csv(path_transformed_data, header=True, index=False)
    else:
        return gens_ts[cols]


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 7:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "transform_gens_ts.py path_transformed_gens path_parsed_nrel118_winds_ts "
            "path_parsed_nrel118_solars_ts path_parsed_nrel118_hydros_ts "
            "path_parsed_nrel118_hydros_nondisp_ts path_transformed_data\n"
        )

    # Run
    transform_gens_ts(
        transformed_gens=sys.argv[1],
        parsed_nrel118_winds_ts=sys.argv[2],
        parsed_nrel118_solars_ts=sys.argv[3],
        parsed_nrel118_hydros_ts=sys.argv[4],
        parsed_nrel118_hydros_nondisp_ts=sys.argv[5],
        path_transformed_data=sys.argv[6],
    )
