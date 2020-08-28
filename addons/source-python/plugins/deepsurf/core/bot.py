"""Module for bot functionality"""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import math

# Source.Python
from effects import beam
from engines.precache import Model
from engines.trace import engine_trace
from engines.server import server
from entities.helpers import index_from_edict
from filters.recipients import RecipientFilter
from mathlib import Vector, NULL_VECTOR, QAngle, NULL_QANGLE
from players.bots import bot_manager, BotCmd
from players.entity import Player

# deepsurf
from .helpers import CustomEntEnum
from .helpers import get_fitness
from .hud import draw_hud
from .zone import Segment

# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
debug = True
beam_model = Model('sprites/laserbeam.vmt')
point_directions = []
# the actual number of directions will be
# x - sqrt(x) + 2, e.g. 100 -> 92
# because we only need 1 for both directly up and down
num_directions = int(round(math.sqrt(100)))
increment = 360.0 / num_directions
theta = 0.0
phi = 0.0

for i in range(0, num_directions + 1):  # theta in range [0.0 : 180.0]
    for j in range(0, num_directions):  # phi in range [0.0 : 360.0 - increment]
        x = math.sin(math.radians(theta)) * math.cos(math.radians(phi))
        y = math.sin(math.radians(theta)) * math.sin(math.radians(phi))
        z = math.cos(math.radians(theta))
        point_directions.append(Vector(x, y, z))

        # only need one direction at north and south poles
        if i == 0 or i == num_directions:
            break

        phi += increment

    theta += increment * 0.5  # theta only changes by 180
    phi = 0.0


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
        self.drawn_directions = 32
        self.time_limit = 10.0
        self.start_time = 0.0
        Bot.__instance = self

    def spawn(self):
        if self.bot is not None or self.controller is not None:
            return

        bot_edict = bot_manager.create_bot("Botty McBotface")
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

        bcmd = self.get_cmd(0, 0)
        self.controller.run_player_move(bcmd)

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
        self.start_time = server.time

    def run(self):
        self.training = False
        self.running = True
        self.reset()
        self.start_time = server.time

    def stop(self):
        self.training = False
        self.running = False
        self.reset()

    def end_run(self):
        fitness = get_fitness(Segment.instance().start_zone.point, Segment.instance().end_zone.point, self.bot.origin)
        print(f"run end, fitness: {fitness}")
        self.reset()
        self.start_time = server.time

    def tick(self):
        if self.bot is None or self.controller is None:
            return

        if self.training is False and self.running is False:
            return

        if server.time > self.start_time + self.time_limit:
            self.end_run()
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
        move_action = 0
        aim_action = 0
        return (move_action, aim_action)

    def get_point_cloud(self):
        points = []

        # Transform to local space of bot
        directions = point_directions.copy()
        orientation = self.bot.view_angle.y
        for direction in directions:
            x = direction.x * math.cos(orientation) - direction.y * math.sin(orientation)
            y = direction.x * math.sin(orientation) + direction.y * math.cos(orientation)
            direction.x = x
            direction.y = y

        direction_num = 1
        for direction in directions:
            point = self.get_single_point(Vector.normalized(direction), 10000.0, direction_num)
            direction_num += 1
            points.append(point)

        if debug:
            # can only draw 32 temporary entities per frame
            self.drawn_directions += 32

        return points

    def get_single_point(self, direction: Vector, distance: float, direction_num):
        point = {
            "distance": distance,
            "surface_type": 0
        }

        destination = self.bot.origin + direction * distance
        entity_enum = CustomEntEnum(self.bot.origin, destination, (self.bot,))

        # Check for normal geometry
        entity_enum.normal_trace()

        # Check for trigger_teleports
        engine_trace.enumerate_entities(
            entity_enum.ray,
            True,
            entity_enum
        )

        if entity_enum.did_hit:
            point["distance"] = Vector.get_distance(self.bot.origin, entity_enum.point)
            point["surface_type"] = entity_enum.surface_type

        if debug is True and self.drawn_directions - 32 < direction_num <= self.drawn_directions:
            color = [255, 0, 0]
            end_position = destination
            if entity_enum.did_hit:
                color = [0, 255, 0]
                end_position = entity_enum.point
                if entity_enum.surface_type == 1:
                    color = [0, 0, 255]
            beam(RecipientFilter(), start=self.bot.origin, end=end_position, parent=False, life_time=100,
                 red=color[0], green=color[1], blue=color[2], alpha=255, speed=1, model_index=beam_model.index,
                 start_width=0.4, end_width=0.4)

        return point

    def set_time_limit(self, value: float):
        self.time_limit = value

    def get_origin(self):
        if self.bot is not None:
            return self.bot.origin
        return NULL_VECTOR
