"""Module for Zones."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from engines.server import server
from engines.precache import Model
from mathlib import Vector, NULL_VECTOR
from effects import box
from filters.recipients import RecipientFilter

# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
model = Model("sprites/laser.vmt")


# =============================================================================
# >> CLASSES
# =============================================================================
class Zone:
    """Class for Segment Zones."""

    def __init__(self, point=NULL_VECTOR, orientation=0):
        """Create a new Zone."""
        # (z) rotation, used for starting zones
        self.orientation = orientation
        self.point = point

    def draw(self):
        """Draw this zone to all players."""
        box(
            RecipientFilter(),
            self.point - Vector(8.0, 8.0, 8.0),
            self.point + Vector(8.0, 8.0, 8.0),
            alpha=255,
            blue=0,
            green=255,
            red=0,
            amplitude=0,
            end_width=5,
            life_time=1,
            start_width=5,
            fade_length=0,
            flags=0,
            frame_rate=255,
            halo=model,
            model=model,
            start_frame=0,
        )
