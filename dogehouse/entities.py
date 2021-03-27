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

from .utils import Repr

from datetime import datetime
from dateutil.parser import isoparse
from typing import List, Dict, List, Union


class BaseUser(Repr):
    def __init__(self, id: str, username: str, displayname: str, avatar_url: str):
        self.id: str = id
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


class User(BaseUser, Repr):
    def __init__(self, id: str, username: str, displayname: str, avatar_url: str, bio: str, last_seen: str):
        super().__init__(id, username, displayname, avatar_url)
        self.bio: str = bio
        self.last_seen: datetime = isoparse(last_seen)

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
        return User(data.get("id"), data.get("username"), data.get("displayname"), data.get("avatarUrl"), data.get("bio"), data.get("lastOnline"))


class UserPreview(Repr):
    def __init__(self, id: str, displayname: str, num_followers: int):
        self.id: str = id
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
            UserPreview: A parsed userpreview object which contains the data from the dictionary.
        """
        return UserPreview(data["id"], data["displayName"], data["numFollowers"])


class Room(Repr):
    def __init__(self, id: str, creator_id: str, name: str, description: str, created_at: str, is_private: bool, count: int, users: List[UserPreview]):
        self.id: str = id
        self.creator_id: str = creator_id
        self.name: str = name
        self.description: str = description
        self.created_at: datetime = isoparse(created_at)
        self.is_private: bool = is_private
        self.count: int = count
        self.users: List[Union[User, UserPreview]] = users

    @staticmethod
    def from_dict(data: dict):
        """
        Parses a Room object from a dictionary.

        Args:
            data (dict): The parsed json websocket response.

        Returns:
            Room: A parsed room object which contains the data from the dictionary.
        """
        return Room(data["id"], data["creatorId"], data["name"], data["description"], data["inserted_at"], data["isPrivate"], data["numPeopleInside"],
                    list(map(UserPreview.from_dict, data["peoplePreviewList"])))


class Message(Repr):
    def __init__(self, id: str, tokens: List[Dict[str, str]], is_wisper: bool, created_at: str, author: BaseUser):
        self.id = id
        self.tokens = tokens
        self.is_wisper = is_wisper
        self.created_at = isoparse(created_at)
        self.author = author
        self.content = self.__convert_tokens()
    
    def __str__(self):
        return self.content
    
    def __convert_tokens(self) -> str:
        """Converts the tokens to a proper message"""
        content = []
        for token in self.tokens:
            if token["t"] == "mention":
                content.append(f"@{token['v']}")
            elif token["t"] == "emote":
                content.append(f":{token['v']}:")
            else:
                content.append(token["v"])
        
        return " ".join(content)
    
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
    def __init__(self, user: User, room: Room, rooms: List[Room], prefix: List[str]):
        self.user: User = None
        self.room: Room = room
        self.rooms: List[Room] = rooms
        self.prefix: List[str] = prefix    


class Context(Repr):
    def __init__(self, client: Client, message: Message):
        self.client: Client = client
        self.bot: Client = self.client
        self.message: Message = message
        self.author: BaseUser = message.author
        