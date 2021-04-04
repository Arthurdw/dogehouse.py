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

import dogehouse
from dogehouse.entities import Context, User
from dogehouse.ext.telemetry import dogegarden

from random import choice, randint
from asyncio import TimeoutError


class Client(dogehouse.DogeClient):
    @dogehouse.event
    async def on_ready(self):
        print("Client is ready!\n"
              "Creating new room!")
        await self.create_room("Fun chats!")

    @dogehouse.command(cooldown=5, aliases=["pepes", "pepe's"])
    async def pepe(self, ctx: Context, user: User = None, *, reason: str = None):
        await self.delete_message(ctx.message.id, ctx.author.id)

        if user is None:
            return await self.send("No user provided!", whisper=[ctx.author.id])

        reason = "literally no reason" if reason is None else reason

        await self.send(f"{user.mention} just got pepe'd by {ctx.author.mention} for {reason} " +
                        f" {choice([':PepeLaugh:', ':pepeD:', ':PepegeHmm:', ':pepeMeltdown:', ':pepeP:', ':PepeS:', ':PepeSpit:'])}" * randint(2, 16))
    
    @dogehouse.event
    async def on_cooldown_trigger(self, ctx: Context, command_name: str, _, time_left: float):
        await self.send(f"{ctx.author.mention} the `{command_name}` command is still on cooldown for {round(time_left, 2)}seconds!")

    @dogehouse.event
    async def on_error(self, error: Exception):
        if isinstance(error, dogehouse.exceptions.CommandNotFound):
            return
        elif isinstance(error, dogehouse.exceptions.MemberNotFound):
            return await self.send("Could not find that member!")
        await self.send(f"Oops, an {type(error).__name__} error got thrown!")
        
    @dogehouse.event
    async def on_speaker_request(self, user_id: str, _):
        await self.add_speaker(user_id)
    
    @dogehouse.event
    async def on_speaker_add(self, user_id: str, _, __):
        await self.send(f"Welcome to the stage {(await self.fetch_user(user_id)).mention}")
        

if __name__ == "__main__":
    Client("token", "refresh_token", prefix=[".", "!", "$"], telemetry=dogegarden).run()
