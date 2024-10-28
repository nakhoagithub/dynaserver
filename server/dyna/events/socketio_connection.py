import os
from dyna.socketio.socket import socketio, request, disconnect
from dyna.logger import log
from dyna.environment import env
from .blinker_event import connect_signal, disconnect_signal

@socketio.on("connect")
def on_connect():
    sid: str = request.sid
    try:
        session = request.headers.get("Session", None)
        account_obj = env["Account"]
        account = account_obj.get_account_from_session(session)
        if account is not None:
            account_obj.update({"id": account.id, "is_online": True, "sid": sid})
            connect_signal.send(account)
            if os.environ.get("PRINT_CONSOLE_SOCKET_CONNECTION", "true") == "true":
                log(f"Client connected | SID: {sid}", name= "SOCKET_CONNECTED")
        else:
            disconnect(sid)
    except Exception as e:
        disconnect(sid)


@socketio.on("disconnect")
def on_disconnect():
    try:
        sid: str = request.sid
        account_obj = env["Account"]
        account = account_obj.get_account_from_sid(sid)
        if account is not None:
            account_obj.update({"id": account.id, "is_online": False, "sid": None})
            if os.environ.get("PRINT_CONSOLE_SOCKET_CONNECTION", "true") == "true":
                log(f"Client disconnected | SID: {sid}", name= "SOCKET_DISCONNECTED")

        disconnect_signal.send(account)
    except Exception as e:
        pass