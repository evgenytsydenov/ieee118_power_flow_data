from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

import pandas as pd
from tqdm import tqdm

from definitions import DATE_FORMAT, MODEL_NAME_FORMAT, PLANT_MODE
from src.utils.data_loaders import load_df_data


class BaseRegimeBuilder(ABC):
    """Base class for creating power regimes."""

    def __init__(self) -> None:
        """Base class for creating power regimes."""
        self._is_plant_mode = PLANT_MODE
        self._buses = None
        self._branches = None
        self._loads = None
        self._loads_ts = None
        self._gens = None
        self._gens_ts = None
        self._timestamps = None
        self._model = None

    def load_data(
        self,
        buses: str | pd.DataFrame,
        branches: str | pd.DataFrame,
        loads: str | pd.DataFrame,
        loads_ts: str | pd.DataFrame,
        gens: str | pd.DataFrame,
        gens_ts: str | pd.DataFrame,
    ) -> None:
        """Load data for creating regimes.

        Args:
            buses: Path or DataFrame with bus data.
            branches: Path or DataFrame with branch data.
            loads: Path or DataFrame with load data.
            loads_ts: Path or DataFrame with load time-series data.
            gens: Path or DataFrame with generation data.
            gens_ts: Path or DataFrame with generation time-series data.
        """
        # Load raw data
        self._buses = load_df_data(
            buses,
            dtypes={
                "bus_name": str,
                "region": str,
                "in_service": bool,
                "v_rated_kv": float,
                "is_slack": bool,
                "min_v_pu": float,
                "max_v_pu": float,
                "x_coordinate": float,
                "y_coordinate": float,
            },
        )
        self._branches = load_df_data(
            data=branches,
            dtypes={
                "branch_name": str,
                "from_bus": str,
                "to_bus": str,
                "parallel": int,
                "in_service": bool,
                "r_ohm": float,
                "x_ohm": float,
                "b_µs": float,
                "trafo_ratio_rel": float,
                "max_i_ka": float,
            },
        )
        self._loads = load_df_data(
            data=loads,
            dtypes={
                "load_name": str,
                "bus_name": str,
            },
        )
        self._loads_ts = load_df_data(
            data=loads_ts,
            dtypes={
                "datetime": str,
                "load_name": str,
                "in_service": bool,
                "q_mvar": float,
                "p_mw": float,
            },
        )
        self._gens = load_df_data(
            data=gens,
            dtypes={
                "gen_name": str,
                "bus_name": str,
                "max_p_mw": float,
                "min_p_mw": float,
                "is_optimized": bool,
            },
        )
        self._gens_ts = load_df_data(
            data=gens_ts,
            dtypes={
                "datetime": str,
                "gen_name": str,
                "in_service": bool,
                "p_mw": float,
                "max_q_mvar": float,
                "min_q_mvar": float,
            },
        )

        # Datetime ranges in load and gen time-series are equal
        load_timestamps = sorted(self._loads_ts["datetime"].unique())
        gen_timestamps = sorted(self._gens_ts["datetime"].unique())
        assert (
            load_timestamps == gen_timestamps
        ), "Gen and load timestamps are different"
        self._timestamps = gen_timestamps

    @property
    def model(self) -> Any:
        """Power flow model"""
        raise NotImplementedError

    def run_first(self, verbose: bool = True) -> Any:
        """Run the building process.

        Args:
            verbose: If to print info messages.
        Returns:
            Power flow regime corresponding to the first timestamp of the provided data.
        """
        # Create base model
        self._build_base_model()

        # Refresh regime data in accordance to the first timestamp
        timestamp = self._timestamps[0]
        if verbose:
            print(f"Use data for {timestamp}")
        self._apply_next_timestamp(timestamp)

        # Calculate power flows
        is_converged = self._calculate_regime()
        if not is_converged:
            print(f"Regime at {timestamp} did not converge.")
        return self.model

    def run(self, path_models: str, display: bool = False) -> None:
        """Run the building process.

        Args:
            path_models: Path if it is necessary to save models.
            display: If to show a progress bar.
        """

        # Create base model
        self._build_base_model()

        # Timestamps are equal for all time-series data
        for timestamp in tqdm(self._timestamps, disable=not display):

            # Refresh regime data in accordance to datetime
            self._apply_next_timestamp(timestamp)

            # Calculate power flows
            is_converged = self._calculate_regime()
            if not is_converged:
                print(f"Regime at {timestamp} did not converge.")

            # Save model
            model_name = datetime.strptime(timestamp, DATE_FORMAT).strftime(
                MODEL_NAME_FORMAT
            )
            self._save_model(path=path_models, model_name=model_name)
            break

    @abstractmethod
    def _build_base_model(self) -> None:
        """Create power flow model."""
        raise NotImplementedError

    @abstractmethod
    def _save_model(self, path: str, model_name: str) -> None:
        """Save model.

        Args:
            path: Path to save the model.
            model_name: Model name.
        """
        raise NotImplementedError

    @abstractmethod
    def _apply_next_timestamp(self, timestamp: str) -> None:
        """Refresh regime data in accordance to datetime.

        Args:
            timestamp: Current datetime.
        """
        raise NotImplementedError

    @abstractmethod
    def _calculate_regime(self) -> bool:
        """Calculate power flows.

        Returns:
            True if the calculation was successful, False otherwise.
        """
        raise NotImplementedError
