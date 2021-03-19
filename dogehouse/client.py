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
from json import loads
from typing import Awaitable
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
from logging import debug

from .utils import Repr
from .config import apiUrl, heartbeatInterval
from .exceptions import NoConnectionException


class DogeClient(Repr):
    def __init__(self, token: str, refresh_token: str):
        self.__token = token
        self.__refresh_token = refresh_token
        self.__socket = None
        self.__active = False
        self.__eventHandlers = []
        
    async def __main(self):
        """This instance handles the websocket connections."""
        try:
            debug("Connecting with dogehouse API")
            async with websockets.connect(apiUrl) as ws:
                debug("dogehouse API connection established successfully")
                self.__active = True 
                self.__socket = ws
                # print(loads(await ws.recv()))
                
                # while self.__active:
                #     for handler in self.__eventHandlers:
                #         await handler(loads(await ws.recv()))
        except ConnectionClosedOK:
            debug("Dogehouse API connection closed peacefully.")
            self.__active = False
        # except ConnectionClosedError:
            
    
    def run(self):
        """Establishes a connection to the websocket servers."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.__main())
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
