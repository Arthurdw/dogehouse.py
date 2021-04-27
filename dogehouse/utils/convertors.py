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

from ..exceptions import MemberNotFound
from asyncio.exceptions import TimeoutError


class Convertor:
    basic_types = (str, int, float, bool)

    @staticmethod
    def _member_not_found(method: str, argument: str):
        raise MemberNotFound(
            f"Could not find/create {method} using the {method} convertor for argument `{argument}`")

    @staticmethod
    async def _get_user(convertor: str, client, param, argument):
        if argument == param.default:
            return argument

        try:
            user = await client.fetch_user(argument)

            # if user is None:
            #     user = await client.wait_for("user_fetch", timeout=60)
            return user
        except (MemberNotFound, TimeoutError):
            Convertor._member_not_found(convertor, argument)

    @staticmethod
    def handle_basic_types(param, argument):
        if argument == param.default:
            return argument

        try:
            return Convertor.convert_basic_types(argument, param.annotation)
        except TypeError:
            return argument

    @staticmethod
    def convert_basic_types(value, out: type):
        if not isinstance(out, type):
            raise TypeError(f"The out value must be a type. But '{out}' was supplied!")

        if isinstance(value, out):
            return value

        if not isinstance(out, Convertor.basic_types):
            raise TypeError(f"The 'out' parameter must be one of the basic types. But '{out.__name__}' was supplied!"
                            f"(basic types: {', '.join(t.__name__ for t in Convertor.basic_types)})")

        if not isinstance(value, Convertor.basic_types):
            raise TypeError(f"Can not convert '{type(value)}' into {out}, because it is not one of the basic types."
                            f"(basic types: {', '.join(t.__name__ for t in Convertor.basic_types)})")

        return out(round(float(value)) if issubclass(out, int) else value)
