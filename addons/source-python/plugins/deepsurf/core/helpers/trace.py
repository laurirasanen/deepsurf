# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from engines.trace import EntityEnumerator
from engines.trace import engine_trace
from engines.trace import GameTrace
from engines.trace import TraceFilterSimple
from engines.trace import Ray
from entities.entity import Entity
from memory import make_object
from entities import HandleEntity
from entities.helpers import index_from_basehandle
from mathlib import Vector, NULL_VECTOR
from engines.trace import ContentMasks


# =============================================================================
# >> CLASSES
# =============================================================================
class CustomEntEnum(EntityEnumerator):
    did_hit = False
    is_teleport = 0
    point = NULL_VECTOR
    ray = None
    filter = ()
    entity = None
    distance = 0
    origin = NULL_VECTOR

    def __init__(self, origin, destination, filter):
        super().__init__()
        self.origin = origin
        self.ray = Ray(origin, destination)
        self.filter = filter

    def enum_entity(self, entity_handle):
        handle_entity = make_object(HandleEntity, entity_handle)
        entity = Entity(index_from_basehandle(handle_entity.basehandle))

        for ent in self.filter:
            if ent.index == entity.index:
                return True

        trace = GameTrace()
        engine_trace.clip_ray_to_entity(self.ray, ContentMasks.ALL, entity_handle, trace)

        if trace.did_hit() and entity.classname == "trigger_teleport":
            distance = Vector.get_distance(self.origin, trace.end_position)
            if distance < self.distance:
                self.distance = distance
                self.point = trace.end_position
                self.did_hit = True
                self.is_teleport = True
                self.entity = entity

        return True

    def normal_trace(self):
        trace = GameTrace()
        engine_trace.trace_ray(
            self.ray,
            ContentMasks.ALL,
            # Ignore bot
            TraceFilterSimple(self.filter),
            trace
        )

        if trace.did_hit():
            self.did_hit = True
            self.is_teleport = False
            self.point = trace.end_position
            self.entity = trace.entity
            self.distance = Vector.get_distance(self.origin, trace.end_position)
