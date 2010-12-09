#!python
#
# Format Identification for Digital Objects

import re, cStringIO, zipfile, os
from xml.etree import ElementTree as ET

class NS:
    """Helper class for XML name spaces in ElementTree.
       Use like MYNS=NS("{http://some/uri}") and then
       MYNS(tag1/tag2).
    """
    def __init__(self, uri):
        self.uri = uri
    def __getattr__(self, tag):
        return self.uri + tag
    def __call__(self, path):
        return "/".join(getattr(self, tag) for tag in path.split("/"))

# XHTML namespace
XHTML = NS("{http://www.w3.org/1999/xhtml}")
# TNA namespace
TNA = NS("{http://pronom.nationalarchives.gov.uk}")

def get_text_tna(element, tag, default=''):
    """Helper function to return the text for a tag or path using the TNA namespace.
    """
    part = element.find(TNA(tag))
    return part.text.strip() if part != None and part.text != None else default

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    from xml.dom import minidom
    rough_string = ET.tostring(elem, 'UTF-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

class FormatInfo:
    def __init__(self, pronom_files, format_list=[]):
        self.info = {}
        self.formats = []
        self.pronom_files = pronom_files
        for f in format_list:
            self.add_format(f)
                             
    def save(self, dst):
        """Write the fido XML format definitions to @param dst
        """
        tree = ET.ElementTree(ET.Element('formats', {'version':'0.1'}))
        root = tree.getroot()
        for f in self.formats:
            if f.find('signature'):
                root.append(f)
        with open(dst, 'wb') as out:
                tree.write(out, 'UTF-8')     

    def load_pronom_xml(self):
        """Load the pronom XML from self.pronom_files and convert it to fido XML.
           As a side-effect, set self.formats to a list of ElementTree.Element
        """
        formats = []
        try:
            zip = zipfile.ZipFile(self.pronom_files, 'r')
            for item in zip.infolist():
                try:
                    stream = zip.open(item)
                    # Work is done here!
                    formats.append(self.parse_pronom_xml(stream))
                finally:
                    stream.close()
        finally:
            zip.close()
        # Replace the formatID with puids in has_priority_over
        id_map = {}
        for element in formats:
            puid = element.find('puid').text
            pronom_id = element.find('pronom_id').text
            id_map[pronom_id] = puid
        for element in formats:
            for rel in element.findall('has_priority_over'):
                rel.text = id_map[rel.text]
        self._sort_formats(formats)
        self.formats = formats
                    
    def parse_pronom_xml(self, source):
        """Read a pronom XML from @param source, convert it to fido XML and
           @return ET.ElementTree Element representing it.
        """
        pronom_xml = ET.parse(source)
        pronom_root = pronom_xml.getroot()
        pronom_format = pronom_root.find(TNA('report_format_detail/FileFormat'))
        fido_format = ET.Element('format')
        # Get the base Format information
        for id in pronom_format.findall(TNA('FileFormatIdentifier')):
            type = get_text_tna(id, 'IdentifierType')
            if type == 'MIME':
                ET.SubElement(fido_format, 'mime').text = get_text_tna(id, 'Identifier')
            elif type == 'PUID':
                puid = get_text_tna(id, 'Identifier')
                ET.SubElement(fido_format, 'puid').text = puid
                if puid == 'x-fmt/263':
                    ET.SubElement(fido_format, 'container').text = 'zip'
                elif puid == 'x-fmt/265':
                    ET.SubElement(fido_format, 'container').text = 'tar'
        ET.SubElement(fido_format, 'name').text = get_text_tna(pronom_format, 'FormatName')
        ET.SubElement(fido_format, 'pronom_id').text = get_text_tna(pronom_format, 'FormatID')
        # Get the extensions from the ExternalSignature
        for x in pronom_format.findall(TNA('ExternalSignature')):
                ET.SubElement(fido_format, 'extension').text = get_text_tna(x, 'Signature')
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
                if max_offset == None:
                    pass
                regex = convert_to_regex(bytes, 'Little', pos, offset, max_offset)
                ET.SubElement(fido_pat, 'position').text = pos
                ET.SubElement(fido_pat, 'pronom_pattern').text = bytes
                #FIXME: Perhaps there is a better approach to escaping the regex?
                ET.SubElement(fido_pat, 'regex').text = regex.encode('string_escape')
        return fido_format  
    
    #FIXME: I don't think that this quite works yet!
    def _sort_formats(self, formatlist):
        """Sort the format list based on their priority relationships so higher priority
           formats appear earlier in the list.
        """
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
    """@return BOF/EOF/VAR instead of the more verbose pronom position names.
    """
    if pronom_position == 'Absolute from BOF':
        return 'BOF'
    elif pronom_position == 'Absolute from EOF':
        return 'EOF'
    elif pronom_position == 'Variable':
        return 'VAR'
    else:
        raise Exception("Unknown pronom PositionType=" + pronom_position)    

def _convert_err_msg(msg, c, i, chars):
    return "Conversion: {0}: char='{1}', at pos {2} in \n  {3}\n  {4}^".format(msg, c, i, chars, i * ' ')

def doByte(chars, i, littleendian):
    """Convert two chars[i] and chars[i+1] into a byte.  
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
    return (re.escape(val), 2)

def convert_to_regex(chars, endianness='', pos='BOF', offset='0', maxoffset=''):
    """Convert @param chars, a pronom bytesequence, into a @return regular expression.
       @param endianness is not used.
    """
    if 'Big' in endianness:
        littleendian = False
    else:
        littleendian = True
    if len(offset) == 0:
        offset = '0'
    if len(maxoffset) == 0:
        maxoffset = None
    buf = cStringIO.StringIO()
    buf.write("(?s)")   #If a regex starts with (?s), it is equivalent to DOTALL.   
    i = 0
    state = 'start'
    if 'BOF' in pos:
        buf.write('\\A')
        if offset != '0':
            buf.write('.{')
            buf.write(str(offset))
            if maxoffset != None:
                buf.write(',' + maxoffset)
            buf.write('}')
        elif maxoffset != None:
            buf.write('.{0,' + maxoffset + '}')
            
    while True:
        if i == len(chars):
            break
        #print _convert_err_msg(state,chars[i],i,chars)
        if state == 'start':
            if chars[i].isalnum():
                state = 'bytes'
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
        elif state == 'bracket':
            try:
                buf.write('[')
                i += 1
                (byt, inc) = doByte(chars, i, littleendian)
                buf.write(byt)
                i += inc
                assert(chars[i] == ':')
                buf.write('-')
                i += 1
                (byt, inc) = doByte(chars, i, littleendian)
                buf.write(byt)
                i += inc

                assert(chars[i] == ']')
                buf.write(']')
                i += 1
            except Exception:
                print _convert_err_msg('Illegal character in bracket', chars[i], i, chars)
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
                else:
                    raise Exception(_convert_err_msg('Illegal character in paren', chars[i], i, chars))
            buf.write(')')
            i += 1
            state = 'start'
        elif state in ['curly', 'curly-after-bracket']:
            # {nnnn} or {nnn-nnn} or {nnn-*}
            # {nnn} or {nnn,nnn} or {nnn,}
            # when there is a curly-after-bracket, then the {m,n} applies to the bracketed item
            # The above, while sensible, appears to be incorrect.  A '.' is always needed.
            # for droid equiv behavior
            #if state == 'curly':
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
                elif chars[i] == '*': # skip the *
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
        if offset != '0':
            buf.write('.{' + offset)
            if maxoffset != None:
                buf.write(',' + maxoffset)
            buf.write('}')
        elif maxoffset != None:
            buf.write('.{0,' + maxoffset + '}')
        buf.write('\\Z')
    val = buf.getvalue()
    buf.close()
    return val
    
if __name__ == '__main__':
    info = FormatInfo(os.path.join(os.path.dirname(__file__), 'conf', 'pronom-xml.zip'))
    info.load_pronom_xml()
    info.save(os.path.join(os.path.dirname(__file__), 'conf', 'formats.xml'))
    print 'FIDO: {0} formats'.format(len(info.formats))
    
