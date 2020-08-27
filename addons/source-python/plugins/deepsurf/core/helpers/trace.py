# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from engines.trace import TraceFilter
from entities import HandleEntity


# =============================================================================
# >> CLASSES
# =============================================================================
class CustomTraceFilter(TraceFilter):
    def __init__(self, ignore=[]):
        self.ignore = ignore

    def should_hit_entity(self, entity: HandleEntity, mask: int):
        return True
