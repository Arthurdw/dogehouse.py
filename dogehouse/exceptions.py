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


class DogehouseException(Exception):
    """The base exceptions object."""
    pass


class InvalidAccessToken(DogehouseException):
    """The exception that gets raised when an invalid access token is present."""
    def __init__(self):
        message = "An invalid access token is present."
        super(InvalidAccessToken, self).__init__(message)


class ConnectionTaken(DogehouseException):
    """The exception that gets raised when another client has already taken the connection."""
    def __init__(self):
        message = "Another client has already taken the connection."
        super(ConnectionTaken, self).__init__(message)


class NoConnectionException(DogehouseException):
    """The exception that gets raised when an action gets executed while no connection has been established yet."""
    def __init__(self, message: str = None):
        message = message if message else "No connection has been established yet."
        super(NoConnectionException, self).__init__(message)


class InvalidSize(DogehouseException):
    """The exception that gets raised when a variable is not within the requested size."""
    pass


class NotEnoughArguments(DogehouseException):
    """Not enough arguments where provided."""
    pass


class CommandNotFound(DogehouseException):
    """Command is not registered."""
    pass


class MemberNotFound(DogehouseException):
    """The requested member was not found!"""
    pass

class CommandAlreadyDefined(DogehouseException):
    """The command has already been defined by another name or alias."""
    pass 
