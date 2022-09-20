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
    gens = pd.concat(parts, axis=1, join="inner").round(decimals=6)

    # Return results
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
