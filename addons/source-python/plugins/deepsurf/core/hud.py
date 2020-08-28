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
def draw_hud(bot, training, reward):
    """Draw hud to players."""
    _draw_timer(bot.spectators, training, reward)


def _draw_timer(spectators, training, reward):
    """Draw timer for bot."""

    # lines for timer hud
    time_line = "00:00:00"
    reward_line = f"Total reward: {round(reward, 2)}"

    # combine lines
    combined = time_line + "\n"

    if training is True:
        combined += "Training\n"
        combined += reward_line
    else:
        combined += "Running"

    hint_text = HintText(combined)

    # draw
    hint_text.send(spectators)
