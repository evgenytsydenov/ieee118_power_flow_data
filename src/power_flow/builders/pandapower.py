import logging
import math
import os
import warnings

import numpy as np
import pandapower as pp
import pandas as pd
from pandapower import LoadflowNotConverged, OPFNotConverged

from src.power_flow.builders.base import BasePowerFlowBuilder

# Supress warnings
warnings.simplefilter(action="ignore", category=FutureWarning)
logging.getLogger("pandapower.opf.make_objective").setLevel(logging.ERROR)


class PandaPowerFlowBuilder(BasePowerFlowBuilder):
    """Class for creating power flow cases using PandaPower.

    Args:
        s_base_mva: Base power.
        f_hz: Power system frequency.

    Attributes:
        s_base_mva: Base power of the system.
        f_hz: System frequency.
    """

    def __init__(self, s_base_mva: float, f_hz: float) -> None:
        super().__init__()
        self.s_base_mva = s_base_mva
        self.f_hz = f_hz
        self._bus_name_to_id = None
        self._bus_name_to_v_rated = None
        self._slack_bus = None
        self._slack_bus_id = None
        self._gen_slice = None
        self._load_vars = ["in_service", "p_mw", "q_mvar"]
        self._gen_vars_model = [
            "in_service",
            "p_mw",
            "min_q_mvar",
            "max_q_mvar",
            "max_p_mw",
            "min_p_mw",
        ]
        self._gen_vars_ts = [
            "in_service",
            "p_mw",
            "min_q_mvar",
            "max_q_mvar",
            "max_opf_p_mw",
            "min_opf_p_mw",
        ]

    def _prepare_data(self) -> None:
        """Prepare data for faster access."""
        # Prepare buses
        self._buses.sort_values("bus_name", inplace=True, ignore_index=True)
        self._bus_name_to_id = pd.Series(
            data=self._buses.index.values, index=self._buses["bus_name"].values
        )
        self._bus_name_to_v_rated = pd.Series(
            data=self._buses["v_rated_kv"].values, index=self._buses["bus_name"].values
        )

        # Prepare slack bus
        self._slack_bus = self._buses.loc[self._buses["is_slack"], "bus_name"].values[0]
        self._slack_bus_id = self._bus_name_to_id[self._slack_bus]

        # Prepare branches
        self._branches.sort_values("branch_name", inplace=True, ignore_index=True)
        self._branches["from_bus_id"] = self._branches["from_bus"].map(
            self._bus_name_to_id
        )
        self._branches["to_bus_id"] = self._branches["to_bus"].map(self._bus_name_to_id)

        # Prepare loads
        self._loads.sort_values("load_name", inplace=True, ignore_index=True)
        self._loads["bus_id"] = self._loads["bus_name"].map(self._bus_name_to_id)

        # Prepare loads ts
        self._loads_ts[self._load_vars] = self._loads_ts[self._load_vars].astype(float)
        self._loads_ts.sort_values(["datetime", "load_name"], inplace=True)
        if "datetime" not in self._loads_ts.index.names:
            self._loads_ts.set_index("datetime", inplace=True)

        # Prepare gens
        self._gens["is_optimized"] = True
        mask = self._gens["opt_category"] == "non_optimized"
        self._gens.loc[mask, "is_optimized"] = False
        self._gens.sort_values("gen_name", inplace=True)
        self._gens["bus_id"] = self._gens["bus_name"].map(self._bus_name_to_id)

        # Prepare gens ts
        optimized_names = self._gens.loc[self._gens["is_optimized"], "gen_name"]
        self._gens_ts["is_optimized"] = self._gens_ts["gen_name"].isin(optimized_names)
        self._gens_ts["max_opf_p_mw"] = np.where(
            self._gens_ts["is_optimized"],
            self._gens_ts["max_p_mw"],
            self._gens_ts["p_mw"],
        )
        self._gens_ts["min_opf_p_mw"] = np.where(
            self._gens_ts["is_optimized"],
            self._gens_ts["min_p_mw"],
            self._gens_ts["p_mw"],
        )
        self._gens_ts[self._gen_vars_ts] = self._gens_ts[self._gen_vars_ts].astype(
            float
        )
        self._gens_ts.sort_values(["datetime", "gen_name"], inplace=True)
        if "datetime" not in self._gens_ts.index.names:
            self._gens_ts.set_index("datetime", inplace=True)

    def _build_base_model(self) -> pp.pandapowerNet:
        """Create power flow model.

        Returns:
            Model with predefined parameters.
        """
        # Create empty network
        model = pp.create_empty_network(
            sn_mva=self.s_base_mva, f_hz=self.f_hz, add_stdtypes=False
        )

        # Add tables
        self._add_buses(model)
        self._add_lines(model)
        self._add_transformers(model)
        self._add_loads(model)
        self._add_generators(model)
        self._add_slack(model)
        return model

    def _add_slack(self, model: pp.pandapowerNet) -> None:
        """Add slack bus info to the power flow model.

        Args:
            model: Power system model.
        """
        pp.create_ext_grid(
            net=model,
            bus=self._slack_bus_id,
            name=self._slack_bus,
            vm_pu=1,
            va_degree=0,
            in_service=True,
            controllable=True,
        )

    def _add_buses(self, model: pp.pandapowerNet) -> None:
        """Add bus info to the power flow model.

        Args:
            model: Power system model.
        """
        pp.create_buses(
            net=model,
            nr_buses=len(self._buses),
            index=self._buses.index,
            vn_kv=self._buses["v_rated_kv"],
            name=self._buses["bus_name"],
            zone=self._buses["region"],
            in_service=self._buses["in_service"],
            max_vm_pu=self._buses["max_v_pu"],
            min_vm_pu=self._buses["min_v_pu"],
            geodata=list(zip(self._buses["x_coordinate"], self._buses["y_coordinate"])),
        )

    def _add_lines(self, model: pp.pandapowerNet) -> None:
        """Add line info to the power flow model.

        Args:
            model: Power system model.
        """
        # Get only lines
        lines = self._branches[self._branches["trafo_ratio_rel"].isna()]

        # Convert to farads
        lines["c_nf"] = lines["b_µs"] * 1e3 / (2 * self.f_hz * math.pi)

        # Add lines to the model
        pp.create_lines_from_parameters(
            net=model,
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

    def _add_transformers(self, model: pp.pandapowerNet) -> None:
        """Add transformer info to the power flow model.

        Args:
            model: Power system model.
        """

        # Get only transformers
        trafos = self._branches[~self._branches["trafo_ratio_rel"].isna()]

        # Consider from_bus is a high voltage level bus
        vn_hv_kv = self._bus_name_to_v_rated.loc[trafos["from_bus"]].values
        vn_lv_kv = self._bus_name_to_v_rated.loc[trafos["to_bus"]].values

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
            net=model,
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

    def _add_loads(self, model: pp.pandapowerNet) -> None:
        """Add load info to the power flow model.

        Args:
            model: Power system model.
        """
        # Actual parameters will be populated later for each timestamp
        pp.create_loads(
            net=model,
            name=self._loads["load_name"],
            buses=self._loads["bus_id"],
            p_mw=0,
            q_mvar=0,
            in_service=True,
            controllable=False,
        )

    def _add_generators(self, model: pp.pandapowerNet) -> None:
        """Add gen info to the power flow model.

        Args:
            model: Power system model.
        """
        # Actual parameters will be populated later for each timestamp
        pp.create_gens(
            net=model,
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

    def _apply_next_timestamp(self, model: pp.pandapowerNet, timestamp: str) -> None:
        """Refresh data in accordance to the timestamp.

        Prepare the model for OPF.

        Args:
            model: Power system model.
            timestamp: Current datetime.
        """
        # Assume that load_ts is sorted by datetime and load_name
        model.load[self._load_vars] = self._loads_ts.loc[
            timestamp, self._load_vars
        ].values

        # Assume that gen_ts_prep is sorted by datetime and gen_name
        self._gen_slice = self._gens_ts.loc[timestamp]
        model.gen[self._gen_vars_model] = self._gen_slice[self._gen_vars_ts].values

        # Need to refresh values after the previous run
        model.gen["controllable"] = True
        model.gen["vm_pu"] = 1.0
        model.ext_grid["vm_pu"] = 1.0

    def _save_sample(
        self, model: pp.pandapowerNet, path: str, sample_name: str
    ) -> None:
        """Save sample.

        Args:
            model: Power system model.
            path: Path to save the sample.
            sample_name: Sample name.
        """
        sample_path = os.path.join(path, f"{sample_name}.json")
        pp.to_json(model, sample_path)

    def _calculate_opf(self, model: pp.pandapowerNet) -> bool:
        """Solve optimal power flow task.

        Args:
            model: Power system model.

        Returns:
            True if the calculation was successful, False otherwise.
        """
        try:
            # Run OPF
            pp.runopp(model, init="flat")

            # Add optimized values to the model
            model.gen[["p_mw", "vm_pu"]] = model.res_gen[["p_mw", "vm_pu"]].values
            model.ext_grid["vm_pu"] = model.res_bus.loc[self._slack_bus_id, "vm_pu"]
        except OPFNotConverged:
            pp.clear_result_tables(model)
            return False

        finally:

            # Restore original limits of gen outputs and controllable flag
            model.gen[["min_p_mw", "max_p_mw"]] = self._gen_slice[
                ["min_p_mw", "max_p_mw"]
            ].values
            model.gen["controllable"] = self._gens["is_optimized"].values

        return True

    def _calculate_power_flow(self, model: pp.pandapowerNet) -> bool:
        """Calculate power flows.

        Args:
            model: Power system model.

        Returns:
            True if the calculation was successful, False otherwise.
        """
        try:
            pp.runpp(
                net=model,
                algorithm="nr",
                calculate_voltage_angles=True,
                init="flat",
                enforce_q_lims=True,
            )
        except LoadflowNotConverged:
            pp.clear_result_tables(model)
            return False
        return True
