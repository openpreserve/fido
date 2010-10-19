Format Identification for Digital Objects (fido). FIDO is a command-line tool
to identify the file formats of digital objects. It is designed for simple
integration into automated work-flows.

usage: python -m fido.run [-h] [-v] [-q] [-bufsize BUFSIZE] [-recurse] [-zip] [-diagnose]
              [-matchprintf FORMATSTRING] [-nomatchprintf FORMATSTRING]
              [-input INPUT]
              [FILE [FILE ...]]

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

Author: Adam Farquhar
2010 FIDO uses the UK National Archives (TNA) PRONOM File Format descriptions.
PRONOM is available from www.tna.gov.uk/pronom.

===Beg:License
Copyright 2010 The British Library

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
===End:License             