#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import io
from time import sleep

from fido import fido
from fido.fido import PerfTimer

# Magic number for fmt/1000.
MAGIC = b"\x5A\x58\x54\x61\x70\x65\x21\x1A\x01"


def test_perf_timer():
    timer = PerfTimer()
    sleep(3.6)
    duration = timer.duration()
    assert duration > 0


def test_file_identification(tmp_path):
    """Reference for Fido-based format identification
        1. Create a byte-stream with a known magic number and serialise to tempfile.
        2. Call identify_file(...) to identify the file against Fido's known formats.
    """
    # Create a temporary file and write our skeleton file out to it.
    tmp_file = tmp_path / "tmp_file"
    tmp_file.write_bytes(MAGIC)

    # Create a Fido instance and call identify_file. The identify_file function
    # will create and manage a file for itself.
    f = fido.Fido()
    f.identify_file(str(tmp_file))


def test_stream_identification():
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
