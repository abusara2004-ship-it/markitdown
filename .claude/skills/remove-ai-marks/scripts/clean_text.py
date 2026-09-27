#!/usr/bin/env python3
"""Strip hidden Unicode marks often left in AI-generated or copy-pasted text.

Usage: clean_text.py [FILE]   (reads stdin when FILE is omitted)
"""
import sys

REMOVE = dict.fromkeys(map(ord, "​‌‍⁠﻿­"), None)
REPLACE = {
    " ": " ", " ": " ", " ": " ",
    "‘": "'", "’": "'", "“": '"', "”": '"',
}


def clean(text: str) -> str:
    text = text.translate(REMOVE)
    for old, new in REPLACE.items():
        text = text.replace(old, new)
    return text


if __name__ == "__main__":
    src = open(sys.argv[1], encoding="utf-8") if len(sys.argv) > 1 else sys.stdin
    sys.stdout.write(clean(src.read()))
