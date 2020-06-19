"""Module for base Segments."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# deepsurf
from .zone import Zone


# =============================================================================
# >> CLASSES
# =============================================================================
class Segment:
    """Collection of zones for maps, stages, etc."""

    def __init__(self):
        """Create a new Segment."""
        self.checkpoints = []
        self.start_zone = None
        self.end_zone = None

    def add_checkpoint(self, checkpoint):
        """Add a checkpoint to the Segment."""
        self.checkpoints.append(checkpoint)

    def add_start_zone(self, zone):
        """Add a start zone to the Segment."""
        self.start_zone = zone

    def add_end_zone(self, zone):
        """Add a end zone to the Segment."""
        self.end_zone = zone

    def draw(self):
        if self.start_zone is not None:
            self.start_zone.draw()
        if self.end_zone is not None:
            self.end_zone.draw()
        for cp in self.checkpoints:
            cp.draw()
