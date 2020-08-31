# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from mathlib import Vector


def get_fitness(start, end, origin):
    segment_distance = Vector.get_distance(start, end)
    current_distance = Vector.get_distance(origin, end)
    done = current_distance < 100.0
    return segment_distance - current_distance, done
