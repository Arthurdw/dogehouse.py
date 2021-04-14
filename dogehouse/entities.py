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

from datetime import datetime
from typing import Dict, List, Union, Optional

from dateutil.parser import isoparse
from represents import Represents as Repr

from .utils.convertors import Convertor
from .utils.parsers import parse_tokens_to_message as parse_tokens


class BaseUser(Convertor, Repr):
    def __init__(self, user_id: str, username: str, displayname: str, avatar_url: str):
        """
        Represents the most basic information of a fetched user.

        Args:
            user_id (str): The user their id.
            username (str): The username of the user. (Their mention name)
            displayname (str): The displayname of the user.
            avatar_url (str): The user their avatar URL.
        """
        self.id: str = user_id
        self.username: str = username
        self.displayname: str = displayname
        self.avatar_url: str = avatar_url
        self.mention: str = f"@{username}"

    def __str__(self):
        return self.username

    @staticmethod
    def from_dict(data: dict):
        """
        Parses a BaseUser object from a dictionary.

        Args:
            data (dict): The parsed json websocket response.

        Returns:
            BaseUser: A parsed BaseUser object which contains the data from the dictionary.
        """
        return BaseUser(data.get("userId"), data.get("username"), data.get("displayName"), data.get("avatarUrl"))

    @classmethod
    async def convert(cls, ctx, param, argument: str):
        return (await cls._get_user(cls.__name__, ctx.client, param, argument)).to_base_user()


class Permission(Repr):
    def __init__(self, asked_to_speak: bool, is_mod: bool, is_admin: bool, is_speaker: bool):
        """
        Represents a user their permissions

        Args:
            asked_to_speak (bool): Whether the user has requested to speak.
            is_mod (bool): Whether the user is a room moderator.
            is_admin (bool): Whether the user is a room admin.
            is_speaker (bool): Whether the user is a speaker.
        """
        self.asked_to_speak: bool = asked_to_speak
        self.is_mod: bool = is_mod
        self.is_admin: bool = is_admin
        self.is_speaker: bool = is_speaker

    @staticmethod
    def from_dict(data: dict):
        """
        Parses permissions from a dictionary.

        Args:
            data (dict): The parsed json websocket response.

        Returns:
            Permission: A parsed Permission object which contains the data from the dictionary.
        """
        if data:
            return Permission(data.get("askedToSpeak", False), data.get("isMod", False), False,
                              data.get("isSpeaker", False))
        return Permission(False, False, False, False)


class User(BaseUser, Repr):
    def __init__(self, user_id: str, username: str, displayname: str, avatar_url: str, bio: str, last_seen: str,
                 online: bool,
                 following: bool, room_permissions: Permission, num_followers: int, num_following: int,
                 follows_me: bool, current_room_id: str):
        """
        Represents a dogehouse.tv user.

        Args:
            user_id (str): The user their id.
            username (str): The username of the user. (Their mention name)
            displayname (str): The displayname of the user.
            avatar_url (str): The user their avatar URL.
            bio (str): The user their biography.
            last_seen (str): When the user was last online.
            online (bool): Whether or not the user is currently online
            following (bool): Whether or not the client is following this user.
            room_permissions (Permission): The user their permissions for the current room.
            num_followers (int): The amount of followers the user has.
            num_following (int): The amount of users this user is following.
            follows_me (bool): Whether or not the user follows the client.
            current_room_id (str): The user their current room id.
        """
        super().__init__(user_id, username, displayname, avatar_url)
        self.bio: str = bio
        self.last_seen: datetime = isoparse(last_seen)
        self.online: bool = online
        self.following: bool = following
        self.room_permissions: Permission = room_permissions
        self.num_followers: int = num_followers
        self.num_following: int = num_following
        self.follows_me: bool = follows_me
        self.current_room_id: str = current_room_id

    def __str__(self):
        return self.username

    @staticmethod
    def from_dict(data: dict):
        """
        Parses a User object from a dictionary.

        Args:
            data (dict): The parsed json websocket response.

        Returns:
            User: A parsed User object which contains the data from the dictionary.
        """
        return User(data.get("id"), data.get("username"), data.get("displayName"), data.get("avatarUrl"),
                    data.get("bio"), data.get("lastOnline"),
                    data.get("online"), data.get("youAreFollowing"), Permission.from_dict(data.get("roomPermissions")),
                    data.get("numFollowers"),
                    data.get("numFollowing"), data.get("followsYou"), data.get("currentRoomId"))

    def to_base_user(self) -> BaseUser:
        """
        Convert a user object to a base user object.
        This is intended for internal use (Convertors), as you can access all BaseUser properties from the user object.

        Returns:
            BaseUser: The newly created BaseUser object, which is derived from the current object.
        """
        return BaseUser(self.id, self.username, self.displayname, self.avatar_url)

    @classmethod
    async def convert(cls, ctx, param, argument: str):
        return await cls._get_user(cls.__name__, ctx.client, param, argument)


class UserPreview(Convertor, Repr):
    def __init__(self, user_id: str, displayname: str, num_followers: int):
        """
        Represents a user-preview from the Client.rooms users list.

        Args:
            user_id (string): The user their id.
            displayname (string): The display name of the user.
            num_followers (integer): The amount of followers the user has.
        """
        self.id: str = user_id
        self.displayname: str = displayname
        self.num_followers: int = num_followers

    def __str__(self):
        return self.displayname

    @staticmethod
    def from_dict(data: dict):
        """
        Parses a UserPreview object from a dictionary.

        Args:
            data (dict): The parsed json websocket response.

        Returns:
            UserPreview: A parsed UserPreview object which contains the data from the dictionary.
        """
        return UserPreview(data["id"], data["displayName"], data["numFollowers"])

    @classmethod
    async def convert(cls, ctx, param, argument: str):
        user = await cls._get_user(cls.__name__, ctx.client, param, argument)
        return UserPreview(user.id, user.displayname, user.num_followers)


class Room(Repr):
    def __init__(self, room_id: str, creator_id: str, name: str, description: str, created_at: str, is_private: bool,
                 count: int, users: List[Union[User, UserPreview]]):
        """
        Represents a dogehouse.tv room.

        Args:
            room_id (str): The id of the room.
            creator_id (str): The id of the user who created the room.
            name (str): The name of the room.
            description (str): The description of the room.
            created_at (str): When the room was created.
            is_private (bool): Whether or not the room is a private or public room
            count (int): The amount of users the room has.
            users (List[Union[User, UserPreview]]): A list of users whom reside in this room.
        """
        self.id: str = room_id
        self.creator_id: str = creator_id
        self.name: str = name
        self.description: str = description
        self.created_at: datetime = isoparse(created_at)
        self.is_private: bool = is_private
        self.count: int = count
        self.users: List[Union[User, UserPreview]] = users

    def __str__(self):
        return self.name

    def __sizeof__(self):
        return self.count

    @staticmethod
    def from_dict(data: dict):
        """
        Parses a Room object from a dictionary.

        Args:
            data (dict): The parsed json websocket response.

        Returns:
            Room: A parsed room object which contains the data from the dictionary.
        """
        return Room(data["id"], data["creatorId"], data["name"], data["description"], data["inserted_at"],
                    data["isPrivate"], data["numPeopleInside"],
                    list(map(UserPreview.from_dict, data["peoplePreviewList"])))


class Message(Repr):
    def __init__(self, message_id: str, tokens: List[Dict[str, str]], is_whisper: bool, created_at: str,
                 author: BaseUser):
        """
        Represents a message that gets sent in the chat.

        Args:
            message_id (str): The message its id
            tokens (List[Dict[str, str]]): The message content tokens, for if you want to manually parse the message.
            is_whisper (bool): Whether or not the message was whispered to the client.
            created_at (str): When the message was created.
            author (BaseUser): The user who sent the message
        """
        self.id = message_id
        self.tokens = tokens
        self.is_whisper = is_whisper
        self.created_at = isoparse(created_at)
        self.author = author
        self.content = parse_tokens(tokens)

    def __str__(self):
        return self.content

    @staticmethod
    def from_dict(data: dict):
        """
        Parses a Message object from a dictionary.

        Args:
            data (dict): The parsed json websocket response.

        Returns:
            Message: A parsed message object which contains the data from the dictionary.
        """
        return Message(data["id"], data["tokens"], data["isWhisper"], data["sentAt"], BaseUser.from_dict(data))


class Client(Repr):
    def __init__(self, user: Optional[User], room: Optional[Union[Room, str]], rooms: List[Room], prefix: List[str]):
        """
        The base client for the DogeHouse client.

        Args:
            user (Optional User): The client its user object.
            room (Optional Room): The current room in which the Client resides. Is `None` if no room has been joined.
            rooms (List[Room]): A collection of all the rooms which the client has cached. This gets fetched
                                automatically if no room has been joined. You can also update this using the
                                `async DogeClient.get_top_public_rooms` method.
            prefix (List[str]): A collection of prefixes to which the client should respond.
        """
        self.user: Optional[User] = user
        self.room: Optional[Union[Room, str]] = room
        self.rooms: List[Room] = rooms
        self.prefix: List[str] = prefix


class Context(Repr):
    def __init__(self, client: Client, message: Message):
        """
        Represents a message its context.

        Args:
            client (Client): The current client.
            message (Message): The message that was sent.
        """
        self.client: Client = client
        self.bot: Client = self.client
        self.message: Message = message
        self.author: BaseUser = message.author
