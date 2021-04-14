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

from dogehouse import DogeClient, event, command
from dogehouse.entities import Context


class CustomContext(Context):
    def __init__(self, my_client, ctx: Context):
        super().__init__(ctx.client, ctx.message)
        self.my_client = my_client

    async def send(self, message: str):
        """
        Sends a message to the client its current room!
        """
        await self.my_client.send(message)


def use_custom_context(func: callable):
    def wrapper(my_client, context: Context):
        return func(my_client, CustomContext(my_client, context))

    return wrapper


class MyClient(DogeClient):
    @event
    async def on_ready(self):
        print(f"Successfully connected as {self.user}!")
        await self.create_room("Hello World!")

    @command(name="sample")
    @use_custom_context
    async def custom_context(self, ctx: CustomContext):
        await ctx.send("Hi there!")


if __name__ == "__main__":
    MyClient("token", "refresh_token").run()
