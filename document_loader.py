# Compatibility shim - re-export backend.document_loader
from backend.document_loader import *

__all__ = [name for name in globals() if not name.startswith("_")]
