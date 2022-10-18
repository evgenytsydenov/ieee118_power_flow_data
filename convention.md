# Project Convention

## Naming

### Buses

- "bus_name" --- bus name in form "bus_<number>"
- "region" --- name of region where the bus is located
- "in_service" --- if the bus is in service (not in maintenance)
- "v_rated_kv" --- rated voltage of the bus in kilovolts

### Branches

- "branch_name" --- branch name in form "branch_<number>" or "trafo_<number>"
- "from_bus" --- name of the bus where the branch starts
- "to_bus" --- name of the bus where the branch ends
- "parallel" --- number of the branch in parallel branches
- "in_service" --- if the branch is in service (not in maintenance)
- "r_ohm" --- branch resistance in ohms
- "x_ohm" --- branch reactance in ohms
- "b_µs" --- branch active conductance in microsiemens
- "trafo_ratio_rel" --- transformation ratio (relative to the ratio of voltage levels of the high and low sides) if the branch is a transformer
- "max_i_ka" --- maximum current over the branch in kiloamperes

### Loads

- "load_name" --- load name in form "load_<number>"
- "bus_name" --- name of the bus where the load is placed
- "in_service" --- if the load is in service
- "p_mw" --- active demand of the load in megawatts
- "q_mvar" --- reactive demand of the load in megavolt-amperes
- "datetime" --- date and time of variable measurement

### Generators

- "gen_name" --- generator name in form "<gen_type>_<number>"
- "bus_name" --- name of the bus where the generator is placed
- "q_max_mvar" --- max limit of reactive output in megavolt-amperes
- "q_min_mvar" --- min limit of reactive output in megavolt-amperes
- "v_set_kv" --- set voltage of the generator in kilovolts
- "in_service" --- if the generator is in service (not in maintenance)
- "p_mw" --- active output of the generator in megawatts
- "datetime" --- date and time of variable measurement
- "max_p_mw" --- max active output in megawatts

## Assumptions

1. Buses are always in service (see [here](src/data/prepare_buses.py)).
2. Branches are always in service (see [here](src/data/prepare_branches.py)).
3. Loads are always in service (see [here](src/data/prepare_loads_ts.py)).
4. Missing outputs of power plants are set to zero (see [here](src/data/transform_gens_ts.py)).
5. Range of reactive generator output set from -0.35 to 0.75 of the actual active output (see [here](src/data/transform_gens_ts.py)).
6. Rated voltage of generators are equal to bus voltages (see [here](src/data/transform_gens_ts.py)).
7. Missing power plants in the outage data are always in service (see [here](src/data/transform_outages_ts.py)).
8. When grouping generators into power plants, rated voltage is calculated as an average of generator voltages (see [here](src/data/prepare_plants_ts.py)).
