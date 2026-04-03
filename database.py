# Compatibility shim - re-export backend.database
# Project has been reorganized: real code lives in backend/
from backend.database import *

__all__ = [name for name in globals() if not name.startswith("_")]
