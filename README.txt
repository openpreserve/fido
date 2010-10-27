Format Identification for Digital Objects (fido). FIDO is a command-line tool
to identify the file formats of digital objects. It is designed for simple
integration into automated work-flows.

Usage
-----

python -m fido.run [-h] [-v] [-q] [-bufsize BUFSIZE] [-recurse] [-zip] [-diagnose]
              [-matchprintf FORMATSTRING] [-nomatchprintf FORMATSTRING]
              [-formats PUIDS] [-excludeformats PUIDS] [-showformats]
              [-input INPUT]
              [FILE [FILE ...]]

Format Identification for Digital Objects (fido). FIDO is a command-line tool
to identify the file formats of digital objects. It is designed for simple
integration into automated work-flows.

positional arguments:
  FILE                  files to check

optional arguments:
  -h, --help            show this help message and exit
  -v                    show version information
  -q                    run (more) quietly
  -bufsize BUFSIZE      size of the buffer to match against
  -recurse              recurse into subdirectories
  -zip                  recurse into zip files
  -diagnose             show some diagnostic information
  -matchprintf FORMATSTRING
                        format string (Python style) to use on match.
                        {0}=path, {1}=format object, {2}=signature, {3}=match
                        count, {4}=now.
  -nomatchprintf FORMATSTRING
                        format string (Python style) to use if no match.
                        {0}=path, {1}=now.
  -formats PUIDS        comma separated string of formats to use in
                        identification
  -excludeformats PUIDS
                        comma separated string of formats not to use in
                        identification
  -showformats          show current format set
  -input INPUT          file containing a list of files to check, one per
                        line. - means stdin

Open Planets Foundation (www.openplanetsfoundation.org) Author: Adam Farquhar,
2010 FIDO uses the UK National Archives (TNA) PRONOM File Format descriptions.
PRONOM is available from www.tna.gov.uk/pronom.

Dependencies
------------

Fido 0.5.x requires Python 2.7.  It uses the argparse module, as well as the new format string syntax.

Download and install Python 2.7 from http://www.python.org/download/releases/2.7/ 

This is very simple for Windows users.  For Linux users, it will require building Python as well.
The instructions in the download are surprisingly straightforward.

Examples
--------
Identify all files in the current directory and below, sending output into file-info.csv
	python -m fido.run -r . > file-info.csv

Only show files that could not be identified.
	python -m fido.run -r -matchprintf "" .

License information
-------------------

See the file "LICENSE.txt" for information on the history of this
software, terms & conditions for usage, and a DISCLAIMER OF ALL
WARRANTIES.

