try:
    from socketio import AsyncClient
    from socketio.exceptions import ConnectionError
except (ImportError, ModuleNotFoundError):
    raise ImportError(
        "To use telemetry you must install the `telemetry` option. (run `pip install -U dogehouse[telemetry]`)")

from json import dumps

socket = AsyncClient()
activated = False
err_occurred_on_connect = False


@socket.event
async def connect():
    global activated

    activated = True


async def transmit(client):
    global activated, err_occurred_on_connect

    if err_occurred_on_connect:
        return await start()

    if not activated or not hasattr(client.user, "id"):
        return

    await socket.emit("transmit", dumps({
        "bot": {
            "type": "dogehouse.py",
            "uuid": client.user.id,
            "username": client.user.username,
            "avatarURL": client.user.avatar_url
        },
        "room": {
            "uuid": client.room.id,
            "name": client.room.name,
            "listening": client.room.count,
            "users": [
                {
                    "id": user.id,
                    "bio": user.bio if hasattr(user, "bio") else None,
                    "avatarUrl": user.avatar_url if hasattr(user, "avatar_url") else None,
                    "username": user.username if hasattr(user, "username") else None,
                    "displayName": user.displayname,
                    "numFollowers": user.num_followers,
                    "numFollowing": user.num_following if hasattr(user, "num_following") else 0,
                } for user in client.room.users
            ]
        } if client.room else None
    }))


async def start():
    global err_occurred_on_connect
    try:
        await socket.connect("wss://socket.dogegarden.net", transports=["websocket"], socketio_path="/socket")
        err_occurred_on_connect = False
        await socket.wait()
    except ConnectionError:
        err_occurred_on_connect = True


class Dogegarden:
    start = start
    transmit = transmit


dogegarden = Dogegarden
