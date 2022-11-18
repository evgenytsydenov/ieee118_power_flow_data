# Base power
S_BASE_MVA = 100

# Frequency
F_HZ = 60

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

# Which engine to use for building power flow cases
POWER_FLOW_ENGINE = "pandapower"

# Format of names for each power flow case
# Power flow cases built for each timestamp should have unique names
# Each name can contain timestamp parameters
# The extension will be added automatically
SAMPLE_NAME_FORMAT = "%Y_%m_%d_%H_%M_%S"

# Logging parameters
LOG_FORMAT_DEBUG = "%(asctime)s | %(name)s | %(funcName)s | %(levelname)s | %(message)s"
LOG_FORMAT_INFO = "%(asctime)s | %(levelname)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S %Z"
LOG_PATH = "logs/system.log"

# Number of workers to use for building of power flow cases
WORKERS_COUNT = -1
