#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FIDO CSV output to XML.

Author: Maurice de Rooij <maurice.de.rooij@nationaalarchief.nl>, September 2011

Usage in combination with FIDO:
- Windows: python fido.py [ARGS] | python toxml.py > output.xml
- Linux: fido.py [ARGS] | toxml.py > output.xml

Usage afterwards:
- Windows: type output.csv | toxml.py > output.xml
- Linux: cat output.csv | toxml.py > output.xml

For difference in usage, see:
- http://bugs.python.org/issue9390
- http://support.microsoft.com/default.aspx?kbid=321788
"""

from __future__ import absolute_import

import csv
import sys

from . import __version__
from .versions import get_local_versions


def main():
    """Generate XML as read from CSV and send it to the standard output stream."""
    sys.stdout.write("""<?xml version="1.0" encoding="utf-8"?>
<fido_output>
    <versions>
        <fido_version>{0}</fido_version>
        <signature_version>{1}</signature_version>
    </versions>""".format(__version__, get_local_versions().pronom_version))

    reader = csv.reader(sys.stdin)

    for row in reader:
        sys.stdout.write("""
    <file>
        <filename>{0}</filename>
        <status>{1}</status>
        <matchtype>{2}</matchtype>
        <time>{3}</time>
        <puid>{4}</puid>
        <mimetype>{5}</mimetype>
        <formatname>{6}</formatname>
        <signaturename>{7}</signaturename>
        <filesize>{8}</filesize>
    </file>""".format(row[6], row[0], row[8], row[1], row[2], row[7], row[3], row[4], row[5]))

    sys.stdout.write("\n</fido_output>\n")


if __name__ == '__main__':
    main()
