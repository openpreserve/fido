import pytest

from fido.cli_args import MIN_BUFSIZE, parse_cli_args
from fido.fido import defaults

# Common argument string


def test_parse_args_input_valid():
    arg_string = (
        "-v -q -recurse -zip -noextension -nocontainer -pronom_only "
        "-input files.txt "
        "-useformats=fmt1,fmt2 -nouseformats=fmt3,fmt4"
    )
    args = parse_cli_args(arg_string.split(), defaults)
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
    assert args.q
    assert args.zip
    assert not args.noextension
    assert not args.nocontainer
    assert not args.pronom_only
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


def test_parse_args_bufsize_defaults_to_none():
    assert parse_cli_args(["file.ext"], defaults).bufsize is None


@pytest.mark.parametrize("value", [str(MIN_BUFSIZE), "131072"])
def test_parse_args_bufsize_accepts_the_minimum_and_above(value):
    assert parse_cli_args(["-bufsize", value, "file.ext"], defaults).bufsize == int(value)


@pytest.mark.parametrize("value", ["0", "-1", str(MIN_BUFSIZE - 1)])
def test_parse_args_bufsize_below_the_minimum_is_a_usage_error(value, capsys):
    with pytest.raises(SystemExit) as exc:
        parse_cli_args(["-bufsize", value, "file.ext"], defaults)
    assert exc.value.code == 2
    assert f"at least {MIN_BUFSIZE} bytes" in capsys.readouterr().err


def test_parse_args_bufsize_not_an_integer_is_a_usage_error(capsys):
    with pytest.raises(SystemExit) as exc:
        parse_cli_args(["-bufsize", "many", "file.ext"], defaults)
    assert exc.value.code == 2
    assert "invalid buffer_size value: 'many'" in capsys.readouterr().err
