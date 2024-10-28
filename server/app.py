import os
import threading
import dotenv
dotenv.load_dotenv()

from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

from dyna.app import app
from dyna.http.api import api
from dyna.socketio.socket import socketio
from dyna.database import db_connect
from dyna.modules.module import system_initialized

# Connect MongoDB
db_connect()

# Initialized Module
system_initialized()

# Initialized API
api.init_app(app)

# Initialized SockerIO
socketio.init_app(app)

# Import event
from dyna import events

__all__ = [
    "events"
]

def run():
    '''Thread server'''

    def _run():
        host = os.environ.get("SERVER_HOST", "0.0.0.0")
        port = int(os.environ.get("SERVER_PORT", "8569"))
        http_server = WSGIServer((host, port), app, log=None, handler_class=WebSocketHandler)
        print(f"Server running on: http://{host}:{port}")
        http_server.serve_forever()

    threading.Thread(target=_run, daemon=True).start()