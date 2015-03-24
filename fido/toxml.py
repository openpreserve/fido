#!usr/bin/env python
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
# Windows: type output.csv | toxml.py > output.xml
# Linux: cat output.csv | toxml.py > output.xml
#
# for difference in usage, see:
# http://bugs.python.org/issue9390
# http://support.microsoft.com/default.aspx?kbid=321788
#
# Modified by D. Dietrich 2013-11-27 (dd388@cornell.edu)

import sys
import csv
import string
import xml.etree.ElementTree as xml

# If needed, adjust for path to fido.py
# sys.path.append('/path/to/fido')
from fido import version

# define FIDO version
fidoVersion = version

# define PRONOM signature version
signatureVersion = get_signatureVersion_xml = xml.parse('conf/versions.xml').getroot().find('pronomVersion').text
# signatureVersion = '56'


def indent(elem, level=0):
# From http://effbot.org/zone/element-lib.htm#prettyprint
# In order to workaround lack of pretty print
# Optionally, can use lxml, but that would introduce a dependency
	i = "\n" + level*"\t"
	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + "\t"
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
		for elem in elem:
			indent(elem, level+1)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i


def main():
	# Top of XML
	fido_output = xml.Element('fido_output')
	fido_versions = xml.SubElement(fido_output, 'versions')

	fido_version = xml.SubElement(fido_versions, 'fido_version')
	fido_version.text = fidoVersion

	fido_signature_version = xml.SubElement(fido_versions, 'signature_version')
	fido_signature_version.text = signatureVersion

	# Writing out individual elements
	reader = csv.reader(sys.stdin)

	for row in reader:
		fido_file = xml.SubElement(fido_output, 'file')

		fido_filename = xml.SubElement(fido_file, 'filename')
		fido_filename.text = row[6]

		fido_status = xml.SubElement(fido_file, 'status')
		fido_status.text = row[0]

		fido_matchtype = xml.SubElement(fido_file, 'matchtype')
		fido_matchtype.text = row[8]

		fido_time = xml.SubElement(fido_file, 'time')
		fido_time.text = row[1]

		fido_puid = xml.SubElement(fido_file, 'puid')
		fido_puid.text = row[2]

		fido_mimetype = xml.SubElement(fido_file, 'mimetype')
		fido_mimetype.text = row[7]

		fido_formatname = xml.SubElement(fido_file, 'formatname')
		fido_formatname.text = row[3]

		fido_signaturename = xml.SubElement(fido_file, 'signaturename')
		fido_signaturename.text = row[4]

		fido_filesize = xml.SubElement(fido_file, 'filesize')
		fido_filesize.text = row[5]

	indent(fido_output)
	pre_fido_output = xml.ElementTree(fido_output)
	pre_fido_output.write(sys.stdout, encoding='utf-8', xml_declaration=True, method='xml')

if __name__ == "__main__":
	main()
