import pytest

from fido.cli_args import parse_cli_args
from fido.fido import defaults

# Common argument string


def test_parse_args_input_valid():
    arg_string = (
        "-v -q -recurse -zip -noextension -nocontainer -pronom_only "
        "-input files.txt "
        "-useformats=fmt1,fmt2 -nouseformats=fmt3,fmt4"
    )
    args = parse_cli_args(arg_string.split(), defaults)
    print(arg_string.split())
    print(args)
    assert args.v
    assert args.q
    assert args.recurse
    assert args.zip
    assert args.noextension
    assert args.nocontainer
    assert args.pronom_only
    assert args.input == "files.txt"
    assert args.useformats == "fmt1,fmt2"
    assert args.nouseformats == "fmt3,fmt4"


def test_parse_args_files_valid():
    arg_string = "-q -zip file1.ext file2.ext"
    args = parse_cli_args(arg_string.split(), defaults)
    print(arg_string.split())
    print(args)
    assert args.q
    assert args.zip
    assert args.noextension
    assert args.nocontainer
    assert args.pronom_only
    assert args.files == ["file1.ext", "file2.ext"]
    assert args.useformats is None
    assert args.nouseformats is None


def test_parse_args_invalid():
    arg_string = "-q -zip -bad_arg file1.ext file2.ext"
    with pytest.raises(SystemExit):
        parse_cli_args(arg_string.split(), defaults)


def test_parse_files_and_input_invalid():
    arg_string = "-q -zip -input files.txt file1.ext file2.ext"
    with pytest.raises(SystemExit):
        parse_cli_args(arg_string.split(), defaults)
