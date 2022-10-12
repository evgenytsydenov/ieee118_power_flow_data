import math
import os

import numpy as np
import pandapower as pp
import pandas as pd
from pandapower import LoadflowNotConverged

from src.model.samplers.base import BaseRegimeSampler


class PandaRegimeSampler(BaseRegimeSampler):
    """Class for creating power regimes using PandaPower.

    Args:
        s_base_mva: Base power.
        f_hz: Power system frequency.
    """

    def __init__(self, s_base_mva: float, f_hz: float) -> None:
        super().__init__()
        self.s_base_mva = s_base_mva
        self.f_hz = f_hz
        self._bus_name_to_id = None
        self._bus_v_rates = None

    def _build_model(self) -> None:
        """Create power flow model."""

        # Create empty network
        self._model = pp.create_empty_network(sn_mva=self.s_base_mva, f_hz=self.f_hz)

        # Add buses
        pp.create_buses(
            self._model,
            nr_buses=len(self._buses),
            vn_kv=self._buses["v_rated_kv"],
            name=self._buses["bus_name"],
            zone=self._buses["region"],
            in_service=self._buses["in_service"],
        )
        self._bus_name_to_id = {
            v: k for k, v in self._model.bus["name"].to_dict().items()
        }
        self._bus_v_rates = self._buses[["bus_name", "v_rated_kv"]].set_index(
            "bus_name"
        )

        # Add slack buses
        pp.create_ext_grid(
            self._model,
            bus=self._bus_name_to_id["bus_69"],
            vm_pu=1,
            va_degree=0,
            in_service=True,
        )

        # Add the rest
        self._add_lines()
        self._add_transformers()
        self._add_loads()
        self._add_generators()

        # Some modifications for faster access
        self._gens_ts.rename(
            columns={
                "q_min_mvar": "min_q_mvar",
                "q_max_mvar": "max_q_mvar",
            },
            inplace=True,
        )
        v_gen_bus_kv = pd.merge(
            self._gens,
            self._bus_v_rates,
            right_index=True,
            left_on="bus_name",
            how="left",
        )
        self._gens_ts = pd.merge(
            self._gens_ts.reset_index(),
            v_gen_bus_kv[["gen_name", "v_rated_kv"]],
            how="left",
            on="gen_name",
        ).set_index("datetime")
        self._gens_ts["vm_pu"] = self._gens_ts["v_set_kv"] / self._gens_ts["v_rated_kv"]

    def _add_lines(self) -> None:
        """Add line info to the power flow model."""

        # Drop transformers
        lines = self._branches[self._branches["trafo_ratio_rel"].isna()]

        # Convert bus names to indices
        lines["from_bus_id"] = lines["from_bus"].map(self._bus_name_to_id)
        lines["to_bus_id"] = lines["to_bus"].map(self._bus_name_to_id)

        # Add lines to the model
        pp.create_lines_from_parameters(
            self._model,
            name=lines["branch_name"],
            from_buses=lines["from_bus_id"],
            to_buses=lines["to_bus_id"],
            parallel=lines["parallel"],
            length_km=1,
            r_ohm_per_km=lines["r_ohm"],
            x_ohm_per_km=lines["x_ohm"],
            c_nf_per_km=lines["b_µs"] * 1e3 / (2 * self._model.f_hz * math.pi),
            max_i_ka=lines["max_i_ka"],
            in_service=lines["in_service"],
        )

    def _add_transformers(self) -> None:
        """Add transformer info to the power flow model."""

        # Extract transformers
        trafos = self._branches[~self._branches["trafo_ratio_rel"].isna()]

        # Convert bus names to indices
        trafos["from_bus_id"] = trafos["from_bus"].map(self._bus_name_to_id)
        trafos["to_bus_id"] = trafos["to_bus"].map(self._bus_name_to_id)

        # Consider from_bus is a high voltage level bus
        vn_hv_kv = self._bus_v_rates.loc[trafos["from_bus"], "v_rated_kv"].values
        vn_lv_kv = self._bus_v_rates.loc[trafos["to_bus"], "v_rated_kv"].values

        # Calculate trafo parameters
        z_base_net = vn_hv_kv**2 / self.s_base_mva
        s_base_trafo_mva = self.s_base_mva
        vk_percent = (
            100 * (trafos["x_ohm"] / z_base_net) * (s_base_trafo_mva / self.s_base_mva)
        )
        vkr_percent = (
            100 * (trafos["r_ohm"] / z_base_net) * (s_base_trafo_mva / self.s_base_mva)
        )
        tap_diff = trafos["trafo_ratio_rel"] - 1

        # Add trafos to the model
        pp.create_transformers_from_parameters(
            self._model,
            name=trafos["branch_name"],
            hv_buses=trafos["from_bus_id"],
            lv_buses=trafos["to_bus_id"],
            sn_mva=s_base_trafo_mva,
            vn_hv_kv=vn_hv_kv,
            vn_lv_kv=vn_lv_kv,
            vk_percent=vk_percent,
            vkr_percent=vkr_percent,
            pfe_kw=0,
            i0_percent=0,
            parallel=trafos["parallel"],
            in_service=trafos["in_service"],
            tap_side="hv",
            tap_neutral=0,
            tap_step_percent=np.abs(tap_diff) * 100,
            tap_pos=np.sign(tap_diff),
        )

    def _add_loads(self) -> None:
        """Add load info to the power flow model."""
        pp.create_loads(
            self._model,
            name=self._loads["load_name"],
            buses=self._loads["bus_name"].map(self._bus_name_to_id),
            p_mw=0,
            q_mvar=0,
            in_service=True,
        )

    def _add_generators(self) -> None:
        """Add gen info to the power flow model."""
        pp.create_gens(
            self._model,
            name=self._gens["gen_name"],
            buses=self._gens["bus_name"].map(self._bus_name_to_id),
            p_mw=0,
            max_q_mvar=0,
            min_q_mvar=0,
            vm_pu=0,
            in_service=True,
        )

    def _apply_next_timestamp(self, timestamp: str) -> None:
        """Refresh regime data in accordance to datetime.

        Args:
            timestamp: Current datetime.
        """
        # Set load
        load = self._loads_ts.loc[timestamp].set_index("load_name")
        load_cols = ["in_service", "p_mw", "q_mvar"]
        self._model.load[load_cols] = (
            load.loc[self._model.load["name"], load_cols].astype(float).values
        )

        # Set gens
        gen = self._gens_ts.loc[timestamp].set_index("gen_name")
        gen_cols = ["in_service", "p_mw", "min_q_mvar", "max_q_mvar", "vm_pu"]
        self._model.gen[gen_cols] = (
            gen.loc[self._model.gen["name"], gen_cols].astype(float).values
        )

    def _save_model(self, path: str, model_name: str) -> None:
        """Save model.

        Args:
            path: Path to save the model.
            model_name: Model name.
        """
        model_path = os.path.join(path, f"{model_name}.json")
        pp.to_json(self._model, model_path)

    def _calculate_regime(self) -> bool:
        """Calculate power flows.

        Returns:
            True if the calculation was successful, False otherwise.
        """
        try:
            pp.runpp(
                self._model,
                algorithm="nr",
                calculate_voltage_angles=True,
                init="flat",
                enforce_q_lims=True,
            )
            return True
        except LoadflowNotConverged:
            return False
