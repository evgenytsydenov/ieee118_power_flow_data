# Project Convention

## Naming

### Buses

- "bus_name" --- bus name in form "bus__{number}"
- "region" --- name of region where the bus is located
- "in_service" --- if the bus is in service (not in maintenance)
- "v_rated__kv" --- rated voltage of the bus in kilovolts

### Branches

- "branch_name" --- branch name in form "branch__{number}" or "trafo__{number}"
- "from_bus" --- name of the bus where the branch starts
- "to_bus" --- name of the bus where the branch ends
- "parallel" --- number of the branch in parallel branches
- "in_service" --- if the branch is in service (not in maintenance)
- "r__ohm" --- branch resistance in ohms
- "x__ohm" --- branch reactance in ohms
- "b__µs" --- branch active conductance in microsiemens
- "trafo_ratio" --- transformation ratio if the branch is a transformer
- "max_i__ka" --- maximum current over the branch in kiloamperes

### Loads

- "load_name" --- load name in form "load__{number}"
- "bus_name" --- name of the bus where the load is placed
- "in_service" --- if the load is in service
- "p__mw" --- active demand of the load in megawatts
- "q__mvar" --- reactive demand of the load in megavolt-amperes
- "datetime" --- date and time of variable measurement

### Generators

- "gen_name" --- generator name in form "{gen_type}__{number}"
- "bus_name" --- name of the bus where the generator is placed
- "q_max__mvar" --- max limit of reactive output in megavolt-amperes
- "q_min__mvar" --- min limit of reactive output in megavolt-amperes
- "v_set__kv" --- set voltage of the generator in kilovolts
- "in_service" --- if the generator is in service (not in maintenance)
- "p__mw" --- active output of the generator in megawatts
- "datetime" --- date and time of variable measurement
