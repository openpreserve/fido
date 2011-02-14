usage: fido.py [-h] [-v] [-q] [-recurse] [-zip] [-input INPUT]
               [-useformats INCLUDEPUIDS] [-nouseformats EXCLUDEPUIDS]
               [-extension] [-matchprintf FORMATSTRING]
               [-nomatchprintf FORMATSTRING] [-bufsize BUFSIZE] [-show SHOW]
               [-loadformats XML1,...,XMLn] [-confdir CONFDIR] [-convert]
               [-import IMPORT] [-export EXPORT]
               [FILE [FILE ...]]

Format Identification for Digital Objects (fido). FIDO is a command-line tool
to identify the file useformats of digital objects. It is designed for simple
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
  -zip                  recurse into zip and tar files
  -input INPUT          file containing a list of files to check, one per
                        line. - means stdin
  -useformats INCLUDEPUIDS
                        comma separated string of useformats to use in
                        identification
  -nouseformats EXCLUDEPUIDS
                        comma separated string of useformats not to use in
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
  -convert              Convert pronom xml to fido xml
  -import IMPORT        import from a zip file containing only Pronom xml
                        files
  -export EXPORT        export fido xml output file

Open Planets Foundation (http://www.openplanetsfoundation.org) See License.txt
for license information. Download from:
http://github.com/openplanets/fido/downloads Author: Adam Farquhar, 2010 FIDO
uses the UK National Archives (TNA) PRONOM File Format descriptions. PRONOM is
available from www.tna.gov.uk/pronom.
