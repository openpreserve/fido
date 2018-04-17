import re

from fido.prepare import convert_to_regex


def test_any_bitmasks():
    # ~07 = 00000111. Match bytes with any of the first three bits set.
    pronom_bytesequence = '~07'
    patt = convert_to_regex(pronom_bytesequence)
    for byt in range(0x100):
        binrep = bin(byt)[2:].zfill(8)
        if '1' in binrep[-3:]:
            assert re.search(patt, chr(byt))
        else:
            assert not re.search(patt, chr(byt))

    # ~7f = 01111111. Match bytes with any of the first seven bits set.
    pronom_bytesequence = '~7f'
    patt = convert_to_regex(pronom_bytesequence)
    for byt in range(0x100):
        binrep = bin(byt)[2:].zfill(8)
        if '1' in binrep[-7:]:
            assert re.search(patt, chr(byt))
        else:
            assert not re.search(patt, chr(byt))

    # ~00 = 00000000. Match no bytes.
    # TODO: is it possible to write a regular expression that matches no bytes?
    # The regex pattern returned here matches ANY byte...
    pronom_bytesequence = '~00'
    patt = convert_to_regex(pronom_bytesequence)
    assert patt == r'(?s)\A()'
    for byt in range(0x100):
        binrep = bin(byt)[2:].zfill(8)
        char = chr(byt)
        assert re.search(patt, char)


def test_neg_any_bitmasks():
    # [!~80] = 10000000. Match bytes without the last bit set.
    pronom_bytesequence = '[!~80]'
    patt = convert_to_regex(pronom_bytesequence)
    for byt in range(0x100):
        binrep = bin(byt)[2:].zfill(8)
        if binrep.startswith('0'):
            assert re.search(patt, chr(byt))
        else:
            assert not re.search(patt, chr(byt))

    # [!~ff] = 11111111. Match bytes without any of the bitmask bits set.
    pronom_bytesequence = '[!~ff]'
    patt = convert_to_regex(pronom_bytesequence)
    for byt in range(0x100):
        if byt == 0:
            assert re.search(patt, chr(byt))
        else:
            assert not re.search(patt, chr(byt))

    # [!~87] = 10000111.
    pronom_bytesequence = '[!~87]'
    patt = convert_to_regex(pronom_bytesequence)
    for byt in range(0x100):
        binrep = bin(byt)[2:].zfill(8)
        if binrep.startswith('0') and binrep.endswith('000'):
            assert re.search(patt, chr(byt))
        else:
            assert not re.search(patt, chr(byt))


def test_all_bitmasks():
    # &07 = 00000111. Match bytes with all first three bits set.
    pronom_bytesequence = '&07'
    patt = convert_to_regex(pronom_bytesequence)
    for byt in range(0x100):
        binrep = bin(byt)[2:].zfill(8)
        if binrep.endswith('111'):
            assert re.search(patt, chr(byt))
        else:
            assert not re.search(patt, chr(byt))

    # &7f = 01111111. Match bytes with all first seven bits set.
    pronom_bytesequence = '&7f'
    patt = convert_to_regex(pronom_bytesequence)
    for byt in range(0x100):
        binrep = bin(byt)[2:].zfill(8)
        if binrep.endswith('1111111'):
            assert re.search(patt, chr(byt))
        else:
            assert not re.search(patt, chr(byt))

    # &00 = 00000000. Matches any byte.
    pronom_bytesequence = '&00'
    patt = convert_to_regex(pronom_bytesequence)
    for byt in range(0x100):
        binrep = bin(byt)[2:].zfill(8)
        assert re.search(patt, chr(byt))


def test_neg_all_bitmasks():

    # !&80 = 10000000. Match bytes without the last bit set.
    pronom_bytesequence = '[!&80]'
    patt = convert_to_regex(pronom_bytesequence)
    for byt in range(0x100):
        binrep = bin(byt)[2:].zfill(8)
        if binrep.startswith('0'):
            assert re.search(patt, chr(byt))
        else:
            assert not re.search(patt, chr(byt))

    # !&87 = 10000111. Match all bytes that don't have the first three bits set
    # and the last bit set also.
    pronom_bytesequence = '[!&87]'
    patt = convert_to_regex(pronom_bytesequence)
    for byt in range(0x100):
        binrep = bin(byt)[2:].zfill(8)
        if binrep.startswith('1') and binrep.endswith('111'):
            assert not re.search(patt, chr(byt))
        else:
            assert re.search(patt, chr(byt))

    # !&ff = 11111111. Match all bytes except 255.
    pronom_bytesequence = '[!&ff]'
    patt = convert_to_regex(pronom_bytesequence)
    for byt in range(0x100):
        if byt == 255:
            assert not re.search(patt, chr(byt))
        else:
            assert re.search(patt, chr(byt))
