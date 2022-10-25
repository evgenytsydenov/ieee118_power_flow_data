import sys
from typing import Optional

import numpy as np
import pandas as pd

from definitions import DATE_FORMAT, DATE_RANGE, FILL_METHOD, PLANT_MODE
from src.utils.data_loaders import load_df_data


def prepare_gens_ts(
    transformed_gens: str | pd.DataFrame,
    transformed_gens_ts: str | pd.DataFrame,
    transformed_outages_ts: str | pd.DataFrame,
    path_prepared_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Prepare final generation time-series data.

    Args:
        transformed_gens: Path or dataframe with transformed generation data.
        transformed_outages_ts: Path or dataframe with time-series outage data.
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
            "v_set_kv": float,
            "q_max_mvar": float,
            "q_min_mvar": float,
        },
    )
    outages_ts = load_df_data(
        data=transformed_outages_ts,
        dtypes={"datetime": str, "gen_name": str, "in_service": bool},
    )
    gens = load_df_data(
        data=transformed_gens,
        dtypes={"gen_name": str, "is_slack": bool},
    )

    # Select by date range
    # Each generator has at least one measurement at "2024-01-01 00:00:00"
    start_date, end_date, frequency = DATE_RANGE
    date_range = pd.date_range(
        start_date, end_date, freq=frequency, name="datetime", inclusive="left"
    )
    parts = []
    for df in [gens_ts, outages_ts]:
        df["datetime"] = pd.to_datetime(df["datetime"], format=DATE_FORMAT)
        parts.append(
            df.sort_values("datetime")
            .set_index("datetime")
            .groupby("gen_name")
            .apply(lambda x: x.reindex(date_range, method=FILL_METHOD))
            .drop(columns=["gen_name"])
            .round(decimals=6)
        )
    gens_ts = pd.concat(parts, axis=1, join="inner").round(decimals=6)
    gens_ts.reset_index(inplace=True)

    # If gen is not in service, its parameters are undefined
    value_cols = ["p_mw", "v_set_kv", "q_max_mvar", "q_min_mvar"]
    gens_ts.loc[~gens_ts["in_service"], value_cols] = np.nan

    # Drop gens in the slack bus
    slack_gens = gens.loc[gens["is_slack"], "gen_name"]
    gens_ts = gens_ts.loc[~gens_ts["gen_name"].isin(slack_gens)]

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
            "q_max_mvar": "sum",
            "q_min_mvar": "sum",
            "v_set_kv": "mean",
            "in_service": "sum",
        }
        gens_ts = gens_ts.groupby(["plant_name", "datetime"], as_index=False).agg(
            agg_funcs
        )

        # If the number of gens, which are in service, equals to zero,
        # the plant is out of service and its parameters should be undefined
        gens_ts["in_service"] = gens_ts["in_service"].astype(bool)
        value_cols = ["p_mw", "v_set_kv", "q_max_mvar", "q_min_mvar"]
        gens_ts.loc[~gens_ts["in_service"], value_cols] = np.nan

        # Rename columns for consistency in future scripts
        gens_ts.rename(columns={"plant_name": "gen_name"}, inplace=True)

    # Return results
    cols = [
        "datetime",
        "gen_name",
        "in_service",
        "p_mw",
        "v_set_kv",
        "q_max_mvar",
        "q_min_mvar",
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
    if len(sys.argv) != 5:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython prepare_gens_ts.py "
            "path_transformed_gens path_transformed_gens_ts "
            "path_transformed_outages_ts path_prepared_data\n"
        )

    # Run
    prepare_gens_ts(
        transformed_gens=sys.argv[1],
        transformed_gens_ts=sys.argv[2],
        transformed_outages_ts=sys.argv[3],
        path_prepared_data=sys.argv[4],
    )
