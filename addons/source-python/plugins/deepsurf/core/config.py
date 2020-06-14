"""Module for parsing and holding plugin config."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
from configparser import ConfigParser

# Source.Python
from cvars import ConVar

# deepsurf
from .constants import CFG_PATH

# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
PARSER = ConfigParser()

CORE_CFG_FILE = CFG_PATH / "core.ini"
PARSER.read(CORE_CFG_FILE)
DB_CFG = dict(PARSER.items("database"))

# validate stuff
assert "foo" in DB_CFG


def apply_cvars():
    # apply cvars
    CVAR_CFG = dict(PARSER.items("cvar"))
    for cvar in CVAR_CFG.keys():
        ConVar(cvar).set_string(CVAR_CFG[cvar])
