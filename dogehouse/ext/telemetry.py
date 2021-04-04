from json import dumps
from asyncio import run
from socketio import AsyncClient

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
            "avatar": client.user.avatar_url 
        },
        "room":  {
            "uuid": client.room.id,
            "name": client.room.name,
            "listening": client.room.count,
            "users": []
        } if client.room else None
    }))

async def start():
    await socket.connect("wss://socket.dogehouse.xyz", transports=["websocket"], socketio_path="/socket")
    await socket.wait()
