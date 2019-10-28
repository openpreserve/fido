#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Character handling routines for Format Identification for Digital Objects (FIDO)."""

# \a\b\n\r\t\v
# MdR: took out '<' and '>' out of _ordinary because they were converted to entities &lt;&gt;
# MdR: moved '!' from _ordinary to _special because it means "NOT" in the regex world. At this time no regex in any sig has a negate set, did this to be on the safe side
ORDINARY = frozenset(' "#%&\',-/0123456789:;=@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz~')
SPECIAL = '$()*+.?![]^\\{|}'  # Before: '$*+.?![]^\\{|}'
HEX = '0123456789abcdef'


def escape_char(c):
    """Add appropriate escape sequence to passed character c."""
    if c in '\n':
        return '\\n'
    if c == '\r':
        return '\\r'
    if c in SPECIAL:
        return '\\' + c
    (high, low) = divmod(ord(c), 16)
    return '\\x' + HEX[high] + HEX[low]


def escape(string):
    """Escape characters in pattern that are non-printable, non-ascii, or special for regexes."""
    return ''.join(c if c in ORDINARY else escape_char(c) for c in string)
