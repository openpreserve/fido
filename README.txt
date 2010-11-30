usage: python -m fido.run [-h] [-v] [-q] [-recurse] [-zip] [-input INPUT] [-formats PUIDS]
              [-excludeformats PUIDS] [-extension] [-matchprintf FORMATSTRING]
              [-nomatchprintf FORMATSTRING] [-bufsize BUFSIZE] [-show SHOW]
              [-xmlformats XML1,...,XMLn]
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
                        nomatchprintf, README.txt.
  -nomatchprintf FORMATSTRING
                        format string (Python style) to use if no match. See
                        README.txt
  -bufsize BUFSIZE      size of the buffer to match against
  -show SHOW            show "format" or "defaults"
  -xmlformats XML1,...,XMLn
                        comma separated string of XML format specifications to
                        add.

Open Planets Foundation (http://www.openplanetsfoundation.org) See License.txt
for license information. Download from:
http://github.com/openplanets/fido/downloads Author: Adam Farquhar, 2010 FIDO
uses the UK National Archives (TNA) PRONOM File Format descriptions. PRONOM is
available from www.tna.gov.uk/pronom.

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

Fido 0.7 and later will run on Python 2.6 or Python 2.7 with no other dependencies.

Format Definitions
------------------

By default, Fido loads format information from two files conf/formats.xml
and conf/format_extensions.xml. Addition format files can be specified using
the -xmlformats command line argument.  They should use the same syntax as 
conf/format_extensions.xml. If more than one format file needs to be specified,
then they should be comma separated as with the -formats argument.

Output
------

Output is controlled with the two parameters matchprintf and nomatchprintf.
Each is a string that may contain formating information.  They have access to
an object called info.  

When there is no match, info has fields: 
  count 		- This is the nth item matched.
  group_size	- And there are match_count matches in this group.
  filename, filesize, time (in msecs).
When there is a match, info has additional fields:
  group_index	- This is the nth match for this item 
  puid, formatname, signaturename, 
  mimetype (the first one).

Note that the reported time is in milliseconds for an entire group.  If you sum the times and
there is only one match per group, then the total is correct.

The defaults for Fido 0.8.3 are:
  printmatch: 
  "OK,{info.time},{info.puid},{info.formatname},{info.signaturename},{info.filesize},\"{info.filename}\"\n"
  printnomatch:
  "KO,{info.time},,,,{info.filesize},\"{info.filename}\"\n"

It can be useful to provide an empty string for either, for example to ignore all failed matches,
or all successful ones.
     
Note that a newline needs to be added to the end of the string using \n.

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
