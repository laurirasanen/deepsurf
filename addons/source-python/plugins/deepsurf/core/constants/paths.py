"""Maps plugin name as a subdirectory to paths.
i.e. 	   /resource/source-python/translations/deepsurf/chat_strings.ini
instead of /resource/source-python/translations/chat_strings.ini"""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
from paths import CFG_PATH as _CFG_PATH

# Custom Imports
from .info import info

# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
CFG_PATH = _CFG_PATH / info.name
