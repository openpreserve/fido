fido
====

[![Build Status](https://secure.travis-ci.org/edsu/fido.png)](http://travis-ci.org/edsu/fido)

Format Identification for Digital Objects (fido). FIDO is a command-line tool
to identify the file formats of digital objects. It is designed for simple
integration into automated work-flows.

Open Planets Foundation (http://www.openplanetsfoundation.org)
See License.txt for license information.
Download from: http://github.com/openplanets/fido/downloads
Author: Adam Farquhar, 2010
Maintainer: Maurice de Rooij (OPF/NANETH), 2011, 2012
FIDO uses the UK National Archives (TNA) PRONOM File Format and Container descriptions.
PRONOM is available from http://www.nationalarchives.gov.uk/pronom/

Installation
------------

Any platform
1. Download the latest zip release from http://github.com/openplanets/fido/downloads (or use the big Downloads button on http://github.com/openplanets/fido)
1. Unzip into some directory
1. Open a command shell, cd to the directory that you placed the zip contents into and cd into folder 'fido'
1. You should now be able to see the help text: python fido.py -h
1. Before identifying files with FIDO for the first time, please update signatures first using the `update_signatures.py` script (see below for instructions).

Updating signatures
-------------------

To update FIDO with the latest PRONOM file format definitions, run:

    python update_signatures.py

This is an interactive CLI script which downloads the latest PRONOM signature file and signatures. Please note that it can take a while to download all PUID signatures.

If you are having trouble running the script due to firewall restrictions, see OPF wiki: http://wiki.opf-labs.org/display/PT/Command+Line+Interface+proxy+usage

Please note that this WILL NOT update the container signature file located in the 'conf' folder.  The reason for this that the PRONOM container signature file contains special types of sequences which need to be tested before FIDO can use them. If there is an update available for the PRONOM container signature file it will show up in a next commit.

Dependencies
------------

FIDO 1.0 and later will run on Python 2.7 with no other dependencies.

Format Definitions
------------------

By default, FIDO loads format information from two files conf/formats.xml
and conf/format_extensions.xml. Addition format files can be specified using
the -loadformats command line argument.  They should use the same syntax as 
conf/format_extensions.xml. If more than one format file needs to be specified,
then they should be comma separated as with the -formats argument.

Output
------

Output is controlled with the two parameters matchprintf and nomatchprintf.
Each is a string that may contain formating information.  They have access to
an object called info with the following fields:

printmatch: info.version (file format version X), info.alias (format also called X), info.apple_uti (Apple Uniform Type Identifier), info.group_size and info.group_index (if a file has multiple (tentative) hits), info.count (file N)

printnomatch: info.count (file N)

The defaults for FIDO 1.0 are:
  printmatch: 
    "OK,%(info.time)s,%(info.puid)s,%(info.formatname)s,%(info.signaturename)s,%(info.filesize)s,\"%(info.filename)s\",\"%(info.mimetype)s\",\"%(info.matchtype)s\"\n"

  printnomatch:
    "KO,%(info.time)s,,,,%(info.filesize)s,\"%(info.filename)s\",,\"%(info.matchtype)s\"\n"

It can be useful to provide an empty string for either, for example to ignore all failed matches, or all successful ones (see examples below). 
Note that a newline needs to be added to the end of the string using \n.

Matchttypes
-----------

FIDO returns the following matchtypes:

- fail:      the object could not be identified with signature or file extension
- extension: the object could only be identified by file extension
- signature: the object has been identified with (a) PRONOM signature(s)
- container: the object has been idenfified with (a) PRONOM container signature(s)

(In some cases multiple results are returned.)

Examples running FIDO
---------------------

### Identify all files in the current directory and below, sending output into file-info.csv:

    python fido.py -recurse . > file-info.csv

### Do the same as above, but also look inside of zip or tar files:

    python fido.py -recurse -zip . > file-info.csv

### Take input from a list of files:

Linux:

    ls > files.txt
    python fido.py -input files.txt

Windows:

    dir /b > files.txt
    python fido.py -input files.txt

### Take input from a pipe:

Linux:

    find . -type f | python fido.py -input -

Windows:

    dir /b | python fido.py -input -

### Only show files that could not be identified.

    python fido.py -matchprintf "" .

### Only show files that could be identified.

    python fido.py -nomatchprintf "" .

Deep scan of container objects
------------------------------

By default, when FIDO detects that a file is a container (compound) object,
it will start a deep (complete) scan of the file using the PRONOM container signatures.  When identifying big files, this behaviour can cause FIDO to slow down sigificantly.  You can disable deep scanning by invoking FIDO with the '-nocontainer' argument.  While disabling deep scan speeds up identification, it may reduce accuracy.

At the moment (version 1.0) FIDO is not yet able to perform scanning containers which are passed through STDIN. A workaround would be to save the stream to a temporary file and have FIDO identify this file.

License information
-------------------

See the file "LICENSE.txt" for information on the history of this
software, terms & conditions for usage, and a DISCLAIMER OF ALL
WARRANTIES...
