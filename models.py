# Compatibility shim - re-export backend.models
from backend.models import *

__all__ = [name for name in globals() if not name.startswith("_")]
