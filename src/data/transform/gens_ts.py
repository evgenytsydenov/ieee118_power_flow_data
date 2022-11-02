import sys
from datetime import datetime
from typing import Optional

import pandas as pd

from definitions import DATE_FORMAT, DATE_RANGE, FILL_METHOD
from src.utils.data_loaders import load_df_data


def transform_gens_ts(
    transformed_gens: str | pd.DataFrame,
    parsed_nrel118_winds_ts: str | pd.DataFrame,
    parsed_nrel118_solars_ts: str | pd.DataFrame,
    parsed_nrel118_hydros_ts: str | pd.DataFrame,
    parsed_nrel118_hydros_nondisp_ts: str | pd.DataFrame,
    transformed_gens_escalated_ts: str | pd.DataFrame,
    transformed_outages_ts: str | pd.DataFrame,
    path_transformed_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Concat time-series data about generators.

    Args:
        transformed_gens: Path or dataframe with transformed generation data.
        transformed_outages_ts: Path or dataframe with time-series outage data.
        parsed_nrel118_winds_ts: Path or dataframe with time-series wind data
          from the NREL-118 dataset.
        parsed_nrel118_solars_ts: Path or dataframe with time-series solar data
          from the NREL-118 dataset.
        parsed_nrel118_hydros_ts: Path or dataframe with time-series hydro data
          from the NREL-118 dataset.
        parsed_nrel118_hydros_nondisp_ts: Path or dataframe with time-series data
          of non-dispatchable hydro plants from the NREL-118 dataset.
        transformed_gens_escalated_ts: Path or dataframe with transformed time-series
          data of generator adjusted by escalators from the NREL-118 dataset.
        path_transformed_data: Path to save transformed data.

    Returns:
        Transformed data or None if `path_transformed_data` is passed
          and the data were saved.
    """
    # Load gens data
    outages_ts = load_df_data(
        data=transformed_outages_ts,
        dtypes={"datetime": str, "gen_name": str, "in_service": bool},
    )
    gens = load_df_data(
        data=transformed_gens,
        dtypes={"gen_name": str, "is_ts_missed": bool, "min_p_mw": float},
    )

    # Load gens time-series data
    gens_ts = []
    for data in [
        parsed_nrel118_winds_ts,
        parsed_nrel118_solars_ts,
        parsed_nrel118_hydros_ts,
        parsed_nrel118_hydros_nondisp_ts,
        transformed_gens_escalated_ts,
    ]:
        gen_data = load_df_data(
            data=data,
            dtypes={"datetime": str, "gen_name": str, "p_mw": float},
        )
        gens_ts.append(gen_data)

    # Generators whose outputs are missed and will be optimized
    gens_missed = pd.DataFrame(
        data={
            "gen_name": gens.loc[gens["is_ts_missed"], "gen_name"].values,
            "datetime": datetime(2024, 1, 1, 0, 0, 0).strftime(DATE_FORMAT),
            "p_mw": gens.loc[gens["is_ts_missed"], "min_p_mw"].values,
        }
    )
    gens_ts.append(gens_missed)
    gens_ts = pd.concat(gens_ts, ignore_index=True)

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

    # Return results
    gens_ts.sort_values(["datetime", "gen_name"], inplace=True, ignore_index=True)
    cols = ["datetime", "gen_name", "in_service", "p_mw"]
    if path_transformed_data:
        gens_ts[cols].to_csv(path_transformed_data, header=True, index=False)
    else:
        return gens_ts[cols]


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 9:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "transform_gens_ts.py path_transformed_gens path_parsed_nrel118_winds_ts "
            "path_parsed_nrel118_solars_ts path_parsed_nrel118_hydros_ts "
            "path_parsed_nrel118_hydros_nondisp_ts path_transformed_gens_escalated_ts "
            "path_transformed_outages_ts path_transformed_data\n"
        )

    # Run
    transform_gens_ts(
        transformed_gens=sys.argv[1],
        parsed_nrel118_winds_ts=sys.argv[2],
        parsed_nrel118_solars_ts=sys.argv[3],
        parsed_nrel118_hydros_ts=sys.argv[4],
        parsed_nrel118_hydros_nondisp_ts=sys.argv[5],
        transformed_gens_escalated_ts=sys.argv[6],
        transformed_outages_ts=sys.argv[7],
        path_transformed_data=sys.argv[8],
    )
