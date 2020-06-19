"""Module for bot functionality"""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from engines.server import engine_server
from players.entity import Player
from players.bots import bot_manager, BotCmd
from entities.helpers import index_from_edict
from mathlib import Vector, NULL_VECTOR, QAngle, NULL_QANGLE

# deepsurf
from .hud import draw_hud


# =============================================================================
# >> CLASSES
# =============================================================================
class Bot:
    """A controllable bot class"""

    def __init__(self, name):
        """Create a new bot"""
        self.name = name
        self.bot = None
        self.controller = None
        self.start_zone = None
        self.end_zone = None
        self.checkpoints = None

    def set_segment(self, segment):
        self.start_zone = segment.start_zone
        self.end_zone = segment.end_zone
        self.checkpoints = segment.checkpoints

    def spawn(self):
        if self.bot is not None or self.controller is not None:
            raise ValueError("Bot already exists")

        bot_edict = bot_manager.create_bot(self.name)
        if bot_edict is None:
            raise ValueError("Failed to create a bot.")

        self.controller = bot_manager.get_bot_controller(bot_edict)
        if self.controller is None:
            raise ValueError("Failed to get the bot controller.")

        self.bot = Player(index_from_edict(bot_edict))
        self.bot.set_noblock(True)
        self.bot.team = 2
        self.bot.set_property_uchar("m_PlayerClass.m_iClass", 7)
        self.bot.set_property_uchar("m_Shared.m_iDesiredPlayerClass", 7)
        self.bot.spawn(force=True)

    def reset(self):
        if self.bot is None:
            return
        if self.start_zone is None:
            raise ValueError("No start zone")
        self.bot.teleport(self.start_zone.point, NULL_QANGLE, NULL_VECTOR)
        self.bot.set_view_angle(QAngle(0, self.start_zone.orientation, 0))

    def kick(self, reason):
        if self.bot is not None:
            self.bot.kick(reason)
            self.bot = None
            self.controller = None

    def tick(self):
        if self.bot is None or self.controller is None:
            return

        (move_input, aim_input) = self.get_action()
        bcmd = self.get_cmd(move_input, aim_input)
        self.controller.run_player_move(bcmd)

        draw_hud(self.bot)

    def get_cmd(self, move_input=0, aim_input=0):
        """Get BotCmd for move direction and aim delta"""

        bcmd = BotCmd()
        bcmd.reset()
        view_angles = self.bot.view_angle

        if aim_input != 0:
            view_angles.y -= aim_input

        bcmd.view_angles = view_angles

        if move_input != 0:
            # Map move direction to forward + side axis
            move_speed = 400
            move_options = {
                1: {"forward_move": move_speed, "side_move": 0},
                2: {"forward_move": move_speed, "side_move": move_speed},
                3: {"forward_move": 0, "side_move": move_speed},
                4: {"forward_move": -move_speed, "side_move": move_speed},
                5: {"forward_move": -move_speed, "side_move": 0},
                6: {"forward_move": -move_speed, "side_move": -move_speed},
                7: {"forward_move": 0, "side_move": -move_speed},
                8: {"forward_move": move_speed, "side_move": -move_speed},
            }
            move = move_options[move_input]
            bcmd.forward_move = move["forward_move"]
            bcmd.side_move = move["side_move"]

        return bcmd

    def get_action(self):
        # TODO: get action from NN here
        move_input = 0
        aim_input = 0
        return (move_input, aim_input)
