import os
import re

import pytest

from fido.prepare import FormatInfo, absolute_max_offset, convert_to_regex

PRONOM_RECORDS = os.path.join(os.path.dirname(__file__), 'fixtures', 'pronom')


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


def converted_patterns(record_name):
    """Convert a real PRONOM v125 record and return its (position, regex) pairs."""
    with open(os.path.join(PRONOM_RECORDS, record_name), 'rb') as record:
        fido_format = FormatInfo(None).parse_pronom_xml(record)
    return [(pattern.findtext('position'), pattern.findtext('regex')) for pattern in fido_format.iter('pattern')]


@pytest.mark.parametrize(
    ('offset', 'max_offset', 'expected'),
    (
        ('3000', '700', '3700'),
        ('1', '2', '3'),
        ('0', '8', '8'),
        ('', '5', '5'),
        ('4', '', ''),
        ('4', '0', '0'),
    )
)
def test_absolute_max_offset(offset, max_offset, expected):
    assert absolute_max_offset(offset, max_offset) == expected


def test_bof_window_runs_from_offset_to_offset_plus_max_offset():
    """fmt/1202 has Offset 1 and MaxOffset 2, so DROID matches its sequence at offsets 1 to 3."""
    [(position, regex)] = converted_patterns('puid.fmt.1202.xml')
    sequence = 'GUYMAGER ACQUISITION INFO FILE'
    assert position == 'BOF'
    for offset in (1, 2, 3):
        assert re.search(regex, '\x00' * offset + sequence), 'expected a match at offset {}'.format(offset)
    for offset in (0, 4):
        assert not re.search(regex, '\x00' * offset + sequence), 'expected no match at offset {}'.format(offset)


def test_max_offset_below_offset_converts_to_a_valid_regex():
    """fmt/1558 has Offset 3000 and MaxOffset 700, which used to convert to the invalid .{3000,700}."""
    [(position, regex)] = converted_patterns('puid.fmt.1558.xml')
    sequence = 'C64/C128 SELF EXTRACTING LHARCHIVE'
    re.compile(regex)
    for offset in (3000, 3370, 3700):
        assert re.search(regex, '\x00' * offset + sequence), 'expected a match at offset {}'.format(offset)
    for offset in (2999, 3701):
        assert not re.search(regex, '\x00' * offset + sequence), 'expected no match at offset {}'.format(offset)


def test_eof_window_runs_from_offset_to_offset_plus_max_offset():
    """fmt/1646's EOF sequence has Offset 109 and MaxOffset 11, so it ends 109 to 120 bytes before EOF."""
    regex = dict(converted_patterns('puid.fmt.1646.xml'))['EOF']
    sequence = '\x02\xff\xfe\xff\x05A\x00r\x00i\x00a\x00l'
    for trailing in (109, 115, 120):
        assert re.search(regex, sequence + '\x00' * trailing), 'expected a match {} bytes before EOF'.format(trailing)
    for trailing in (108, 121):
        assert not re.search(regex, sequence + '\x00' * trailing), 'expected no match {} bytes before EOF'.format(trailing)
