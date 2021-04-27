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

from asyncio.exceptions import TimeoutError

from dogehouse import DogeClient, command, event
from dogehouse.entities import Context


class Client(DogeClient):
    @event
    async def on_ready(self):
        await self.create_room("Sample user fetch")

    @command
    async def test(self, ctx: Context, *, argument: str):
        user = await self.fetch_user(argument)

        if user is None:
            try:
                user = await self.wait_for("user_fetch")
            except TimeoutError:
                return await self.send("Could not find that user!")

        await self.send(f"{user.username} | {user.id}", whisper=[ctx.author.id])


if __name__ == "__main__":
    Client("token", "refresh token").run()
