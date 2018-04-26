"""Constants for FIDO."""

# \a\b\n\r\t\v
# MdR: took out '<' and '>' out of _ordinary because they were converted to
# entities &lt;&gt;
# MdR: moved '!' from _ordinary to _special because it means "NOT" in the regex
# world. At this time no regex in any sig has a negate set, did this to be on
# the safe side
ORDINARY = frozenset(
    ' "#%&\',-/0123456789:;=@ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    '_abcdefghijklmnopqrstuvwxyz~')

SPECIAL = '$()*+.?![]^\\{|}'

HEX = '0123456789abcdef'
