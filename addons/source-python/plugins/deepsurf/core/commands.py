"""Module for console commands."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from commands.typed import TypedSayCommand, TypedClientCommand
from players.entity import Player
from messages import SayText2


# =============================================================================
# >> FUNCTIONS
# =============================================================================

@TypedSayCommand("!setstart")
@TypedClientCommand("ds_setstart")
def _setstart_handler(command):
    player = Player(command.index)
    origin = player.get_property_vector("m_vecOrigin")
    SayText2(f"[deepsurf] TODO: setstart {origin}").send(command.index)
    print(f"[deepsurf] TODO: setstart {origin}")


@TypedSayCommand("!setend")
@TypedClientCommand("ds_setend")
def _setend_handler(command):
    player = Player(command.index)
    origin = player.get_property_vector("m_vecOrigin")
    SayText2(f"[deepsurf] TODO: setend {origin}").send(command.index)
    print(f"[deepsurf] TODO: setend {origin}")


@TypedSayCommand("!addcp")
@TypedClientCommand("ds_addcp")
def _addcp_handler(command):
    player = Player(command.index)
    origin = player.get_property_vector("m_vecOrigin")
    SayText2(f"[deepsurf] TODO: add_cp {origin}").send(command.index)
    print(f"[deepsurf] TODO: add_cp {origin}")


@TypedSayCommand("!removecp")
@TypedClientCommand("ds_removecp")
def _removecp_handler(command):
    SayText2(f"[deepsurf] TODO: remove_cp").send(command.index)
    print(f"[deepsurf] TODO: remove_cp")
