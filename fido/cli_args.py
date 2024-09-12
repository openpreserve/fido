import argparse
import sys
from argparse import ArgumentParser, RawTextHelpFormatter


def parse_cli_args(argv: list[str], defaults: dict) -> argparse.Namespace:
    """
    Parse command-line arguments.
    Args:
        argv (list[str]): List of command-line arguments. Could be sys.argv
        defaults (dict): Dictionary of default values. Expects to find configdir, bufsize and container_bufsize.
    Returns:
        argparse.Namespace: Parsed command-line arguments. Reference via name as in args.v or args.recurse.
    """

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
    parser.add_argument(
        "-matchprintf",
        metavar="FORMATSTRING",
        default=None,
        help="format string (Python style) to use on match. See nomatchprintf, README.txt.",
    )
    parser.add_argument(
        "-nomatchprintf",
        metavar="FORMATSTRING",
        default=None,
        help="format string (Python style) to use if no match. See README.txt",
    )
    parser.add_argument(
        "-bufsize",
        type=int,
        default=None,
        help=f"size (in bytes) of the buffer to match against (default={defaults['bufsize']})",
    )
    parser.add_argument(
        "-sigs",
        default=None,
        metavar="SIG_ACT",
        help='SIG_ACT "check" for new version\nSIG_ACT "update" to latest\nSIG_ACT "list" available versions\nSIG_ACT "n" use version n.',
    )
    parser.add_argument(
        "-container_bufsize",
        type=int,
        default=None,
        help=f"size (in bytes) of the buffer to match against (default={defaults['container_bufsize']}).",
    )
    parser.add_argument(
        "-loadformats", default=None, metavar="XML1,...,XMLn", help="comma separated string of XML format files to add."
    )
    parser.add_argument(
        "-confdir",
        default=defaults["config_dir"],
        help="configuration directory to load_fido_xml, for example, the format specifications from.",
    )

    return parser.parse_args(argv)
