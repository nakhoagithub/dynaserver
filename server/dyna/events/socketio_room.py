import json
from dyna.socketio.socket import socketio, join_room, leave_room

@socketio.on("join")
def join(data):

    d: dict | None = None
    try:
        d = json.loads(json.dumps(data))
    except:
        pass
    if d is None:
        return
    
    room = d.get("room", None) or "all"
    join_room(room=room)


@socketio.on("leave")
def leave(data):
    d: dict | None = None
    try:
        d = json.loads(json.dumps(data))
    except:
        pass
    if d is None:
        return
    
    room = d.get("room", None) or "all"
    leave_room(room=room)