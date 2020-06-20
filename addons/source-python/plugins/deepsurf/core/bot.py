"""Module for bot functionality"""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import math

# Source.Python
from engines.trace import engine_trace
from engines.trace import ContentMasks
from engines.trace import GameTrace
from engines.trace import Ray
from engines.trace import TraceFilterSimple
from entities.helpers import index_from_edict
from mathlib import Vector, NULL_VECTOR, QAngle, NULL_QANGLE
from players.bots import bot_manager, BotCmd
from players.entity import Player

# deepsurf
from .hud import draw_hud
from .zone import Segment


# =============================================================================
# >> CLASSES
# =============================================================================
class Bot:
    """A controllable bot class"""

    __instance = None

    @staticmethod
    def instance():
        """Singleton instance"""
        if Bot.__instance is None:
            Bot()
        return Bot.__instance

    def __init__(self):
        """Create a new bot"""
        if Bot.__instance is not None:
            raise Exception("This class is a singleton, use .instance() access method.")

        self.bot = None
        self.controller = None
        self.training = False
        self.running = False
        Bot.__instance = self

    def spawn(self):
        if self.bot is not None or self.controller is not None:
            return

        bot_edict = bot_manager.create_bot("DeepSurf")
        if bot_edict is None:
            raise ValueError("Failed to create a bot")

        self.controller = bot_manager.get_bot_controller(bot_edict)
        if self.controller is None:
            raise ValueError("Failed to get bot controller")

        self.bot = Player(index_from_edict(bot_edict))
        self.bot.set_noblock(True)
        self.bot.team = 2
        self.bot.set_property_uchar("m_PlayerClass.m_iClass", 7)
        self.bot.set_property_uchar("m_Shared.m_iDesiredPlayerClass", 7)
        self.bot.spawn(force=True)

    def reset(self):
        if self.bot is None:
            return

        if Segment.instance().start_zone is None:
            print("[deepsurf] No start zone")
            return

        self.bot.teleport(Segment.instance().start_zone.point, NULL_QANGLE, NULL_VECTOR)
        self.bot.set_view_angle(QAngle(0, Segment.instance().start_zone.orientation, 0))

    def kick(self, reason):
        if self.bot is not None:
            self.bot.kick(reason)
            self.bot = None
            self.controller = None

    def train(self):
        self.running = False
        self.training = True
        self.reset()

    def run(self):
        self.training = False
        self.running = True
        self.reset()

    def stop(self):
        self.training = False
        self.running = False
        self.reset()

    def tick(self):
        if self.bot is None or self.controller is None:
            return

        if self.training is False and self.running is False:
            return

        point_cloud = self.get_point_cloud()
        velocity = self.bot.get_property_vector("m_vecVelocity")
        (move_action, aim_action) = self.get_action(point_cloud, velocity)
        bcmd = self.get_cmd(move_action, aim_action)
        self.controller.run_player_move(bcmd)

        draw_hud(self.bot)

    def get_cmd(self, move_action=0, aim_action=0):
        """Get BotCmd for move direction and aim delta"""

        bcmd = BotCmd()
        bcmd.reset()
        view_angles = self.bot.view_angle

        if aim_action != 0:
            view_angles.y -= aim_action

        bcmd.view_angles = view_angles

        if move_action != 0:
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
            move = move_options[move_action]
            bcmd.forward_move = move["forward_move"]
            bcmd.side_move = move["side_move"]

        return bcmd

    def get_action(self, point_cloud, velocity):
        # TODO: get action from NN here
        print(f"[deepsurf] velocity {velocity}")
        print(f"[deepsurf] p0 distance {point_cloud[0]['distance']}")
        move_action = 0
        aim_action = 0
        return (move_action, aim_action)

    def get_point_cloud(self):
        points = []

        # TODO: figure out better way to get directions
        directions = [
            Vector(0.0, 1.0, 0.0),  # F
            Vector(1.0, 1.0, 0.0),  # FR
            Vector(1.0, 0.0, 0.0),  # R
            Vector(1.0, -1.0, 0.0),  # BR
            Vector(0.0, -1.0, 0.0),  # B
            Vector(-1.0, -1.0, 0.0),  # BL
            Vector(-1.0, 0.0, 0.0),  # L
            Vector(-1.0, 1.0, 0.0),  # FL
        ]
        # Transform to local space of bot, where
        # y = forward
        # x = right
        # z = up
        orientation = -self.bot.view_angle.y
        for direction in directions:
            x = direction.x * math.cos(orientation) - direction.y * math.sin(orientation)
            y = direction.x * math.sin(orientation) + direction.y * math.cos(orientation)
            direction.x = x
            direction.y = y

        down_and_up = []
        for direction in directions:
            down_and_up.append(direction + Vector(0.0, 0.0, -1.0))
        down_and_up.append(Vector(0.0, 0.0, -1.0))
        for direction in directions:
            down_and_up.append(direction + Vector(0.0, 0.0, 1.0))
        down_and_up.append(Vector(0.0, 0.0, 1.0))
        directions.extend(down_and_up)

        for direction in directions:
            point = self.get_single_point(Vector.normalized(direction), 10000.0)
            points.append(point)

        return points

    def get_single_point(self, direction: Vector, distance: float):
        point = {
            "distance": distance,
            "teleport": False
        }

        destination = self.bot.origin + direction * distance
        trace = GameTrace()

        engine_trace.trace_ray(
            Ray(self.bot.origin, destination),
            ContentMasks.PLAYER_SOLID,  # TODO: PLAYER_SOLID probably doesn't include teleport triggers
            # Ignore bot
            TraceFilterSimple((self.bot,)),
            trace
        )

        if trace.did_hit():
            point["distance"] = Vector.get_distance(self.bot.origin, trace.end_position)
            # TODO: check if teleport trigger

        return point
