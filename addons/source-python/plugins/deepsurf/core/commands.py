"""Module for console commands."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import json
import pathlib

# Source.Python
from commands.typed import TypedSayCommand, TypedClientCommand, TypedServerCommand
from engines.server import server
from mathlib import Vector
from messages import SayText2
from players.entity import Player

# deepsurf
from .zone import Segment, Zone, Checkpoint
from .bot import Bot
from .helpers import CustomEntEnum


# Helper for responding to commands
def respond(text, index):
    if index is None or index <= 0:
        print(text)
    else:
        SayText2(text).send(index)


# =============================================================================
# >> COMMANDS
# =============================================================================
@TypedSayCommand("!setstart")
@TypedClientCommand("dps_setstart")
def _setstart_handler(command):
    player = Player(command.index)
    origin = player.get_property_vector("m_vecOrigin")
    orientation = int(round(player.get_view_angle().y))
    # Create new vector to avoid reference
    Segment.instance().set_start_zone(
        Zone(Vector(origin.x, origin.y, origin.z), orientation)
    )
    respond(f"[deepsurf] Set start at ({origin})", command.index)


@TypedSayCommand("!setend")
@TypedClientCommand("dps_setend")
def _setend_handler(command):
    player = Player(command.index)
    origin = player.get_property_vector("m_vecOrigin")
    Segment.instance().set_end_zone(Zone(Vector(origin.x, origin.y, origin.z)))
    respond(f"[deepsurf] Set end at ({origin})", command.index)


@TypedSayCommand("!addcp")
@TypedClientCommand("dps_addcp")
def _addcp_handler(command):
    player = Player(command.index)
    origin = player.get_property_vector("m_vecOrigin")
    num = Segment.instance().add_checkpoint(
        Checkpoint(
            len(Segment.instance().checkpoints), Vector(origin.x, origin.y, origin.z)
        )
    )
    respond(f"[deepsurf] Added checkpoint {num} at ({origin})", command.index)


@TypedSayCommand("!removecp")
@TypedClientCommand("dps_removecp")
@TypedServerCommand("dps_removecp")
def _removecp_handler(command):
    num = Segment.instance().remove_checkpoint()
    if num > 0:
        respond(f"[deepsurf] Removed checkpoint {num}", command.index)
    else:
        respond(f"[deepsurf] No checkpoints to remove", command.index)


@TypedSayCommand("!clear")
@TypedClientCommand("dps_clear")
@TypedServerCommand("dps_clear")
def _clear_handler(command):
    Segment.instance().clear()
    respond(f"[deepsurf] Cleared segment", command.index)


@TypedSayCommand("!savecfg")
@TypedClientCommand("dps_savecfg")
@TypedServerCommand("dps_savecfg")
def _savecfg_handler(command, index: int = 0):
    data = Segment.instance().serialize()
    if data is None:
        respond(f"[deepsurf] Could not serialize segment", command.index)
        return

    # Relative to tf2 folder
    path = "./tf/resource/source-python/deepsurf/"
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    path += f"{server.map_name}_{index}.json"

    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    respond(f"[deepsurf] Saved segment to '{path}'", command.index)


@TypedSayCommand("!loadcfg")
@TypedClientCommand("dps_loadcfg")
@TypedServerCommand("dps_loadcfg")
def _loadcfg_handler(command, index: int = 0):
    path = f"./tf/resource/source-python/deepsurf/{server.map_name}_{index}.json"
    with open(path) as f:
        data = json.load(f)
        Segment.instance().deserialize(data)
    respond(f"[deepsurf] Loaded segment from '{path}'", command.index)


@TypedSayCommand("!spawn")
@TypedClientCommand("dps_spawn")
@TypedServerCommand("dps_spawn")
def _train_handler(command):
    Bot.instance().spawn()


@TypedSayCommand("!train")
@TypedClientCommand("dps_train")
@TypedServerCommand("dps_train")
def _train_handler(command):
    if Segment.instance().is_valid() is False:
        respond("[deepsurf] Invalid segment", command.index)
        return

    Bot.instance().train()


@TypedSayCommand("!run")
@TypedClientCommand("dps_run")
@TypedServerCommand("dps_run")
def _run_handler(command):
    if Segment.instance().is_valid() is False:
        respond("[deepsurf] Invalid segment", command.index)
        return

    Bot.instance().run()


@TypedSayCommand("!stop")
@TypedClientCommand("dps_stop")
@TypedServerCommand("dps_stop")
def _run_handler(command):
    Bot.instance().stop()


@TypedSayCommand("!timelimit")
@TypedClientCommand("dps_timelimit")
@TypedServerCommand("dps_timelimit")
def _run_handler(command, value: int = 10):
    Bot.instance().set_time_limit(value)
    respond(f"[deepsurf] Time limit set to {value}", command.index)


@TypedSayCommand("!place")
@TypedClientCommand("dps_place")
def _place_handler(command):
    player = Player(command.index)
    origin = player.get_property_vector("m_vecOrigin")
    orientation = player.get_view_angle()
    forward = Vector()
    orientation.get_angle_vectors(forward)

    destination = origin + forward * 10000.0
    entity_enum = CustomEntEnum(
        origin,
        destination,
        (
            Bot.instance().bot,
            player,
        ),
    )

    # Check for normal geometry
    entity_enum.normal_trace()

    if entity_enum.did_hit:
        Bot.instance().bot.snap_to_position(
            entity_enum.point,
            orientation,
        )
        respond(f"[deepsurf] Placing bot at ({entity_enum.point})", command.index)
    else:
        respond(f"[deepsurf] Did not hit a surface to place bot on", command.index)
