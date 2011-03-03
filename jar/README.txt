usage: java -jar fido.jar 
               [-h] [-v] [-q] [-recurse] [-zip] [-input INPUT]
               [-useformats INCLUDEPUIDS] [-nouseformats EXCLUDEPUIDS]
               [-extension] [-matchprintf FORMATSTRING]
               [-nomatchprintf FORMATSTRING] [-bufsize BUFSIZE] [-show SHOW]
               [-loadformats XML1,...,XMLn] [-confdir CONFDIR] [-checkformats]
               [-convert] [-source SOURCE] [-target TARGET]
               [FILE [FILE ...]]

Format Identification for Digital Objects (fido). FIDO is a command-line tool
to identify the file formats of digital objects. It is designed for simple
integration into automated work-flows.

positional arguments:
  FILE                  files to check. The jar version does not yet support
                        reading content from stdin.

optional arguments:
  -h, --help            show this help message and exit
  -v                    show version information
  -q                    run (more) quietly
  -recurse              recurse into subdirectories
  -zip                  recurse into zip and tar files
  -input INPUT          file containing a list of files to check, one per
                        line.
  -useformats INCLUDEPUIDS
                        comma separated string of formats to use in
                        identification
  -nouseformats EXCLUDEPUIDS
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
  -loadformats XML1,...,XMLn
                        comma separated string of XML format files to add.
  -confdir CONFDIR      configuration directory to load_fido_xml, for example,
                        the format specifications from.
  -checkformats         Check the supplied format XML files for quality.
  -convert              Convert pronom xml to fido xml
  -source SOURCE        import from a zip file containing only Pronom xml
                        files
  -target TARGET        export fido xml output file

Open Planets Foundation (http://www.openplanetsfoundation.org) See License.txt
for license information. Download from:
http://github.com/openplanets/fido/downloads Author: Adam Farquhar, 2010 FIDO
uses the UK National Archives (TNA) PRONOM File Format descriptions. PRONOM is
available from www.tna.gov.uk/pronom.

Jarred by Maurice de Rooij (NANETH)

Installation
------------

Any platform
1. Download the latest release from http://github.com/openplanets/fido/downloads
   (or use the big Downloads button on http://github.com/openplanets/fido)
2. Unzip into some directory 
3. Open a command shell, cd to the directory that you placed the zip contents into
4. You should now be able to see the help text: 
   java -jar fido.jar -h

Dependencies
------------

Fido.jar v0.9.5 and later will run on Java 6 Update 23 or later with no other dependencies.

Known limitations and bugs
--------------------------

1. The jar version is not yet able to walk through zip and tar files, though they are correctly identified.
2. The jar version is not yet able to read from STDIN.
3. When the jar version terminates you might experience harmless but ugly messages in some cases (switch: -h).
4. Program termination (CTRL-C) is not yet supported.

Format Definitions
------------------

By default, Fido loads format information from two files conf/formats.xml
and conf/format_extensions.xml. Addition format files can be specified using
the -loadformats command line argument.  They should use the same syntax as 
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
   java -jar fido.jar -recurse . > file-info.csv

Take input from a list of files:
   ls > files.txt (linux/mac)
   dir > files.txt (windows)
   java -jar fido.jar -f files.txt

Only show files that could not be identified.
   java -jar fido.jar -recurse -matchprintf "" .

Exclude a specific format from consideration:
   java -jar fido.jar -recurse -exclude "fmt/134" . > file-info.csv

License information
-------------------

See the file "LICENSE.txt" for information on the history of this
software, terms & conditions for usage, and a DISCLAIMER OF ALL
WARRANTIES.
