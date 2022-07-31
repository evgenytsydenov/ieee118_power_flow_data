# Project Convention

## Naming

### Buses

- "name" --- bus name in form "bus_{number}"
- "region" --- name of region where the bus is located
- "in_service" --- if the bus is in service (not in maintenance)
- "v_rated__kv" --- rated voltage of the bus in kilovolts

### Branches

- "name" --- branch name in form "branch_{number}"
- "from_bus" --- bus name where the branch starts
- "to_bus" --- bus name where the branch ends
- "parallel" --- number of the branch in parallel branches
- "in_service" --- if the branch is in service (not in maintenance)
- "r__ohm" --- branch resistance in ohms
- "x__ohm" --- branch reactance in ohms
- "b__µs" --- branch active conductance in microsiemens
- "trafo_ratio" --- transformation ratio if the branch is a transformer
- "max_i__ka" --- maximum current over the branch in kiloamperes
