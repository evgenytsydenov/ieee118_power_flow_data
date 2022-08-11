from typing import Optional

import pandas as pd


def load_df_data(
    data: str | pd.DataFrame,
    dtypes: dict,
    nrows: Optional[int] = None,
    sep: str = ",",
    decimal: str = ".",
) -> pd.DataFrame:
    """Load dataframes and convert data to the proper types.

    Args:
        decimal: Character to recognize as decimal point.
        sep: Delimiter to use.
        dtypes: Path for each column.
        data: Path or dataframe with data.
        nrows: Number of first rows to return.

    Returns:
        Loaded data as a dataframe.
    """
    cols = dtypes.keys()
    if isinstance(data, str):
        return pd.read_csv(
            data,
            header=0,
            usecols=cols,
            dtype=dtypes,
            nrows=nrows,
            decimal=decimal,
            sep=sep,
        )
    result = data if nrows is None else data.head(nrows)
    return result[cols].astype(dtypes)
