import sys
from typing import Optional

import pandas as pd

from definitions import DATE_FORMAT, DATE_RANGE, FILL_METHOD
from src.utils.data_loaders import load_df_data


def prepare_gens_ts(
    transformed_gens_ts: str | pd.DataFrame,
    transformed_outages_ts: str | pd.DataFrame,
    path_prepared_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Prepare final generation time-series data.

    Args:
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

    # Set datetime as index, drop unused variables
    gens_ts["datetime"] = pd.to_datetime(gens_ts["datetime"], format=DATE_FORMAT)
    gens = gens_ts.pivot(
        index="datetime",
        columns=["gen_name"],
        values=["p_mw", "q_min_mvar", "q_max_mvar", "v_set_kv"],
    )

    # Each generator has at least one measurement at "2024-01-01 00:00:00"
    # One part of generators have measurements per hour, other part --- once per month
    gens.fillna(method="pad", inplace=True)

    # Extract necessary date range
    start_date, end_date, frequency = DATE_RANGE
    mask = (gens.index >= start_date) & (gens.index < end_date)
    if FILL_METHOD == "pad":
        gens = gens[mask].asfreq(frequency, method="pad")
    else:
        raise AttributeError(f"Unknown value of FILL_METHOD: {FILL_METHOD}")

    # Round
    cols = ["p_mw", "q_min_mvar", "q_max_mvar", "v_set_kv"]
    cols_idx = gens.columns.get_level_values(0).isin(cols)
    gens.loc[:, cols_idx] = gens.loc[:, cols_idx].round(decimals=6)

    # Add info about outages
    outages_ts["datetime"] = pd.to_datetime(outages_ts["datetime"], format=DATE_FORMAT)
    outages_ts = outages_ts.pivot(
        index="datetime",
        columns=["gen_name"],
        values=["in_service"],
    )

    # Align timestamps
    # Each generator has at least one state measurement at "2024-01-01 00:00:00"
    outages_ts, _ = outages_ts.align(gens, join="outer", axis=0, method="pad")

    # Return results
    gens = pd.concat([gens, outages_ts], axis=1, join="inner")
    if path_prepared_data:
        gens.to_csv(
            path_prepared_data, header=True, index=True, date_format=DATE_FORMAT
        )
    else:
        return gens


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 4:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython prepare_gens_ts.py "
            "transformed_gens_ts transformed_outages_ts path_prepared_data\n"
        )

    # Run
    prepare_gens_ts(
        transformed_gens_ts=sys.argv[1],
        transformed_outages_ts=sys.argv[2],
        path_prepared_data=sys.argv[3],
    )
