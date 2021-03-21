# -*- coding: utf-8 -*-
# MIT License

# Copyright (c) 2021 Arthur

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import asyncio
import websockets
from uuid import uuid4
from typing import Awaitable
from json import loads, dumps
from logging import info, debug
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

from .utils import Repr
from .entities import User, Room, UserPreview
from .exceptions import NoConnectionException, InvalidAccessToken
from .config import apiUrl, heartbeatInterval, topPublicRoomsInterval

listeners = {}


def event(func: Awaitable):
    """
    Create an event listener for dogehouse.
    
    Example:
        class Client(dogehouse.DogeClient):
            @dogehouse.event
            async def on_ready(self):
                print(f"Logged in as {self.user.username}")
        
        if __name__ == "__main__":
            Client("token", "refresh_token").run()
    """
    listeners[func.__name__] = [func, False]
    return func


class DogeClient(Repr):
    """Represents your Dogehouse client."""
    def __init__(self, token: str, refresh_token: str, *, room: int = None, muted: bool = False, reconnect_voice: bool = False):
        """
        Initialize your Dogehouse client

        Args:
            token (str): Your super secret client token.
            refresh_token (str): Your super secret client refresh token.
            room (int, optional): The room your client should join. Defaults to None.
            muted (bool, optional): Wether or not the client should be muted. Defaults to False.
            reconnect_voice (bool, optional): When the client disconnects from the voice server, should it try to reconnect. Defaults to False.
        """
        self.user = None
        self.rooms = []

        self.__token = token
        self.__refresh_token = refresh_token
        self.__socket = None
        self.__active = False
        self.__room = room
        self.__muted = muted
        self.__reconnect_voice = reconnect_voice
        self.__listeners = listeners
        self.__fetches = {}

    def listener(self, name: str = None):
        """
        Create an event listener for dogehouse.

        Args:
            name (str, optional): The name of the event. Defaults to the function name.
            
        Example:
            client = dogehouse.DogeClient("token", "refresh_token")
            
            @client.listener()
            async def on_ready():
                print(f"Logged in as {self.user.username}")
            
            client.run()
            
            # Or:
            
            client = dogehouse.DogeClient("token", "refresh_token")
            
            @client.listener(name="on_ready")
            async def bot_has_started():
                print(f"Logged in as {self.user.username}")
            
            client.run()
        """
        def decorator(func: Awaitable):
            self.__listeners[name if name else func.__name__] = [func, True]
            return func

        return decorator

    async def __send(self, opcode: str, data: dict, *, fetch_id: str = None):
        """Internal websocket sender method."""
        raw_data = dict(op=opcode, d=data)
        if fetch_id:
            raw_data["fetchId"] = fetch_id
        await self.__socket.send(dumps(raw_data))

    async def __main(self, loop: asyncio.ProactorEventLoop):
        """This instance handles the websocket connections."""
        async def event_loop():
            async def execute_listener(listener: str, *args):
                listener = self.__listeners.get(listener)
                if listener:
                    asyncio.ensure_future(listener[0](
                        *args) if listener[1] else asyncio.create_task(listener[0](self, *args)))

            info("Dogehouse: Starting event listener loop")
            while self.__active:
                res = loads(await self.__socket.recv())
                op = res if isinstance(res, str) else res.get("op")
                if op == "auth-good":
                    info("Dogehouse: Received client ready")
                    user = res["d"]["user"]
                    self.user = User(user.get("id"), user.get("username"), user.get("displayname"), user.get(
                        "avatarUrl"), user.get("bio"), user.get("lastOnline"))
                    await execute_listener("on_ready")
                elif op == "new-tokens":
                    info("Dogehouse: Received new authorization tokens")
                    self.__token = res["d"]["accessToken"]
                    self.__refresh_token = res["d"]["refreshToken"]

                if op == "fetch_done":
                    fetch = self.__fetches.get(res.get("fetchId"), False)
                    if fetch:
                        del self.__fetches[res.get("fetchId")]
                        if fetch == "get_top_public_rooms":
                            info("Dogehouse: Received new rooms")
                            self.rooms = [Room(room["id"], room["creatorId"], room["name"], room["description"], room["inserted_at"], room["isPrivate"], room["numPeopleInside"],
                                               [UserPreview(user["id"], user["displayName"], user["numFollowers"]) for user in room["peoplePreviewList"]]) for room in res["d"]["rooms"]]

        async def heartbeat():
            debug("Dogehouse: Starting heartbeat")
            while self.__active:
                await self.__socket.send("ping")
                await asyncio.sleep(heartbeatInterval)

        async def get_top_rooms_loop():
            debug("Dogehouse: Starting to get all rooms")
            while self.__active:
                await self.get_top_public_rooms()
                await asyncio.sleep(topPublicRoomsInterval)

        try:
            info("Dogehouse: Connecting with Dogehouse websocket")
            async with websockets.connect(apiUrl) as ws:
                info("Dogehouse: Websocket connection established successfully")
                self.__active = True
                self.__socket = ws

                info("Dogehouse: Attemting to authenticate")
                await self.__send('auth', {
                    "accessToken": self.__token,
                    "refreshToken": self.__refresh_token,
                    "reconnectToVoice": self.__reconnect_voice,
                    "muted": self.__muted,
                    "currentRoomId": self.__room,
                    "platform": "dogehouse.py"
                })
                info("Dogehouse: Successfully authenticated")

                event_loop_task = loop.create_task(event_loop())
                get_top_rooms_task = loop.create_task(get_top_rooms_loop())
                await heartbeat()
                await event_loop_task()
                await get_top_rooms_task()
        except ConnectionClosedOK:
            info("Dogehouse: Websocket connection closed peacefully")
            self.__active = False
        except ConnectionClosedError as e:
            if (e.code == 4004):
                raise InvalidAccessToken()

    def run(self):
        """Establishes a connection to the websocket servers."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.__main(loop))
        loop.close()

    async def close(self):
        """
        Closes the established connection.

        Raises:
            NoConnectionException: No connection has been established yet. Aka got nothing to close.
        """
        if not isinstance(self.__socket, websockets.WebSocketClientProtocol):
            raise NoConnectionException()

        self.__active = False

    async def get_top_public_rooms(self, *, cursor=0) -> None:
        """
        Manually send a request to update the client rooms property.
        This method gets triggered every X seconds. (Stated in dogehouse.config.topPublicRoomsInterval)
        
        Args:
            # TODO: Add cursor description
            cursor (int, optional): [description]. Defaults to 0.
        """
        fetch = str(uuid4())

        await self.__send("get_top_public_rooms", dict(cursor=cursor), fetch_id=fetch)
        self.__fetches[fetch] = "get_top_public_rooms"
