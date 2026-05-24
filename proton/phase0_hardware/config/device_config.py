"""
Device and project configuration.

Values that are facts about the hardware live here so they are not scattered
across scripts. The sensitivity is intentionally left as None by default,
because the right thing to do is read it off the device with
get_tube_sensitivity rather than trust a hardcoded number. It is here only as
a documented fallback for offline testing.
"""

# Serial settings are fixed by the Rad Pro firmware.
BAUDRATE = 115200

# Leave as None to force reading from the device. The two documented values
# are kept here purely as reference, not as defaults to rely on.
SENSITIVITY_CPM_PER_USV_H = None
SENSITIVITY_REFERENCE = {
    "amazon_listing_co60": 80.0,
    "radpro_gc01_default": 153.8,
}

# Default poll interval for live logging, in seconds. One second matches the
# rate at which the firmware updates its own rate field, so going much faster
# mostly adds serial traffic without adding real information at background levels.
DEFAULT_POLL_INTERVAL = 1.0

# Where things get written.
DATA_RAW = "data/raw"
DATA_PROCESSED = "data/processed"
DATA_LOGS = "data/logs"
