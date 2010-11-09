usage: python -m fido.run [-h] [-v] [-q] [-recurse] [-zip] [-input INPUT] [-formats PUIDS]
              [-excludeformats PUIDS] [-extension] [-matchprintf FORMATSTRING]
              [-nomatchprintf FORMATSTRING] [-bufsize BUFSIZE] [-show SHOW]
              [FILE [FILE ...]]

Format Identification for Digital Objects (fido). FIDO is a command-line tool
to identify the file formats of digital objects. It is designed for simple
integration into automated work-flows.

positional arguments:
  FILE                  files to check. If the file is -, then read content
                        from stdin. In this case, python must be invoked with
                        -u or it may convert the line terminators.

optional arguments:
  -h, --help            show this help message and exit
  -v                    show version information
  -q                    run (more) quietly
  -recurse              recurse into subdirectories
  -zip                  recurse into zip files
  -input INPUT          file containing a list of files to check, one per
                        line. - means stdin
  -formats PUIDS        comma separated string of formats to use in
                        identification
  -excludeformats PUIDS
                        comma separated string of formats not to use in
                        identification
  -extension            use file extensions if the patterns fail. May return
                        many matches.
  -matchprintf FORMATSTRING
                        format string (Python style) to use on match. See
                        nomatchprintf. You also have access to info.count, the
                        number of matches; format; and sig.
  -nomatchprintf FORMATSTRING
                        format string (Python style) to use if no match. You
                        have access to info with attributes name, size, time.
  -bufsize BUFSIZE      size of the buffer to match against
  -show SHOW            show "format" or "defaults"

Open Planets Foundation (www.openplanetsfoundation.org) See License.txt for
license information. Download from: http://github.com/openplanets/fido Author:
Adam Farquhar, 2010 FIDO uses the UK National Archives (TNA) PRONOM File
Format descriptions. PRONOM is available from www.tna.gov.uk/pronom.

Installation
------------

Any platform
1. Download the latest zip release from http://github.com/openplanets/fido/downloads
   (or use the big Downloads button on http://github.com/openplanets/fido)
2. Unzip into some directory
3. Open a command shell, cd to the directory that you placed the zip contents into
4. python setup.py install
5. You should now be able to see the help text: 
   python -m fido.run -h
   If you are lucky, you may also be able to run with 
   fido.sh -h

Windows
1. Download the latest msi release from http://github.com/openplanets/fido/downloads
   (or use the big Downloads button on http://github.com/openplanets/fido)
2. Double click
3. Open a comnand shell.  You should now be able to run fido:
   python -m fido.run -h

Dependencies
------------

Fido 0.7 and later will run on Python 2.6 or Python 2.7.

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
