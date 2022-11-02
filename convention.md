# Project Convention

## Naming

### Buses

- "bus_name" --- bus name in form "bus_<number>"
- "region" --- name of region where the bus is located
- "in_service" --- if the bus is in service (not in maintenance)
- "v_rated_kv" --- rated voltage of the bus in kilovolts
- "x_coordinate" --- x-coordinate of the bus
- "y_coordinate" --- y-coordinate of the bus
- "is_slack" --- whether the bus is a slack bus
- "max_v_pu" --- rated max limit of bus voltage in per units
- "min_v_pu" --- rated min limit of bus voltage in per units

### Branches

- "branch_name" --- branch name in form "branch_<from_bus number>_<to_bus number>_<parallel>"
- "from_bus" --- name of the bus where the branch starts
- "to_bus" --- name of the bus where the branch ends
- "parallel" --- number of the branch in parallel branches
- "in_service" --- if the branch is in service (not in maintenance)
- "r_ohm" --- branch resistance in ohms
- "x_ohm" --- branch reactance in ohms
- "b_µs" --- branch reactive conductance in microsiemens
- "trafo_ratio_rel" --- transformation ratio (relative to the ratio of voltage levels of the high and low sides) if the branch is a transformer
- "max_i_ka" --- maximum current over the branch in kiloamperes

### Loads

- "load_name" --- load name in form "load_<bus number>"
- "bus_name" --- name of the bus where the load is placed
- "in_service" --- if the load is in service
- "p_mw" --- actual active demand of the load in megawatts
- "q_mvar" --- actual reactive demand of the load in megavolt-amperes
- "datetime" --- date and time of variable measurement

### Generators

- "gen_name" --- generator name in form "<gen_type>_<number>" or "plant_<bus number>"
- "bus_name" --- name of the bus where the generator is placed
- "in_service" --- if the generator is in service (not in maintenance)
- "p_mw" --- actual active output of the generator in megawatts
- "max_q_mvar" --- actual max limit of reactive output in megavolt-amperes according to PQ-diagram
- "min_q_mvar" --- actual min limit of reactive output in megavolt-amperes according to PQ-diagram
- "max_p_mw" --- rated max active output in megawatts
- "min_p_mw" --- rated min active output in megawatts
- "datetime" --- date and time of variable measurement
- "max_p_opf_mw" --- actual max limit of active output in megawatts used for optimisation
- "min_p_opf_mw" --- actual min limit of active output in megawatts used for optimisation
