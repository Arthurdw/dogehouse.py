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
from typing import Awaitable
from json import loads, dumps
from logging import info, debug
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

from .utils import Repr
from .entities import User, Room
from .config import apiUrl, heartbeatInterval
from .exceptions import NoConnectionException, InvalidAccessToken

listeners = {}

def event(func: Awaitable):
    listeners[func.__name__] = [func, False]
    return func
    

class DogeClient(Repr):
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
        self.__token = token
        self.__refresh_token = refresh_token
        self.__socket = None
        self.__active = False
        self.__room = room
        self.__muted = muted
        self.__reconnect_voice = reconnect_voice
        self.__listeners = listeners
        self.user = None

    def listener(self):
        def decorator(func: Awaitable):
            self.__listeners[func.__name__] = [func, True]
            return func
        
        return decorator
        
    async def __send(self, opcode: str, data: dict):
        raw = dumps(dict(op=opcode, d=data))
        await self.__socket.send(raw)

    async def __main(self, loop: asyncio.ProactorEventLoop):
        """This instance handles the websocket connections."""
        async def event_loop():
            async def execute_listener(listener: str, *args):
                listener = self.__listeners.get(listener)
                if listener:
                    if listener[1]:
                        await listener[0](*args)
                    else:
                        await listener[0](self, *args)

            debug("Starting event listener loop")
            while self.__active:
                res = loads(await self.__socket.recv())
                if res.get("op") == "auth-good":
                    user = res["d"]["user"]
                    self.user = User(user.get("id"), user.get("username"), user.get("displayname"), user.get(
                        "avatarUrl"), user.get("bio"), Room(user.get("currentRoomId")), user.get("lastOnline"))
                    await execute_listener("on_ready")

        async def heartbeat():
            debug("Starting heartbeat")
            while self.__active:
                await self.__socket.send("ping")
                await asyncio.sleep(heartbeatInterval)

        try:
            info("Connecting with dogehouse API")
            async with websockets.connect(apiUrl) as ws:
                info("Dogehouse API connection established successfully")
                self.__active = True
                self.__socket = ws

                info("Attemting to authenticate Dogehouse credentials")
                await self.__send('auth', {
                    "accessToken": self.__token,
                    "refreshToken": self.__refresh_token,
                    "reconnectToVoice": self.__reconnect_voice,
                    "muted": self.__muted,
                    "currentRoomId": self.__room,
                    "platform": "dogehouse.py"
                })
                info("Successfully authenticated on Dogehouse.")

                event_loop_task = loop.create_task(event_loop())
                await heartbeat()
                await event_loop_task()
        except ConnectionClosedOK:
            info("Dogehouse API connection closed peacefully.")
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
