#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import csv
import io
from time import sleep

from fido import fido
from fido.fido import PerfTimer

# Magic number for fmt/1000.
MAGIC = b"\x5A\x58\x54\x61\x70\x65\x21\x1A\x01"

# Expected positive PUID.
PUID = "fmt/1000"

# Expected result.
OK = "OK"


def test_perf_timer():
    timer = PerfTimer()
    sleep(3.6)
    duration = timer.duration()
    assert duration > 0


def test_file_identification(tmp_path, capsys):
    """Reference for Fido-based format identification
        1. Create a byte-stream with a known magic number and serialize to tempfile.
        2. Call identify_file(...) to identify the file against Fido's known formats.
    """
    # Create a temporary file and write our skeleton file out to it.
    tmp_file = tmp_path / "tmp_file"
    tmp_file.write_bytes(MAGIC)

    # Create a Fido instance and call identify_file. The identify_file function
    # will create and manage a file for itself.
    f = fido.Fido()
    f.identify_file(str(tmp_file))

    # Capture the stdout returned by Fido and make assertions about its
    # validity.
    captured = capsys.readouterr()
    assert captured.err == ""
    reader = csv.reader(io.StringIO(captured.out), delimiter=",")
    assert reader is not None
    row = next(reader)
    assert row[0] == OK, "row hasn't returned a positive identification"
    assert row[2] == PUID, "row doesn't contain expected PUID value"
    assert int(row[5]) == len(MAGIC), "row doesn't contain stream length"


def test_stream_identification(capsys):
    """Reference for Fido-based format identification
        1. Create a byte-stream with a known magic number.
        2. Call identify_stream(...) to identify the file against Fido's known formats.
    """
    # Create the stream object with the known magic-number.
    fstream = io.BytesIO(MAGIC)

    # Create a Fido instance and call identify_stream. The identify_stream function
    # will work on the stream as-is. This could be an open file handle that the
    # caller is managing for itself.
    f = fido.Fido()
    f.identify_stream(fstream, "filename to display", extension=False)

    # Capture the stdout returned by Fido and make assertions about its
    # validity.
    captured = capsys.readouterr()
    assert captured.err == ""
    reader = csv.reader(io.StringIO(captured.out), delimiter=",")
    assert reader is not None
    row = next(reader)
    assert row[0] == OK, "row hasn't returned a positive identification"
    assert row[2] == PUID, "row doesn't contain expected PUID value"
    assert int(row[5]) == len(MAGIC), "row doesn't contain stream length"
