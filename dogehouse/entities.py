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

from typing import List
from dateutil.parser import isoparse


class User(Repr):
    def __init__(self, id: str, username: str, displayname: str, avatar_url: str, bio: str, last_seen: str):
        self.id = id
        self.username = username
        self.displayname = displayname
        self.avatar_url = avatar_url
        self.bio = bio
        self.last_seen = isoparse(last_seen)


class UserPreview(Repr):
    def __init__(self, id: str, displayname: str, num_followers: int):
        self.id = id
        self.displayname = displayname
        self.num_followers = num_followers


class Room(Repr):
    def __init__(self, id: str, creator_id: str, name: str, description: str, created_at: str, is_private: bool, count: int, users: List[UserPreview]):
        self.id = id
        self.creator_id = creator_id
        self.name = name
        self.description = description
        self.created_at = isoparse(created_at)
        self.is_private = is_private
        self.count = count
        self.users = users
