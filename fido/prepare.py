#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Format Identification for Digital Objects."""

from __future__ import print_function

from argparse import ArgumentParser
import hashlib
import sys
from xml.dom import minidom
from xml.etree import ElementTree as ET
import zipfile

from six.moves import cStringIO
from six.moves.urllib.request import urlopen

from .pronomutils import get_local_pronom_versions


# MdR: 'reload(sys)' and 'setdefaultencoding("utf-8")' needed to fix utf-8 encoding errors
# when converting from PRONOM to FIDO format
reload(sys)
sys.setdefaultencoding("utf-8")


class NS:
    """
    Helper class for XML name spaces in ElementTree.

    Use like MYNS=NS("{http://some/uri}") and then MYNS(tag1/tag2).
    """

    def __init__(self, uri):
        """Instantiate class with `uri` argument."""
        self.uri = uri

    def __getattr__(self, tag):
        """Append URI to the class attributes."""
        return self.uri + tag

    def __call__(self, path):
        """Define behavior when the instant is used as a function."""
        return "/".join(getattr(self, tag) for tag in path.split("/"))


XHTML = NS("{http://www.w3.org/1999/xhtml}")  # XHTML namespace
TNA = NS("{http://pronom.nationalarchives.gov.uk}")  # TNA namespace


def get_text_tna(element, tag, default=''):
    """Helper function to return the text for a tag or path using the TNA namespace."""
    part = element.find(TNA(tag))
    if part is None or part.text is None:
        return default
    return part.text.strip()


def prettify(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, 'UTF-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


class FormatInfo:
    """Convert PRONOM formats into FIDO signatures."""

    def __init__(self, pronom_files, format_list=[]):
        """Instantiate class, take a list of PRONOM files and an optional list of formats."""
        self.info = {}
        self.formats = []
        self.pronom_files = pronom_files
        for f in format_list:
            self.add_format(f)  # FIXME: add_format is undefined!

    def save(self, dst=sys.stdout):
        """Write the fido XML format definitions to @param dst."""
        tree = ET.ElementTree(ET.Element('formats', {
            'version': '0.3',
            'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
            'xsi:noNamespaceSchemaLocation': "fido-formats.xsd",
            'xmlns:dc': "http://purl.org/dc/elements/1.1/",
            'xmlns:dcterms': "http://purl.org/dc/terms/"
        }))
        root = tree.getroot()
        for f in self.formats:
            # MdR: this skipped puids without sig, but we want them ALL
            # because puid might be matched on extension
            # if f.find('signature'):
            root.append(f)
        self.indent(root)
        with open(dst, 'wb') as file_:
            # print >>out, ET.tostring(root,encoding='utf-8')
            print(ET.tostring(root), file=file_)

    def indent(self, elem, level=0):
        """Indent output."""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def load_pronom_xml(self, puid_filter=None):
        """
        Load the pronom XML from self.pronom_files and convert it to fido XML.

        As a side-effect, set self.formats to a list of ElementTree.Element.
        If a @param puid is specified, only that one will be loaded.
        """
        formats = []
        # for p in self.pronom_files:
        #    print p
        # print self.pronom_files
        # exit()
        try:
            zip = zipfile.ZipFile(self.pronom_files, 'r')
            for item in zip.infolist():
                # print item.filename
                try:
                    stream = zip.open(item)
                    # Work is done here!
                    # if item.filename != 'github/fido/fido/conf/pronom-xml/puid.fmt.11.xml':
                    format_ = self.parse_pronom_xml(stream, puid_filter)
                    if len(format_):
                        formats.append(format_)
                finally:
                    stream.close()
        finally:
            try:
                zip.close()
            except Exception as e:
                print("An error occured loading '{0}' (exception: {1})".format(self.pronom_files, e), file=sys.stderr)
                sys.exit()
        # Replace the formatID with puids in has_priority_over
        id_map = {}
        for element in formats:
            puid = element.find('puid').text
            # print "working on puid:",puid
            pronom_id = element.find('pronom_id').text
            id_map[pronom_id] = puid
        for element in formats:
            for rel in element.findall('has_priority_over'):
                rel.text = id_map[rel.text]

        self._sort_formats(formats)
        self.formats = formats

    def parse_pronom_xml(self, source, puid_filter=None):
        """
        Parse PRONOM XML and convert into FIDO XML.

        If a @param puid is specified, only that one will be loaded.
        @return ET.ElementTree Element representing it.
        """
        pronom_xml = ET.parse(source)
        pronom_root = pronom_xml.getroot()
        pronom_format = pronom_root.find(TNA('report_format_detail/FileFormat'))
        fido_format = ET.Element('format')
        # Get the base Format information
        for id in pronom_format.findall(TNA('FileFormatIdentifier')):
            type = get_text_tna(id, 'IdentifierType')
            if type == 'PUID':
                puid = get_text_tna(id, 'Identifier')
                ET.SubElement(fido_format, 'puid').text = puid
                if puid_filter and puid != puid_filter:
                    return None
        # A bit clumsy.  I want to have puid first, then mime, then container.
        for id in pronom_format.findall(TNA('FileFormatIdentifier')):
            type = get_text_tna(id, 'IdentifierType')
            if type == 'MIME':
                ET.SubElement(fido_format, 'mime').text = get_text_tna(id, 'Identifier')
            elif type == 'PUID':
                puid = get_text_tna(id, 'Identifier')
                if puid == 'x-fmt/263':
                    ET.SubElement(fido_format, 'container').text = 'zip'
                elif puid == 'x-fmt/265':
                    ET.SubElement(fido_format, 'container').text = 'tar'
        ET.SubElement(fido_format, 'name').text = get_text_tna(pronom_format, 'FormatName')
        ET.SubElement(fido_format, 'version').text = get_text_tna(pronom_format, 'FormatVersion')
        ET.SubElement(fido_format, 'alias').text = get_text_tna(pronom_format, 'FormatAliases')
        ET.SubElement(fido_format, 'pronom_id').text = get_text_tna(pronom_format, 'FormatID')
        # Get the extensions from the ExternalSignature
        for x in pronom_format.findall(TNA('ExternalSignature')):
                ET.SubElement(fido_format, 'extension').text = get_text_tna(x, 'Signature')
        for id in pronom_format.findall(TNA('FileFormatIdentifier')):
            type = get_text_tna(id, 'IdentifierType')
            if type == 'Apple Uniform Type Identifier':
                ET.SubElement(fido_format, 'apple_uid').text = get_text_tna(id, 'Identifier')
        # Handle the relationships
        for x in pronom_format.findall(TNA('RelatedFormat')):
            rel = get_text_tna(x, 'RelationshipType')
            if rel == 'Has priority over':
                ET.SubElement(fido_format, 'has_priority_over').text = get_text_tna(x, 'RelatedFormatID')
        # Get the InternalSignature information
        for pronom_sig in pronom_format.findall(TNA('InternalSignature')):
            fido_sig = ET.SubElement(fido_format, 'signature')
            ET.SubElement(fido_sig, 'name').text = get_text_tna(pronom_sig, 'SignatureName')
            # There are some funny chars in the notes, which caused me trouble and it is a unicode string,
            ET.SubElement(fido_sig, 'note').text = get_text_tna(pronom_sig, 'SignatureNote').encode('UTF-8')
            for pronom_pat in pronom_sig.findall(TNA('ByteSequence')):
                fido_pat = ET.SubElement(fido_sig, 'pattern')
                pos = fido_position(get_text_tna(pronom_pat, 'PositionType'))
                bytes = get_text_tna(pronom_pat, 'ByteSequenceValue')
                offset = get_text_tna(pronom_pat, 'Offset')
                max_offset = get_text_tna(pronom_pat, 'MaxOffset')
                if not max_offset:
                    pass
                # print "working on puid:", puid, ", position: ", pos, "with offset, maxoffset: ", offset, ",", max_offset
                regex = convert_to_regex(bytes, 'Little', pos, offset, max_offset)
                # print "done puid", puid
                if regex == "__INCOMPATIBLE_SIG__":
                    print("Error: incompatible PRONOM signature found for puid {} skipping...".format(puid), file=sys.stderr)
                    # remove the empty 'signature' nodes
                    # now that the signature is not compatible and thus "regex" is empty
                    remove = fido_format.findall('signature')
                    for r in remove:
                        fido_format.remove(r)
                    continue
                ET.SubElement(fido_pat, 'position').text = pos
                ET.SubElement(fido_pat, 'pronom_pattern').text = bytes
                ET.SubElement(fido_pat, 'regex').text = regex
        # Get the format details
        fido_details = ET.SubElement(fido_format, 'details')
        ET.SubElement(fido_details, 'dc:description').text = get_text_tna(pronom_format, 'FormatDescription').encode('utf8')
        ET.SubElement(fido_details, 'dcterms:available').text = get_text_tna(pronom_format, 'ReleaseDate')
        ET.SubElement(fido_details, 'dc:creator').text = get_text_tna(pronom_format, 'Developers/DeveloperCompoundName')
        ET.SubElement(fido_details, 'dcterms:publisher').text = get_text_tna(pronom_format, 'Developers/OrganisationName')
        for x in pronom_format.findall(TNA('RelatedFormat')):
            rel = get_text_tna(x, 'RelationshipType')
            if rel == 'Is supertype of':
                ET.SubElement(fido_details, 'is_supertype_of').text = get_text_tna(x, 'RelatedFormatID')
        for x in pronom_format.findall(TNA('RelatedFormat')):
            rel = get_text_tna(x, 'RelationshipType')
            if rel == 'Is subtype of':
                ET.SubElement(fido_details, 'is_subtype_of').text = get_text_tna(x, 'RelatedFormatID')
        ET.SubElement(fido_details, 'content_type').text = get_text_tna(pronom_format, 'FormatTypes')
        # References
        for x in pronom_format.findall(TNA("Document")):
            r = ET.SubElement(fido_details, 'reference')
            ET.SubElement(r, 'dc:title').text = get_text_tna(x, 'TitleText')
            ET.SubElement(r, 'dc:creator').text = get_text_tna(x, 'Author/AuthorCompoundName')
            ET.SubElement(r, 'dc:publisher').text = get_text_tna(x, 'Publisher/PublisherCompoundName')
            ET.SubElement(r, 'dcterms:available').text = get_text_tna(x, 'PublicationDate')
            for id in x.findall(TNA('DocumentIdentifier')):
                type = get_text_tna(id, 'IdentifierType')
                if type == 'URL':
                    ET.SubElement(r, 'dc:identifier').text = "http://" + get_text_tna(id, 'Identifier')
                else:
                    ET.SubElement(r, 'dc:identifier').text = get_text_tna(id, 'IdentifierType') + ":" + get_text_tna(id, 'Identifier')
            ET.SubElement(r, 'dc:description').text = get_text_tna(x, 'DocumentNote')
            ET.SubElement(r, 'dc:type').text = get_text_tna(x, 'DocumentType')
            ET.SubElement(r, 'dcterms:license').text = get_text_tna(x, 'AvailabilityDescription') + " " + get_text_tna(x, 'AvailabilityNote')
            ET.SubElement(r, 'dc:rights').text = get_text_tna(x, 'DocumentIPR')
        # Examples
        for x in pronom_format.findall(TNA("ReferenceFile")):
            rf = ET.SubElement(fido_details, 'example_file')
            ET.SubElement(rf, 'dc:title').text = get_text_tna(x, 'ReferenceFileName')
            ET.SubElement(rf, 'dc:description').text = get_text_tna(x, 'ReferenceFileDescription')
            checksum = ""
            for id in x.findall(TNA('ReferenceFileIdentifier')):
                type = get_text_tna(id, 'IdentifierType')
                if type == 'URL':
                    url = "http://" + get_text_tna(id, 'Identifier')
                    ET.SubElement(rf, 'dc:identifier').text = url
                    # And calculate the checksum of this resource:
                    m = hashlib.md5()
                    sock = urlopen(url)
                    m.update(sock.read())
                    sock.close()
                    checksum = m.hexdigest()
                else:
                    ET.SubElement(rf, 'dc:identifier').text = get_text_tna(id, 'IdentifierType') + ":" + get_text_tna(id, 'Identifier')
            ET.SubElement(rf, 'dcterms:license').text = ""
            ET.SubElement(rf, 'dc:rights').text = get_text_tna(x, 'ReferenceFileIPR')
            checksumElement = ET.SubElement(rf, 'checksum')
            checksumElement.text = checksum
            checksumElement.attrib['type'] = "md5"
        # Record Metadata
        md = ET.SubElement(fido_details, 'record_metadata')
        ET.SubElement(md, 'status').text = 'unknown'
        ET.SubElement(md, 'dc:creator').text = get_text_tna(pronom_format, 'ProvenanceName')
        ET.SubElement(md, 'dcterms:created').text = get_text_tna(pronom_format, 'ProvenanceSourceDate')
        ET.SubElement(md, 'dcterms:modified').text = get_text_tna(pronom_format, 'LastUpdatedDate')
        ET.SubElement(md, 'dc:description').text = get_text_tna(pronom_format, 'ProvenanceDescription').encode('utf8')
        return fido_format

    # FIXME: I don't think that this quite works yet!
    def _sort_formats(self, formatlist):
        """Sort the format list based on their priority relationships so higher priority formats appear earlier in the list."""
        def compare_formats(f1, f2):
            f1ID = f1.find('puid').text
            f2ID = f2.find('puid').text
            for worse in f1.findall('has_priority_over'):
                if worse.text == f2ID:
                    return - 1
            for worse in f2.findall('has_priority_over'):
                if worse.text == f1ID:
                    return 1
            if f1ID < f2ID:
                return - 1
            elif f1ID == f2ID:
                return 0
            else:
                return 1
        return sorted(formatlist, cmp=compare_formats)


def fido_position(pronom_position):
    """Return BOF/EOF/VAR instead of the more verbose pronom position names."""
    if pronom_position == 'Absolute from BOF':
        return 'BOF'
    elif pronom_position == 'Absolute from EOF':
        return 'EOF'
    elif pronom_position == 'Variable':
        return 'VAR'
    elif pronom_position == 'Indirect From BOF':
        return 'IFB'
    else:  # to make sure FIDO does not crash (IFB aftermath)
        sys.stderr.write("Unknown pronom PositionType:" + pronom_position)
        return 'VAR'


def _convert_err_msg(msg, c, i, chars):
    return "Conversion: {0}: char='{1}', at pos {2} in \n  {3}\n  {4}^\nBuffer = {5}".format(msg, c, i, chars, i * ' ', buf.getvalue())


def doByte(chars, i, littleendian):
    """
    Convert two chars[i] and chars[i+1] into a byte.

    @return a tuple (byte, 2)
    """
    c1 = '0123456789ABCDEF'.find(chars[i].upper())
    c2 = '0123456789ABCDEF'.find(chars[i + 1].upper())
    if (c1 < 0 or c2 < 0):
        raise Exception(_convert_err_msg('bad byte sequence', chars[i:i + 2], i, chars))
    if littleendian:
        val = chr(16 * c1 + c2)
    else:
        val = chr(c1 + 16 * c2)
    return (escape(val), 2)

# \a\b\n\r\t\v
# MdR: took out '<' and '>' out of _ordinary because they were converted to entities &lt;&gt;
# MdR: moved '!' from _ordinary to _special because it means "NOT" in the regex world. At this time no regex in any sig has a negate set, did this to be on the safe side
_ordinary = frozenset(' "#%&\',-/0123456789:;=@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz~')
_special = '$()*+.?![]^\\{|}'
_hex = '0123456789abcdef'


def _escape_char(c):
    if c in '\n':
        return '\\n'
    elif c == '\r':
        return '\\r'
    elif c in _special:
        return '\\' + c
    else:
        (high, low) = divmod(ord(c), 16)
        return '\\x' + _hex[high] + _hex[low]


def escape(string):
    """Escape characters in pattern that are non-printable, non-ascii, or special for regexes."""
    return ''.join(c if c in _ordinary else _escape_char(c) for c in string)


def calculate_repetition(char, pos, offset, maxoffset):
    """Recursively calculates offset/maxoffset repetition, when one or both offsets is greater than 65535 bytes (64KB). See: https://bugs.python.org/issue13169."""
    calcbuf = cStringIO()

    calcremain = False
    offsetremain = 0
    maxoffsetremain = 0

    if offset and int(offset) > 65535:
        offsetremain = str(int(offset) - 65535)
        offset = '65535'
        calcremain = True
    if maxoffset and int(maxoffset) > 65535:
        maxoffsetremain = str(int(maxoffset) - 65535)
        maxoffset = '65535'
        calcremain = True

    if pos == "BOF" or pos == "EOF":
        if offset != '0':
            calcbuf.write(char + '{' + str(offset))
            if maxoffset:
                calcbuf.write(',' + maxoffset)
            calcbuf.write('}')
        elif maxoffset:
            calcbuf.write(char + '{0,' + maxoffset + '}')

    if pos == "IFB":
        if offset != '0':
            calcbuf.write(char + '{' + str(offset))
            if maxoffset:
                calcbuf.write(',' + maxoffset)
            calcbuf.write('}')
            if maxoffset:
                calcbuf.write(',}')
        elif maxoffset:
            calcbuf.write(char + '{0,' + maxoffset + '}')

    if calcremain:  # recursion happens here
        calcbuf.write(calculate_repetition(char, pos, offsetremain, maxoffsetremain))

    val = calcbuf.getvalue()
    calcbuf.close()
    return val


def convert_to_regex(chars, endianness='', pos='BOF', offset='0', maxoffset=''):
    """
    Convert to regular expression.

    Endianness is not used.

    @param chars, a pronom bytesequence, into a
    @return regular expression.
    """
    if 'Big' in endianness:
        littleendian = False
    else:
        littleendian = True
    if len(offset) == 0:
        offset = '0'
    if len(maxoffset) == 0:
        maxoffset = None
    # make buf global so we can print it @'_convert_err_msg' while debugging (MdR)
    global buf
    buf = cStringIO()
    buf.write("(?s)")  # If a regex starts with (?s), it is equivalent to DOTALL.
    i = 0
    state = 'start'
    if 'BOF' in pos:
        buf.write('\\A')  # start of regex
        buf.write(calculate_repetition('.', pos, offset, maxoffset))

    if 'IFB' in pos:
        buf.write('\\A')
        buf.write(calculate_repetition('.', pos, offset, maxoffset))

    while True:
        if i == len(chars):
            break
        # print _convert_err_msg(state,chars[i],i,chars)
        if state == 'start':
            if chars[i].isalnum():
                state = 'bytes'
            elif chars[i] == '[' and chars[i + 1] == '!':
                state = 'non-match'
            elif chars[i] == '[':
                state = 'bracket'
            elif chars[i] == '{':
                state = 'curly'
            elif chars[i] == '(':
                state = 'paren'
            elif chars[i] in '*+?':
                state = 'specials'
            else:
                raise Exception(_convert_err_msg('Illegal character in start', chars[i], i, chars))
        elif state == 'bytes':
            (byt, inc) = doByte(chars, i, littleendian)
            buf.write(byt)
            i += inc
            state = 'start'
        elif state == 'non-match':
            buf.write('(!')
            i += 2
            while True:
                if chars[i].isalnum():
                    (byt, inc) = doByte(chars, i, littleendian)
                    buf.write(byt)
                    i += inc
                elif chars[i] == ']':
                    break
                else:
                    raise Exception(_convert_err_msg('Illegal character in non-match', chars[i], i, chars))
            buf.write(')')
            i += 1
            state = 'start'

        elif state == 'bracket':
            try:
                buf.write('[')
                i += 1
                (byt, inc) = doByte(chars, i, littleendian)
                buf.write(byt)
                i += inc
                # assert(chars[i] == ':')
                if chars[i] != ':':
                    return "__INCOMPATIBLE_SIG__"
                buf.write('-')
                i += 1
                (byt, inc) = doByte(chars, i, littleendian)
                buf.write(byt)
                i += inc
                # assert(chars[i] == ']')
                if chars[i] != ']':
                    return "__INCOMPATIBLE_SIG__"
                buf.write(']')
                i += 1
            except Exception:
                print(_convert_err_msg('Illegal character in bracket', chars[i], i, chars))
                raise
            if i < len(chars) and chars[i] == '{':
                state = 'curly-after-bracket'
            else:
                state = 'start'
        elif state == 'paren':
            buf.write('(?:')
            i += 1
            while True:
                if chars[i].isalnum():
                    (byt, inc) = doByte(chars, i, littleendian)
                    buf.write(byt)
                    i += inc
                elif chars[i] == '|':
                    buf.write('|')
                    i += 1
                elif chars[i] == ')':
                    break
                # START fix FIDO-20
                elif chars[i] == '[':
                    buf.write('[')
                    i += 1
                    (byt, inc) = doByte(chars, i, littleendian)
                    buf.write(byt)
                    i += inc
                    # assert(chars[i] == ':')
                    if chars[i] != ':':
                        return "__INCOMPATIBLE_SIG__"
                    buf.write('-')
                    i += 1
                    (byt, inc) = doByte(chars, i, littleendian)
                    buf.write(byt)
                    i += inc

                    # assert(chars[i] == ']')
                    if chars[i] != ']':
                        return "__INCOMPATIBLE_SIG__"
                    buf.write(']')
                    i += 1
                else:
                    raise Exception(_convert_err_msg(('Current state = \'{0}\' : Illegal character in paren').format(state), chars[i], i, chars))
            buf.write(')')
            i += 1
            state = 'start'
            # END fix FIDO-20
        elif state in ['curly', 'curly-after-bracket']:
            # {nnnn} or {nnn-nnn} or {nnn-*}
            # {nnn} or {nnn,nnn} or {nnn,}
            # when there is a curly-after-bracket, then the {m,n} applies to the bracketed item
            # The above, while sensible, appears to be incorrect.  A '.' is always needed.
            # for droid equiv behavior
            # if state == 'curly':
            buf.write('.')
            buf.write('{')
            i += 1                # skip the (
            while True:
                if chars[i].isalnum():
                    buf.write(chars[i])
                    i += 1
                elif chars[i] == '-':
                    buf.write(',')
                    i += 1
                elif chars[i] == '*':  # skip the *
                    i += 1
                elif chars[i] == '}':
                    break
                else:
                    raise Exception(_convert_err_msg('Illegal character in curly', chars[i], i, chars))
            buf.write('}')
            i += 1                # skip the )
            state = 'start'
        elif state == 'specials':
            if chars[i] == '*':
                buf.write('.*')
                i += 1
            elif chars[i] == '+':
                buf.write('.+')
                i += 1
            elif chars[i] == '?':
                if chars[i + 1] != '?':
                    raise Exception(_convert_err_msg('Illegal character after ?', chars[i + 1], i + 1, chars))
                buf.write('.?')
                i += 2
            state = 'start'
        else:
            raise Exception('Illegal state {0}'.format(state))

    if 'EOF' in pos:
        buf.write(calculate_repetition('.', pos, offset, maxoffset))
        buf.write('\\Z')

    val = buf.getvalue()
    buf.close()
    return val


def main(args=None):
    """Convert PRONOM formats into FIDO signatures."""
    if args is None:
        args = sys.argv[1:]

    versions = get_local_pronom_versions()

    parser = ArgumentParser(description='Produce the FIDO format XML that is loaded at run-time')
    parser.add_argument('-input', default=versions.get_zip_file(), help='Input file, a Zip containing PRONOM XML files')
    parser.add_argument('-output', default=versions.get_signature_file(), help='Ouptut file')
    parser.add_argument('-puid', default=None, help='A particular PUID record to extract')
    args = parser.parse_args(args)

    info = FormatInfo(args.input)
    info.load_pronom_xml(args.puid)
    info.save(args.output)
    print('Converted {0} PRONOM formats to FIDO signatures'.format(len(info.formats)), file=sys.stderr)


if __name__ == '__main__':
    main()
