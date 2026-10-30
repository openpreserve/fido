import os
import re
from types import SimpleNamespace
from xml.etree import ElementTree as XET
import hashlib
import io
import urllib.error

import pytest

from fido.pronom import prepare
from fido.pronom.prepare import absolute_max_offset, convert_to_regex

TEST_DATA_PRONOM = os.path.normpath(os.path.join(__file__, "..", "test_data/pronom"))


def binrep_convert(byt):
    """Returns a binary string representation of an integer.

    The returned string has '0' padding on the left to make it minimally eight
    digits in length.
    """
    return bin(byt)[2:].zfill(8)


@pytest.mark.parametrize(
    ("pronom_bytesequence", "matches_predicate"),
    (
        # ANY BITMASKS, e.g., ~FF
        # ~07 = 00000111. Match bytes with any of the first three bits set.
        ("~07", lambda binrep: "1" in binrep[-3:]),
        # ~7f = 01111111. Match bytes with any of the first seven bits set.
        ("~7f", lambda binrep: "1" in binrep[-7:]),
        # ~00 = 00000000. Match no bytes.
        # TODO: is it possible to write a regular expression that matches no
        # bytes? The regex pattern returned here matches ANY byte...
        ("~00", lambda binrep: True),
        # NEGATED ANY BITMASKS, e.g., [!~FF]
        # [!~80] = 10000000. Match bytes without the last bit set.
        ("[!~80]", lambda binrep: binrep.startswith("0")),
        # [!~ff] = 11111111. Match bytes without any of the bitmask bits set.
        ("[!~ff]", lambda binrep: binrep == "00000000"),
        # [!~87] = 10000111.
        ("[!~87]", lambda br: br.startswith("0") and br.endswith("000")),
        # ALL BITMASKS, e.g., &FF
        # &07 = 00000111. Match bytes with all first three bits set.
        ("&07", lambda binrep: binrep.endswith("111")),
        # &7f = 01111111. Match bytes with all first seven bits set.
        ("&7f", lambda binrep: binrep.endswith("1111111")),
        # &00 = 00000000. Matches any byte.
        ("&00", lambda binrep: True),
        # NEGATED ALL BITMASKS, e.g., [!&FF]
        # !&80 = 10000000. Match bytes without the last bit set.
        ("[!&80]", lambda binrep: binrep.startswith("0")),
        # !&87 = 10000111. Match all bytes that don't have the first three bits
        # set and the last bit set also.
        ("[!&87]", lambda br: not (br.startswith("1") and br.endswith("111"))),
        # !&ff = 11111111. Match all bytes except 255.
        ("[!&ff]", lambda binrep: not binrep == "11111111"),
    ),
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
    ("pronom_bytesequence", "input_", "matches_bool"),
    (
        # These are good:
        ("ab{3}cd(01|02|03)~07ff", "\xab\xdd\xdd\xdd\xcd\x02\x11\xff", True),
        ("ab{3}cd(01|02|03)~07ff", "\xab\xdd\xdd\xdd\xcd\x03\x11\xff", True),
        ("ab{3}cd(01|02|03)~07ff", "\xab\xdd\xdd\xdd\xcd\x02\xfe\xff", True),
        # Bad because missing three anythings between AB and CD
        ("ab{3}cd(01|02|03)~07ff", "\xab\xdd\xdd\xcd\x02\x11\xff", False),
        # Bad because not at start of string
        ("ab{3}cd(01|02|03)~07ff", "\xda\xab\xdd\xdd\xdd\xcd\x02\x11\xff", False),
        # Bad because 04 is not in (01|02|03)
        ("ab{3}cd(01|02|03)~07ff", "\xab\xdd\xdd\xdd\xcd\x04\x11\xff", False),
        # Bad because 18 is not in ~07
        ("ab{3}cd(01|02|03)~07ff", "\xab\xdd\xdd\xdd\xcd\x02\x18\xff", False),
    ),
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


def _make_format_element(puid, pronom_id, priority_over=None):
    element = XET.Element("format")
    XET.SubElement(element, "puid").text = puid
    XET.SubElement(element, "pronom_id").text = pronom_id
    if priority_over is not None:
        XET.SubElement(element, "has_priority_over").text = priority_over
    return element


def test_ns_helper_supports_attr_and_path_calls():
    namespace = prepare.NS("{urn:test}")

    assert namespace.value == "{urn:test}value"
    assert namespace("one/two") == "{urn:test}one/{urn:test}two"


def test_get_text_tna_returns_text_or_default():
    root = XET.Element("root")
    parent = XET.SubElement(root, prepare.TNA("foo"))
    tag = XET.SubElement(parent, prepare.TNA("bar"))
    tag.text = "  value  "

    assert prepare.get_text_tna(root, "foo/bar") == "value"
    assert prepare.get_text_tna(root, "missing", default="fallback") == "fallback"


def test_fido_position_unknown_value_writes_stderr(capsys):
    result = prepare.fido_position("Unknown position")

    captured = capsys.readouterr()
    assert result == "VAR"
    assert "Unknown pronom PositionType" in captured.err


def test_calculate_repetition_handles_large_offsets(monkeypatch):
    monkeypatch.setattr(prepare, "MAX_REGEX_REPS", 4)

    repetition = prepare.calculate_repetition(".", "BOF", "5", "6")

    assert repetition == ".{4,4}.{1,2}"


def test_convert_to_regex_supports_eof_position():
    regex = convert_to_regex("ab", pos="EOF", offset="1", maxoffset="2")

    assert regex.startswith("(?s)")
    assert regex.endswith("\\Z")
    assert ".{1,2}" in regex


def test_cmp_to_key_supports_custom_sorting():
    values = [1, 3, 2]
    key = prepare._cmp_to_key(lambda a, b: b - a)

    assert sorted(values, key=key) == [3, 2, 1]


def test_run_uses_default_versions_and_calls_formatinfo(monkeypatch, capsys):
    calls = {}
    versions = SimpleNamespace(
        get_zip_file=lambda: "input.zip",
        get_signature_file=lambda: "output.xml",
    )

    class DummyFormatInfo:
        def __init__(self, input_file):
            calls["input_file"] = input_file
            self.formats = ["fmt/1", "fmt/2"]

        def load_pronom_xml(self, puid):
            calls["puid"] = puid

        def save(self, output_file):
            calls["output_file"] = output_file

    monkeypatch.setattr(prepare, "get_local_versions", lambda: versions)
    monkeypatch.setattr(prepare, "FormatInfo", DummyFormatInfo)

    prepare.run()

    captured = capsys.readouterr()
    assert calls == {"input_file": "input.zip", "puid": None, "output_file": "output.xml"}
    assert "Converted 2 PRONOM formats" in captured.err


def test_main_parses_args_and_dispatches(monkeypatch):
    calls = {}

    def fake_run(input_file=None, output_file=None, puid=None):
        calls["input_file"] = input_file
        calls["output_file"] = output_file
        calls["puid"] = puid

    monkeypatch.setattr(prepare, "run", fake_run)

    prepare.main(["-input", "a.zip", "-output", "b.xml", "-puid", "fmt/99"])

    assert calls == {"input_file": "a.zip", "output_file": "b.xml", "puid": "fmt/99"}


def test_load_pronom_xml_rewrites_priority_ids(monkeypatch):
    class DummyStream:
        def close(self):
            return None

    class DummyZip:
        def __init__(self, *_args, **_kwargs):
            self.items = ["one.xml", "two.xml"]

        def infolist(self):
            return list(self.items)

        def open(self, _item):
            return DummyStream()

        def close(self):
            return None

    format_one = _make_format_element("fmt/1", "100", "200")
    format_two = _make_format_element("fmt/2", "200")
    parsed = [format_one, format_two]

    info = prepare.FormatInfo("dummy.zip")
    monkeypatch.setattr(prepare.zipfile, "ZipFile", DummyZip)
    monkeypatch.setattr(info, "parse_pronom_xml", lambda _stream, _puid: parsed.pop(0))
    monkeypatch.setattr(info, "_sort_formats", lambda formats: formats)

    info.load_pronom_xml()

    assert info.formats[0].find("has_priority_over").text == "fmt/2"
    assert len(info.formats) == 2


def _minimal_pronom_xml(puid="x-fmt/263", include_reference_url=True):
    ns = "http://pronom.nationalarchives.gov.uk"

    def n(tag):
        return f"{{{ns}}}{tag}"

    root = XET.Element(n("root"))
    report = XET.SubElement(root, n("report_format_detail"))
    fmt = XET.SubElement(report, n("FileFormat"))

    for id_type, ident in [
        ("PUID", puid),
        ("MIME", "application/test"),
        ("Apple Uniform Type Identifier", "public.test"),
    ]:
        xml_id = XET.SubElement(fmt, n("FileFormatIdentifier"))
        XET.SubElement(xml_id, n("IdentifierType")).text = id_type
        XET.SubElement(xml_id, n("Identifier")).text = ident

    XET.SubElement(fmt, n("FormatName")).text = "Test Format"
    XET.SubElement(fmt, n("FormatVersion")).text = "1.0"
    XET.SubElement(fmt, n("FormatAliases")).text = "Alias"
    XET.SubElement(fmt, n("FormatID")).text = "100"
    XET.SubElement(fmt, n("FormatDescription")).text = "Description"
    XET.SubElement(fmt, n("ReleaseDate")).text = "2020-01-01"
    XET.SubElement(fmt, n("FormatTypes")).text = "Text"
    XET.SubElement(fmt, n("ProvenanceName")).text = "Creator"
    XET.SubElement(fmt, n("ProvenanceSourceDate")).text = "2020-01-01"
    XET.SubElement(fmt, n("LastUpdatedDate")).text = "2021-01-01"
    XET.SubElement(fmt, n("ProvenanceDescription")).text = "Meta"

    devs = XET.SubElement(fmt, n("Developers"))
    XET.SubElement(devs, n("DeveloperCompoundName")).text = "Dev"
    XET.SubElement(devs, n("OrganisationName")).text = "Org"

    ext_sig = XET.SubElement(fmt, n("ExternalSignature"))
    XET.SubElement(ext_sig, n("Signature")).text = "tst"

    rel = XET.SubElement(fmt, n("RelatedFormat"))
    XET.SubElement(rel, n("RelationshipType")).text = "Has priority over"
    XET.SubElement(rel, n("RelatedFormatID")).text = "200"

    internal = XET.SubElement(fmt, n("InternalSignature"))
    XET.SubElement(internal, n("SignatureName")).text = "sig"
    XET.SubElement(internal, n("SignatureNote")).text = "note"
    byte_seq = XET.SubElement(internal, n("ByteSequence"))
    XET.SubElement(byte_seq, n("PositionType")).text = "Absolute from BOF"
    XET.SubElement(byte_seq, n("ByteSequenceValue")).text = "ab"
    XET.SubElement(byte_seq, n("Offset")).text = "0"
    XET.SubElement(byte_seq, n("MaxOffset")).text = ""

    doc = XET.SubElement(fmt, n("Document"))
    XET.SubElement(doc, n("TitleText")).text = "Doc"
    author = XET.SubElement(doc, n("Author"))
    XET.SubElement(author, n("AuthorCompoundName")).text = "A"
    publisher = XET.SubElement(doc, n("Publisher"))
    XET.SubElement(publisher, n("PublisherCompoundName")).text = "P"
    XET.SubElement(doc, n("PublicationDate")).text = "2020"
    doc_id = XET.SubElement(doc, n("DocumentIdentifier"))
    XET.SubElement(doc_id, n("IdentifierType")).text = "URL"
    XET.SubElement(doc_id, n("Identifier")).text = "example.test/spec"
    XET.SubElement(doc, n("DocumentNote")).text = "note"
    XET.SubElement(doc, n("DocumentType")).text = "type"
    XET.SubElement(doc, n("AvailabilityDescription")).text = "avail"
    XET.SubElement(doc, n("AvailabilityNote")).text = "note"
    XET.SubElement(doc, n("DocumentIPR")).text = "ipr"

    ref_file = XET.SubElement(fmt, n("ReferenceFile"))
    XET.SubElement(ref_file, n("ReferenceFileName")).text = "sample.bin"
    XET.SubElement(ref_file, n("ReferenceFileDescription")).text = "desc"
    XET.SubElement(ref_file, n("ReferenceFileIPR")).text = "ipr"
    ref_id = XET.SubElement(ref_file, n("ReferenceFileIdentifier"))
    XET.SubElement(ref_id, n("IdentifierType")).text = "URL" if include_reference_url else "DOI"
    XET.SubElement(ref_id, n("Identifier")).text = "example.test/file" if include_reference_url else "10.1/xyz"

    return XET.tostring(root, encoding="utf-8")


def _tna(tag):
    return "{http://pronom.nationalarchives.gov.uk}" + tag


def test_parse_pronom_xml_extracts_core_fields(monkeypatch):
    payload = b"checksum-data"

    class DummySock:
        def read(self):
            return payload

        def close(self):
            return None

    info = prepare.FormatInfo("dummy.zip")
    monkeypatch.setattr(prepare, "ET", XET)
    monkeypatch.setattr(prepare, "urlopen", lambda _url: DummySock())

    result = info.parse_pronom_xml(io.BytesIO(_minimal_pronom_xml()))

    assert result.find("puid").text == "x-fmt/263"
    assert result.find("container").text == "zip"
    assert result.find("mime").text == "application/test"
    assert result.find("apple_uti").text == "public.test"
    assert result.find("has_priority_over").text == "200"
    assert result.find("signature/pattern/regex").text
    ref_identifiers = [node.text for node in result.findall("details/reference/*") if node.tag == "dc:identifier"]
    assert "http://example.test/spec" in ref_identifiers
    checksum = result.find("details/example_file/checksum")
    assert checksum.attrib["type"] == "md5"
    assert checksum.text == hashlib.md5(payload).hexdigest()


def test_parse_pronom_xml_respects_puid_filter(monkeypatch):
    info = prepare.FormatInfo("dummy.zip")
    monkeypatch.setattr(prepare, "ET", XET)

    assert info.parse_pronom_xml(io.BytesIO(_minimal_pronom_xml(puid="fmt/1")), puid_filter="fmt/2") is None


def test_parse_pronom_xml_skips_incompatible_signature(monkeypatch, capsys):
    info = prepare.FormatInfo("dummy.zip")
    monkeypatch.setattr(prepare, "ET", XET)
    monkeypatch.setattr(prepare, "convert_to_regex", lambda *_a, **_k: prepare.FLG_INCOMPATIBLE)

    result = info.parse_pronom_xml(io.BytesIO(_minimal_pronom_xml(include_reference_url=False)))

    assert result.findall("signature") == []
    assert "incompatible PRONOM signature found" in capsys.readouterr().err


def test_prettify_outputs_xml_string():
    elem = XET.Element("root")
    XET.SubElement(elem, "child").text = "value"

    pretty = prepare.prettify(elem)

    assert "<?xml" in pretty
    assert "<child>value</child>" in pretty


def test_formatinfo_save_writes_formats_xml(monkeypatch, tmp_path):
    info = prepare.FormatInfo("dummy.zip")
    fmt = XET.Element("format")
    XET.SubElement(fmt, "puid").text = "fmt/1"
    info.formats = [fmt]
    monkeypatch.setattr(prepare, "ET", XET)

    out = tmp_path / "formats.xml"
    info.save(str(out))

    content = out.read_text(encoding="utf-8")
    assert "<formats" in content
    assert "<puid>fmt/1</puid>" in content


def test_sort_formats_orders_by_priority_relationship(monkeypatch):
    info = prepare.FormatInfo("dummy.zip")
    f1 = _make_format_element("fmt/1", "100", priority_over="fmt/2")
    f2 = _make_format_element("fmt/2", "200")

    sorted_formats = info._sort_formats([f2, f1])

    assert [f.find("puid").text for f in sorted_formats] == ["fmt/1", "fmt/2"]


@pytest.mark.parametrize(
    "position, expected",
    [
        ("Absolute from BOF", "BOF"),
        ("Absolute from EOF", "EOF"),
        ("Variable", "VAR"),
        ("Indirect From BOF", "IFB"),
    ],
)
def test_fido_position_known_values(position, expected):
    assert prepare.fido_position(position) == expected


def test_do_byte_rejects_invalid_hex_pair():
    with pytest.raises(Exception) as exc:
        prepare.do_byte("ZZ", 0, True)

    assert "bad byte sequence" in str(exc.value)


def test_convert_to_regex_rejects_invalid_start_char():
    with pytest.raises(ValueError):
        prepare.convert_to_regex("^")


def test_convert_to_regex_question_mark_requires_double_question_mark():
    with pytest.raises(Exception) as exc:
        prepare.convert_to_regex("?a")

    assert "Illegal character after ?" in str(exc.value)


def test_convert_to_regex_bracket_returns_incompatible_for_bad_separator():
    assert prepare.convert_to_regex("[0102]") == prepare.FLG_INCOMPATIBLE


def test_convert_to_regex_paren_raises_on_illegal_char():
    with pytest.raises(Exception):
        prepare.convert_to_regex("(01!)")


def test_load_pronom_xml_reports_unmapped_priority(monkeypatch, capsys):
    class DummyStream:
        def close(self):
            return None

    class DummyZip:
        def __init__(self, *_args, **_kwargs):
            self.items = ["one.xml"]

        def infolist(self):
            return list(self.items)

        def open(self, _item):
            return DummyStream()

        def close(self):
            return None

    info = prepare.FormatInfo("dummy.zip")
    fmt = _make_format_element("fmt/1", "100", priority_over="999")
    monkeypatch.setattr(prepare.zipfile, "ZipFile", DummyZip)
    monkeypatch.setattr(info, "parse_pronom_xml", lambda _stream, _puid: fmt)
    monkeypatch.setattr(info, "_sort_formats", lambda formats: formats)

    info.load_pronom_xml()

    assert "Error looking up priority over PRONOM ID 999" in capsys.readouterr().err


def test_load_pronom_xml_exits_when_zip_close_fails(monkeypatch):
    class DummyStream:
        def close(self):
            return None

    class DummyZip:
        def __init__(self, *_args, **_kwargs):
            self.items = ["one.xml"]

        def infolist(self):
            return list(self.items)

        def open(self, _item):
            return DummyStream()

        def close(self):
            raise RuntimeError("close failed")

    info = prepare.FormatInfo("dummy.zip")
    monkeypatch.setattr(prepare.zipfile, "ZipFile", DummyZip)
    monkeypatch.setattr(info, "parse_pronom_xml", lambda _stream, _puid: None)

    with pytest.raises(SystemExit):
        info.load_pronom_xml()


def test_parse_pronom_xml_extracts_super_and_subtype_relationships(monkeypatch):
    root = XET.fromstring(_minimal_pronom_xml())
    fmt = root.find(".//" + _tna("FileFormat"))

    rel_super = XET.SubElement(fmt, _tna("RelatedFormat"))
    XET.SubElement(rel_super, _tna("RelationshipType")).text = "Is supertype of"
    XET.SubElement(rel_super, _tna("RelatedFormatID")).text = "300"

    rel_sub = XET.SubElement(fmt, _tna("RelatedFormat"))
    XET.SubElement(rel_sub, _tna("RelationshipType")).text = "Is subtype of"
    XET.SubElement(rel_sub, _tna("RelatedFormatID")).text = "301"

    info = prepare.FormatInfo("dummy.zip")
    monkeypatch.setattr(prepare, "ET", XET)
    monkeypatch.setattr(prepare, "urlopen", lambda _url: io.BytesIO(b"x"))

    result = info.parse_pronom_xml(io.BytesIO(XET.tostring(root, encoding="utf-8")))

    assert result.find("details/is_supertype_of").text == "300"
    assert result.find("details/is_subtype_of").text == "301"


def test_parse_pronom_xml_reference_file_http_404_continues(monkeypatch, capsys):
    info = prepare.FormatInfo("dummy.zip")
    monkeypatch.setattr(prepare, "ET", XET)
    monkeypatch.setattr(
        prepare,
        "urlopen",
        lambda _url: (_ for _ in ()).throw(
            urllib.error.HTTPError(url="http://example.test/file", code=404, msg="missing", hdrs=None, fp=None)
        ),
    )

    result = info.parse_pronom_xml(io.BytesIO(_minimal_pronom_xml()))

    checksum = result.find("details/example_file/checksum")
    assert checksum is not None
    assert checksum.text in (None, "")
    assert "HTTP 404 error loading resource" in capsys.readouterr().err


def test_parse_pronom_xml_reference_file_http_non_404_uses_empty_hash(monkeypatch, capsys):
    info = prepare.FormatInfo("dummy.zip")
    monkeypatch.setattr(prepare, "ET", XET)
    monkeypatch.setattr(
        prepare,
        "urlopen",
        lambda _url: (_ for _ in ()).throw(
            urllib.error.HTTPError(url="http://example.test/file", code=500, msg="error", hdrs=None, fp=None)
        ),
    )

    result = info.parse_pronom_xml(io.BytesIO(_minimal_pronom_xml()))

    checksum = result.find("details/example_file/checksum")
    assert checksum.text == hashlib.md5(b"").hexdigest()
    assert "HTTP 500 error loading resource" in capsys.readouterr().err


def converted_patterns(monkeypatch, record_name):
    """Convert a real PRONOM v125 record and return its (position, regex) pairs."""
    monkeypatch.setattr(prepare, "ET", XET)
    info = prepare.FormatInfo("dummy.zip")
    with open(os.path.join(TEST_DATA_PRONOM, record_name), "rb") as record:
        fido_format = info.parse_pronom_xml(record)
    return [
        (pattern.findtext("position"), pattern.findtext("regex"))
        for pattern in fido_format.iter("pattern")
    ]


@pytest.mark.parametrize(
    ("offset", "max_offset", "expected"),
    (
        ("3000", "700", "3700"),
        ("1", "2", "3"),
        ("0", "8", "8"),
        ("", "5", "5"),
        ("4", "", ""),
        ("4", "0", "0"),
    ),
)
def test_absolute_max_offset(offset, max_offset, expected):
    assert absolute_max_offset(offset, max_offset) == expected


def test_bof_window_runs_from_offset_to_offset_plus_max_offset(monkeypatch):
    """fmt/1202 has Offset 1 and MaxOffset 2, so DROID matches its sequence at offsets 1 to 3."""
    [(position, regex)] = converted_patterns(monkeypatch, "puid.fmt.1202.xml")
    sequence = "GUYMAGER ACQUISITION INFO FILE"
    assert position == "BOF"
    for offset in (1, 2, 3):
        assert re.search(regex, "\x00" * offset + sequence), "expected a match at offset {}".format(offset)
    for offset in (0, 4):
        assert not re.search(regex, "\x00" * offset + sequence), "expected no match at offset {}".format(offset)


def test_max_offset_below_offset_converts_to_a_valid_regex(monkeypatch):
    """fmt/1558 has Offset 3000 and MaxOffset 700, which used to convert to the invalid .{3000,700}."""
    [(position, regex)] = converted_patterns(monkeypatch, "puid.fmt.1558.xml")
    sequence = "C64/C128 SELF EXTRACTING LHARCHIVE"
    re.compile(regex)
    for offset in (3000, 3370, 3700):
        assert re.search(regex, "\x00" * offset + sequence), "expected a match at offset {}".format(offset)
    for offset in (2999, 3701):
        assert not re.search(regex, "\x00" * offset + sequence), "expected no match at offset {}".format(offset)


def test_eof_window_runs_from_offset_to_offset_plus_max_offset(monkeypatch):
    """fmt/1646's EOF sequence has Offset 109 and MaxOffset 11, so it ends 109 to 120 bytes before EOF."""
    regex = dict(converted_patterns(monkeypatch, "puid.fmt.1646.xml"))["EOF"]
    sequence = "\x02\xff\xfe\xff\x05A\x00r\x00i\x00a\x00l"
    for trailing in (109, 115, 120):
        assert re.search(regex, sequence + "\x00" * trailing), "expected a match {} bytes before EOF".format(trailing)
    for trailing in (108, 121):
        assert not re.search(regex, sequence + "\x00" * trailing), "expected no match {} bytes before EOF".format(
            trailing
        )
