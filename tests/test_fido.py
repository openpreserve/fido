#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import errno
import io
import os
import struct
import subprocess  # nosec B404  # runs fido itself in the stdin tests
import sys
import zlib
from xml.etree import ElementTree as XET
from time import sleep
from types import SimpleNamespace

import pytest

import fido.fido as fido_mod
from fido.fido import Fido
from fido.utils.timer import PerfTimer


def test_perf_timer():
    timer = PerfTimer()
    sleep(0.2)
    duration = timer.duration()
    assert duration > 0


id_test_data = [(b"\x5a\x58\x54\x61\x70\x65\x21\x1a\x01", "fmt/1000", "OK")]


@pytest.mark.parametrize(
    "magic, expected_puid, expected_result",
    id_test_data,
    # Add additional test cases here
)
def test_file_identification(tmp_path, capsys, magic: bytes, expected_puid: str, expected_result: str):
    """Reference for Fido-based format identification
    1. Create a byte-stream with a known magic number and serialize to tempfile.
    2. Call identify_file(...) to identify the file against Fido's known formats.
    """
    # Create a temporary file and write our skeleton file out to it.
    tmp_file = tmp_path / "tmp_file"
    tmp_file.write_bytes(magic)

    # Create a Fido instance and call identify_file. The identify_file function
    # will create and manage a file for itself.
    f = Fido()
    f.identify_file(str(tmp_file))

    # Capture the stdout returned by Fido and make assertions about its
    # validity.
    captured = capsys.readouterr()
    # TODO: there is a signature that generates an error
    # min repeat greater than max repeat at position 8
    # assert captured.err == ""
    reader = csv.reader(io.StringIO(captured.out), delimiter=",")
    assert reader is not None
    row = next(reader)
    assert row[0] == expected_result, "row hasn't returned a positive identification"
    assert row[2] == expected_puid, "row doesn't contain expected PUID value"
    assert int(row[5]) == len(magic), "row doesn't contain stream length"


@pytest.mark.parametrize(
    "magic, expected_puid, expected_result",
    id_test_data,
    # Add additional test cases here
)
def test_stream_identification(capsys, magic: bytes, expected_puid: str, expected_result: str):
    """Reference for Fido-based format identification
    1. Create a byte-stream with a known magic number.
    2. Call identify_stream(...) to identify the file against Fido's known formats.
    """
    # Create the stream object with the known magic-number.
    fstream = io.BytesIO(magic)

    # Create a Fido instance and call identify_stream. The identify_stream function
    # will work on the stream as-is. This could be an open file handle that the
    # caller is managing for itself.
    f = Fido()
    f.identify_stream(fstream, "filename to display", extension=False)

    # Capture the stdout returned by Fido and make assertions about its
    # validity.
    captured = capsys.readouterr()
    # TODO: as above, there is a signature that outputs an error
    # min repeat greater than max repeat at position 8
    # assert captured.err == ""
    reader = csv.reader(io.StringIO(captured.out), delimiter=",")
    assert reader is not None
    row = next(reader)
    assert row[0] == expected_result, "row hasn't returned a positive identification"
    assert row[2] == expected_puid, "row doesn't contain expected PUID value"
    assert int(row[5]) == len(magic), "row doesn't contain stream length"


def _text_stdin(content: bytes):
    """Behave like the interpreter's sys.stdin: a text wrapper around a binary buffer."""
    return io.TextIOWrapper(io.BytesIO(content), encoding="utf-8")


STDIN_STREAMS = pytest.mark.parametrize(
    "stdin_factory",
    [_text_stdin, io.BytesIO],
    ids=["text wrapper over a binary buffer", "plain binary stream without a buffer attribute"],
)


@STDIN_STREAMS
@pytest.mark.parametrize(
    "magic, expected_puid, expected_result",
    id_test_data,
    # Add additional test cases here
)
def test_main_identifies_stdin(
    monkeypatch, capsys, stdin_factory, magic: bytes, expected_puid: str, expected_result: str
):
    """`fido -` must identify the bytes on stdin; the stream tests bypass the wiring in main()."""
    # main() stores the signature files it loads in this dict, so run it on a copy
    monkeypatch.setattr(fido_mod, "defaults", dict(fido_mod.defaults))
    monkeypatch.setattr(fido_mod.sys, "stdin", stdin_factory(magic))

    fido_mod.main(["-q", "-"])

    row = next(csv.reader(io.StringIO(capsys.readouterr().out)))
    assert row[0] == expected_result, "row hasn't returned a positive identification"
    assert row[2] == expected_puid, "row doesn't contain expected PUID value"
    assert int(row[5]) == len(magic), "row doesn't contain stream length"


def _png_with_crlf_and_high_bytes():
    """A 1x1 PNG. Its signature holds a high byte and a CRLF pair, which text handling would damage."""

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(b"\x00\xff\x00\x00"))
        + chunk(b"IEND", b"")
    )


@STDIN_STREAMS
def test_main_passes_stdin_bytes_through_unchanged(monkeypatch, capsys, stdin_factory):
    """Only an intact signature identifies this over a pipe, so any decoding or newline conversion shows."""
    png = _png_with_crlf_and_high_bytes()
    monkeypatch.setattr(fido_mod, "defaults", dict(fido_mod.defaults))
    monkeypatch.setattr(fido_mod.sys, "stdin", stdin_factory(png))

    fido_mod.main(["-q", "-"])

    row = next(csv.reader(io.StringIO(capsys.readouterr().out)))
    assert row[2] == "fmt/11"
    assert row[8] == "signature"
    assert int(row[5]) == len(png)


def test_main_reports_an_empty_stdin_as_no_match(monkeypatch, capsys):
    """An empty buffer satisfies the RTF signatures, so it must not be matched at all, as for an empty file."""
    monkeypatch.setattr(fido_mod, "defaults", dict(fido_mod.defaults))
    monkeypatch.setattr(fido_mod.sys, "stdin", _text_stdin(b""))

    fido_mod.main(["-q", "-"])

    rows = list(csv.reader(io.StringIO(capsys.readouterr().out)))
    assert len(rows) == 1, rows
    assert rows[0][0] == "KO"
    assert int(rows[0][5]) == 0


def _format_element(puid, container=None, extension=None, has_priority_over=None):
    fmt = XET.Element("format")
    XET.SubElement(fmt, "puid").text = puid
    XET.SubElement(fmt, "name").text = puid
    if container is not None:
        XET.SubElement(fmt, "container").text = container
    if extension is not None:
        XET.SubElement(fmt, "extension").text = extension
    if has_priority_over is not None:
        XET.SubElement(fmt, "has_priority_over").text = has_priority_over
    return fmt


def _make_fido(monkeypatch):
    monkeypatch.setattr(Fido, "load_fido_xml", lambda self, _path: None)
    return Fido(format_files=[])


def test_container_type_detects_zip_ole_and_false(monkeypatch):
    fido = _make_fido(monkeypatch)

    zip_fmt = _format_element("fmt/999", container="zip")
    ole_fmt = _format_element("fmt/111")
    plain_fmt = _format_element("fmt/1")

    assert fido.container_type([(zip_fmt, "sig")]) == "zip"
    assert fido.container_type([(ole_fmt, "sig")]) == "ole"
    assert fido.container_type([(plain_fmt, "sig")]) is False


def test_identify_contents_dispatches_supported_types(monkeypatch):
    fido = _make_fido(monkeypatch)
    calls = {"zip": 0, "tar": 0}

    monkeypatch.setattr(fido, "walk_zip", lambda *_args, **_kwargs: calls.__setitem__("zip", calls["zip"] + 1))
    monkeypatch.setattr(fido, "walk_tar", lambda *_args, **_kwargs: calls.__setitem__("tar", calls["tar"] + 1))

    fido.identify_contents("a.zip", type="zip")
    fido.identify_contents("a.tar", type="tar")
    fido.identify_contents("a.bin", type="unknown")
    fido.identify_contents("a.bin", type=False)

    assert calls == {"zip": 1, "tar": 1}


def test_get_buffers_seekable_branches(monkeypatch):
    fido = _make_fido(monkeypatch)
    fido.bufsize = 8
    data = b"0123456789abcdefghij"

    bof_1, eof_1, _ = fido.get_buffers(io.BytesIO(data), length=12)
    assert bof_1 == data[:8]
    assert eof_1 == data[4:12]

    bof_2, eof_2, _ = fido.get_buffers(io.BytesIO(data), length=16)
    assert bof_2 == data[:8]
    assert eof_2 == data[8:16]

    bof_3, eof_3, _ = fido.get_buffers(io.BytesIO(data), length=20, seekable=True)
    assert bof_3 == data[:8]
    assert eof_3 == data[-8:]


def test_match_extensions_honors_priority_over(monkeypatch):
    fido = _make_fido(monkeypatch)
    superior = _format_element("fmt/1", extension="txt", has_priority_over="fmt/2")
    inferior = _format_element("fmt/2", extension="txt")
    fido.formats = [superior, inferior]
    fido.puid_has_priority_over_map = {
        "fmt/1": frozenset(["fmt/2"]),
        "fmt/2": frozenset(),
    }

    matches = fido.match_extensions("sample.txt")

    assert len(matches) == 1
    assert matches[0][0].find("puid").text == "fmt/1"
    assert matches[0][1] == "External"


def test_identify_file_reports_io_error(monkeypatch, capsys):
    fido = _make_fido(monkeypatch)
    monkeypatch.setattr("builtins.open", lambda *_a, **_k: (_ for _ in ()).throw(IOError("boom")))

    fido.identify_file("/does/not/exist")

    assert "FIDO: Error in identify_file" in capsys.readouterr().err


def test_identify_file_prefers_container_matches(monkeypatch, tmp_path):
    fido = _make_fido(monkeypatch)
    hits = {}
    sample = tmp_path / "sample.bin"
    sample.write_bytes(b"abc")
    zip_fmt = _format_element("fmt/999", container="zip")

    monkeypatch.setattr(fido, "match_formats", lambda *_a: [(zip_fmt, "sig")])
    monkeypatch.setattr(fido, "match_container", lambda *_a: [(zip_fmt, "container sig")])
    monkeypatch.setattr(fido_mod.ET, "parse", lambda _p: XET.ElementTree(XET.Element("root")))
    monkeypatch.setattr(
        fido,
        "handle_matches",
        lambda filename, matches, _duration, matchtype: hits.update(
            {"filename": filename, "matches": matches, "matchtype": matchtype}
        ),
    )

    fido.identify_file(str(sample))

    assert hits["matchtype"] == "container"
    assert hits["filename"] == str(sample)
    assert len(hits["matches"]) == 1


def test_identify_file_extension_fallback(monkeypatch, tmp_path):
    fido = _make_fido(monkeypatch)
    sample = tmp_path / "sample.txt"
    sample.write_bytes(b"abc")
    ext_fmt = _format_element("fmt/1", extension="txt")
    hits = {}

    monkeypatch.setattr(fido, "match_formats", lambda *_a: [])
    monkeypatch.setattr(fido, "match_extensions", lambda _name: [(ext_fmt, "External")])
    monkeypatch.setattr(
        fido,
        "handle_matches",
        lambda _filename, _matches, _duration, matchtype: hits.update({"matchtype": matchtype}),
    )

    fido.identify_file(str(sample), extension=True)

    assert hits["matchtype"] == "extension"


def test_identify_file_recurses_into_zip_when_enabled(monkeypatch, tmp_path):
    fido = _make_fido(monkeypatch)
    fido.zip = True
    sample = tmp_path / "sample.zip"
    sample.write_bytes(b"abc")
    zip_fmt = _format_element("fmt/999", container="zip")
    calls = {"recurse": 0}

    monkeypatch.setattr(fido, "match_formats", lambda *_a: [(zip_fmt, "sig")])
    monkeypatch.setattr(fido, "handle_matches", lambda *_a: None)
    monkeypatch.setattr(
        fido,
        "identify_contents",
        lambda _filename, type=None, extension=True: calls.__setitem__("recurse", calls["recurse"] + 1),
    )

    fido.identify_file(str(sample), extension=False)

    assert calls["recurse"] == 1


def test_identify_stream_non_windows_fallback_filename(monkeypatch):
    fido = _make_fido(monkeypatch)
    calls = {}
    monkeypatch.setattr(fido, "match_formats", lambda *_a: [])
    monkeypatch.setattr(
        fido,
        "match_extensions",
        lambda filename: calls.__setitem__("ext_filename", filename) or [],
    )
    monkeypatch.setattr(
        fido,
        "handle_matches",
        lambda filename, _matches, _duration, matchtype: calls.update(
            {"handled_filename": filename, "matchtype": matchtype}
        ),
    )
    fake_os = SimpleNamespace(
        name="posix",
        readlink=lambda _p: (_ for _ in ()).throw(OSError("no link")),
    )
    monkeypatch.setattr(fido_mod, "os", fake_os)

    fido.identify_stream(io.BytesIO(b"abc"), "provided.name", extension=True)

    assert calls["ext_filename"] == "provided.name"
    assert calls["handled_filename"] == "STDIN"
    assert calls["matchtype"] == "extension"


def test_identify_stream_windows_uses_provided_filename(monkeypatch):
    fido = _make_fido(monkeypatch)
    calls = {}
    monkeypatch.setattr(fido, "match_formats", lambda *_a: [])
    monkeypatch.setattr(
        fido,
        "match_extensions",
        lambda filename: calls.__setitem__("ext_filename", filename) or [],
    )
    monkeypatch.setattr(
        fido,
        "handle_matches",
        lambda filename, _matches, _duration, _matchtype: calls.update({"handled_filename": filename}),
    )
    fake_os = SimpleNamespace(name="nt")
    monkeypatch.setattr(fido_mod, "os", fake_os)

    fido.identify_stream(io.BytesIO(b"abc"), "provided.name", extension=True)

    assert calls["ext_filename"] == "provided.name"
    assert calls["handled_filename"] == "provided.name"


def _readlink_returning(link):
    def readlink(_path):
        if isinstance(link, Exception):
            raise link
        return link

    return readlink


@pytest.mark.parametrize(
    "link, filename, expected",
    [
        ("pipe:[1234]", None, "STDIN"),
        ("pipe:[1234]", "provided.txt", "provided.txt"),
        ("socket:[5678]", None, "STDIN"),
        ("socket:[5678]", "provided.txt", "provided.txt"),
        ("/data/redirected.csv", None, "/data/redirected.csv"),
        ("/data/redirected.csv", "provided.txt", "provided.txt"),
        (OSError("no /proc"), None, "STDIN"),
        (OSError("no /proc"), "provided.txt", "provided.txt"),
    ],
    ids=[
        "pipe",
        "pipe with -filename",
        "socket",
        "socket with -filename",
        "redirect",
        "-filename wins over a redirect",
        "no /proc (macOS)",
        "no /proc with -filename",
    ],
)
def test_stdin_name(monkeypatch, link, filename, expected):
    monkeypatch.setattr(fido_mod, "os", SimpleNamespace(name="posix", readlink=_readlink_returning(link)))

    name = fido_mod.stdin_name(filename)

    assert name == expected, f"/proc/self/fd/0 -> {link!r}, -filename {filename!r}: got {name!r}, expected {expected!r}"


@pytest.mark.parametrize("filename, expected", [(None, "STDIN"), ("provided.txt", "provided.txt")])
def test_stdin_name_on_windows_never_reads_proc(monkeypatch, filename, expected):
    """Windows has no /proc; even a path that happens to resolve there must not name stdin."""
    calls = []
    monkeypatch.setattr(
        fido_mod, "os", SimpleNamespace(name="nt", readlink=lambda path: calls.append(path) or "/data/redirected.txt")
    )

    name = fido_mod.stdin_name(filename)

    assert name == expected, f"-filename {filename!r}: got {name!r}, expected {expected!r}"
    assert calls == [], f"readlink was called on Windows with {calls!r}"


def test_identify_stream_linux_pipe_uses_provided_filename(monkeypatch):
    """On Linux /proc/self/fd/0 of a pipe links to pipe:[N], which must not hide -filename (#260)."""
    fido = _make_fido(monkeypatch)
    calls = {}
    monkeypatch.setattr(fido, "match_formats", lambda *_a: [])
    monkeypatch.setattr(
        fido,
        "match_extensions",
        lambda filename: calls.__setitem__("ext_filename", filename) or [],
    )
    monkeypatch.setattr(
        fido,
        "handle_matches",
        lambda filename, _matches, _duration, matchtype: calls.update(
            {"handled_filename": filename, "matchtype": matchtype}
        ),
    )
    monkeypatch.setattr(fido_mod, "os", SimpleNamespace(name="posix", readlink=_readlink_returning("pipe:[1234]")))

    fido.identify_stream(io.BytesIO(b"abc"), "provided.name", extension=True)

    assert calls["ext_filename"] == "provided.name", f"extension step matched against {calls['ext_filename']!r}"
    assert calls["handled_filename"] == "STDIN"
    assert calls["matchtype"] == "extension"


def _fido_row_for_stdin(args, piped=None, redirected=None):
    """
    Run `fido -q ARGS -` in a fresh interpreter and return its first output row.

    A fresh process is needed because the bug depends on what file descriptor 0 really is:
    `piped` bytes arrive through a pipe, `redirected` is an open file that becomes stdin.
    """
    result = subprocess.run(  # nosec B603  # fixed arguments, runs fido itself
        [sys.executable, "-m", "fido.fido", "-q", *args, "-"],
        input=piped,
        stdin=redirected,
        capture_output=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )
    assert result.returncode == 0, result.stderr.decode()
    rows = list(csv.reader(io.StringIO(result.stdout.decode())))
    assert rows, f"no output row, stderr: {result.stderr.decode()!r}"
    return rows[0]


needs_proc = pytest.mark.skipif(
    not os.path.exists("/proc/self/fd/0"), reason="without /proc there is no stdin link to hide -filename"
)


@needs_proc
@pytest.mark.parametrize(
    "args, expected_result, expected_puid",
    [(["-filename", "foo.txt"], "OK", "x-fmt/111"), ([], "KO", "")],
    ids=["-filename foo.txt", "no -filename"],
)
def test_main_uses_filename_for_a_piped_stdin(args, expected_result, expected_puid):
    """`cat hello.txt | fido -filename foo.txt -` matches the extension of foo.txt; text has no signature."""
    row = _fido_row_for_stdin(args, piped=b"hello\n")

    assert row[0] == expected_result, f"row {row}"
    assert row[2] == expected_puid, f"row {row}"
    assert row[6] == "STDIN", f"row {row}"


@needs_proc
@pytest.mark.parametrize(
    "args, expected_puid",
    [([], "x-fmt/111"), (["-filename", "foo.csv"], "x-fmt/18")],
    ids=["redirect from hello.txt", "-filename foo.csv wins over the redirect"],
)
def test_main_names_a_redirected_stdin(tmp_path, args, expected_puid):
    """`fido - < hello.txt` matches the extension of the redirected file, unless -filename says otherwise."""
    hello = tmp_path / "hello.txt"
    hello.write_bytes(b"hello\n")

    with open(hello, "rb") as stdin:
        row = _fido_row_for_stdin(args, redirected=stdin)

    assert row[0] == "OK", f"row {row}"
    assert row[2] == expected_puid, f"row {row}"
    assert row[8] == "extension", f"row {row}"


def test_walk_zip_handles_bad_zip(monkeypatch, capsys):
    fido = _make_fido(monkeypatch)
    monkeypatch.setattr(fido_mod.zipfile, "ZipFile", lambda *_a, **_k: (_ for _ in ()).throw(fido_mod.zipfile.BadZipfile()))

    fido.walk_zip("bad.zip")

    assert "FIDO: ZipError bad.zip" in capsys.readouterr().err


def test_walk_zip_reports_an_archive_with_an_entry_name_that_is_not_valid_utf8(monkeypatch, tmp_path, capsys):
    """Some tools set the UTF-8 flag on names in a legacy code page; the archive is reported, the run goes on."""
    fido = _make_fido(monkeypatch)
    buffer = io.BytesIO()
    with fido_mod.zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("\u00e9.txt", b"content")
    sample = tmp_path / "sample.zip"
    sample.write_bytes(buffer.getvalue().replace("\u00e9".encode("utf-8"), b"\xe9\xff"))

    fido.walk_zip(str(sample))

    error = capsys.readouterr().err
    assert error.startswith(f"FIDO: ZipError {sample}: "), error
    assert "codec can't decode" in error, error


def test_walk_tar_handles_tar_error(monkeypatch, capsys):
    fido = _make_fido(monkeypatch)
    monkeypatch.setattr(fido_mod.tarfile, "TarFile", lambda *_a, **_k: (_ for _ in ()).throw(fido_mod.tarfile.TarError()))

    fido.walk_tar("bad.tar", None)

    assert "FIDO: Error: TarError bad.tar" in capsys.readouterr().err


def _main_args(**overrides):
    args = {
        "confdir": "/tmp",
        "pronom_only": False,
        "v": False,
        "sigs": None,
        "matchprintf": None,
        "nomatchprintf": None,
        "q": True,
        "bufsize": None,
        "container_bufsize": None,
        "zip": False,
        "nocontainer": False,
        "loadformats": None,
        "useformats": None,
        "nouseformats": None,
        "input": None,
        "files": ["-"],
        "recurse": False,
        "noextension": False,
        "filename": None,
    }
    args.update(overrides)
    return SimpleNamespace(**args)


def test_main_version_flag_exits(monkeypatch, capsys):
    monkeypatch.setattr(fido_mod, "parse_cli_args", lambda *_a: _main_args(v=True))
    monkeypatch.setattr(
        fido_mod,
        "get_local_versions",
        lambda _c: SimpleNamespace(
            pronom_signature="formats-v116.xml",
            pronom_container_signature="container-signature.xml",
            fido_extension_signature="format_extensions.xml",
        ),
    )

    with pytest.raises(SystemExit) as exc:
        fido_mod.main(["-v"])

    assert exc.value.code == 0
    assert "FIDO v" in capsys.readouterr().out


def test_main_version_flag_wins_over_sigs(monkeypatch, capsys):
    monkeypatch.setattr(fido_mod, "parse_cli_args", lambda *_a: _main_args(v=True, sigs="update"))
    monkeypatch.setattr(
        fido_mod,
        "get_local_versions",
        lambda _c: SimpleNamespace(
            pronom_signature="formats-v116.xml",
            pronom_container_signature="container-signature.xml",
            fido_extension_signature="format_extensions.xml",
        ),
    )
    monkeypatch.setattr(fido_mod, "sig_file_actions", lambda *_a: pytest.fail("-sigs must not run when -v is given"))

    with pytest.raises(SystemExit) as exc:
        fido_mod.main(["-v", "-sigs", "update"])

    assert exc.value.code == 0
    assert "FIDO v" in capsys.readouterr().out


def test_main_sigs_calls_action(monkeypatch):
    calls = {}
    monkeypatch.setattr(fido_mod, "parse_cli_args", lambda *_a: _main_args(sigs="LiSt"))
    monkeypatch.setattr(
        fido_mod,
        "get_local_versions",
        lambda _c: SimpleNamespace(
            pronom_signature="formats-v116.xml",
            pronom_container_signature="container-signature.xml",
            fido_extension_signature="format_extensions.xml",
        ),
    )
    monkeypatch.setattr(fido_mod, "sig_file_actions", lambda value, conf_dir: calls.update(sigs=value, conf_dir=conf_dir))

    with pytest.raises(SystemExit) as exc:
        fido_mod.main(["-sig", "list"])

    assert exc.value.code == 0
    assert calls["sigs"] == "list"
    assert calls["conf_dir"] == _main_args().confdir, "-confdir must reach the signature actions"


def test_main_stdin_zip_raises_runtime(monkeypatch):
    class DummyFido:
        def __init__(self, **kwargs):
            self.zip = kwargs["zip"]
            self.current_file = ""

        def print_summary(self, _secs):
            return None

    monkeypatch.setattr(fido_mod, "parse_cli_args", lambda *_a: _main_args(zip=True, files=["-"]))
    monkeypatch.setattr(
        fido_mod,
        "get_local_versions",
        lambda _c: SimpleNamespace(
            pronom_signature="formats-v116.xml",
            pronom_container_signature="container-signature.xml",
            fido_extension_signature="format_extensions.xml",
        ),
    )
    monkeypatch.setattr(fido_mod, "Fido", DummyFido)

    with pytest.raises(RuntimeError):
        fido_mod.main([])


UNRECOGNISED_BYTES = b"\x01\x02\x03\x04"

needs_unprivileged_user = pytest.mark.skipif(
    fido_mod.os.name == "nt" or (hasattr(fido_mod.os, "geteuid") and fido_mod.os.geteuid() == 0),
    reason="needs a directory this user is not allowed to read",
)


def _run_main(monkeypatch, *arguments):
    """Run main() end to end: real argument parsing, real signatures, isolated module defaults."""
    monkeypatch.setattr(fido_mod, "defaults", dict(fido_mod.defaults))
    fido_mod.main(list(arguments))


def test_main_nomatchprintf_alone_expands_escapes(monkeypatch, tmp_path, capsys):
    unknown = tmp_path / "unknown.zzz"
    unknown.write_bytes(UNRECOGNISED_BYTES)

    _run_main(monkeypatch, "-q", "-nomatchprintf", r"NOMATCH %(info.filename)s\n", str(unknown))

    assert capsys.readouterr().out == f"NOMATCH {unknown}\n"


def test_main_matchprintf_and_nomatchprintf_each_expand_their_own_escapes(monkeypatch, tmp_path, capsys):
    known = tmp_path / "known"
    known.write_bytes(id_test_data[0][0])
    unknown = tmp_path / "unknown.zzz"
    unknown.write_bytes(UNRECOGNISED_BYTES)

    _run_main(
        monkeypatch,
        "-q",
        "-matchprintf",
        r"MATCH %(info.puid)s\t%(info.filename)s\n",
        "-nomatchprintf",
        r"NOMATCH\t%(info.filename)s\n",
        str(known),
        str(unknown),
    )

    assert capsys.readouterr().out == f"MATCH fmt/1000\t{known}\nNOMATCH\t{unknown}\n"


def test_list_files_yields_files_and_the_contents_of_directories(tmp_path):
    single = tmp_path / "single.bin"
    single.write_bytes(b"x")
    folder = tmp_path / "folder"
    folder.mkdir()
    inside = folder / "inside.bin"
    inside.write_bytes(b"x")

    assert list(fido_mod.list_files([str(single), str(folder)])) == [str(single), str(inside)]


def test_list_files_reports_a_missing_path_and_carries_on(tmp_path, capsys):
    present = tmp_path / "present.bin"
    present.write_bytes(b"x")
    missing = tmp_path / "missing.bin"

    assert list(fido_mod.list_files([str(missing), str(present)])) == [str(present)]

    assert capsys.readouterr().err == f"FIDO: Not a file or directory: {missing}\n"


def test_main_reports_a_missing_path_even_when_quiet_and_identifies_the_rest(monkeypatch, tmp_path, capsys):
    present = tmp_path / "present"
    present.write_bytes(id_test_data[0][0])
    missing = tmp_path / "missing"

    _run_main(monkeypatch, "-q", str(missing), str(present))

    captured = capsys.readouterr()
    assert f"FIDO: Not a file or directory: {missing}\n" in captured.err
    assert next(csv.reader(io.StringIO(captured.out)))[2] == "fmt/1000"


def _make_stat_fail(monkeypatch, path, error):
    real_stat = fido_mod.os.stat

    def failing_stat(candidate, *args, **kwargs):
        if candidate == str(path):
            raise error
        return real_stat(candidate, *args, **kwargs)

    monkeypatch.setattr(fido_mod.os, "stat", failing_stat)


def test_list_files_reports_a_path_it_cannot_access_and_carries_on(monkeypatch, tmp_path, capsys):
    denied = tmp_path / "denied.bin"
    denied.write_bytes(b"x")
    present = tmp_path / "present.bin"
    present.write_bytes(b"x")
    _make_stat_fail(monkeypatch, denied, PermissionError(errno.EACCES, "Permission denied", str(denied)))

    assert list(fido_mod.list_files([str(denied), str(present)])) == [str(present)]

    assert capsys.readouterr().err == f"FIDO: Cannot access {denied}: Permission denied\n"


def test_main_reports_a_path_it_cannot_access_even_when_quiet_and_identifies_the_rest(monkeypatch, tmp_path, capsys):
    denied = tmp_path / "denied"
    denied.write_bytes(b"x")
    present = tmp_path / "present"
    present.write_bytes(id_test_data[0][0])
    _make_stat_fail(monkeypatch, denied, PermissionError(errno.EACCES, "Permission denied", str(denied)))

    _run_main(monkeypatch, "-q", str(denied), str(present))

    captured = capsys.readouterr()
    assert f"FIDO: Cannot access {denied}: Permission denied\n" in captured.err
    assert "Not a file or directory" not in captured.err
    assert next(csv.reader(io.StringIO(captured.out)))[2] == "fmt/1000"


@needs_unprivileged_user
def test_list_files_reports_a_file_inside_an_unreadable_directory_as_inaccessible(tmp_path, capsys):
    locked = tmp_path / "locked"
    locked.mkdir()
    inside = locked / "inside.bin"
    inside.write_bytes(b"x")
    present = tmp_path / "present.bin"
    present.write_bytes(b"x")
    locked.chmod(0o000)
    try:
        listed = list(fido_mod.list_files([str(inside), str(present)]))
    finally:
        locked.chmod(0o700)

    assert listed == [str(present)]
    assert capsys.readouterr().err == f"FIDO: Cannot access {inside}: {fido_mod.os.strerror(errno.EACCES)}\n"


@pytest.mark.skipif(not hasattr(fido_mod.os, "symlink") or fido_mod.os.name == "nt", reason="needs POSIX symlinks")
def test_list_files_reports_a_symlink_loop_as_inaccessible(tmp_path, capsys):
    loop = tmp_path / "loop"
    loop.symlink_to(loop)

    assert list(fido_mod.list_files([str(loop)])) == []

    assert capsys.readouterr().err == f"FIDO: Cannot access {loop}: {fido_mod.os.strerror(errno.ELOOP)}\n"


@pytest.mark.skipif(not hasattr(fido_mod.os, "mkfifo"), reason="needs POSIX named pipes")
def test_list_files_reports_a_named_pipe_as_not_a_file_or_directory(tmp_path, capsys):
    pipe = tmp_path / "pipe"
    fido_mod.os.mkfifo(pipe)

    assert list(fido_mod.list_files([str(pipe)])) == []

    assert capsys.readouterr().err == f"FIDO: Not a file or directory: {pipe}\n"


def test_list_files_reports_a_path_with_a_nul_character_as_not_a_file_or_directory(capsys):
    assert list(fido_mod.list_files(["bad\0name"])) == []

    assert capsys.readouterr().err == "FIDO: Not a file or directory: bad\0name\n"


def test_list_files_skips_an_empty_root_and_carries_on(tmp_path, capsys):
    present = tmp_path / "present.bin"
    present.write_bytes(b"x")

    assert list(fido_mod.list_files(["", "\n", str(present)], strip_line_endings=True)) == [str(present)]

    assert capsys.readouterr().err == "FIDO: Empty path skipped\n" * 2


def test_main_skips_an_empty_path_argument_and_identifies_the_rest(monkeypatch, tmp_path, capsys):
    present = tmp_path / "present"
    present.write_bytes(id_test_data[0][0])

    _run_main(monkeypatch, "-q", "", str(present))

    captured = capsys.readouterr()
    assert "FIDO: Empty path skipped" in captured.err
    assert next(csv.reader(io.StringIO(captured.out)))[2] == "fmt/1000"


@pytest.mark.parametrize(
    "line, expected",
    [
        ("path\n", "path"),
        ("path\r\n", "path"),
        ("path", "path"),
        ("path\r", "path\r"),
        ("path\n\n", "path\n"),
        ("\r\n", ""),
        ("\n", ""),
        ("", ""),
    ],
)
def test_strip_line_ending_drops_one_line_ending_only(line, expected):
    assert fido_mod.strip_line_ending(line) == expected, f"{line!r} stripped to something other than {expected!r}"


def test_list_files_strips_line_endings_from_listed_paths_when_asked(tmp_path):
    unix = tmp_path / "unix.bin"
    unix.write_bytes(b"x")
    windows = tmp_path / "windows.bin"
    windows.write_bytes(b"x")
    last = tmp_path / "last.bin"
    last.write_bytes(b"x")

    listed = list(fido_mod.list_files([f"{unix}\n", f"{windows}\r\n", str(last)], strip_line_endings=True))

    assert listed == [str(unix), str(windows), str(last)]


def test_list_files_keeps_a_trailing_newline_of_a_root_by_default(tmp_path, capsys):
    record = tmp_path / "record"
    record.write_bytes(b"x")

    assert list(fido_mod.list_files([f"{record}\n"])) == []

    assert capsys.readouterr().err == f"FIDO: Not a file or directory: {record}\n\n"


@pytest.mark.skipif(fido_mod.os.name == "nt", reason="Windows file names cannot contain a newline")
def test_list_files_finds_a_file_whose_name_ends_in_a_newline_by_default(tmp_path, capsys):
    plain = tmp_path / "record"
    plain.write_bytes(b"x")
    with_newline = tmp_path / "record\n"
    with_newline.write_bytes(b"x")

    assert list(fido_mod.list_files([str(with_newline)])) == [str(with_newline)]

    assert capsys.readouterr().err == ""


def _write_iso_like_image(path):
    """Write what the ISO 9660 signature needs: a primary descriptor at 32768, a terminator one 2048 byte block on."""
    primary_offset = 32768
    terminator_offset = primary_offset + 2048
    image = bytearray(terminator_offset + 4096)
    image[primary_offset : primary_offset + 7] = b"\x01CD001\x01"
    image[terminator_offset : terminator_offset + 7] = b"\xffCD001\x01"
    path.write_bytes(image)


def test_main_bufsize_shorter_than_a_signature_offset_falls_back_to_the_extension(monkeypatch, tmp_path, capsys):
    image = tmp_path / "disc.iso"
    _write_iso_like_image(image)

    _run_main(monkeypatch, "-q", "-bufsize", "2048", str(image))

    rows = list(csv.reader(io.StringIO(capsys.readouterr().out)))
    assert rows, "no match line was printed"
    assert {row[8] for row in rows} == {"extension"}, f"expected extension matches only, got {rows}"
    assert "fmt/468" not in {row[2] for row in rows}, f"ISO 9660 matched in a buffer shorter than its signature: {rows}"


def test_main_bufsize_beyond_a_signature_offset_matches_it(monkeypatch, tmp_path, capsys):
    image = tmp_path / "disc.iso"
    _write_iso_like_image(image)

    _run_main(monkeypatch, "-q", "-bufsize", "131072", str(image))

    rows = list(csv.reader(io.StringIO(capsys.readouterr().out)))
    assert [(row[2], row[8]) for row in rows] == [("fmt/468", "signature")], f"unexpected matches: {rows}"


def test_main_does_not_strip_a_newline_from_a_path_argument(monkeypatch, tmp_path, capsys):
    record = tmp_path / "record"
    record.write_bytes(id_test_data[0][0])

    _run_main(monkeypatch, "-q", f"{record}\n")

    captured = capsys.readouterr()
    assert captured.err == f"FIDO: Not a file or directory: {record}\n\n"
    assert captured.out == "", f"the file {record} was identified through a path that does not exist: {captured.out}"


def test_main_identifies_crlf_terminated_paths_from_stdin_and_skips_blank_lines(monkeypatch, tmp_path, capsys):
    first = tmp_path / "first"
    first.write_bytes(id_test_data[0][0])
    second = tmp_path / "second"
    second.write_bytes(id_test_data[0][0])
    monkeypatch.setattr(fido_mod.sys, "stdin", io.StringIO(f"{first}\r\n\r\n{second}\r\n"))

    _run_main(monkeypatch, "-q", "-input", "-")

    captured = capsys.readouterr()
    assert captured.err == "FIDO: Empty path skipped\n", f"unexpected diagnostics: {captured.err!r}"
    rows = list(csv.reader(io.StringIO(captured.out)))
    assert [(row[2], row[6]) for row in rows] == [("fmt/1000", str(first)), ("fmt/1000", str(second))]


def test_main_identifies_paths_listed_in_an_input_file_with_either_line_ending(monkeypatch, tmp_path, capsys):
    unix = tmp_path / "unix"
    unix.write_bytes(id_test_data[0][0])
    windows = tmp_path / "windows"
    windows.write_bytes(id_test_data[0][0])
    listing = tmp_path / "paths.txt"
    listing.write_bytes(f"{unix}\n{windows}\r\n".encode())

    _run_main(monkeypatch, "-q", "-input", str(listing))

    captured = capsys.readouterr()
    assert captured.err == "", f"unexpected diagnostics: {captured.err!r}"
    assert [row[6] for row in csv.reader(io.StringIO(captured.out))] == [str(unix), str(windows)]


@pytest.fixture(params=[pytest.param("chmod", marks=needs_unprivileged_user), "faked scandir"])
def make_unlistable(request, monkeypatch):
    """Return a function that makes a directory fail to list, for real with chmod or, for any user, by faking the error."""
    chmodded = []

    def make(directory):
        if request.param == "chmod":
            directory.chmod(0o000)
            chmodded.append(directory)
            return
        real_scandir = fido_mod.os.scandir

        def failing_scandir(path="."):
            if path == str(directory):
                raise PermissionError(errno.EACCES, fido_mod.os.strerror(errno.EACCES), path)
            return real_scandir(path)

        monkeypatch.setattr(fido_mod.os, "scandir", failing_scandir)

    yield make
    for directory in chmodded:
        directory.chmod(0o700)


def test_list_files_reports_a_directory_it_cannot_read_and_carries_on(tmp_path, capsys, make_unlistable):
    unreadable = tmp_path / "unreadable"
    unreadable.mkdir()
    present = tmp_path / "present.bin"
    present.write_bytes(b"x")
    make_unlistable(unreadable)

    listed = list(fido_mod.list_files([str(unreadable), str(present)]))

    assert listed == [str(present)]
    assert capsys.readouterr().err == f"FIDO: Cannot scan directory: {unreadable}\n"


def test_list_files_recurse_reports_an_unreadable_subdirectory_and_yields_the_rest(tmp_path, capsys, make_unlistable):
    top = tmp_path / "top"
    readable = top / "readable"
    unreadable = top / "unreadable"
    for directory in (readable, unreadable):
        directory.mkdir(parents=True)
    (top / "top.bin").write_bytes(b"x")
    (readable / "readable.bin").write_bytes(b"x")
    (unreadable / "hidden.bin").write_bytes(b"x")
    make_unlistable(unreadable)

    listed = sorted(fido_mod.list_files([str(top)], recurse=True))

    assert listed == [str(readable / "readable.bin"), str(top / "top.bin")], f"unexpected files: {listed}"
    assert capsys.readouterr().err == f"FIDO: Cannot scan directory: {unreadable}\n"


def test_print_matches_no_match_outputs_ko(monkeypatch, capsys):
    fido = _make_fido(monkeypatch)
    fido.current_filesize = 12
    fido.current_count = 1

    fido.print_matches("/tmp/file.bin", [], 0.01)

    assert "KO" in capsys.readouterr().out


def test_print_matches_with_match_outputs_ok(monkeypatch, capsys):
    fido = _make_fido(monkeypatch)
    fmt = _format_element("fmt/1", extension="txt")
    XET.SubElement(fmt, "mime").text = "text/plain"
    XET.SubElement(fmt, "version").text = "1.0"
    XET.SubElement(fmt, "alias").text = "Alias"
    fido.current_filesize = 12
    fido.current_count = 1

    fido.print_matches("/tmp/file.txt", [(fmt, "sig")], 0.01, "signature")

    output = capsys.readouterr().out
    assert "OK" in output
    assert "fmt/1" in output


def test_match_formats_covers_positions_and_exception_path(monkeypatch, capsys):
    fido = _make_fido(monkeypatch)

    def add_signature(fmt, name, pos, regex):
        sig = XET.SubElement(fmt, "signature")
        XET.SubElement(sig, "name").text = name
        pat = XET.SubElement(sig, "pattern")
        XET.SubElement(pat, "position").text = pos
        XET.SubElement(pat, "regex").text = regex

    bof_fmt = _format_element("fmt/1")
    eof_fmt = _format_element("fmt/2")
    var_fmt = _format_element("fmt/3")
    ifb_fmt = _format_element("fmt/4")
    bad_fmt = _format_element("fmt/5")

    add_signature(bof_fmt, "bof", "BOF", "abc")
    add_signature(eof_fmt, "eof", "EOF", "xyz")
    add_signature(var_fmt, "var", "VAR", "abc")
    add_signature(ifb_fmt, "ifb", "IFB", "abc")
    bad_sig = XET.SubElement(bad_fmt, "signature")
    XET.SubElement(bad_sig, "name").text = "bad"
    bad_pat = XET.SubElement(bad_sig, "pattern")
    XET.SubElement(bad_pat, "position").text = "BOF"

    fido.formats = [bof_fmt, eof_fmt, var_fmt, ifb_fmt, bad_fmt]
    fido.puid_has_priority_over_map = {
        "fmt/1": frozenset(),
        "fmt/2": frozenset(),
        "fmt/3": frozenset(),
        "fmt/4": frozenset(),
        "fmt/5": frozenset(),
    }

    matches = fido.match_formats(b"abc", b"xyz")
    matched_puids = {m[0].find("puid").text for m in matches}

    assert {"fmt/1", "fmt/2", "fmt/3", "fmt/4"}.issubset(matched_puids)
    assert "NoneType" in capsys.readouterr().err


def test_get_buffers_non_seekable_long_stream(monkeypatch):
    fido = _make_fido(monkeypatch)
    fido.bufsize = 8
    data = b"0123456789abcdefghijABCDEFGHIJ"

    bof, eof, _ = fido.get_buffers(io.BytesIO(data), length=len(data), seekable=False)

    assert bof == data[:8]
    assert eof == data[-8:]


def test_buffered_read_overlap_and_non_overlap(monkeypatch, tmp_path):
    fido = _make_fido(monkeypatch)
    sample = tmp_path / "sample.bin"
    sample.write_bytes(b"0123456789abcdefghij")
    fido.current_file = str(sample)
    fido.current_filesize = sample.stat().st_size
    fido.bufsize = 8
    fido.container_bufsize = 4

    no_overlap = fido.buffered_read(0, overlap=False)
    with_overlap = fido.buffered_read(2, overlap=True)

    assert no_overlap == b"01234567"
    assert with_overlap == b"23456789"


def test_walk_zip_recurses_for_nested_container(monkeypatch, tmp_path):
    fido = _make_fido(monkeypatch)
    sample = tmp_path / "sample.zip"
    import zipfile

    with zipfile.ZipFile(sample, "w") as zf:
        zf.writestr("inner.bin", b"abc")

    zip_fmt = _format_element("fmt/999", container="zip")
    calls = {"recurse": 0}
    monkeypatch.setattr(fido, "match_formats", lambda *_a: [(zip_fmt, "sig")])
    monkeypatch.setattr(fido, "handle_matches", lambda *_a: None)
    monkeypatch.setattr(
        fido,
        "identify_contents",
        lambda *_a, **_k: calls.__setitem__("recurse", calls["recurse"] + 1),
    )

    fido.walk_zip(str(sample), extension=False)

    assert calls["recurse"] == 1


def test_walk_tar_processes_files_and_recurses(monkeypatch):
    fido = _make_fido(monkeypatch)
    zip_fmt = _format_element("fmt/999", container="zip")
    calls = {"handled": 0, "recurse": 0}

    class DummyMember:
        def __init__(self, name, is_file=True):
            self.name = name
            self.size = 3
            self._is_file = is_file

        def isfile(self):
            return self._is_file

    class DummyTar:
        def __init__(self, *_a, **_k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def getmembers(self):
            return [DummyMember("dir", is_file=False), DummyMember("file.bin", is_file=True)]

        def extractfile(self, _item):
            return io.BytesIO(b"abc")

    monkeypatch.setattr(fido_mod.tarfile, "TarFile", DummyTar)
    monkeypatch.setattr(fido, "get_buffers", lambda *_a, **_k: (b"abc", b"abc", 3))
    monkeypatch.setattr(fido, "match_formats", lambda *_a: [(zip_fmt, "sig")])
    monkeypatch.setattr(fido, "handle_matches", lambda *_a: calls.__setitem__("handled", calls["handled"] + 1))
    monkeypatch.setattr(fido, "identify_contents", lambda *_a, **_k: calls.__setitem__("recurse", calls["recurse"] + 1))

    fido.walk_tar("archive.tar", None)

    assert calls["handled"] == 1
    assert calls["recurse"] == 1


def test_main_loadformats_and_useformats(monkeypatch, tmp_path, capsys):
    class DummyFido:
        def __init__(self, **kwargs):
            self.zip = kwargs["zip"]
            self.current_file = ""
            self.loaded = []
            self.formats = [_format_element("fmt/1"), _format_element("fmt/2")]

        def load_fido_xml(self, file):
            self.loaded.append(file)

        def identify_file(self, *_a, **_k):
            return None

        def print_summary(self, _secs):
            return None

    listed = tmp_path / "files.txt"
    listed.write_text("a.bin\n", encoding="utf-8")
    created = {}
    monkeypatch.setattr(
        fido_mod,
        "parse_cli_args",
        lambda *_a: _main_args(
            q=False,
            loadformats="extra1.xml,extra2.xml",
            useformats="fmt/1",
            input=str(listed),
            files=[],
        ),
    )
    monkeypatch.setattr(
        fido_mod,
        "get_local_versions",
        lambda _c: SimpleNamespace(
            pronom_signature="formats-v116.xml",
            pronom_container_signature="container-signature.xml",
            fido_extension_signature="format_extensions.xml",
        ),
    )
    monkeypatch.setattr(fido_mod, "list_files", lambda *_a, **_k: [])
    monkeypatch.setattr(fido_mod, "Fido", lambda **kwargs: created.setdefault("fido", DummyFido(**kwargs)))

    fido_mod.main([])

    assert created["fido"].loaded == ["extra1.xml", "extra2.xml"]
    assert len(created["fido"].formats) == 1
    assert created["fido"].formats[0].find("puid").text == "fmt/1"
    assert "FIDO v" in capsys.readouterr().err


def test_main_keyboard_interrupt_exits_with_context(monkeypatch):
    class DummyFido:
        def __init__(self, **kwargs):
            self.zip = kwargs["zip"]
            self.current_file = "STDIN"

        def identify_stream(self, *_a, **_k):
            raise KeyboardInterrupt()

        def print_summary(self, _secs):
            return None

    monkeypatch.setattr(fido_mod, "parse_cli_args", lambda *_a: _main_args(zip=False, files=["-"]))
    monkeypatch.setattr(
        fido_mod,
        "get_local_versions",
        lambda _c: SimpleNamespace(
            pronom_signature="formats-v116.xml",
            pronom_container_signature="container-signature.xml",
            fido_extension_signature="format_extensions.xml",
        ),
    )
    monkeypatch.setattr(fido_mod, "Fido", DummyFido)

    with pytest.raises(SystemExit) as exc:
        fido_mod.main([])

    assert "Interrupt while identifying file STDIN" in str(exc.value)


def test_signature_regexes_are_compiled_once_and_re_cache_is_untouched(monkeypatch, tmp_path):
    """Fido must not depend on (or resize) the re module cache: with more signatures than the
    cache holds, every file used to recompile every regex."""
    max_cache = fido_mod.re._MAXCACHE
    compiled = []
    real_compile = fido_mod.re.compile
    monkeypatch.setattr(fido_mod.re, "compile", lambda p, *a: compiled.append(p) or real_compile(p, *a))
    formats = tmp_path / "formats.xml"
    formats.write_text(
        "<formats>"
        + "".join(
            "<format><puid>fmt/{0}</puid><name>F{0}</name><signature><name>S{0}</name><pattern>"
            "<position>BOF</position><regex>(?s)\\A{1}</regex></pattern></signature></format>".format(i, magic)
            for i, magic in enumerate(("ZXTape", "GIF8", "%PDF"))
        )
        + "</formats>"
    )
    sample = tmp_path / "sample.bin"
    sample.write_bytes(b"ZXTape!\x1a\x01")

    f = Fido(quiet=True, nocontainer=True, format_files=[str(formats)])
    f.identify_file(str(sample))
    first_run = len(compiled)
    f.identify_file(str(sample))

    assert fido_mod.re._MAXCACHE == max_cache
    assert first_run > 0
    assert len(compiled) == first_run
    assert len(set(compiled)) == len(compiled)


def _create_file_named_with_bytes(directory, name, content):
    """Create a file whose name is not valid UTF-8, or skip where the platform or file system cannot hold one."""
    if fido_mod.sys.platform == "win32":
        pytest.skip("Windows cannot build a name from a byte that is not valid UTF-8, os.fsdecode raises")
    path = directory / fido_mod.os.fsdecode(name)
    try:
        path.write_bytes(content)
    except OSError as error:
        pytest.skip(f"this file system rejects names that are not valid UTF-8: {error}")
    return path


def test_main_continues_past_a_filename_that_is_not_valid_utf8(monkeypatch, tmp_path, capsys):
    """A name from a foreign file system must not abort the run, nor hide the files after it."""
    magic = id_test_data[0][0]
    undecodable = _create_file_named_with_bytes(tmp_path, b"bad\xffname", magic)
    decodable = tmp_path / "good"
    decodable.write_bytes(magic)
    monkeypatch.setattr(fido_mod, "defaults", dict(fido_mod.defaults))

    fido_mod.main(["-q", str(undecodable), str(decodable)])

    rows = list(csv.reader(io.StringIO(capsys.readouterr().out)))
    assert [row[2] for row in rows] == ["fmt/1000", "fmt/1000"], "the file after the bad name was not identified"
    assert rows[0][6].endswith("bad\\udcffname"), "the undecodable byte should be written as an escape"
    assert rows[1][6].endswith("good")


def _add_signature(fmt, name, position, regex=None):
    sig = XET.SubElement(fmt, "signature")
    XET.SubElement(sig, "name").text = name
    pat = XET.SubElement(sig, "pattern")
    XET.SubElement(pat, "position").text = position
    if regex is not None:
        XET.SubElement(pat, "regex").text = regex


def test_match_formats_names_the_format_whose_signature_fails(monkeypatch, capsys):
    fido = _make_fido(monkeypatch)
    broken = _format_element("fmt/1558")
    _add_signature(broken, "bad range", "BOF", r"(?s)\A.{3000,700}")
    valid = _format_element("fmt/1")
    _add_signature(valid, "abc", "BOF", "abc")
    fido.formats = [broken, valid]
    fido.puid_has_priority_over_map = {"fmt/1558": frozenset(), "fmt/1": frozenset()}

    matches = fido.match_formats(b"abc", b"abc")

    assert [match[0] for match in matches] == [valid], "the format after the broken one was not matched"
    error = capsys.readouterr().err
    assert error.startswith("FIDO: Error matching fmt/1558: "), error
    assert "min repeat greater than max repeat" in error


def test_match_formats_reports_a_format_without_a_puid_and_continues(monkeypatch, capsys):
    """The diagnostic for a broken entry must not itself fail on the entry that is broken."""
    fido = _make_fido(monkeypatch)
    without_puid = XET.Element("format")
    _add_signature(without_puid, "no regex", "BOF")
    valid = _format_element("fmt/1")
    _add_signature(valid, "abc", "BOF", "abc")
    fido.formats = [without_puid, valid]
    fido.puid_has_priority_over_map = {"fmt/1": frozenset()}

    matches = fido.match_formats(b"abc", b"abc")

    assert [match[0] for match in matches] == [valid], "the format after the broken one was not matched"
    error = capsys.readouterr().err
    assert error.startswith("FIDO: Error matching unknown: "), error
    assert "NoneType" in error, error


def test_process_format_element_replaces_an_existing_format_without_a_deprecation_warning(monkeypatch, recwarn):
    fido = _make_fido(monkeypatch)
    first = _format_element("fmt/1")
    second = _format_element("fmt/1")

    fido.process_format_element(first)
    fido.process_format_element(second)

    assert fido.formats == [second]
    assert fido.puid_format_map["fmt/1"] is second
    assert not [w for w in recwarn if issubclass(w.category, DeprecationWarning)]


class _FalsyFormat(XET.Element):
    def __bool__(self):
        return False


def test_process_format_element_replaces_an_existing_format_that_is_falsy(monkeypatch):
    """An earlier format is found by identity, whatever its truth value, so a reload does not add a duplicate."""
    fido = _make_fido(monkeypatch)
    first = _FalsyFormat("format")
    XET.SubElement(first, "puid").text = "fmt/1"
    second = _format_element("fmt/1")

    fido.process_format_element(first)
    fido.process_format_element(second)

    assert fido.formats == [second], f"expected the first format to be replaced, got {len(fido.formats)} formats"
    assert fido.puid_format_map["fmt/1"] is second


@pytest.mark.parametrize(
    "stream_errors, expected_name",
    [
        ("strict", b"bad\\udcffname"),
        ("surrogateescape", b"bad\xffname"),
        ("replace", b"bad?name"),
    ],
)
def test_main_only_replaces_a_strict_stdout_error_handler(monkeypatch, tmp_path, stream_errors, expected_name):
    """A stdout that already tolerates the name (C locale, UTF-8 mode) must keep writing the original byte."""
    path = _create_file_named_with_bytes(tmp_path, b"bad\xffname", id_test_data[0][0])
    monkeypatch.setattr(fido_mod, "defaults", dict(fido_mod.defaults))
    written = io.BytesIO()
    stream = io.TextIOWrapper(written, encoding="utf-8", errors=stream_errors, newline="")
    monkeypatch.setattr(fido_mod.sys, "stdout", stream)

    fido_mod.main(["-q", str(path)])
    stream.flush()

    output = written.getvalue()
    assert b"/" + expected_name + b'"' in output, f"stdout errors={stream_errors!r} wrote {output!r}"


def _identify_listed_names(monkeypatch, capsys, listing, arguments):
    monkeypatch.setattr(fido_mod, "defaults", dict(fido_mod.defaults))
    monkeypatch.setattr(fido_mod.sys, "stdin", io.TextIOWrapper(io.BytesIO(listing), encoding="utf-8"))

    fido_mod.main(["-q", *arguments])

    return list(csv.reader(io.StringIO(capsys.readouterr().out)))


def _assert_both_listed_names_identified(rows):
    assert [row[2] for row in rows] == ["fmt/1000", "fmt/1000"], f"expected both listed files identified, got {rows}"
    assert rows[0][6].endswith("bad\\udcffname"), f"the undecodable name was not kept: {rows[0][6]}"
    assert rows[1][6].endswith("good"), f"the file after the undecodable name was not identified: {rows[1][6]}"


def test_main_identifies_a_filename_that_is_not_valid_utf8_listed_on_stdin(monkeypatch, tmp_path, capsys):
    bad = _create_file_named_with_bytes(tmp_path, b"bad\xffname", id_test_data[0][0])
    good = tmp_path / "good"
    good.write_bytes(id_test_data[0][0])
    listing = fido_mod.os.fsencode(bad) + b"\n" + fido_mod.os.fsencode(good) + b"\n"

    rows = _identify_listed_names(monkeypatch, capsys, listing, ["-input", "-"])

    _assert_both_listed_names_identified(rows)


def test_main_identifies_a_filename_that_is_not_valid_utf8_listed_in_a_file(monkeypatch, tmp_path, capsys):
    bad = _create_file_named_with_bytes(tmp_path, b"bad\xffname", id_test_data[0][0])
    good = tmp_path / "good"
    good.write_bytes(id_test_data[0][0])
    listing = tmp_path / "files.txt"
    listing.write_bytes(fido_mod.os.fsencode(bad) + b"\n" + fido_mod.os.fsencode(good) + b"\n")

    rows = _identify_listed_names(monkeypatch, capsys, b"", ["-input", str(listing)])

    _assert_both_listed_names_identified(rows)
