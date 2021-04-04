try:
    from socketio import AsyncClient
except (ImportError, ModuleNotFoundError):
    raise ImportError("To use telemetry you must install the `telemetry` option. (run `pip install -U dogehouse[telemetry]`)")    

from json import dumps
from asyncio import run

socket = AsyncClient()
activated = False

@socket.event
async def connect():
    global activated
    
    activated = True
    await socket.emit("init")
    
async def transmit(client):
    global activated

    if not activated or not hasattr(client.user, "id"):
        return
    
    await socket.emit("transmit", dumps({
        "bot": {
            "uuid": client.user.id,
            "username": client.user.username,
            "avatarURL": client.user.avatar_url 
        },
        "room":  {
            "uuid": client.room.id,
            "name": client.room.name,
            "listening": client.room.count,
            "users": [
                {
                    "id": user.id,
                    "bio": user.bio if hasattr(user, "bio") else None,
                    "avatarUrl": user.avatar_url if hasattr(user, "avatar_url") else None,
                    "username": user.username if hasattr(user, "username") else None,
                    "displayname": user.displayname,
                    "numFollowers": user.num_followers,
                    "numFollowing": user.num_following if hasattr(user, "num_following") else 0,
                } for user in client.room.users
            ]
        } if client.room else None
    }))

async def start():
    await socket.connect("wss://socket.dogehouse.xyz", transports=["websocket"], socketio_path="/socket")
    await socket.wait()
