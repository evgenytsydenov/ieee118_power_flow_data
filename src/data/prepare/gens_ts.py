import sys
from typing import Optional

import numpy as np
import pandas as pd

from definitions import DATE_FORMAT, PLANT_MODE
from src.utils.data_loaders import load_df_data


def prepare_gens_ts(
    transformed_gens: str | pd.DataFrame,
    transformed_gens_ts: str | pd.DataFrame,
    path_prepared_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Prepare final generation time-series data.

    Args:
        transformed_gens: Path or dataframe with transformed generation data.
        transformed_gens_ts: Path or dataframe with time-series gens data.
        path_prepared_data: Path to save prepared data.

    Returns:
        Prepared data or None if `path_prepared_data` is passed and the data were saved.
    """
    # Load data
    gens_ts = load_df_data(
        data=transformed_gens_ts,
        dtypes={
            "datetime": str,
            "gen_name": str,
            "p_mw": float,
            "in_service": bool,
        },
    )
    gens = load_df_data(
        data=transformed_gens,
        dtypes={
            "gen_name": str,
            "is_slack": bool,
            "is_optimized": bool,
            "max_p_mw": float,
            "min_p_mw": float,
        },
    )

    # Join info about gens
    gens_ts = gens_ts.merge(gens, on="gen_name", how="left")

    # Drop gens in the slack bus
    slack_gens = gens.loc[gens["is_slack"], "gen_name"]
    gens_ts = gens_ts.loc[~gens_ts["gen_name"].isin(slack_gens)]
    gens_ts.drop(columns="is_slack", inplace=True)

    # Clip outputs which exceed the max limit
    gens_ts["p_mw"].clip(
        upper=gens_ts["max_p_mw"], lower=gens_ts["min_p_mw"], inplace=True
    )

    # Reactive power limits
    gens_ts["max_q_mvar"] = 0.7 * gens_ts["max_p_mw"]
    gens_ts["min_q_mvar"] = -0.3 * gens_ts["max_p_mw"]

    # Limits for OPF
    gens_ts["max_p_opf_mw"] = gens_ts["p_mw"]
    gens_ts["min_p_opf_mw"] = gens_ts["p_mw"]
    mask = gens_ts["is_optimized"]
    gens_ts.loc[mask, "max_p_opf_mw"] = gens_ts.loc[mask, "max_p_mw"]
    gens_ts.loc[mask, "min_p_opf_mw"] = gens_ts.loc[mask, "min_p_mw"]

    # If gen is not in service, its parameters are undefined
    value_cols = ["p_mw", "max_q_mvar", "min_q_mvar", "max_p_opf_mw", "min_p_opf_mw"]
    gens_ts.loc[~gens_ts["in_service"], value_cols] = np.nan

    if PLANT_MODE:
        # Load mapping of plants and gens
        plants = load_df_data(
            data=transformed_gens,
            dtypes={"gen_name": str, "plant_name": str},
        )

        # Add plant names to time-series data of gens
        gens_ts = pd.merge(gens_ts, plants, how="left", on="gen_name")

        # Group gen parameters
        agg_funcs = {
            "p_mw": "sum",
            "max_q_mvar": "sum",
            "min_q_mvar": "sum",
            "max_p_opf_mw": "sum",
            "min_p_opf_mw": "sum",
            "in_service": "sum",
        }
        gens_ts = gens_ts.groupby(["plant_name", "datetime"], as_index=False).agg(
            agg_funcs
        )

        # If the number of gens, which are in service, equals to zero,
        # the plant is out of service and its parameters should be undefined
        gens_ts["in_service"] = gens_ts["in_service"].astype(bool)
        gens_ts.loc[~gens_ts["in_service"], value_cols] = np.nan

        # Rename columns for consistency in further scripts
        gens_ts.rename(columns={"plant_name": "gen_name"}, inplace=True)

    # Return results
    cols = [
        "datetime",
        "gen_name",
        "in_service",
        "p_mw",
        "max_q_mvar",
        "min_q_mvar",
        "max_p_opf_mw",
        "min_p_opf_mw",
    ]
    gens_ts = gens_ts.sort_values(["datetime", "gen_name"], ignore_index=True)
    if path_prepared_data:
        gens_ts[cols].to_csv(
            path_prepared_data, header=True, index=False, date_format=DATE_FORMAT
        )
    else:
        return gens_ts[cols]


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 4:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython prepare_gens_ts.py "
            "path_transformed_gens path_transformed_gens_ts path_prepared_data\n"
        )

    # Run
    prepare_gens_ts(
        transformed_gens=sys.argv[1],
        transformed_gens_ts=sys.argv[2],
        path_prepared_data=sys.argv[3],
    )
