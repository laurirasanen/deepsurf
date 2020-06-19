"""Module for conversions."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import math

# Source.Python
from engines.server import server


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def ticks_to_timestamp(ticks):
    """Convert ticks to a timestamp."""
    ticks = abs(ticks)

    milliseconds, seconds = math.modf(ticks * server.tick_interval)
    minutes = math.floor(seconds / 60)
    hours = math.floor(minutes / 60)

    seconds -= minutes * 60
    minutes -= hours * 60

    timestamp = ""

    if 0 < hours < 10:
        timestamp += f"0{hours}:"
    elif hours >= 10:
        timestamp += f"{hours}:"

    if minutes == 0 or 0 < minutes < 10:
        timestamp += f"0{minutes}:"
    elif minutes >= 10:
        timestamp += f"{minutes}:"

    if seconds == 0 or 0 < seconds < 10:
        timestamp += f"0{str(seconds)[0]}."
    elif seconds >= 10:
        timestamp += f"{str(seconds)[:2]}."

    if milliseconds == 0:
        timestamp += f"00"
    elif milliseconds > 0:
        timestamp += str(milliseconds)[2:4]

    return timestamp
