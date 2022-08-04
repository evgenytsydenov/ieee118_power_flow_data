import pandas as pd


def load_df_data(data: str | pd.DataFrame, dtypes: dict) -> pd.DataFrame:
    """Load dataframes and convert data to the proper types.

    Args:
        dtypes: Path for each column
        data: Path or dataframe with data.

    Returns:
        Loaded data as a dataframe.
    """
    cols = dtypes.keys()
    if isinstance(data, str):
        return pd.read_csv(data, header=0, usecols=cols, dtype=dtypes)
    else:
        return data[cols].astype(dtypes)
