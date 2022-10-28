import math
import os

import numpy as np
import pandapower as pp
from pandapower import LoadflowNotConverged, OPFNotConverged

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
        self._bus_name_to_v_rate = None
        self._slack_bus_id = None
        self._load_cols = ["in_service", "p_mw", "q_mvar"]
        self._gen_cols = [
            "in_service",
            "p_mw",
            "min_q_mvar",
            "max_q_mvar",
            "max_p_mw",
            "min_p_mw",
        ]

    def _build_model(self) -> None:
        """Create power flow model."""

        # Create empty network
        self._model = pp.create_empty_network(sn_mva=self.s_base_mva, f_hz=self.f_hz)

        # Prepare and add buses first
        self._add_buses()

        # For faster access
        self._bus_name_to_id = self._model.bus.reset_index().set_index("name")["index"]
        self._bus_name_to_v_rate = self._model.bus.set_index("name")["vn_kv"]

        # Prepare and add the rest
        self._add_lines()
        self._add_transformers()
        self._add_loads()
        self._add_generators()
        self._add_slack()

    def _add_slack(self) -> None:
        """Add slack bus info to the power flow model."""
        slack_bus = self._buses.loc[self._buses["is_slack"], "bus_name"].values[0]
        self._slack_bus_id = self._bus_name_to_id[slack_bus]
        pp.create_ext_grid(
            self._model,
            bus=self._slack_bus_id,
            name=slack_bus,
            vm_pu=1,
            va_degree=0,
            in_service=True,
            controllable=True,
        )

    def _add_buses(self) -> None:
        """Add bus info to the power flow model."""

        # Prepare
        self._buses.sort_values("bus_name", inplace=True)

        # Add buses
        pp.create_buses(
            self._model,
            nr_buses=len(self._buses),
            vn_kv=self._buses["v_rated_kv"],
            name=self._buses["bus_name"],
            zone=self._buses["region"],
            in_service=self._buses["in_service"],
            max_vm_pu=self._buses["max_vm_pu"],
            min_vm_pu=self._buses["min_vm_pu"],
            geodata=list(zip(self._buses["x_coordinate"], self._buses["y_coordinate"])),
        )

    def _add_lines(self) -> None:
        """Add line info to the power flow model."""

        # Get only lines
        lines = self._branches[self._branches["trafo_ratio_rel"].isna()]
        lines.sort_values("branch_name", inplace=True)

        # Convert bus names to indices
        lines["from_bus_id"] = lines["from_bus"].map(self._bus_name_to_id)
        lines["to_bus_id"] = lines["to_bus"].map(self._bus_name_to_id)

        # Convert to farads
        lines["c_nf"] = lines["b_µs"] * 1e3 / (2 * self.f_hz * math.pi)

        # Add lines to the model
        pp.create_lines_from_parameters(
            self._model,
            name=lines["branch_name"],
            from_buses=lines["from_bus_id"],
            to_buses=lines["to_bus_id"],
            parallel=lines["parallel"],
            r_ohm_per_km=lines["r_ohm"],
            x_ohm_per_km=lines["x_ohm"],
            c_nf_per_km=lines["c_nf"],
            max_i_ka=lines["max_i_ka"],
            in_service=lines["in_service"],
            length_km=1,
            max_loading_percent=100,
            type="ol",
        )

    def _add_transformers(self) -> None:
        """Add transformer info to the power flow model."""

        # Get only transformers
        trafos = self._branches[~self._branches["trafo_ratio_rel"].isna()]
        trafos.sort_values("branch_name", inplace=True)

        # Convert bus names to indices
        trafos["from_bus_id"] = trafos["from_bus"].map(self._bus_name_to_id)
        trafos["to_bus_id"] = trafos["to_bus"].map(self._bus_name_to_id)

        # Consider from_bus is a high voltage level bus
        vn_hv_kv = self._bus_name_to_v_rate.loc[trafos["from_bus"]].values
        vn_lv_kv = self._bus_name_to_v_rate.loc[trafos["to_bus"]].values

        # Calculate trafo parameters
        z_base_net = vn_hv_kv**2 / self.s_base_mva
        s_base_trafo_mva = trafos["max_i_ka"] * vn_hv_kv * 3**0.5
        vk_percent = (
            100 * (trafos["x_ohm"] / z_base_net) * (s_base_trafo_mva / self.s_base_mva)
        )
        vkr_percent = (
            100 * (trafos["r_ohm"] / z_base_net) * (s_base_trafo_mva / self.s_base_mva)
        )
        tap_diff = (trafos["trafo_ratio_rel"] - 1).values
        tap_step_percent = np.abs(tap_diff) * 100
        tap_pos = np.sign(tap_diff)

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
            parallel=trafos["parallel"],
            in_service=trafos["in_service"],
            tap_pos=tap_pos,
            tap_step_percent=tap_step_percent,
            tap_side="hv",
            tap_neutral=0,
            pfe_kw=0,
            i0_percent=0,
            max_loading_percent=100,
        )

    def _add_loads(self) -> None:
        """Add load info to the power flow model."""

        # Prepare load info
        self._loads["bus_id"] = self._loads["bus_name"].map(self._bus_name_to_id)
        self._loads.sort_values("load_name", inplace=True)

        # Add basic info
        # Actual parameters will be populated later for each timestamp
        pp.create_loads(
            self._model,
            name=self._loads["load_name"],
            buses=self._loads["bus_id"],
            p_mw=0,
            q_mvar=0,
            in_service=True,
            controllable=False,
        )

        # Prepare time-series
        self._loads_ts[self._load_cols] = self._loads_ts[self._load_cols].astype(float)
        self._loads_ts.sort_values(["datetime", "load_name"], inplace=True)
        self._loads_ts.set_index("datetime", inplace=True)

    def _add_generators(self) -> None:
        """Add gen info to the power flow model."""

        # Prepare gen info
        self._gens["bus_id"] = self._gens["bus_name"].map(self._bus_name_to_id)
        self._gens.sort_values("gen_name", inplace=True)

        # Add basic info
        # Actual parameters will be populated later for each timestamp
        pp.create_gens(
            self._model,
            name=self._gens["gen_name"],
            buses=self._gens["bus_id"],
            p_mw=0,
            max_q_mvar=0,
            min_q_mvar=0,
            min_p_mw=0,
            max_p_mw=0,
            vm_pu=1,
            in_service=True,
            controllable=True,
        )

        # Some modifications for faster access
        self._gens_ts.rename(
            columns={
                "q_min_mvar": "min_q_mvar",
                "q_max_mvar": "max_q_mvar",
                "max_p_opf_mw": "max_p_mw",
                "min_p_opf_mw": "min_p_mw",
            },
            inplace=True,
        )
        self._gens_ts[self._gen_cols] = self._gens_ts[self._gen_cols].astype(float)
        self._gens_ts.sort_values(["datetime", "gen_name"], inplace=True)
        self._gens_ts.set_index("datetime", inplace=True)

    def _apply_next_timestamp(self, timestamp: str) -> None:
        """Refresh regime data in accordance to datetime.

        Args:
            timestamp: Current datetime.
        """
        # Set load
        load = self._loads_ts.loc[timestamp].set_index("load_name")
        self._model.load[self._load_cols] = load.loc[
            self._model.load["name"], self._load_cols
        ].values

        # Set gens
        gen = self._gens_ts.loc[timestamp].set_index("gen_name")
        self._model.gen[self._gen_cols] = gen.loc[
            self._model.gen["name"], self._gen_cols
        ].values

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
            pp.runopp(self._model)
            self._model.gen[["p_mw", "vm_pu"]] = self._model.res_gen[
                ["p_mw", "vm_pu"]
            ].values
            self._model.ext_grid["vm_pu"] = self._model.res_bus.loc[
                self._slack_bus_id, "vm_pu"
            ]
            pp.runpp(
                self._model,
                algorithm="nr",
                calculate_voltage_angles=True,
                init="flat",
                enforce_q_lims=True,
            )
            return True
        except (LoadflowNotConverged, OPFNotConverged):
            return False
