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
from json import loads, dumps
from inspect import signature
from logging import info, debug
from typing import Awaitable, List, Union
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

from .utils import Repr
from .entities import User, Room, UserPreview, Message
from .config import apiUrl, heartbeatInterval, topPublicRoomsInterval
from .exceptions import NoConnectionException, InvalidAccessToken, InvalidSize, NotEnoughArguments, CommandNotFound

listeners = {}
commands = {}


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
    listeners[func.__name__.lower()] = [func, False]
    return func


def command(func: Awaitable):
    """
    Create a new command for dogehouse.

    Example:
        class Client(dogehouse.DogeClient):
            @dogehouse.command
            async def hello(self, ctx):
                await self.send(f"Hello {ctx.author.mention}")

        if __name__ == "__main__":
            Client("token", "refresh_token").run()
    """
    commands[func.__name__.lower()] = [func, False]
    return func
    


class DogeClient(Repr):
    """Represents your Dogehouse client."""

    def __init__(self, token: str, refresh_token: str, *, room: str = None, muted: bool = False, reconnect_voice: bool = False, prefix: Union[str, List[str]] = "!"):
        """
        Initialize your Dogehouse client

        Args:
            token (str): Your super secret client token.
            refresh_token (str): Your super secret client refresh token.
            room (int, optional): The room your client should join. Defaults to None.
            muted (bool, optional): Wether or not the client should be muted. Defaults to False.
            reconnect_voice (bool, optional): When the client disconnects from the voice server, should it try to reconnect. Defaults to False.
            prefix (List of strings or a string): The bot prefix.
        """
        self.user = None
        self.room = room
        self.rooms = []
        self.prefix = prefix

        self.__token = token
        self.__refresh_token = refresh_token
        self.__socket = None
        self.__active = False
        self.__muted = muted
        self.__reconnect_voice = reconnect_voice
        self.__listeners = listeners
        self.__fetches = {}
        self.__commands = commands

    async def __fetch(self, op: str, data: dict):
        fetch = str(uuid4())

        await self.__send(op, data, fetch_id=fetch)
        self.__fetches[fetch] = op

    async def __send(self, opcode: str, data: dict, *, fetch_id: str = None):
        """Internal websocket sender method."""
        raw_data = dict(op=opcode, d=data)
        if fetch_id:
            raw_data["fetchId"] = fetch_id
        await self.__socket.send(dumps(raw_data))

    async def __main(self, loop):
        """This instance handles the websocket connections."""
        async def event_loop():            
            async def execute_listener(listener: str, *args):
                listener = self.__listeners.get(listener.lower())
                if listener:
                    asyncio.ensure_future(listener[0](*args) if listener[1] else
                                          listener[0](self, *args))
                    
            async def execute_command(command_name: str, ctx: Message, *args):
                command = self.__commands.get(command_name.lower())
                if command:
                    arguments = []
                    params = {}
                    parameters = list(signature(command[0]).parameters.items())
                    if not command[1]:
                        arguments.append(self)
                        parameters.pop(0)
                    
                    if parameters:
                        arguments.append(ctx)
                        parameters.pop(0)
                        for idx, (key, param) in enumerate(parameters):
                            value = args[idx]
                            if param.kind == param.KEYWORD_ONLY:
                                value = " ".join(args[idx::])
                            params[key] = value
                    try:
                        asyncio.ensure_future(command[0](*arguments, **params))
                    except TypeError:
                        raise NotEnoughArguments(f"Not enough arguments were provided in command `{command_name}`.")
                else:
                    raise CommandNotFound(f"The requested command `{command_name}` does not exist.")

            info("Dogehouse: Starting event listener loop")
            while self.__active:
                res = loads(await self.__socket.recv())
                op = res if isinstance(res, str) else res.get("op")
                if op == "auth-good":
                    info("Dogehouse: Received client ready")
                    self.user = User.from_dict(res["d"]["user"])
                    await execute_listener("on_ready")
                elif op == "new-tokens":
                    info("Dogehouse: Received new authorization tokens")
                    self.__token = res["d"]["accessToken"]
                    self.__refresh_token = res["d"]["refreshToken"]
                elif op == "fetch_done":
                    fetch = self.__fetches.get(res.get("fetchId"), False)
                    if fetch:
                        del self.__fetches[res.get("fetchId")]
                        if fetch == "get_top_public_rooms":
                            info("Dogehouse: Received new rooms")
                            self.rooms = list(map(Room.from_dict, res["d"]["rooms"]))
                            await execute_listener("on_rooms_fetch")
                        elif fetch == "create_room":
                            info("Dogehouse: Created new room")
                            self.room = Room.from_dict(res["d"]["room"])
                elif op == "you-joined-as-speaker":
                    await execute_listener("on_room_join", True)
                elif op == "join_room_done":
                    self.room = Room.from_dict(res["d"]["room"])
                    await execute_listener("on_room_join", False)
                elif op == "new_user_join_room":
                    await execute_listener("on_user_join", User.from_dict(res["d"]["user"]))
                elif op == "user_left_room":
                    await execute_listener("on_user_leave", res["d"]["userId"])
                elif op == "new_chat_msg":
                    msg = Message.from_dict(res["d"]["msg"])
                    await execute_listener("on_message", msg)
                    try:
                        async def handle_command(prefix: str):
                            if msg.content.startswith(prefix) and len(msg.content) > len(prefix) + 1:
                                splitted = msg.content[len(prefix)::].split(" ")
                                await execute_command(splitted[0], msg, *splitted[1::])
                                return True
                            return False
                            
                        prefixes = []
                        if isinstance(self.prefix, str):
                            prefixes.append(self.prefix)
                        else:
                            prefixes = self.prefix
                        
                        for prefix in prefixes:
                            if await handle_command(prefix):
                                break                            
                    except Exception as e:
                        await execute_listener("on_error", e)

        async def heartbeat():
            debug("Dogehouse: Starting heartbeat")
            while self.__active:
                await self.__socket.send("ping")
                await asyncio.sleep(heartbeatInterval)

        async def get_top_rooms_loop():
            debug("Dogehouse: Starting to get all rooms")
            while self.__active and not self.room:
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
                    "currentRoomId": self.room,
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
            self.__listeners[(name if name else func.__name__).lower()] = [func, True]
            return func

        return decorator
        
    def command(self, name: str = None):
        """
        Create an command for dogehouse.

        Args:
            name (str, optional): The name of the command. Defaults to the function name.

        Example:
            client = dogehouse.DogeClient("token", "refresh_token")

            @client.command()
            async def hello(ctx):
                await client.send(f"Hello {ctx.author.mention}")

            client.run()

            # Or:

            client = dogehouse.DogeClient("token", "refresh_token")

            @client.listener(name="hello")
            async def hello_command(ctx):
                await client.send(f"Hello {ctx.author.mention}")

            client.run()
        """
        def decorator(func: Awaitable):
            self.__commands[(name if name else func.__name__).lower()] = [func, True]
            return func

        return decorator

    async def get_top_public_rooms(self, *, cursor=0) -> None:
        """
        Manually send a request to update the client rooms property.
        This method gets triggered every X seconds. (Stated in dogehouse.config.topPublicRoomsInterval)

        Args:
            # TODO: Add cursor description
            cursor (int, optional): [description]. Defaults to 0.
        """
        await self.__fetch("get_top_public_rooms", dict(cursor=cursor))
        
    async def create_room(self, name: str, description: str = "", *, public = True) -> None:
        """
        Creates a room, when the room is created a request will be sent to join the room.
        When the client joins the room the `on_room_join` event will be triggered.

        Args:
            name (str): The name for room.
            description (str): The description for the room.
            public (bool, optional): Wether or not the room should be publicly visible. Defaults to True.
        """
        if 2 <= len(name) <= 60:
            return await self.__fetch("create_room", dict(name=name, description=description, privacy="public" if public else "private"))
        
        raise InvalidSize("The `name` property length should be 2-60 characters long.")

    async def join_room(self, id: str) -> None:
        """
        Send a request to join a room as a listener.

        Args:
            id (str): The ID of the room you want to join.
        """
        await self.__send("join_room", dict(roomId=id))
        
    async def send(self, message: str, *, whisper: List[str] = []) -> None:
        """
        Send a message to the current room.

        Args:
            message (str): The message that should be sent.
            whisper (List[str], optional): A collection of user id's who should only see the message. Defaults to [].
        
        Raises:
            NoConnectionException: Gets thrown when the client hasn't joined a room yet.
        """
        if not self.room:
            raise NoConnectionException("No room has been joined yet!")
        
        def parse_message():
            tokens = []
            for token in message.split(" "):
                t, v = "text", token
                if v.startswith("@") and len(v) >= 3:
                    t = "mention"
                    v = v[1:]
                elif v.startswith("http") and len(v) >= 8:
                    t = "link"
                elif v.startswith(":") and v.endswith(":") and len(v) >= 3:
                    t = "emote"
                    v = v[1:-1]
                
                tokens.append(dict(t=t, v=v))
                
            return tokens
        
        await self.__send("send_room_chat_msg", dict(whisperedTo=whisper, tokens=parse_message()))
