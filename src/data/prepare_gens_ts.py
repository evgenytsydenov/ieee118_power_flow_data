import sys
from typing import Optional

import numpy as np
import pandas as pd

from definitions import DATE_FORMAT, DATE_RANGE, FILL_METHOD
from src.utils.data_loaders import load_df_data


def prepare_gens_ts(
    parsed_nrel118_winds_ts: str | pd.DataFrame,
    parsed_nrel118_solars_ts: str | pd.DataFrame,
    parsed_nrel118_hydros_ts: str | pd.DataFrame,
    parsed_nrel118_hydros_nondisp_ts: str | pd.DataFrame,
    transformed_gens_escalated_ts: str | pd.DataFrame,
    parsed_nrel118_outages_ts: str | pd.DataFrame,
    path_prepared_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Prepare final generation time-series data.

    Args:
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
        parsed_nrel118_outages_ts: Path or dataframe with time-series outage data
          from the NREL-118 dataset.
        path_prepared_data: Path to save prepared data.

    Returns:
        Prepared data or None if `path_prepared_data` is passed and the data were saved.
    """

    # Load gens data
    gen_ts = []
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
        gen_ts.append(gen_data)
    gens = pd.concat(gen_ts, ignore_index=True)

    # Temporary assumptions
    gens["v_set_kv"] = np.nan
    gens["q_max_mvar"] = np.nan
    gens["q_min_mvar"] = np.nan

    # Set datetime as index, drop unused variables
    gens["datetime"] = pd.to_datetime(gens["datetime"], format=DATE_FORMAT)
    gens = gens.pivot(
        index="datetime",
        columns=["gen_name"],
        values=["p_mw", "q_min_mvar", "q_max_mvar", "v_set_kv"],
    )

    # Each generator has at least one measurement at "2024-01-01 00:00:00"
    # One part of generators have measurements per hour
    # Other part --- once per month
    gens.fillna(method="pad", inplace=True)

    # Extract necessary date range
    start_date, end_date, frequency = DATE_RANGE
    mask = (gens.index >= start_date) & (gens.index < end_date)
    if FILL_METHOD == "pad":
        gens = gens[mask].asfreq(frequency, method="pad")
    else:
        raise AttributeError(f"Unknown value of FILL_METHOD: {FILL_METHOD}")

    # Add info about outages
    outages_ts = load_df_data(
        data=parsed_nrel118_outages_ts,
        dtypes={"datetime": str, "gen_name": str, "in_outage": bool},
    )
    outages_ts["datetime"] = pd.to_datetime(outages_ts["datetime"], format=DATE_FORMAT)
    outages_ts["in_service"] = ~outages_ts["in_outage"]
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
    if len(sys.argv) != 8:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython prepare_gens_ts.py "
            "path_parsed_nrel118_wind_ts path_parsed_nrel118_solar_ts "
            "path_parsed_nrel118_hydro_ts path_parsed_nrel118_hydro_nondisp_ts "
            "path_transformed_gens_escalated_ts path_parsed_nrel118_outages_ts "
            "path_prepared_data\n"
        )

    # Run
    prepare_gens_ts(
        parsed_nrel118_winds_ts=sys.argv[1],
        parsed_nrel118_solars_ts=sys.argv[2],
        parsed_nrel118_hydros_ts=sys.argv[3],
        parsed_nrel118_hydros_nondisp_ts=sys.argv[4],
        transformed_gens_escalated_ts=sys.argv[5],
        parsed_nrel118_outages_ts=sys.argv[6],
        path_prepared_data=sys.argv[7],
    )
