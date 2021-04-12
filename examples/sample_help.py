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

from inspect import getdoc
from dogehouse import DogeClient, event, command

class Client(DogeClient):
    @event
    async def on_ready(self):
        print("Client is ready!")
        await self.create_room("test")
    
    @command
    async def foo(self):
        """Sends a foo!"""
        await self.send("foo")
    
    @command
    async def bar(self):
        """Sends a bar!"""
        await self.send("bar")
        
    @command
    async def help(self, _, cmd: str = None):
        """
        The main help menu! Arguments: cmd = an optional argument which specifies a command, so that you can see the command description.
        """
        if cmd is None:
            await self.send(f"Hello, my prefix is {self.prefix} and my commands are: " + ", ".join(self.commands.keys()))
        else:
            cmd = cmd.lower()
            try:
                await self.send(f"`{cmd}` : {getdoc(self.commands[cmd][0])}")
            except IndexError:
                await self.send(f"Could not find '{cmd}'! Use {self.prefix}help to see all commands!")
    
if __name__ == "__main__":
    Client("token", "refresh_token").run()
