import argparse

import pytest

from fido.cli_args import build_parser, parse_args

# Common argument string
ARG_STRING = (
    "-v -q -recurse -zip -noextension -nocontainer -pronom_only"
    "-input files.txt"
    "-useformats=fmt1,fmt2 -nouseformats=fmt3,fmt4"
)

ARG_STRING = (
    "-v -q -recurse -zip -noextension -nocontainer -pronom_only"
    "-input files.txt"
    "-useformats=fmt1,fmt2 -nouseformats=fmt3,fmt4"
)


def test_build_parser():
    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)

    # Check if all expected arguments are present
    expected_args = ARG_STRING.split()
    for arg in expected_args:
        assert arg in parser._option_string_actions


def test_parse_args_valid():
    parser = build_parser()

    args = parse_args(parser.parse_args(ARG_STRING.split()))

    assert args.v is True
    assert args.q is True
    assert args.recurse is True
    assert args.zip is True
    assert args.noextension is True
    assert args.nocontainer is True
    assert args.pronom_only is True
    assert args.input == "input_file"
    assert args.files == ["file1", "file2"]
    assert args.filename == "filename"
    assert args.useformats == "fmt1,fmt2"
    assert args.nouseformats == "fmt3,fmt4"


def test_parse_args_invalid(monkeypatch):
    parser = build_parser()

    # Simulate invalid argument input
    monkeypatch.setattr("sys.argv", ["prog", "--invalid"])
    with pytest.raises(SystemExit):
        parse_args(parser)

    # Simulate missing required argument
    monkeypatch.setattr("sys.argv", ["prog", "-input"])
    with pytest.raises(SystemExit):
        parse_args(parser)
