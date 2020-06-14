"""Module for registering commands"""

# =============================================================================
# >> IMPORTS
# =============================================================================
# deepsurf
from .clientcommands import CommandHandler, Argument


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def _ping_handler(player, command):
    """Called when player uses /t command."""
    print(f"[deepsurf] player {player.name} invoked ping")
    return "[deepsurf] pong"


def register_commands():
    """Register commands"""

    CommandHandler.instance().add_command(
        name="ping",
        callback=_ping_handler,
        alias=["p"],
        description="Ping command",
        usage="/ping",
    )
