# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from mathlib import Vector

# deepsurf
from .zone import Segment
from .helpers import CustomEntEnum


class Reward:
    current = 0
    previous = 0
    scale = 1.0
    bot = None

    def __init__(self, bot, scale=1.0):
        self.current = 0
        self.previous = 0
        self.bot = bot
        self.scale = scale

    def tick(self):
        raise NotImplementedError()

    def get(self):
        diff = self.current - self.previous
        self.previous = self.current
        return diff * self.scale

    def reset(self):
        self.current = 0
        self.previous = 0


# TODO: include checkpoints
class DistanceReward(Reward):
    def tick(self):
        start = Segment.instance().start_zone.point
        end = Segment.instance().end_zone.point
        origin = self.bot.origin
        segment_distance = Vector.get_distance(start, end)
        current_distance = Vector.get_distance(origin, end)
        self.current = segment_distance - current_distance


# TODO: include checkpoints
class VelocityReward(Reward):
    def tick(self):
        end = Segment.instance().end_zone.point
        origin = self.bot.origin
        want_direction = (end - origin).normalized()
        velocity = self.bot.velocity
        return want_direction.dot(velocity)


# TODO: include checkpoints
class FaceReward(Reward):
    def tick(self):
        end = Segment.instance().end_zone.point
        origin = self.bot.origin
        want_direction = (end - origin).normalized()
        view_direction = want_direction
        self.bot.get_view_angle().get_angle_vectors(forward=view_direction)
        return want_direction.dot(view_direction)


class RampReward(Reward):
    def tick(self):
        # TODO: use bot mins/maxs instead of simple ray and reduce z distance
        destination = self.bot.origin + Vector(0, 0, -32.0)
        entity_enum = CustomEntEnum(self.bot.origin, destination, (self.bot,))

        # Check for normal geometry
        entity_enum.normal_trace()

        if entity_enum.did_hit and entity_enum.normal.z < 0.7:
            self.current += 1
