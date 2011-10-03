#!python
# -*- coding: utf-8 -*-
#
# FIDO csv output to XML
# Author: Maurice de Rooij <maurice.de.rooij@nationaalarchief.nl>, september 2011
#
# Usage in combination with FIDO:
# Windows: python fido.py [ARGS] | python toxml.py > output.xml
# Linux: fido.py [ARGS] | toxml.py > output.xml
#
# Usage afterwards:
# Windows: type output.csv | python toxml.py > output.xml
# Linux: cat output.csv | toxml.py > output.xml
#
# for difference in usage, see:
# http://bugs.python.org/issue9390
# http://support.microsoft.com/default.aspx?kbid=321788
#

import sys
import csv
import string
import datetime

# define FIDO version
fidoVersion = '0.9.6'
# define PRONOM signature version
signatureVersion = '52'
# get date and time
now = datetime.datetime.now()

sys.stdout.write("""<fido_output>
    <datetime>{0}</datetime>
	<versions>
		<fido_version>{1}</fido_version>
		<signature_version>{2}</signature_version>
	</versions>""".format(str(now)[:19],fidoVersion,signatureVersion))

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
	</file>""".format(row[6],row[0],row[8],row[1],row[2],row[7],row[3],row[4],row[5]))

sys.stdout.write("\n</fido_output>\n")
