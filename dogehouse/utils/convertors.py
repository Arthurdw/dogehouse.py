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

from .parsers import parse_word_to_token

from ..exceptions import MemberNotFound


class Convertor:
    @staticmethod
    def _member_not_found(method: str, argument: str):
        raise MemberNotFound(
            f"Could not find/create {method} using the {method} convertor for argument `{argument}`")

    @staticmethod
    async def _get_user(convertor: str, client, param, argument):
        if argument == param.default:
            return argument

        try:
            return await client.fetch_user(argument)
        except MemberNotFound:
            Convertor._member_not_found(convertor, argument)
            
    @staticmethod
    def _handle_basic_types(param, argument):
        if argument == param.default:
            return argument
        
        if issubclass(param.annotation, (str, int, float, bool)):
            return param.annotation(round(float(argument)) if issubclass(param.annotation, int) else argument) 
        
        return argument
        
        
