"""Module for bot functionality"""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import math
import pickle
import rpyc

rpyc.core.protocol.DEFAULT_CONFIG["allow_pickle"] = True

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
from players.constants import PlayerButtons

# deepsurf
from .helpers import CustomEntEnum
from .reward import (
    DistanceReward,
    VelocityReward,
    FaceTargetReward,
    FaceVelocityReward,
    RampReward,
)
from .hud import draw_hud
from .zone import Segment

# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
debug_rays = False
debug_points = False
beam_model = Model("sprites/laserbeam.vmt")
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
    conn = None
    network = None
    state = None
    reward_functions = []

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

        self.spawned = False
        self.bot = None
        self.controller = None
        self.training = False
        self.running = False
        self.drawn_directions = 32
        self.time_limit = 10.0
        self.start_time = 0.0
        self.total_reward = 0.0
        self.conn = rpyc.connect("localhost", 18811)
        self.network = self.conn.root.Network()
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
        self.bot.team = 2
        self.bot.set_property_uchar("m_PlayerClass.m_iClass", 7)
        self.bot.set_property_uchar("m_Shared.m_iDesiredPlayerClass", 7)
        self.bot.spawn(force=True)
        self.reward_functions = [
            DistanceReward(self.bot, 0.5),
            VelocityReward(self.bot, 2.0),
            FaceTargetReward(self.bot, 2.0),
            FaceVelocityReward(self.bot, 2.0),
            RampReward(self.bot, 2.0),
        ]

    def on_spawn(self):
        self.spawned = True
        # these need to be set after spawning
        self.bot.set_noblock(True)
        self.reset()

    def reset(self):
        if self.bot is None:
            return

        if Segment.instance().start_zone is None:
            print("[deepsurf] No start zone")
            return

        self.total_reward = 0.0
        bcmd = self.get_cmd(0, 0, 0, 0, 0)
        self.controller.run_player_move(bcmd)
        self.bot.snap_to_position(
            Segment.instance().start_zone.point,
            QAngle(0, Segment.instance().start_zone.orientation, 0),
        )
        self.state = None
        for rf in self.reward_functions:
            rf.reset()

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

    def get_reward(self):
        reward = 0.0
        for rf in self.reward_functions:
            rf.tick()
            reward += rf.get()
        return reward

    def end_run(self):
        print(f"run end, reward: {self.total_reward}")

        if self.training:
            self.network.end_episode(self.total_reward)

        self.reset()
        self.start_time = server.time

    def tick(self):
        if self.bot is None or self.controller is None:
            return

        if not self.spawned:
            return

        if self.training:
            self.train_tick()
        elif self.running:
            self.run_tick()

    def train_tick(self):
        # use values from previous tick for optimization
        if self.state is None:
            self.state = self.get_state()

        (
            move_action,
            yaw_action,
            pitch_action,
            jump_action,
            duck_action,
        ) = self.get_action(self.state)
        bcmd = self.get_cmd(
            move_action, yaw_action, pitch_action, jump_action, duck_action
        )
        self.controller.run_player_move(bcmd)

        reward = self.get_reward()
        self.total_reward += reward

        time_elapsed = self.time_limit - (server.time - self.start_time)
        if server.tick % 67 == 0:
            draw_hud(self.bot, time_elapsed, self.training, self.total_reward)

        done = self.is_done()

        self.state = self.get_state()
        self.network.post_action(reward, pickle.dumps(self.state), done)
        if done:
            self.end_run()

    def run_tick(self):
        self.state = self.get_state()
        (
            move_action,
            yaw_action,
            pitch_action,
            jump_action,
            duck_action,
        ) = self.get_action_run(self.state)
        bcmd = self.get_cmd(
            move_action, yaw_action, pitch_action, jump_action, duck_action
        )
        self.controller.run_player_move(bcmd)

        time_elapsed = self.time_limit - (server.time - self.start_time)
        if server.tick % 67 == 0:
            draw_hud(self.bot, time_elapsed, self.training, 0)

        if self.is_done():
            self.end_run()

    def is_done(self):
        end_distance = Vector.get_distance(
            self.bot.origin, Segment.instance().end_zone.point
        )
        done = end_distance < 100.0

        if server.time > self.start_time + self.time_limit:
            done = True

        return done

    def get_angle_change(self, index):
        turn_values = 200

        # min 0.05 per tick, max 5.0
        # (3.35 /s , 335 /s)
        if index <= turn_values / 2:
            return index * 0.05

        index -= turn_values / 2
        return index * -0.05

    def get_cmd(
        self, move_action=0, yaw_action=0, pitch_action=0, jump_action=0, duck_action=0
    ):
        """Get BotCmd for move direction and aim delta"""
        bcmd = BotCmd()
        bcmd.reset()
        view_angles = self.bot.view_angle

        if yaw_action != 0:
            view_angles.y += self.get_angle_change(yaw_action)
        if pitch_action != 0:
            view_angles.x += self.get_angle_change(pitch_action)
            if view_angles.x < -89.0:
                view_angles.x = -89.0
            if view_angles.x > 89.0:
                view_angles.x = 89.0

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

        if jump_action != 0:
            bcmd.buttons |= PlayerButtons.JUMP

        if duck_action != 0:
            bcmd.buttons |= PlayerButtons.DUCK

        return bcmd

    def get_action(self, state):
        action = self.network.get_action(pickle.dumps(state))
        return action

    def get_action_run(self, state):
        action = self.network.get_action_run(pickle.dumps(state))
        return action

    def get_state(self):
        point_cloud = self.get_point_cloud()
        state = []
        for point in point_cloud:
            state.append(point["distance"])
        for point in point_cloud:
            state.append(1.0 if point["is_teleport"] else 0.0)

        # project velocity to bots orientation
        velocity = self.bot.get_property_vector("m_vecVelocity")
        forward = Vector()
        right = Vector()
        self.bot.rotation.get_angle_vectors(forward, right)
        state.extend([velocity.dot(forward), velocity.dot(right), velocity.z])

        # next point direction oriented to bot space
        remaining_points = Segment.instance().get_remaining_points(self.bot.origin)
        self.bot.rotation.get_angle_vectors(forward, right)
        next_point = remaining_points[0]  # guaranteed length >= 1 if segment valid
        origin = self.bot.origin
        diff = next_point - origin
        state.extend([diff.dot(forward), diff.dot(right), diff.z])

        # 2nd next point oriented to bot space
        # (same as previous if the end)
        self.bot.rotation.get_angle_vectors(forward, right)
        if len(remaining_points) > 1:
            next_point = remaining_points[1]
        origin = self.bot.origin
        diff = next_point - origin
        state.extend([diff.dot(forward), diff.dot(right), diff.z])

        if debug_points:
            for i in range(0, len(remaining_points)):
                color = [255, 0, 0]
                end_position = remaining_points[i]
                beam(
                    RecipientFilter(),
                    start=self.bot.origin,
                    end=end_position,
                    parent=False,
                    life_time=1,
                    red=color[0],
                    green=color[1],
                    blue=color[2],
                    alpha=255,
                    speed=1,
                    model_index=beam_model.index,
                    start_width=0.4,
                    end_width=0.4,
                )
                if i >= 1:
                    break

        return state

    def get_point_cloud(self):
        points = []

        # Transform to local space of bot
        cos = math.cos(self.bot.view_angle.y)
        sin = math.cos(self.bot.view_angle.y)
        direction_num = 1

        for direction in point_directions:
            local_dir = Vector(
                direction.x * cos - direction.y * sin,
                direction.x * sin + direction.y * cos,
            )
            point = self.get_single_point(
                Vector.normalized(local_dir), 10000.0, direction_num
            )
            direction_num += 1
            points.append(point)

        if debug_rays:
            # can only draw 32 temporary entities per frame
            self.drawn_directions += 32

        return points

    def get_single_point(self, direction: Vector, distance: float, direction_num):
        point = {"distance": distance, "is_teleport": False}

        # shoot rays from above bot origin so they can "see" more of the ground / ramps, etc.
        destination = self.bot.origin + Vector(0, 0, 48) + direction * distance
        entity_enum = CustomEntEnum(self.bot.origin, destination, (self.bot,))

        # Check for normal geometry
        entity_enum.normal_trace()

        # Check for trigger_teleports
        engine_trace.enumerate_entities(entity_enum.ray, True, entity_enum)

        if entity_enum.did_hit:
            point["distance"] = Vector.get_distance(self.bot.origin, entity_enum.point)
            point["is_teleport"] = entity_enum.is_teleport

        if (
            debug_rays is True
            and self.drawn_directions - 32 < direction_num <= self.drawn_directions
        ):
            color = [255, 0, 0]
            end_position = destination
            if entity_enum.did_hit:
                color = [0, 255, 0]
                end_position = entity_enum.point
                if entity_enum.is_teleport is True:
                    color = [0, 0, 255]
            beam(
                RecipientFilter(),
                start=self.bot.origin,
                end=end_position,
                parent=False,
                life_time=100,
                red=color[0],
                green=color[1],
                blue=color[2],
                alpha=255,
                speed=1,
                model_index=beam_model.index,
                start_width=0.4,
                end_width=0.4,
            )

        return point

    def set_time_limit(self, value: float):
        self.time_limit = value

    def get_time_limit(self):
        return self.time_limit

    def get_origin(self):
        if self.bot is not None:
            return self.bot.origin
        return NULL_VECTOR
