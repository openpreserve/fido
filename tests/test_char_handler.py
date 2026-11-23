import pytest

from fido.utils.char_handler import expand_escapes


@pytest.mark.parametrize(
    "text, expected",
    [
        (r"a\nb", "a\nb"),
        (r"a\tb", "a\tb"),
        (r"\n\t", "\n\t"),
        ("already\nexpanded", "already\nexpanded"),
        ("no escapes", "no escapes"),
        (r"unsupported \r and \x41 stay literal", r"unsupported \r and \x41 stay literal"),
        ("", ""),
    ],
    ids=["newline", "tab", "both", "real newline untouched", "plain text", "unsupported escapes", "empty"],
)
def test_expand_escapes(text, expected):
    assert expand_escapes(text) == expected
