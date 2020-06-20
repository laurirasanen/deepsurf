"""Module for console commands."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import json
import pathlib

# Source.Python
from commands.typed import TypedSayCommand, TypedClientCommand
from engines.server import server
from mathlib import Vector
from messages import SayText2
from players.entity import Player

# deepsurf
from .zone import Segment, Zone
from .bot import Bot


# =============================================================================
# >> COMMANDS
# =============================================================================
@TypedSayCommand("!setstart")
@TypedClientCommand("ds_setstart")
def _setstart_handler(command):
    player = Player(command.index)
    origin = player.get_property_vector("m_vecOrigin")
    orientation = int(round(player.get_view_angle().y))
    # Create new vector to avoid reference
    Segment.instance().set_start_zone(Zone(Vector(origin.x, origin.y, origin.z), orientation))
    SayText2(f"[deepsurf] Set start at ({origin})").send(command.index)


@TypedSayCommand("!setend")
@TypedClientCommand("ds_setend")
def _setend_handler(command):
    player = Player(command.index)
    origin = player.get_property_vector("m_vecOrigin")
    Segment.instance().set_end_zone(Zone(Vector(origin.x, origin.y, origin.z)))
    SayText2(f"[deepsurf] Set end at ({origin})").send(command.index)


@TypedSayCommand("!addcp")
@TypedClientCommand("ds_addcp")
def _addcp_handler(command):
    player = Player(command.index)
    origin = player.get_property_vector("m_vecOrigin")
    index = Segment.instance().add_checkpoint(Zone(Vector(origin.x, origin.y, origin.z)))
    SayText2(f"[deepsurf] Added checkpoint {index} at ({origin})").send(command.index)


@TypedSayCommand("!removecp")
@TypedClientCommand("ds_removecp")
def _removecp_handler(command):
    index = Segment.instance().remove_checkpoint()
    if index > 0:
        SayText2(f"[deepsurf] Removed checkpoint {index}").send(command.index)
    else:
        SayText2(f"[deepsurf] No checkpoints to remove").send(command.index)


@TypedSayCommand("!clear")
@TypedClientCommand("ds_clear")
def _clear_handler(command):
    Segment.instance().clear()
    SayText2(f"[deepsurf] Cleared segment").send(command.index)


@TypedSayCommand("!savecfg")
@TypedClientCommand("ds_savecfg")
def _savecfg_handler(command, index: int = 0):
    data = Segment.instance().serialize()
    if data is None:
        SayText2(f"[deepsurf] Could not serialize segment").send(command.index)
        return

    # Relative to tf2 folder
    path = "./tf/resource/source-python/deepsurf/"
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    path += f"{server.map_name}_{index}.json"

    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    SayText2(
        f"[deepsurf] Saved segment to '{path}'").send(
        command.index)


@TypedSayCommand("!loadcfg")
@TypedClientCommand("ds_loadcfg")
def _loadcfg_handler(command, index: int = 0):
    path = f"./tf/resource/source-python/deepsurf/{server.map_name}_{index}.json"
    with open(path) as f:
        data = json.load(f)
        Segment.instance().deserialize(data)
    SayText2(
        f"[deepsurf] Loaded segment from '{path}'").send(
        command.index)


@TypedSayCommand("!spawn")
@TypedClientCommand("ds_spawn")
def _train_handler(command):
    Bot.instance().spawn()


@TypedSayCommand("!train")
@TypedClientCommand("ds_train")
def _train_handler(command):
    if Segment.instance().is_valid() is False:
        SayText2("[deepsurf] Invalid segment").send(command.index)
        return

    Bot.instance().train()


@TypedSayCommand("!run")
@TypedClientCommand("ds_run")
def _run_handler(command):
    if Segment.instance().is_valid() is False:
        SayText2("[deepsurf] Invalid segment").send(command.index)
        return

    Bot.instance().run()


@TypedSayCommand("!stop")
@TypedClientCommand("ds_stop")
def _run_handler(command):
    Bot.instance().stop()
