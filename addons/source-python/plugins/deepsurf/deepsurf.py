"""Main module for deepsurf plugin."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from engines.server import server, queue_command_string
from events import Event
from listeners import OnTick

# deepsurf
from .core.zone import Segment
from .core import commands
from .core.bot import Bot


# =============================================================================
# >> LISTENERS
# =============================================================================
def load():
    """Called when Source.Python loads the plugin."""
    queue_command_string("exec surf")
    queue_command_string("sv_hudhint_sound 0; sv_cheats 1; tf_allow_server_hibernation 0; mp_respawnwavetime 0")
    print(f"[deepsurf] Loaded!")


def unload():
    """Called when Source.Python unloads the plugin."""
    Bot.instance().kick("Plugin unloading")
    print(f"[deepsurf] Unloaded!")


@Event("player_spawn")
def on_player_spawn(game_event):
    queue_command_string("mp_waitingforplayers_cancel 1")
    if game_event.userid == Bot.instance().bot.index:
        Bot.instance().reset()


@OnTick
def on_tick():
    Bot.instance().tick()
    # draw zones every second
    if server.tick % 67 == 0:
        Segment.instance().draw()
