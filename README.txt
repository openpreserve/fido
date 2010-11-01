usage: python -m fido.run [-h] [-v] [-q] [-bufsize BUFSIZE] [-recurse]
              [-zip] [-extension] [-matchprintf FORMATSTRING]
              [-nomatchprintf FORMATSTRING] [-formats PUIDS]
              [-excludeformats PUIDS] [-show SHOW] [-input INPUT]
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
  -extension            use file extensions if the patterns fail. May return
                        many matches.
  -matchprintf FORMATSTRING
                        format string (Python style) to use on match.
                        {0}=path, {1}=delta-t, {2}=fido, {3}=format, {4}=sig,
                        {5}=count.
  -nomatchprintf FORMATSTRING
                        format string (Python style) to use if no match.
                        {0}=path, {1}=delta-t, {2}=fido.
  -formats PUIDS        comma separated string of formats to use in
                        identification
  -excludeformats PUIDS
                        comma separated string of formats not to use in
                        identification
  -show SHOW            show "format" or "defaults"
  -input INPUT          file containing a list of files to check, one per
                        line. - means stdin

Open Planets Foundation (www.openplanetsfoundation.org) See License.txt for
license information. Download from: http://github.com/openplanets/fido Author:
Adam Farquhar, 2010 FIDO uses the UK National Archives (TNA) PRONOM File
Format descriptions. PRONOM is available from www.tna.gov.uk/pronom.


Installation
------------

Any platform
1. Ensure that you have Python 2.7 installed (http://www.python.org/download/releases/2.7)
2. Download the latest zip release from http://github.com/openplanets/fido/downloads
   (or use the big Downloads button on http://github.com/openplanets/fido)
3. Unzip into some directory
4. Open a command shell, cd to the directory that you placed the zip contents into
5. python setup.py install
6. You should now be able to see the help text: 
   python -m fido.run -h

Windows
1. Ensure that you have Python 2.7 installed (http://www.python.org/download/releases/2.7)
2. Download the latest msi release from http://github.com/openplanets/fido/downloads
   (or use the big Downloads button on http://github.com/openplanets/fido)
3. Double click
4. Open a comnand shell.  You should now be able to run fido:
   python -m fido.run -h

Dependencies
------------

Fido 0.6.x requires Python 2.7.  It uses the argparse module, as well as the new format string syntax.

Download and install Python 2.7 from http://www.python.org/download/releases/2.7/ 

This is very simple for Windows users.  For Linux users, it will require building Python as well.
The instructions in the download are surprisingly straightforward.

Examples
--------

Identify all files in the current directory and below, sending output
into file-info.csv
   python -m fido.run -r . > file-info.csv

Do the same as above, but also look inside of zip or tar files:
   python -m fido.run -r -z . > file-info.csv

Do the same as above, but also use file extensions, if a file cannot
be identified through patterns
   python -m fido.run -r -z -ext . > file-info.csv

Take input from a list of files:
   ls > files.txt
   python -m fido.run -f files.txt

Take input from a pipe:
   find . -type f | python -m fido.run -f -
     
Only show files that could not be identified.
	python -m fido.run -r -matchprintf "" .

Exclude a specific format from consideration:
   python -m fido.run -r -z -ext -exclude "fmt/134" . > file-info.csv

License information
-------------------

See the file "LICENSE.txt" for information on the history of this
software, terms & conditions for usage, and a DISCLAIMER OF ALL
WARRANTIES.
