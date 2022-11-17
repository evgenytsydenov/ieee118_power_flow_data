import sys
from typing import Optional

import numpy as np
import pandas as pd

from definitions import DATE_FORMAT, DATE_RANGE, FILL_METHOD
from src.utils.data_loaders import load_df_data


def prepare_gens_ts(
    transformed_gens: str | pd.DataFrame,
    transformed_gens_ts: str | pd.DataFrame,
    transformed_gens_escalated_ts: str | pd.DataFrame,
    transformed_outages_ts: str | pd.DataFrame,
    path_prepared_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Prepare final generation time-series data.

    Args:
        transformed_gens: Path or dataframe with transformed generation data.
        transformed_gens_ts: Path or dataframe with time-series gens data.
        path_prepared_data: Path to save prepared data.
        transformed_gens_escalated_ts: Path or dataframe with transformed time-series
          data of generator adjusted by escalators from the NREL-118 dataset.
        transformed_outages_ts: Path or dataframe with time-series outage data.

    Returns:
        Prepared data or None if `path_prepared_data` is passed and the data were saved.
    """
    # Load data
    gens = load_df_data(
        data=transformed_gens,
        dtypes={"gen_name": str, "is_slack": bool},
    )
    gens_ts = load_df_data(
        data=transformed_gens_ts,
        dtypes={"datetime": str, "gen_name": str, "p_mw": float},
    )
    outages_ts = load_df_data(
        data=transformed_outages_ts,
        dtypes={"datetime": str, "gen_name": str, "in_service": bool},
    )
    escalated_ts = load_df_data(
        data=transformed_gens_escalated_ts,
        dtypes={"datetime": str, "gen_name": str, "max_p_mw": float, "min_p_mw": float},
    )

    # Select by date range
    # Each generator has at least one measurement at "2024-01-01 00:00:00"
    start_date, end_date, frequency = DATE_RANGE
    date_range = pd.date_range(
        start_date, end_date, freq=frequency, name="datetime", inclusive="left"
    )

    # Drop Feb 29 since load, wind, and solar data have no this date
    mask = (date_range.day == 29) & (date_range.month == 2)
    date_range = date_range[~mask]

    parts = []
    for df in [gens_ts, outages_ts, escalated_ts]:
        df["datetime"] = pd.to_datetime(df["datetime"], format=DATE_FORMAT)
        parts.append(
            df.sort_values("datetime")
            .set_index("datetime")
            .groupby("gen_name")
            .apply(lambda x: x.reindex(date_range, method=FILL_METHOD))
            .drop(columns=["gen_name"])
        )
    gens_ts = pd.concat(parts, axis=1, join="inner")
    gens_ts.reset_index(inplace=True)

    # Drop gens in the slack bus
    gens_ts = gens_ts.merge(gens, on="gen_name", how="left")
    gens_ts.drop(labels=gens_ts.index[gens_ts["is_slack"]], inplace=True)
    gens_ts.drop(columns="is_slack", inplace=True)

    # Reactive power limits
    gens_ts["max_q_mvar"] = 0.7 * gens_ts["max_p_mw"]
    gens_ts["min_q_mvar"] = -0.3 * gens_ts["max_p_mw"]

    # If gen is not in service, its parameters are undefined
    value_cols = ["p_mw", "max_q_mvar", "min_q_mvar", "max_p_mw", "min_p_mw"]
    gens_ts.loc[~gens_ts["in_service"], value_cols] = np.nan

    # Round values
    gens_ts.loc[:, value_cols] = gens_ts.loc[:, value_cols].round(decimals=6)

    # Return results
    cols = [
        "datetime",
        "gen_name",
        "in_service",
        "p_mw",
        "max_q_mvar",
        "min_q_mvar",
        "max_p_mw",
        "min_p_mw",
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
    if len(sys.argv) != 6:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython prepare_gens_ts.py "
            "path_transformed_gens path_transformed_gens_ts "
            "path_transformed_gens_escalated_ts path_transformed_outages_ts "
            "path_prepared_data\n"
        )

    # Run
    prepare_gens_ts(
        transformed_gens=sys.argv[1],
        transformed_gens_ts=sys.argv[2],
        transformed_gens_escalated_ts=sys.argv[3],
        transformed_outages_ts=sys.argv[4],
        path_prepared_data=sys.argv[5],
    )
