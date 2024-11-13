#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import io
from time import sleep

import pytest

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
