"""Common utilities for FIDO."""


from .constants import ORDINARY, SPECIAL, HEX


def _escape_char(c):
    if c in '\n':
        return '\\n'
    if c == '\r':
        return '\\r'
    if c in SPECIAL:
        return '\\' + c
    (high, low) = divmod(ord(c), 16)
    return '\\x' + HEX[high] + HEX[low]


def escape(string):
    """Escape characters in pattern ``string``.

    Escape all characters that are non-printable, non-ascii, or special for
    regexes.
    """
    return ''.join(c if c in ORDINARY else _escape_char(c) for c in string)
