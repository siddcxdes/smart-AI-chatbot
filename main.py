# Compatibility shim - expose app from backend.main
from backend.main import app

__all__ = ["app"]
