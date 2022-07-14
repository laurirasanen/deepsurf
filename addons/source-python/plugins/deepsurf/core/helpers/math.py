# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from mathlib import Vector


def closest_point_on_line(start: Vector, end: Vector, point: Vector) -> Vector:
    """Get the closest position on line (start, end) to point"""
    norm = (end - start).normalized()
    to_point = point - start
    frac = to_point.dot(norm)
    return start + frac * norm


def closest_point_on_line_segment(start: Vector, end: Vector, point: Vector) -> Vector:
    """Get the closest position on line segment (start, end) to point"""
    closest = closest_point_on_line(start, end, point)

    # closest is a point projected onto the line
    # and can be outside the line segment, clamp.
    line_dot = start.dot(end)
    closest_dot = closest.dot(end)

    if line_dot * closest_dot > 0:
        # same direction
        if start.get_distance(end) < closest.get_distance(end):
            closest = start
    else:
        # opposite
        if end.get_distance(start) < closest.get_distance(start):
            closest = end

    return closest
