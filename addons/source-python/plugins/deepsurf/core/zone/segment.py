"""Module for base Segments."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from mathlib import Vector

# deepsurf
from .zone import Zone
from .checkpoint import Checkpoint


# =============================================================================
# >> CLASSES
# =============================================================================
class Segment:
    """Collection of zones for maps, stages, etc."""

    __instance = None
    start_zone = None
    end_zone = None

    @staticmethod
    def instance():
        """Singleton instance"""
        if Segment.__instance is None:
            Segment()
        return Segment.__instance

    def __init__(self):
        """Create a new Segment."""
        if Segment.__instance is not None:
            raise Exception("This class is a singleton, use .instance() access method.")

        self.checkpoints = []
        self.start_zone = None
        self.end_zone = None
        Segment.__instance = self

    def add_checkpoint(self, checkpoint):
        """Add a checkpoint to the Segment."""
        self.checkpoints.append(checkpoint)
        return len(self.checkpoints)

    def remove_checkpoint(self):
        """Remove last checkpoint"""
        if len(self.checkpoints > 0):
            self.checkpoints = self.checkpoints[:-1]
            return len(self.checkpoints) + 1
        return -1

    def set_start_zone(self, zone):
        """Add a start zone to the Segment."""
        self.start_zone = zone

    def set_end_zone(self, zone):
        """Add a end zone to the Segment."""
        self.end_zone = zone

    def draw(self):
        if self.start_zone is not None:
            self.start_zone.draw()
        if self.end_zone is not None:
            self.end_zone.draw()
        for cp in self.checkpoints:
            cp.draw()

    def clear(self):
        self.checkpoints = []
        self.start_zone = None
        self.end_zone = None

    def serialize(self):
        if self.is_valid() is False:
            print("[deepsurf] tried to serialize segment without start or end zone")
            return None

        data = {
            "start_zone": {
                "orientation": self.start_zone.orientation,
                "x": self.start_zone.point.x,
                "y": self.start_zone.point.y,
                "z": self.start_zone.point.z,
            },
            "end_zone": {
                "x": self.end_zone.point.x,
                "y": self.end_zone.point.y,
                "z": self.end_zone.point.z,
            },
            "checkpoints": []
        }

        for cp in self.checkpoints:
            data["checkpoints"].append({
                "index": cp.index,
                "x": cp.point.x,
                "y": cp.point.y,
                "z": cp.point.z,
            })

        return data

    def deserialize(self, data):
        self.clear()
        self.set_start_zone(
            Zone(
                Vector(
                    data["start_zone"]["x"],
                    data["start_zone"]["y"],
                    data["start_zone"]["z"]
                ),
                data["start_zone"]["orientation"]
            )
        )
        self.set_end_zone(
            Zone(
                Vector(
                    data["end_zone"]["x"],
                    data["end_zone"]["y"],
                    data["end_zone"]["z"]
                )
            )
        )
        for cp in data["checkpoints"]:
            self.add_checkpoint(
                Checkpoint(
                    cp["index"],
                    Vector(
                        cp["x"],
                        cp["y"],
                        cp["z"]
                    )
                )
            )

    def is_valid(self):
        if self.start_zone is None:
            return False
        if self.end_zone is None:
            return False
        return True
