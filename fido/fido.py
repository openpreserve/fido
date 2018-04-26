#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Format Identification for Digital Objects (FIDO).

FIDO is a command-line tool to identify the file formats of digital objects.
It is designed for simple integration into automated work-flows.
"""

from __future__ import absolute_import

from argparse import ArgumentParser, RawTextHelpFormatter
from contextlib import closing
import os
import re
import sys
import tarfile
import tempfile
import time
from xml.etree import cElementTree as ET
import zipfile

from six.moves import range

from . import __version__, CONFIG_DIR
from .package import OlePackage, ZipPackage
from .pronomutils import get_local_pronom_versions
from .utils import escape


defaults = {
    'bufsize': 128 * 1024,  # (bytes)
    'regexcachesize': 2084,  # (bytes)
    'printmatch': "OK,%(info.time)s,%(info.puid)s,\"%(info.formatname)s\","
                  "\"%(info.signaturename)s\",%(info.filesize)s,"
                  "\"%(info.filename)s\",\"%(info.mimetype)s\","
                  "\"%(info.matchtype)s\"\n",
    'printnomatch': "KO,%(info.time)s,,,,%(info.filesize)s,"
                    "\"%(info.filename)s\",,\"%(info.matchtype)s\"\n",
    'format_files': [
        'formats-v93.xml',
        'format_extensions.xml'
    ],
    'containersignature_file': 'container-signature-20180417.xml',
    'container_bufsize': 512 * 1024,  # (bytes)
    'description': """Format Identification for Digital Objects (fido).
FIDO is a command-line tool to identify the file formats of digital objects.
It is designed for simple integration into automated work-flows.""",
    'epilog': """
Open Planets Foundation (http://www.openplanetsfoundation.org)
See License.txt for license information.
Download from: https://github.com/openplanets/fido/releases
Usage guide: http://wiki.opf-labs.org/display/KB/FIDO+usage+guide
Author: Adam Farquhar (BL), 2010
Maintainer: Maurice de Rooij (OPF/NANETH), 2011, 2012, 2013
FIDO uses the UK National Archives (TNA) PRONOM File Format
and Container descriptions.
PRONOM is available from http://www.nationalarchives.gov.uk/pronom/""",
}


class Fido(object):

    def __init__(self, defaults_, quiet=False, bufsize=None,
                 container_bufsize=None, printnomatch=None, printmatch=None,
                 zip_=False, nocontainer=False, handle_matches=None,
                 conf_dir=CONFIG_DIR, format_files=None):
        self.quiet = quiet
        self.bufsize = defaults_['bufsize'] if bufsize is None else bufsize
        self.container_bufsize = container_bufsize or defaults_[
            'container_bufsize']
        self.printmatch = printmatch or defaults_['printmatch']
        self.printnomatch = printnomatch or defaults_['printnomatch']
        self.handle_matches = handle_matches or self.print_matches
        self.zip = zip_
        self.nocontainer = nocontainer
        self.conf_dir = conf_dir
        self.format_files = format_files or defaults_['format_files']
        self.containersignature_file = defaults_['containersignature_file']
        self.formats = []
        self.puid_format_map = {}
        self.puid_has_priority_over_map = {}
        # load signatures
        for xml_file in self.format_files:
            self.load_fido_xml(
                os.path.join(os.path.abspath(self.conf_dir), xml_file))
        self.current_file = ''
        self.current_filesize = 0
        self.current_format = None
        self.current_sig = None
        self.current_pat = None
        self.current_count = 0  # Count of calls to match_formats
        re._MAXCACHE = defaults_['regexcachesize']
        self.externalsig = ET.XML(
            '<signature><name>External</name></signature>')

    def match_container(self, signature_type, klass, file_, signature_file):
        puids = klass(
            file_,
            extract_signatures(
                signature_file, signature_type=signature_type)).detect_formats()
        results = []
        for puid in puids:
            format_ = self.puid_format_map[puid]
            signature = format_.findtext("name")
            results.append((format_, signature))
        return results

    def load_fido_xml(self, file_):
        """Load the fido format information from @param file_.
        As a side-effect, set self.formats.
        @return list of ElementTree.Element, one for each format.
        """
        tree = ET.parse(file_)
        # print "Loaded format specs in {0:>6.2f}ms".format((t1 - t0) * 1000)
        # TODO: Handle empty regexes properly; perhaps remove from the format
        # list
        for element in tree.getroot().findall('./format'):
            puid = get_puid(element)
            # Handle over-writes in multiple file loads
            existing = self.puid_format_map.get(puid, False)
            if existing:
                # Already have one, so replace old with new!
                self.formats[self.formats.index(existing)] = element
            else:
                self.formats.append(element)
            self.puid_format_map[puid] = element
            # Build some structures to speed things up
            self.puid_has_priority_over_map[puid] = frozenset(
                [puid_element.text for puid_element in
                 element.findall('has_priority_over')])
        return self.formats

    # To delete a format:
    # (1) remove from self.formats,
    # (2) remove from puid_format_map,
    # (3) remove from self.puid_has_priority_over_map

    def has_priority_over(self, format_, possibly_inferior):
        return (get_puid(possibly_inferior) in
                self.puid_has_priority_over_map[get_puid(format_)])

    def print_matches(self, fullname, matches, delta_t, matchtype=''):
        """The default match handler.

        Prints out information for each match in the list.
        @param fullname is name of the file being matched
        @param matches is a list of (format, signature)
        @param delta_t is the time taken for the match.
        @param matchtype is the type of match (signature, containersignature,
            extension, fail)
        """
        count = self.current_count
        group_size = len(matches)
        filename = fullname
        time_ = int(delta_t * 1000)
        filesize = self.current_filesize
        if not matches:
            sys.stdout.write(self.printnomatch % {
                "info.time": time_,
                "info.filesize": filesize,
                "info.filename": filename,
                "info.count": count,
                "info.matchtype": "fail"
            })
            return
        for index, (f, sig_name) in enumerate(matches):
            group_index = index + 1
            puid = get_puid(f)
            formatname = f.find('name').text
            signaturename = sig_name
            mime = f.find('mime')
            mimetype = mime.text if mime is not None else None
            version = f.find('version')
            version = version.text if version is not None else None
            alias = f.find('alias')
            alias = alias.text if alias is not None else None
            apple_uti = f.find('apple_uid')
            apple_uti = apple_uti.text if apple_uti is not None else None
            sys.stdout.write(self.printmatch % {
                "info.time": time_,
                "info.puid": puid,
                "info.formatname": formatname,
                "info.signaturename": signaturename,
                "info.filesize": filesize,
                "info.filename": filename,
                "info.mimetype": mimetype,
                "info.matchtype": matchtype,
                "info.version": version,
                "info.alias": alias,
                "info.apple_uti": apple_uti,
                "info.group_size": group_size,
                "info.group_index": group_index,
                "info.count": count
            })

    def print_summary(self, secs):
        """Print summary information on the number of matches and time taken."""
        count = self.current_count
        if not self.quiet:
            rate = (int(round(count / secs)) if secs != 0 else 9999)
            sys.stderr.write(
                'FIDO: Processed %6d files in %6.2f msec, %2d files/sec\n' %
                (count, secs * 1000, rate))

    def identify_file(self, filename):
        """Identify the type of @param filename.
        Call self.handle_matches instead of returning a value.
        """
        self.current_file = filename
        matchtype = "signature"
        try:
            t0 = time.clock()
            f = open(filename, 'rb')
            size = os.stat(filename)[6]
            self.current_filesize = size
            if self.current_filesize == 0:
                sys.stderr.write(
                    "FIDO: Zero byte file (empty): Path is: " + filename + "\n")
            bofbuffer, eofbuffer, _ = self.get_buffers(f, size, seekable=True)
            matches = self.match_formats(bofbuffer, eofbuffer)
            container_type = get_container_type(matches)
            if not self.nocontainer and container_type in ("zip", "ole"):
                container_file = ET.parse(
                    os.path.join(os.path.abspath(self.conf_dir),
                                 self.containersignature_file))
                if container_type == "zip":
                    container_matches = self.match_container(
                        "ZIP", ZipPackage, filename, container_file)
                else:
                    container_matches = self.match_container(
                        "OLE2", OlePackage, filename, container_file)
                if container_matches:
                    self.handle_matches(
                        filename, container_matches, time.clock() - t0,
                        "container")
                    return
            # from here is also repeated in walk_zip
            # we should make this uniform in a next version!
            #
            # filesize is made conditional because files with 0 bytes
            # are falsely characterised being 'rtf' (due to wacky sig)
            # in these cases we try to match the extension instead
            if matches and self.current_filesize > 0:
                self.handle_matches(filename, matches, time.clock() - t0,
                                    matchtype)
            elif not matches or self.current_filesize == 0:
                matches = self.match_extensions(filename)
                self.handle_matches(filename, matches, time.clock() - t0,
                                    "extension")
            # only recurse into certain containers, like ZIP or TAR
            container = get_container_type(matches)
            # till here matey!
            if self.zip and can_recurse_into_container(container):
                self.identify_contents(filename, type_=container)
        except IOError:
            sys.stderr.write(
                "FIDO: Error in identify_file: Path is {0}\n".format(filename))

    def identify_contents(self, filename, fileobj=None, type_=False):
        """Identify each item in a container (such as a zip or tar file).

        Call self.handle_matches on each item.
        @param fileobj could be a file, or a stream.
        """
        if not type_:
            return
        elif type_ == 'zip':
            self.walk_zip(filename, fileobj)
        elif type_ == 'tar':
            self.walk_tar(filename, fileobj)
        else:  # TODO: ouch!
            raise RuntimeError("Unknown container type: " + repr(type_))

    def identify_multi_object_stream(self, stream):
        """Does not work!

        Stream may contain one or more objects each with an HTTP style header
        that must include content-length. The headers consist of keyword:value
        pairs terminated by a newline. There must be a newline following the
        headers.
        """
        offset = 0
        while True:
            t0 = time.clock()
            content_length = -1
            for line in stream:
                offset += len(line)
                if line == '\n':
                    if content_length < 0:
                        raise EnvironmentError("No content-length provided.")
                    else:
                        break
                pair = line.lower().split(':', 2)
                if pair[0] == 'content-length':
                    content_length = int(pair[1])
            if content_length == -1:
                return
            # Consume exactly content-length bytes
            self.current_file = 'STDIN!(at ' + str(offset) + ' bytes)'
            self.current_filesize = content_length
            bofbuffer, eofbuffer, _ = self.get_buffers(stream, content_length)
            matches = self.match_formats(bofbuffer, eofbuffer)
            # MdR: this needs attention
            if matches:
                self.handle_matches(
                    self.current_file, matches, time.clock() - t0, "signature")
            elif not matches or self.current_filesize == 0:
                matches = self.match_extensions(self.current_file)
                self.handle_matches(
                    self.current_file, matches, time.clock() - t0, "extension")

    def identify_stream(self, stream, filename):
        """Identify the type of @param stream.

        Call self.handle_matches instead of returning a value.
        Does not close stream.
        """
        t0 = time.clock()
        bofbuffer, eofbuffer, bytes_read = self.get_buffers(stream, length=None)
        self.current_filesize = bytes_read
        self.current_file = 'STDIN'
        matches = self.match_formats(bofbuffer, eofbuffer)
        # MdR: this needs attention
        if matches:
            self.handle_matches(
                self.current_file, matches, time.clock() - t0, "signature")
        elif not matches or self.current_filesize == 0:
            # we can only determine the filename from the STDIN stream
            # on Linux, on Windows there is not a (simple) way to do that
            if os.name != "nt":
                try:
                    self.current_file = os.readlink("/proc/self/fd/0")
                except OSError:
                    if filename is not None:
                        self.current_file = filename
                    else:
                        self.current_file = 'STDIN'
            else:
                if filename is not None:
                    self.current_file = filename
            matches = self.match_extensions(self.current_file)
            # we have to reset self.current_file if not on Windows
            if os.name != "nt":
                self.current_file = 'STDIN'
            self.handle_matches(
                self.current_file, matches, time.clock() - t0, "extension")

    def get_buffers(self, stream, length=None, seekable=False):
        """Return buffers from the beginning and end of stream and the number of
        bytes read if there may be more bytes in the stream.

        If length is None, return the length as found.
        If seekable is False, the steam does not support a seek operation.
        """
        if length is None:
            bytes_to_read = self.bufsize
        else:
            bytes_to_read = min(length, self.bufsize)
        bofbuffer = blocking_read(stream, bytes_to_read)
        bytes_read = len(bofbuffer)
        if length is None:
            # A stream with unknown length; have to keep two buffers around
            prevbuffer = bofbuffer
            while True:
                buffer_ = blocking_read(stream, self.bufsize)
                bytes_read += len(buffer_)
                if len(buffer_) == self.bufsize:
                    prevbuffer = buffer_
                else:
                    if not buffer_:
                        eofbuffer = prevbuffer
                    else:
                        eofbuffer = prevbuffer[
                            -(self.bufsize - len(buffer_)):] + buffer_
                    break
            return bofbuffer, eofbuffer, bytes_read
        else:
            bytes_unread = length - len(bofbuffer)
            if bytes_unread == 0:
                eofbuffer = bofbuffer
            elif bytes_unread < self.bufsize:
                # The buffs overlap
                eofbuffer = bofbuffer[
                    bytes_unread:] + blocking_read(stream, bytes_unread)
            elif bytes_unread == self.bufsize:
                eofbuffer = blocking_read(stream, self.bufsize)
            elif seekable:  # easy case when we can just seek!
                stream.seek(length - self.bufsize)
                eofbuffer = blocking_read(stream, self.bufsize)
            else:
                # We have more to read and know how much.
                # n*bufsize + r = length
                (n, r) = divmod(bytes_unread, self.bufsize)
                # skip n-1*bufsize bytes
                for _ in range(1, n):
                    blocking_read(stream, self.bufsize)
                # skip r bytes
                blocking_read(stream, r)
                # and read the remaining bufsize bytes into the eofbuffer
                eofbuffer = blocking_read(stream, self.bufsize)
            return bofbuffer, eofbuffer, bytes_to_read

    def walk_zip(self, filename, fileobj=None):
        """Identify the type of each item in the zip
        @param fileobj.  If fileobj is not provided, open.
        @param filename.
        Call self.handle_matches instead of returning a value.
        """
        try:
            file_ = fileobj if fileobj else filename
            with zipfile.ZipFile(file_, 'r') as zipstream:
                for item in zipstream.infolist():
                    if item.file_size == 0:
                        continue  # TODO: Find a better test for isdir
                    t0 = time.clock()
                    with zipstream.open(item) as f:
                        item_name = filename + '!' + item.filename
                        self.current_file = item_name
                        self.current_filesize = item.file_size
                        if self.current_filesize == 0:
                            sys.stderr.write(
                                "FIDO: Zero byte file (empty): Path is: " +
                                item_name + "\n")
                        bofbuffer, eofbuffer, _ = self.get_buffers(
                            f, item.file_size)
                    matches = self.match_formats(bofbuffer, eofbuffer)
                    if matches and self.current_filesize > 0:
                        self.handle_matches(
                            item_name, matches, time.clock() - t0, "signature")
                    elif not matches or self.current_filesize == 0:
                        matches = self.match_extensions(item_name)
                        self.handle_matches(
                            item_name, matches, time.clock() - t0, "extension")
                    if get_container_type(matches):
                        target = tempfile.SpooledTemporaryFile(prefix='Fido')
                        with zipstream.open(item) as source:
                            self.copy_stream(source, target)
                            # target.seek(0)
                            self.identify_contents(
                                item_name, target, get_container_type(matches))
        except IOError:
            sys.stderr.write("FIDO: ZipError {0}\n".format(filename))
        except zipfile.BadZipfile:
            sys.stderr.write("FIDO: ZipError {0}\n".format(filename))

    def walk_tar(self, filename, fileobj):
        """Identify the type of each item in the tar.
        @param fileobj.  If fileobj is not provided, open.
        @param filename.
        Call self.handle_matches instead of returning a value.
        """
        try:
            with tarfile.TarFile(
                    filename, fileobj=fileobj, mode='r') as tarstream:
                for item in tarstream.getmembers():
                    if not item.isfile():
                        continue
                    t0 = time.clock()
                    with closing(tarstream.extractfile(item)) as f:
                        tar_item_name = filename + '!' + item.name
                        self.current_file = tar_item_name
                        self.current_filesize = item.size
                        bofbuffer, eofbuffer, _ = self.get_buffers(f, item.size)
                        matches = self.match_formats(bofbuffer, eofbuffer)
                        self.handle_matches(
                            tar_item_name, matches, time.clock() - t0)
                        if get_container_type(matches):
                            f.seek(0)
                            self.identify_contents(
                                tar_item_name, f, get_container_type(matches))
        except tarfile.TarError:
            sys.stderr.write("FIDO: Error: TarError {0}\n".format(filename))

    def as_good_as_any(self, f1, match_list):
        """Return True if the proposed format is as good as any in the
        match_list. For example, if there is no format in the match_list that
        has priority over the proposed one
        """
        if match_list != []:
            f1_puid = get_puid(f1)
            for f2, _ in match_list:
                if f1 == f2:
                    continue
                elif f1_puid in self.puid_has_priority_over_map[
                        get_puid(f2)]:
                    return False
        return True

    def buffered_read(self, file_pos, overlap):
        """Buffered read of data chunks."""
        buf = ""
        if not overlap:
            bufsize = self.container_bufsize
        else:
            bufsize = self.container_bufsize + self.overlap_range
        file_end = self.current_filesize
        with open(self.current_file, 'rb') as file_handle:
            file_handle.seek(file_pos)
            if file_end - file_pos < bufsize:
                file_read = file_end - file_pos
            else:
                file_read = self.bufsize
            buf = file_handle.read(file_read)
        return buf

    def match_formats(self, bofbuffer, eofbuffer):
        """Apply the patterns for formats to the supplied buffers.

        @return a match list of (format, signature) tuples.
        The list has inferior matches removed.
        """
        self.current_count += 1
        # t0 = time.clock()
        result = []
        for format_ in self.formats:
            try:
                self.current_format = format_
                if self.as_good_as_any(format_, result):
                    for sig in get_signatures(format_):
                        self.current_sig = sig
                        success = True
                        for pat in get_patterns(sig):
                            self.current_pat = pat
                            pos = get_pos(pat)
                            regex = get_regex(pat)
                            # print 'trying ', regex
                            if pos == 'BOF':
                                if not re.match(regex, bofbuffer):
                                    success = False
                                    break
                            elif pos == 'EOF':
                                if not re.search(regex, eofbuffer):
                                    success = False
                                    break
                            elif pos == 'VAR':
                                if not re.search(regex, bofbuffer):
                                    success = False
                                    break
                            elif pos == 'IFB':
                                if not re.search(regex, bofbuffer):
                                    success = False
                                    break
                        if success:
                            result.append((format_, sig.findtext("name")))
            except Exception as e:
                sys.stderr.write(str(e) + "\n")
                continue
        result = [match for match in result
                  if self.as_good_as_any(match[0], result)]
        return result

    def match_extensions(self, filename):
        """Return the list of (format, self.externalsig) for every format whose
        extension matches the filename.
        """
        myext = os.path.splitext(filename)[1].lower().lstrip(".")
        result = []
        if not myext:
            return result
        for element in self.formats:
            for format_ in element.findall('extension'):
                if myext == format_.text:
                    result.append((element, self.externalsig.findtext("name")))
                    break
        result = [match for match in result
                  if self.as_good_as_any(match[0], result)]
        return result

    def copy_stream(self, source, target):
        while True:
            buf = source.read(self.bufsize)
            if not buf:
                break
            target.write(buf)


def convert_container_sequence(sig):
    """Parse the PRONOM container sequences and convert to regular
    expressions.
    """
    # The sequence is regex matching bytes from a file so the sequence must also be bytes
    seq = b'(?s)'
    inq = False
    byt = False
    rng = False
    ror = False
    for i in range(len(sig)):
        if not inq and not rng:
            if sig[i] == "'":
                inq = True
                continue
            if sig[i] == " ":
                continue
            if sig[i] == "[":
                seq += b"("
                rng = True
                continue
            if not byt:
                seq += b"\\x" + sig[i].lower().encode('utf8')
                byt = True
                continue
            if byt:
                seq += sig[i].lower().encode('utf8')
                byt = False
                continue
        if inq:
            if sig[i] == "'" and not rng:
                inq = False
                continue
            seq += escape(sig[i]).encode('utf8')
            continue
        if rng:
            if sig[i] == "]":
                seq += b")"
                rng = False
                continue
            if sig[i] != "-" and sig[i] != "'" and ror:
                seq += escape(sig[i]).encode('utf8')
                continue
            if (sig[i] != "-" and
                    sig[i] != "'" and
                    sig[i] != " " and
                    sig[i] != ":" and
                    not ror and
                    not byt):
                seq += b"\\x" + sig[i].lower().encode('utf8')
                byt = True
                continue
            if (sig[i] != "-" and
                    sig[i] != "'" and
                    sig[i] != " " and
                    not ror and
                    byt):
                seq += sig[i].lower().encode('utf8')
                byt = False
                continue
            if sig[i] == "-" or sig[i] == " ":
                seq += b"|"
                continue
            if sig[i] == "'" and not ror:
                ror = True
                continue
            if sig[i] == "'" and ror:
                ror = False
                continue
    return seq


def list_files(roots, recurse=False):
    """Return the files one at a time. Roots could be a fileobj or a list.
    """
    for root in roots:
        root = (root if root[-1] != '\n' else root[:-1])
        root = os.path.normpath(root)
        if os.path.isfile(root):
            yield root
        else:
            for path, _, files in os.walk(root):
                for f in files:
                    yield os.path.join(path, f)
                if not recurse:
                    break


def extract_signatures(doc, signature_type="ZIP"):
    """Given an XML container signature file, returns a dictionary of
    signatures.

    The format of the dictionary is:

    {
        path_to_file_inside_zip: {puid: [signatures]}
    }
    """
    root = doc.getroot()
    format_mappings = root.find("FileFormatMappings")

    def get_puid_local(element_id):
        return format_mappings.find(
            'FileFormatMapping[@signatureId="{}"]'.format(
                element_id)).attrib["Puid"]

    def format_signature_attributes(element):
        return {
            "path": element.findtext("Files/File/Path"),
            "id": element.attrib["Id"],
            "signature": convert_container_sequence(
                element.findtext(
                    "Files/File/BinarySignatures/"
                    "InternalSignatureCollection/InternalSignature/"
                    "ByteSequence/SubSequence/Sequence"))
        }

    elements = root.findall(
        "ContainerSignatures/"
        "ContainerSignature[@ContainerType=\"{}\"]".format(signature_type))
    signatures = {}
    for el in elements:
        if el.find("Files/File/BinarySignatures") is None:
            continue

        puid = get_puid_local(el.attrib["Id"])
        signature = format_signature_attributes(el)
        path = signature["path"]
        if path not in signatures:
            signatures[path] = {}
        if puid not in signatures[path]:
            signatures[path][puid] = []
        signatures[path][puid].append(format_signature_attributes(el))
    return signatures


def get_signatures(format_):
    return format_.findall('signature')


def get_puid(format_):
    return format_.find('puid').text


def get_patterns(signature):
    return signature.findall('pattern')


def get_pos(pat):
    return pat.find('position').text


def get_regex(pat):
    # The regex is matching bytes from a file so regex must also be bytes
    return pat.find('regex').text.encode('utf8')


def get_extension(format_):
    return format_.find('extension').text


def get_container_type(matches):
    """Determine if one of the @param matches is the format of a container
    that we can look inside of (e.g., zip, tar).
    @return False, zip, or tar.
    """
    for format_, _ in matches:
        container = format_.find('container')
        if container is not None:
            return container.text

        # aside from checking <container> elements,
        # check for fmt/111, which is OLE
        puid = format_.find('puid')
        if puid is not None and puid.text == 'fmt/111':
            return 'ole'
    return False


def can_recurse_into_container(container_type):
    """Determine if the passed container type can:
    a) be extracted, and
    b) contain individual files which can be identified separately.

    This function is useful for filtering out containers such as OLE,
    which are usually most interesting as compound objects rather than
    for their contents.
    """
    return container_type in ('zip', 'tar')


def blocking_read(file_, bytes_to_read):
    bytes_read = 0
    buffer_ = b''
    while bytes_read < bytes_to_read:
        readbuffer = file_.read(bytes_to_read - bytes_read)
        buffer_ += readbuffer
        bytes_read = len(buffer_)
        # break out if EOF is reached.
        if readbuffer == '':
            break
    return buffer_


def main(args=None):
    if not args:
        args = sys.argv[1:]

    parser = ArgumentParser(
        description=defaults['description'], epilog=defaults['epilog'],
        fromfile_prefix_chars='@', formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        '-v', default=False, action='store_true',
        help='show version information')
    parser.add_argument(
        '-q', default=False, action='store_true', help='run (more) quietly')
    parser.add_argument(
        '-recurse', default=False, action='store_true',
        help='recurse into subdirectories')
    parser.add_argument(
        '-zip', default=False, action='store_true',
        help='recurse into zip and tar files')
    parser.add_argument(
        '-nocontainer', default=False, action='store_true',
        help='disable deep scan of container documents, increases speed but may'
        ' reduce accuracy with big files')
    parser.add_argument(
        '-pronom_only', default=False, action='store_true',
        help='disables loading of format extensions file, only PRONOM'
        ' signatures are loaded, may reduce accuracy of results')

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-input', default=False,
        help='file containing a list of files to check, one per line. - means'
        ' stdin')
    group.add_argument(
        'files', nargs='*', default=[], metavar='FILE',
        help='files to check. If the file is -, then read content from stdin.'
        ' In this case, python must be invoked with -u or it may convert the'
        ' line terminators.')

    parser.add_argument(
        '-filename', default=None,
        help='filename if file contents passed through STDIN')
    parser.add_argument(
        '-useformats', metavar='INCLUDEPUIDS', default=None,
        help='comma separated string of formats to use in identification')
    parser.add_argument(
        '-nouseformats', metavar='EXCLUDEPUIDS', default=None,
        help='comma separated string of formats not to use in identification')
    parser.add_argument(
        '-matchprintf', metavar='FORMATSTRING', default=None,
        help='format string (Python style) to use on match. See nomatchprintf,'
        ' README.txt.')
    parser.add_argument(
        '-nomatchprintf', metavar='FORMATSTRING', default=None,
        help='format string (Python style) to use if no match. See README.txt')
    parser.add_argument(
        '-bufsize', type=int, default=None,
        help='size (in bytes) of the buffer to match against (default={}'
        ' bytes)'.format(str(defaults['bufsize'])))
    parser.add_argument(
        '-container_bufsize', type=int, default=None,
        help='size (in bytes) of the buffer to match against (default={}'
        ' bytes)'.format(str(defaults['container_bufsize'])))
    parser.add_argument(
        '-loadformats', default=None, metavar='XML1,...,XMLn',
        help='comma separated string of XML format files to add.')
    parser.add_argument(
        '-confdir', default=CONFIG_DIR,
        help='configuration directory to load_fido_xml, for example, the format'
        ' specifications from.')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args(args)

    t0 = time.clock()

    versions = get_local_pronom_versions(args.confdir)

    defaults['xml_pronomSignature'] = versions.pronom_signature
    defaults['containersignature_file'] = versions.pronom_container_signature
    defaults['xml_fidoExtensionSignature'] = versions.fido_extension_signature
    defaults['format_files'] = [defaults['xml_pronomSignature']]

    if args.pronom_only:
        versionHeader = "FIDO v{0} ({1}, {2})\n".format(
            __version__,
            defaults['xml_pronomSignature'],
            defaults['containersignature_file'])
    else:
        versionHeader = "FIDO v{0} ({1}, {2}, {3})\n".format(
            __version__,
            defaults['xml_pronomSignature'],
            defaults['containersignature_file'],
            defaults['xml_fidoExtensionSignature'])
        defaults['format_files'].append(defaults['xml_fidoExtensionSignature'])

    if args.v:
        sys.stdout.write(versionHeader)
        sys.exit(0)

    if args.matchprintf:
        args.matchprintf = args.matchprintf.decode('string_escape')
    if args.nomatchprintf:
        args.nomatchprintf = args.nomatchprintf.decode('string_escape')

    fido = Fido(
        defaults,
        quiet=args.q,
        bufsize=args.bufsize,
        container_bufsize=args.container_bufsize,
        printmatch=args.matchprintf,
        printnomatch=args.nomatchprintf,
        zip_=args.zip,
        nocontainer=args.nocontainer,
        conf_dir=args.confdir)

    # TODO: Allow conf options to be dis-included
    if args.loadformats:
        for file_ in args.loadformats.split(','):
            fido.load_fido_xml(file_)

    # TODO: remove from maps
    if args.useformats:
        args.useformats = args.useformats.split(',')
        fido.formats = [f for f in fido.formats
                        if f.find('puid').text in args.useformats]
    elif args.nouseformats:
        args.nouseformats = args.nouseformats.split(',')
        fido.formats = [f for f in fido.formats
                        if f.find('puid').text not in args.nouseformats]

    # Set up to use stdin, or open input files:
    if args.input == '-':
        args.files = sys.stdin
    elif args.input:
        args.files = open(args.input, 'r')

    # RUN
    try:
        if not args.q:
            sys.stderr.write(versionHeader)
            sys.stderr.flush()
        if (not args.input) and len(args.files) == 1 and args.files[0] == '-':
            if fido.zip:
                raise RuntimeError(
                    "Multiple content read from stdin not yet supported.")
                # sys.exit(1)
                # fido.identify_multi_object_stream(sys.stdin)
            else:
                fido.identify_stream(sys.stdin, args.filename)
        else:
            for file_ in list_files(args.files, args.recurse):
                fido.identify_file(file_)
    except KeyboardInterrupt:
        msg = "FIDO: Interrupt while identifying file {0}"
        sys.stderr.write(msg.format(fido.current_file))
        sys.exit(1)

    if not args.q:
        sys.stdout.flush()
        fido.print_summary(time.clock() - t0)
        sys.stderr.flush()


if __name__ == '__main__':
    main()
