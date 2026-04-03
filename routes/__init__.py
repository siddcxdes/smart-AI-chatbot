# Routes package shim - forward to backend.routes
from backend import routes as _backend_routes

# re-export submodules for compatibility
chat = _backend_routes.chat
users = _backend_routes.users
tickets = _backend_routes.tickets

__all__ = ["chat", "users", "tickets"]
