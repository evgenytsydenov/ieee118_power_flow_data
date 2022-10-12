# Base power
S_BASE_MVA = 100

# Frequency
F_HZ = 50

# Unify generation types
GEN_TYPES = {
    "Biomass": "biomass",
    "Hydro": "hydro",
    "Solar": "solar",
    "Wind": "wind",
    "CC NG": "combined_cycle_gas",
    "CT NG": "combustion_gas",
    "CT Oil": "combustion_oil",
    "Geo": "geothermal",
    "ICE NG": "internal_combustion_gas",
    "ST Coal": "steam_coal",
    "ST NG": "steam_gas",
    "ST Other": "steam_other",
}

# Date format used in data
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Date range to extract from time-series data
# The format: (<start_date>, <end_date>, <frequency>)
# Start date must not be less than "2024-01-01 00:00:00"
# End date is not included and must not be grater than "2025-01-01 00:00:00"
# Date format should be "%Y-%m-%d %H:%M:%S"
DATE_RANGE = ("2024-01-01 00:00:00", "2025-01-01 00:00:00", "1h")

# How to fill NaNs if info for timestamp is not provided
# "pad" --- propagate last valid observation forward to next valid
FILL_METHOD = "pad"

# If to group generators by bus to represent as a power plant
PLANT_MODE = True

# Which engin to use for power regime sampling
REGIME_SAMPLER = "pandapower"

# Format of model names
# Power flow cases built for each timestamp should have unique names
# Each name can contain timestamp parameters
# The extension will be added automatically
MODEL_NAME_FORMAT = "%Y_%m_%d_%H_%M_%S"
