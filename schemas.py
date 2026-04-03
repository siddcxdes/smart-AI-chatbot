# Compatibility shim - re-export backend.schemas
from backend.schemas import *

__all__ = [name for name in globals() if not name.startswith("_")]
