"""Main module for deepsurf plugin."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from engines.server import server, queue_command_string
from events import Event
from listeners import OnTick
from cvars import cvar
from players.entity import Player

# deepsurf
from .core.zone import Segment
from .core import commands
from .core.bot import Bot


# =============================================================================
# >> LISTENERS
# =============================================================================
def load():
    """Called when Source.Python loads the plugin."""
    queue_command_string(
        "sv_hudhint_sound 0; sv_cheats 1; tf_allow_server_hibernation 0; mp_respawnwavetime 0; sv_timeout 300"
    )
    cvar.find_var("sv_airaccelerate").set_float(150)
    cvar.find_var("sv_accelerate").set_float(10)
    print(f"[deepsurf] Loaded!")


def unload():
    """Called when Source.Python unloads the plugin."""
    Bot.instance().kick("Plugin unloading")
    print(f"[deepsurf] Unloaded!")


@Event("player_spawn")
def on_player_spawn(game_event):
    queue_command_string("mp_waitingforplayers_cancel 1")
    player = Player.from_userid(game_event["userid"])
    if Bot.instance().bot and Bot.instance().bot.index == player.index:
        Bot.instance().on_spawn()


@OnTick
def on_tick():
    Bot.instance().tick()
    # draw zones every second
    if server.tick % 67 == 0:
        Segment.instance().draw()
