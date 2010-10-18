usage: python -m fido.run [-h] [-v] [-q] [-bufsize BUFSIZE] [-recurse] [-zip] [-diagnose]
              [-matchprintf FORMATSTRING] [-nomatchprintf FORMATSTRING]
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
  -input INPUT          file containing a list of files to check, one per line

Open Planets Foundation (www.openplanetsfoundation.org) 
Author: Adam Farquhar,
2010 FIDO uses the UK National Archives (TNA) PRONOM File Format descriptions.
PRONOM is available from www.tna.gov.uk/pronom.