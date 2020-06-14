"""Module for drawing hud elements."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from messages import HintText

# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
buffer_white_space = "\n\n\n\n\n\n"

# =============================================================================
# >> FUNCTIONS
# =============================================================================
def draw_hud(bot):
    """Draw hud to players."""
    _draw_timer(bot.spectators)


def _draw_timer(spectators):
    """Draw timer for bot."""

    # lines for timer hud
    time_line = "00:00:00"
    zone_line = "[Map Start]"
    mode_line = "Training"
    cp_line = "(cp0: 00:00:00)"

    # combine lines
    combined = ""

    if time_line:
        combined += time_line

    if cp_line:
        combined += "\n" + cp_line + "\n"
    else:
        # NOTE:
        # HintText needs something on "empty" lines or it freaks out,
        # use space between multiple newlines
        combined += "\n \n"

    if zone_line:
        combined += f"{zone_line}\n \n"

    combined += mode_line

    hint_text = HintText(combined)

    # draw
    hint_text.send(spectators)
