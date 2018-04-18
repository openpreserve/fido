import re

import pytest

from fido.prepare import convert_to_regex


def binrep_convert(byt):
    """Returns a binary string representation of an integer.

    The returned string has '0' padding on the left to make it minimally eight
    digits in length.
    """
    return bin(byt)[2:].zfill(8)


@pytest.mark.parametrize(
    ('pronom_bytesequence', 'matches_predicate'),
    (
        # ANY BITMASKS, e.g., ~FF
        # ~07 = 00000111. Match bytes with any of the first three bits set.
        ('~07', lambda binrep: '1' in binrep[-3:]),
        # ~7f = 01111111. Match bytes with any of the first seven bits set.
        ('~7f', lambda binrep: '1' in binrep[-7:]),
        # ~00 = 00000000. Match no bytes.
        # TODO: is it possible to write a regular expression that matches no
        # bytes? The regex pattern returned here matches ANY byte...
        ('~00', lambda binrep: True),

        # NEGATED ANY BITMASKS, e.g., [!~FF]
        # [!~80] = 10000000. Match bytes without the last bit set.
        ('[!~80]', lambda binrep: binrep.startswith('0')),
        # [!~ff] = 11111111. Match bytes without any of the bitmask bits set.
        ('[!~ff]', lambda binrep: binrep == '00000000'),
        # [!~87] = 10000111.
        ('[!~87]', lambda br: br.startswith('0') and br.endswith('000')),

        # ALL BITMASKS, e.g., &FF
        # &07 = 00000111. Match bytes with all first three bits set.
        ('&07', lambda binrep: binrep.endswith('111')),
        # &7f = 01111111. Match bytes with all first seven bits set.
        ('&7f', lambda binrep: binrep.endswith('1111111')),
        # &00 = 00000000. Matches any byte.
        ('&00', lambda binrep: True),

        # NEGATED ALL BITMASKS, e.g., [!&FF]
        # !&80 = 10000000. Match bytes without the last bit set.
        ('[!&80]', lambda binrep: binrep.startswith('0')),
        # !&87 = 10000111. Match all bytes that don't have the first three bits
        # set and the last bit set also.
        ('[!&87]', lambda br: not (br.startswith('1') and br.endswith('111'))),
        # !&ff = 11111111. Match all bytes except 255.
        ('[!&ff]', lambda binrep: not binrep == '11111111'),
    )
)
def test_bitmasks(pronom_bytesequence, matches_predicate):
    patt = convert_to_regex(pronom_bytesequence)
    for byt in range(0x100):
        binrep = binrep_convert(byt)
        if matches_predicate(binrep):
            assert re.search(patt, chr(byt))
        else:
            assert not re.search(patt, chr(byt))


@pytest.mark.parametrize(
    ('pronom_bytesequence', 'input_', 'matches_bool'),
    (
        # These are good:
        ('ab{3}cd(01|02|03)~07ff', '\xAB\xDD\xDD\xDD\xCD\x02\x11\xFF', True),
        ('ab{3}cd(01|02|03)~07ff', '\xAB\xDD\xDD\xDD\xCD\x03\x11\xFF', True),
        ('ab{3}cd(01|02|03)~07ff', '\xAB\xDD\xDD\xDD\xCD\x02\xFE\xFF', True),

        # Bad because missing three anythings between AB and CD
        ('ab{3}cd(01|02|03)~07ff', '\xAB\xDD\xDD\xCD\x02\x11\xFF', False),

        # Bad because not at start of string
        ('ab{3}cd(01|02|03)~07ff', '\xDA\xAB\xDD\xDD\xDD\xCD\x02\x11\xFF', False),

        # Bad because 04 is not in (01|02|03)
        ('ab{3}cd(01|02|03)~07ff', '\xAB\xDD\xDD\xDD\xCD\x04\x11\xFF', False),

        # Bad because 18 is not in ~07
        ('ab{3}cd(01|02|03)~07ff', '\xAB\xDD\xDD\xDD\xCD\x02\x18\xFF', False),
    )
)
def test_heterogenous_sequences(pronom_bytesequence, input_, matches_bool):
    """Tests potential PRONOM sequences in their fullness.

    This lets us monitor syntactical components playing nicely with one other.
    """
    patt = convert_to_regex(pronom_bytesequence)
    if matches_bool:
        assert re.search(patt, input_)
    else:
        assert not re.search(patt, input_)
