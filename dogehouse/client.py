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
from inspect import signature, Parameter
from json import loads, dumps
from logging import info, debug
from time import time
from traceback import print_exc
from typing import Awaitable, List, Union, Tuple, Any, Dict, Optional
from uuid import uuid4

import websockets
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

from .config import apiUrl, heartbeatInterval, topPublicRoomsInterval, telemetryInterval
from .entities import Client, User, Room, UserPreview, Message, BaseUser, Context
from .exceptions import *
from .utils.convertors import Convertor
from .utils.parsers import parse_sentence_to_tokens as parse_message, parse_word_to_token as parse_word

listeners = {}
commands = {}


def event(func: Awaitable, *, name: str = None):
    """
    Create an event listener for dogehouse.

    Args:
        func (Awaitable, optional): Your callback (gets supplied automatically when you use the decorator).
                                    Defaults to None.
        name (str, optional): The event name. Defaults to the function name.

    Example:
        class Client(dogehouse.DogeClient):
            @dogehouse.event
            async def on_ready(self):
                print(f"Logged in as {self.user.username}")

        if __name__ == "__main__":
            Client("token", "refresh_token").run()
    """

    def wrapper(_func: Awaitable):
        listeners[(Convertor.convert_basic_types(name, str) if name else func.__name__).lower()] = [func, False]

    return wrapper(func) if func else wrapper


def command(func: Awaitable = None, *, name: str = None, cooldown: int = 0, aliases: List[str] = []):
    """
    Create a new DogeClient command, which will be handled by the dogehouse python library.

    Args:
        func (Awaitable, optional): Your callback (gets supplied automatically when you use the decorator).
                                    Defaults to None.
        name (str, optional): The call name for your command. Defaults to the function name.
        cooldown (int, optional): The cooldown for the function usage per client. Defaults to 0.
        aliases (List[str], optional): A list of aliases which should trigger your command. Defaults to None.

    Example:
        class Client(dogehouse.DogeClient):
            @dogehouse.command
            async def hello(self, ctx):
                await self.send(f"Hello {ctx.author.mention}")

        if __name__ == "__main__":
            Client("token", "refresh_token").run()
    """

    def wrapper(_func: Awaitable):
        def save(_name: str):
            if _name in commands:
                raise CommandAlreadyDefined(f"Command `{_name}` has already been defined by a name or alias!")
            commands[_name] = [_func, False, int(cooldown)]

        for cmd_name in (name if name else _func.__name__, *aliases):
            save(Convertor.convert_basic_types(cmd_name, str).lower())

        return _func

    return wrapper(func) if func else wrapper


class DogeClient(Client):
    """Represents your Dogehouse client."""

    def __init__(self, token: str, refresh_token: str, *, room: str = None, muted: bool = False,
                 reconnect_voice: bool = False, prefix: Union[str, List[str]] = "!", telemetry=None):
        """
        Initialize your Dogehouse client

        Args:
            token (str): Your super secret client token.
            refresh_token (str): Your super secret client refresh token.
            room (int, optional): The room your client should join. Defaults to None.
            muted (bool, optional): Whether or not the client should be muted. Defaults to False.
            reconnect_voice (bool, optional): When the client disconnects from the voice server, should it try to
                                              reconnect. Defaults to False.
            prefix (List of strings or a string, optional): The bot prefix.
            telemetry (telemetry class, optional): The telemetry class that will be used. Defaults to None.
        """
        super().__init__(None, room, [], prefix)

        self.__token = token
        self.__refresh_token = refresh_token
        self.__socket = None
        self.__active = False
        self.__muted = muted
        self.__reconnect_voice = reconnect_voice
        self.__listeners = listeners
        self.__fetches = {}
        self.__commands = commands
        self.__waiting_for = {}
        self.__waiting_for_fetches = {}
        self.__command_cooldown_cache = {}
        self.telemetry = telemetry

        if telemetry:
            asyncio.ensure_future(telemetry.start())

    @property
    def commands(self):
        return self.__commands

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
                listener_name = listener.lower()
                listener = self.__listeners.get(listener_name)

                if listener:
                    asyncio.ensure_future(listener[0](
                        *(args if listener[1] else [self, *args])))

                if listener_name[3::] in self.__waiting_for:
                    for fetch_id in self.__waiting_for[listener_name[3::]]:
                        self.__waiting_for_fetches[fetch_id] = [*self.__waiting_for_fetches[fetch_id], list(args)] \
                            if fetch_id in self.__waiting_for_fetches else [list(args)]

            async def execute_command(command_name: str, ctx: Context, *args):
                _command = self.__commands.get(command_name.lower())

                if _command:
                    instance_id = f"{command_name}-{ctx.author.id}"
                    invoked_at = time()
                    if _command[2] and instance_id in self.__command_cooldown_cache:
                        passed = invoked_at - self.__command_cooldown_cache[instance_id]
                        if passed < _command[2]:
                            return await execute_listener("on_cooldown_trigger", ctx, command_name, _command[0],
                                                          _command[2] - passed)

                    arguments = []
                    params = {}
                    parameters = list(signature(_command[0]).parameters.items())
                    if not _command[1]:
                        arguments.append(self)
                        parameters.pop(0)

                    try:
                        if parameters:
                            arguments.append(ctx)
                            parameters.pop(0)

                            for idx, (key, param) in enumerate(parameters):
                                if idx + 1 > len(args) and param.default != Parameter.empty:
                                    params[key] = param.default
                                    continue
                                else:
                                    value = args[idx]

                                    if param.kind == param.KEYWORD_ONLY and len(args) - idx - 1 != 0:
                                        value = " ".join(args[idx::])

                                value = value.strip()

                                if value and param.annotation and hasattr(param.annotation, "convert") and callable(
                                        param.annotation.convert):
                                    value = await param.annotation.convert(ctx, param, value)
                                else:
                                    value = Convertor.handle_basic_types(param, value)

                                params[key] = value
                            self.__command_cooldown_cache[instance_id] = invoked_at

                        asyncio.ensure_future(_command[0](*arguments, **params))
                    except (IndexError, TypeError):
                        raise NotEnoughArguments(
                            f"Not enough arguments were provided in command `{command_name}`.")
                else:
                    raise CommandNotFound(
                        f"The requested command `{command_name}` does not exist.")

            info("Dogehouse: Starting event listener loop")
            while self.__active:
                res: Dict[str, Union[Dict, Any]] = loads(await self.__socket.recv())
                op = res if isinstance(res, str) else res.get("op")
                if op == "auth-good":
                    info("Dogehouse: Received client ready")
                    self.user = User.from_dict(dict(res["d"]["user"]))
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
                            self.rooms = list(
                                map(Room.from_dict, res["d"]["rooms"]))
                            await execute_listener("on_rooms_fetch")
                        elif fetch == "create_room":
                            info("Dogehouse: Created new room")
                            self.room = Room.from_dict(res["d"]["room"])
                            self.room.users = [self.user]
                        elif fetch == "get_user_profile":
                            usr = User.from_dict(res["d"])
                            info(f"Dogehouse: Received user `{usr.id}`")
                            if usr.current_room_id == self.room.id:
                                self.room.users = [(user if user.id != usr.id else usr) for user in self.room.users]
                            await execute_listener("on_user_fetch", usr)
                elif op == "you-joined-as-speaker":
                    await execute_listener("on_room_join", True)
                elif op == "join_room_done":
                    self.room = Room.from_dict(res["d"]["room"])
                    self.room.users.append(self.user)
                    await self.__send("get_current_room_users", {})
                    # for user in self.room.users:
                    #     if not isinstance(user, User):
                    #         await self.__fetch("get_user_profile", dict(userId=user.id))

                    # TODO: Check if joined as speaker 
                    await execute_listener("on_room_join", False)
                elif op == "new_user_join_room":
                    user = User.from_dict(res["d"]["user"])
                    self.room.users.append(user)
                    await execute_listener("on_user_join", user)
                elif op == "user_left_room":
                    user = [user for user in self.room.users if user.id == res["d"]["userId"]][0]
                    self.room.users.remove(user)
                    await execute_listener("on_user_leave", user)
                elif op == "new_chat_msg":
                    msg = Message.from_dict(res["d"]["msg"])
                    await execute_listener("on_message", msg)

                    if msg.author.id == self.user.id:
                        continue

                    try:
                        async def handle_command(_prefix: str):
                            if msg.content.startswith(_prefix) and len(msg.content) > len(_prefix) + 1:
                                splitted = msg.content[len(_prefix)::].split(" ")
                                await execute_command(splitted[0], Context(self, msg), *splitted[1::])
                                return True
                            return False

                        prefixes = [self.prefix] if isinstance(
                            self.prefix, str) else self.prefix

                        for prefix in prefixes:
                            if await handle_command(prefix):
                                break
                    except Exception as err:
                        if "on_error" not in self.__listeners:
                            print_exc()
                        else:
                            await execute_listener("on_error", err)
                elif op == "message_deleted":
                    await execute_listener("on_message_delete", res["d"]["deleterId"], res["d"]["messageId"])
                elif op == "speaker_added":
                    for user in self.room.users:
                        if user.id == res["d"]["userId"] and user.current_room_id == res["d"]["roomId"]:
                            user.room_permissions.is_speaker = True
                            await execute_listener("on_speaker_add", user, res["d"]["muteMap"])
                            break
                elif op == "speaker_removed":
                    for user in self.room.users:
                        if user.id == res["d"]["userId"] and user.current_room_id == res["d"]["roomId"]:
                            user.room_permissions.is_speaker = False
                            await execute_listener("on_speaker_delete", user, res["d"]["muteMap"],
                                                   res["d"]["raiseHandMap"])
                            break
                elif op == "chat_user_banned":
                    await execute_listener("on_user_ban", res["d"]["userId"])
                elif op == "hand_raised":
                    await execute_listener("on_speaker_request", res["d"]["userId"], res["d"]["roomId"])
                elif op == "get_current_room_users_done":
                    self.room.users = list(map(User.from_dict, res["d"]["users"]))
                    for user in self.room.users:
                        if user.id == self.room.creator_id:
                            user.room_permissions.is_admin = True
                    await execute_listener("on_room_users_fetch")
                elif op == "mod_changed" or op == "new_room_creator":
                    changed_permission_type = "mod" if op == "mod_changed" else "admin"
                    attribute = f"is_{changed_permission_type}"

                    if changed_permission_type == "admin":
                        for user in self.room.users:
                            if user.room_permissions.is_admin:
                                user.room_permissions.is_admin = False
                                await execute_listener("on_permission_change", user, changed_permission_type)

                    for user in self.room.users:
                        if user.id == res["d"]["userId"] and user.current_room_id == res["d"]["roomId"]:
                            setattr(user.room_permissions, attribute, not getattr(user.room_permissions, attribute))
                            await execute_listener("on_permissions_change", user, changed_permission_type)
                            break

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

        async def perform_telemetry():
            if self.telemetry:
                debug("Dogehouse: Starting to perform telemetry")

                while self.telemetry and self.__active:
                    await self.telemetry.transmit(self)
                    await asyncio.sleep(telemetryInterval)

        try:
            info("Dogehouse: Connecting with Dogehouse websocket")
            async with websockets.connect(apiUrl) as ws:
                info("Dogehouse: Websocket connection established successfully")
                self.__active = True
                self.__socket = ws

                info("Dogehouse: Attempting to authenticate")
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
                perform_telemetry_task = loop.create_task(perform_telemetry())
                await heartbeat()
                await event_loop_task()
                await get_top_rooms_task()
                await perform_telemetry_task()
        except ConnectionClosedOK:
            info("Dogehouse: Websocket connection closed peacefully")
            self.__active = False
        except ConnectionClosedError as e:
            if e.code == 4004:
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
            self.__listeners[str(name if name else func.__name__).lower()] = [
                func, True]
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
            self.__commands[str(name if name else func.__name__).lower()] = [
                func, True]
            return func

        return decorator

    async def get_top_public_rooms(self, *, cursor: int = 0) -> None:
        """
        Manually send a request to update the client rooms property.
        This method gets triggered every X seconds. (Stated in dogehouse.config.topPublicRoomsInterval)

        Args:
            # TODO: Add cursor description
            cursor (int, optional): [description]. Defaults to 0.
        """
        await self.__fetch("get_top_public_rooms", dict(cursor=int(cursor)))

    async def create_room(self, name: str, description: str = "", *, public=True) -> None:
        """
        Creates a room, when the room is created a request will be sent to join the room.
        When the client joins the room the `on_room_join` event will be triggered.

        Args:
            name (str): The name for room.
            description (str): The description for the room.
            public (bool, optional): Whether or not the room should be publicly visible. Defaults to True.
        """
        if 2 <= len(name) <= 60:
            return await self.__fetch("create_room", dict(name=str(name), description=str(description),
                                                          privacy="public" if public else "private"))

        raise InvalidSize("The `name` property length should be 2-60 characters long.")

    async def join_room(self, room_id: str) -> None:
        """
        Send a request to join a room as a listener.

        Args:
            room_id (str): The ID of the room you want to join.
        """
        await self.__send("join_room", dict(roomId=str(room_id)))

    async def send(self, message: str, *, whisper: List[str] = None) -> None:
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

        await self.__send("send_room_chat_msg",
                          dict(whisperedTo=list(map(str, [] if whisper is None else whisper)),
                               tokens=parse_message(message)))

    async def ask_to_speak(self):
        """
        Request in the current room to speak.

        Raises:
            NoConnectionException: Gets raised when no room has been joined yet.   
        """
        if not self.room:
            raise NoConnectionException("No room has been joined yet.")
        await self.__send("ask_to_speak", {})

    async def make_mod(self, user: Union[str, User, BaseUser, UserPreview]):
        """
        Make a user in the room moderator.

        Args:
            user (Union[str, User, BaseUser, UserPreview]): The user which should be promoted to room moderator.
        """
        await self.__send("change_mod_status", dict(userId=str(user if isinstance(user, str) else user.id), value=True))

    async def un_mod(self, user: Union[str, User, BaseUser, UserPreview]):
        """
        Remove a user their room moderator permissions.

        Args:
            user (Union[str, User, BaseUser, UserPreview]): The user from which his permissions should be taken.
        """
        await self.__send("change_mod_status",
                          dict(userId=str(user if isinstance(user, str) else user.id), value=False))

    async def make_admin(self, user: Union[str, User, BaseUser, UserPreview]):
        """
        Make a user the room administrator/owner.
        NOTE: This action is irreversible.

        Args:
            user (Union[str, User, BaseUser, UserPreview]): The user which should be promoted to room admin.
        """
        await self.__send("change_room_creator", dict(userId=str(user if isinstance(user, str) else user.id)))

    async def set_listener(self, user: Union[str, User, BaseUser, UserPreview] = None):
        """
        Force a user to be a listener.

        Args:
            user (Union[str, User, BaseUser, UserPreview], optional): The user which should become a Listener.
                                                                      Defaults to the client.
        """
        if not user:
            user = self.user
        await self.__send("set_listener", dict(userId=str(user if isinstance(user, str) else user.id)))

    async def ban_chat(self, user: Union[str, User, BaseUser, UserPreview]):
        """
        Ban a user from speaking in the room.
        NOTE: This action can not be undone.

        Args:
            user (Union[str, User, BaseUser, UserPreview]): The user from which their chat permissions should be taken.
        """
        await self.__send("ban_from_room_chat", dict(userId=str(user if isinstance(user, str) else user.id)))

    async def ban(self, user: Union[str, User, BaseUser, UserPreview]):
        """
        Bans a user from a room.

        Args:
            user (Union[str, User, BaseUser, UserPreview]): The user who should be banned.
        """
        await self.__send("block_from_room", dict(userId=str(user if isinstance(user, str) else user.id)))

    async def unban(self, user: Union[str, User, BaseUser, UserPreview]):
        """
        Unban a user from the room.

        Args:
            user (Union[str, User, BaseUser, UserPreview]): The user who should be unbanned.
        """
        await self.__send("unban_from_room",
                          dict(userId=str((user if isinstance(user, str) else user.id)), fetch_id=uuid4()))

    async def add_speaker(self, user: Union[str, User, BaseUser, UserPreview]):
        """
        Accept a speaker request from a user.

        Args:
            user (Union[str, User, BaseUser, UserPreview]): The user who will has to be accepted.
        """
        await self.__send("add_speaker", dict(userId=str(user if isinstance(user, str) else user.id)))

    async def delete_message(self, message_id: str, user_id: str):
        """
        Deletes a message that has been sent by a user.

        Args:
            message_id (str): The id of the message that should be removed.
            user_id (str): The author of that message.
        """
        await self.__send("delete_room_chat_message", dict(messageId=str(message_id), userId=str(user_id)))

    async def wait_for(self, event_name: str, *, timeout: float = 60.0, check: callable = None, tick: float = 0.5,
                       fetch_arguments: Tuple[Any] = None) -> Union[Any, Tuple[Any]]:
        """
        Manually wait for an event.

        Args:
            event_name (str): The `on_...` event that should be waited for. (without the `on_` part)
            timeout (float, optional): How long the client will wait for a response.. Defaults to 60.0.
            check (callable, optional): A check which will be checked for the response. Defaults to None.
            tick (float, optional): The tick-rate for the fetch check iteration. Defaults to 0.5.
            fetch_arguments (tuple, optional): A fetch that should be executed before the wait.

        Raises:
            asyncio.TimeoutError: Gets thrown when the timeout has been reached.

        Returns:
            Union[Any, Tuple[Any]]: The parameter(s) of the event.
        """
        fetch_id = str(uuid4())
        self.__waiting_for[event_name] = [*self.__waiting_for[event_name],
                                          fetch_id] if event_name in self.__waiting_for else [fetch_id]

        if fetch_arguments:
            await self.__fetch(*fetch_arguments)

        passed = 0
        while True:
            await asyncio.sleep(tick)
            passed += tick

            if passed > timeout:
                self.__waiting_for[event_name].remove(fetch_id)
                raise asyncio.TimeoutError(
                    f"wait_for event timed out (for `{event_name}`)")
            elif fetch_id in self.__waiting_for_fetches:
                data = self.__waiting_for_fetches[fetch_id]
                if check is not None:
                    check_passed = False
                    for dt in data:
                        if check(*dt):
                            data = [dt]
                            check_passed = True
                            break
                        else:
                            data.remove(dt)

                    if not check_passed:
                        continue
                return (*data[0],) if len(data[0]) > 1 else data[0][0]

<<<<<<< HEAD
    async def fetch_user(self, argument: str, *, tick=0.5, timeout=60) -> User:
        """Currently only calls the DogeClient.get_user method, will implement user fetching in the future tho."""
        # try:
        return self.get_user(argument)
        # except MemberNotFound:
        #     op = "get_user_profile"
        #     fetch_id = str(uuid4())
        #
        #     async def user_fetch_task():
        #         await self.__send(op, dict(userId=argument), fetch_id=fetch_id)
        #         self.__fetches[fetch_id] = op
        #         self.__waiting_for[op] = [*self.__waiting_for[op], fetch_id] if op in self.__waiting_for else [fetch_id]
        #         passed = 0
        #         while True:
        #             print("fetch", passed)
        #             passed += tick
        #             await asyncio.sleep(tick)
        #             if passed > timeout:
        #                 self.__waiting_for[op].remove(fetch_id)
        #                 raise asyncio.TimeoutError(f"wait_for event timed out while fetching user `{argument}`")
        #             elif fetch_id in self.__waiting_for_fetches:
        #                 data = self.__waiting_for_fetches[fetch_id]
        #                 return data
        #
        #     task = asyncio.ensure_future(user_fetch_task())
        #     return await task

        # TODO: IMPLEMENT USER FETCHING
        #     async def waiter():
        #         return await self.wait_for("user_fetch", fetch_arguments=("get_user_profile", dict(userId=value)))

        #     user = await waiter()

        #     if user:
        #         return user
=======
    async def fetch_user(self, argument: str) -> Optional[User]:
        """
        Goes through the local cache to check if a user can be found.
        If no user has been found it will send a request to the server to try and fetch that user.
>>>>>>> 134de9535ed487551d22b01b4fb627c45f260f23

        Args:
            argument (str): The user argument

        Returns:
            User: A user if one got found in the cache, if none got found a None object will be returned.
        """
        try:
            return self.get_user(argument)
        except MemberNotFound:
            await self.__fetch("get_user_profile", dict(userId=argument))

    def get_user(self, argument: str) -> User:
        """
        Fetch a user from the current room.
        Filtering order:
            1. ID match
            2. username match
            3. display name match

        Args:
            argument (str): The user argument.

        Raises:
            MemberNotFound: The requested member could not be found

        Returns:
            User: The user that matches the params.
        """
        # TODO: Implement global caching instead of just the room
        parsed = parse_word(argument)
        if parsed["t"] == "mention":
            argument = argument[1::]

        argument = argument.lower()

        def check(attribute: str):
            for _user in self.room.users:
                if hasattr(_user, attribute):
                    attrs = getattr(_user, attribute)
                    if hasattr(attrs, "lower") and callable(getattr(attrs, "lower", False)) \
                            and attrs.lower() == argument:
                        return _user

        for attr in ["id", "username", "displayname"]:
            user = check(attr)
            if user:
                return user

        raise MemberNotFound(f"Could not find a member which matches the requested argument. (`{parsed['v']}`)")


Bot = DogeClient
