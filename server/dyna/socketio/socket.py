import os
from flask_socketio import SocketIO, disconnect, join_room, leave_room
from flask import request

# Socket IO
socketio = SocketIO(
    async_mode="gevent",
    cors_allowed_origins=os.environ.get("CORS_ALLOW_ORIGINS", "*")
)

__all__ = [
    "disconnect",
    "request",
    "join_room",
    "leave_room",
]