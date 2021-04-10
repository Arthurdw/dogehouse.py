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

from typing import List, Dict

message_formats = {
    "mention": "@{}",
    "emote": ":{}:",
    "block": "`{}`"
}


def parse_sentence_to_tokens(sentence: str) -> List[Dict[str, str]]:
    """
    Parse a sentence to a list of tokens.

    Args:
        sentence (str): The sentence/message that should be parsed

    Returns:
        List[Dict[str, str]]: A proper collection of usable tokens
    """
    return list(map(parse_word_to_token, str(sentence).split(" ")))


def parse_word_to_token(word: str) -> Dict[str, str]:
    """
    Convert a word into a dogehouse message token.

    Args:
        word (str): The word that should be parsed.

    Returns:
        Dict[str, str]: A token which represents the word.
    """
    # TODO: Do some regex magic instead of this
    t, v = "text", str(word)
    if v.startswith("@") and len(v) >= 3:
        t = "mention"
        v = v[1:]
    elif v.startswith("http") and len(v) >= 8:
        t = "link"
    elif v.startswith(":") and v.endswith(":") and len(v) >= 3:
        t = "emote"
        v = v[1:-1]
    elif v.startswith("`") and v.endswith("`") and len(v) >= 3:
        t = "block"
        v = v[1:-1]

    return dict(t=t, v=v)


def parse_tokens_to_message(tokens: List[Dict[str, str]]) -> str:
    """
    Parse a collection of tokens into a usable/readable string.

    Args:
        tokens (List[Dict[str, str]]): The message tokens that should be parsed.

    Returns:
        str: The parsed collection its content
    """
    return " ".join(map(parse_token_to_message, tokens))


def parse_token_to_message(token: Dict[str, str]) -> str:
    v = token["v"]
    for k, fm in message_formats.items():
        if token["t"] == k:
            v = fm.format(token["v"])
            break
    return v
