"""Main module for deepsurf plugin."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from cvars import ConVar
from engines.server import server, execute_server_command, queue_command_string
from events import Event
from listeners import OnTick
from mathlib import Vector
from messages.hooks import HookUserMessage
from players.entity import Player

# deepsurf
from .core.zone import Segment, Zone
from .core.commands import register_commands, CommandHandler
from .core.bot import Bot
from .core.config import apply_cvars

# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
bot = Bot("DeepSurf")
segment = Segment()

# =============================================================================
# >> LISTENERS
# =============================================================================
def load():
    """Called when Source.Python loads the plugin."""
    register_commands()
    queue_command_string("exec surf")
    apply_cvars()

    # surf_beginner stage 1
    segment.add_start_zone(Zone(Vector(-128.0, 170.0, 320.0), 90.0))
    segment.add_end_zone(Zone(Vector(-127.0, 1891.0, -380.0)))

    bot.set_segment(segment)
    bot.spawn()
    print(f"[deepsurf] Loaded!")


def unload():
    """Called when Source.Python unloads the plugin."""
    bot.kick("Plugin unloading")
    print(f"[deepsurf] Unloaded!")


@Event("player_spawn")
def on_player_spawn(game_event):
    queue_command_string("mp_waitingforplayers_cancel 1")
    bot.reset()


@OnTick
def on_tick():
    bot.tick()
    # draw zones every second
    if server.tick % 67 == 0:
        if segment is not None:
            segment.draw()


@HookUserMessage("SayText2")
def saytext2_hook(recipient, data):
    """Hook SayText2 for commands."""
    # TODO: register console commands instead of parsing chat

    # Server
    if data["index"] == 0:
        return

    receiving_player_index = list(recipient)[0]
    sending_player_index = data["index"]

    # Handle commands
    if (
        receiving_player_index
        and sending_player_index
        and receiving_player_index == sending_player_index
        and len(data["param2"]) > 1
        and data["param2"][0] in CommandHandler.instance().prefix
    ):
        recipient.update([])
        command_response = CommandHandler.instance().check_command(
            data["param2"][1:], Player(sending_player_index)
        )
        if command_response:
            data["message"] = command_response
            data["index"] = 0
            recipient.update([sending_player_index])
