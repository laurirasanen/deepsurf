"""Module for checkpoints."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
import mathlib

# deepsurf
from .zone import Zone

# =============================================================================
# >> CLASSES
# =============================================================================
class Checkpoint(Zone):
    def __init__(self, index, p1=mathlib.NULL_VECTOR):
        """Create a new checkpoint."""
        super().__init__(p1)
        self.index = index
