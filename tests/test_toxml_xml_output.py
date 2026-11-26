import csv
import io
import os
import subprocess
import sys
from types import SimpleNamespace
from xml.etree import ElementTree as ET

import pytest

from fido import toxml


XML_FIELDS = (
    "filename", "status", "matchtype", "time", "puid", "mimetype",
    "formatname", "signaturename", "filesize",
)


def csv_input(rows):
    stream = io.StringIO()
    csv.writer(stream).writerows(rows)
    stream.seek(0)
    return stream


def test_toxml_preserves_xml_text_in_every_field(monkeypatch, capsys):
    row = ['{} &amp; <tag> "café"'.format(index) for index in range(9)]
    output = io.StringIO()
    monkeypatch.setattr(toxml.sys, "stdin", csv_input([row]))
    monkeypatch.setattr(toxml.sys, "stdout", output)

    toxml.main()

    root = ET.fromstring(output.getvalue())
    files = root.findall("file")
    assert len(files) == 1
    assert [child.tag for child in files[0]] == list(XML_FIELDS)
    assert [child.text for child in files[0]] == [
        row[6], row[0], row[8], row[1], row[2], row[7], row[3], row[4], row[5],
    ]
    assert capsys.readouterr().err == ""


def test_toxml_escapes_version_text(monkeypatch, capsys):
    fido_version = 'release <1> & "two"'
    signature_version = 'PRONOM <3> & "four"'
    monkeypatch.setattr(toxml, "__version__", fido_version)
    monkeypatch.setattr(toxml, "get_local_versions", lambda: SimpleNamespace(pronom_version=signature_version))
    monkeypatch.setattr(toxml.sys, "stdin", csv_input([]))

    toxml.main()

    captured = capsys.readouterr()
    root = ET.fromstring(captured.out)
    assert root.findtext("versions/fido_version") == fido_version
    assert root.findtext("versions/signature_version") == signature_version
    assert root.findall("file") == []
    assert captured.err == ""


@pytest.mark.parametrize("bad_row", [[], ["short"], ["extra"] * 10, [" "]])
def test_toxml_skips_invalid_rows_and_continues(monkeypatch, capsys, bad_row):
    first = ["OK", "1", "fmt/1", "First", "Sig", "4", "first\nrow.bin", "text/plain", "byte"]
    last = ["KO", "2", "", "Last", "", "8", "last.bin", "", "extension"]
    monkeypatch.setattr(toxml.sys, "stdin", csv_input([first, bad_row, last]))

    toxml.main()

    captured = capsys.readouterr()
    root = ET.fromstring(captured.out)
    assert [node.findtext("filename") for node in root.findall("file")] == ["first\nrow.bin", "last.bin"]
    if bad_row:
        assert captured.err == "Skipping CSV line 3: expected 9 fields, got {}\n".format(len(bad_row))
    else:
        assert captured.err == ""


@pytest.mark.parametrize("value", ["", " \t "])
def test_toxml_keeps_empty_and_whitespace_fields(monkeypatch, capsys, value):
    monkeypatch.setattr(toxml.sys, "stdin", csv_input([[value] * 9]))

    toxml.main()

    captured = capsys.readouterr()
    root = ET.fromstring(captured.out)
    files = root.findall("file")
    assert len(files) == 1
    assert [child.tag for child in files[0]] == list(XML_FIELDS)
    assert [(child.text or "") for child in files[0]] == [value] * 9
    assert captured.err == ""


@pytest.mark.parametrize("stdio_encoding", ["utf-8", "cp1252"])
def test_toxml_emits_utf8_bytes(stdio_encoding):
    row = ["OK", "0", "fmt/1", "Café", "Sig", "4", "café.csv", "text/csv", "byte"]
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = stdio_encoding

    result = subprocess.run(
        [sys.executable, "-m", "fido.toxml"],
        input=csv_input([row]).getvalue().encode(stdio_encoding),
        capture_output=True,
        check=True,
        env=environment,
        timeout=10,
    )

    root = ET.fromstring(result.stdout.decode("utf-8"))
    assert root.findtext("file/filename") == "café.csv"
    assert root.findtext("file/formatname") == "Café"
    assert result.stderr == b""
