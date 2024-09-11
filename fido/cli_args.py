import argparse
import sys
from argparse import ArgumentParser, RawTextHelpFormatter


def build_parser() -> ArgumentParser:
    defaults = {
        "description": "FIDO - File Identification Tool",
        "epilog": "For more information, visit the official documentation.",
    }

    parser = ArgumentParser(
        description=defaults["description"],
        epilog=defaults["epilog"],
        fromfile_prefix_chars="@",
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument("-v", default=False, action="store_true", help="show version information")
    parser.add_argument("-q", default=False, action="store_true", help="run (more) quietly")
    parser.add_argument("-recurse", default=False, action="store_true", help="recurse into subdirectories")
    parser.add_argument("-zip", default=False, action="store_true", help="recurse into zip and tar files")
    parser.add_argument(
        "-noextension",
        default=False,
        action="store_true",
        help="disable extension matching, reduces number of matches but may reduce false positives",
    )
    parser.add_argument(
        "-nocontainer",
        default=False,
        action="store_true",
        help="disable deep scan of container documents, increases speed but may reduce accuracy with big files",
    )
    parser.add_argument(
        "-pronom_only",
        default=False,
        action="store_true",
        help="disables loading of format extensions file, only PRONOM signatures are loaded, may reduce accuracy of results",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-input", default=False, help="file containing a list of files to check, one per line. - means stdin"
    )
    group.add_argument(
        "files",
        nargs="*",
        default=[],
        metavar="FILE",
        help="files to check. If the file is -, then read content from stdin. In this case, python must be invoked with -u or it may convert the line terminators.",
    )

    parser.add_argument("-filename", default=None, help="filename if file contents passed through STDIN")
    parser.add_argument(
        "-useformats",
        metavar="INCLUDEPUIDS",
        default=None,
        help="comma separated string of formats to use in identification",
    )
    parser.add_argument(
        "-nouseformats",
        metavar="EXCLUDEPUIDS",
        default=None,
        help="comma separated string of formats not to use in identification",
    )

    return parser


def parse_args(parser: ArgumentParser) -> argparse.Namespace:
    try:
        args = parser.parse_args()
    except argparse.ArgumentError as e:
        parser.print_help()
        print(f"\nError: {e}\n")
        sys.exit(1)

    return args
