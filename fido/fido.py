#!python

import sys, re, os, time
import hashlib, urllib
from xml.etree import cElementTree as ET    
version = '0.9.4'
defaults = {'bufsize': 32 * 4096,
            'regexcachesize' : 2084,
            'conf_dir' : os.path.join(os.path.dirname(__file__), 'conf'),
            'printmatch': "OK,{info.time},{info.puid},{info.formatname},{info.signaturename},{info.filesize},\"{info.filename}\"\n",
            'printnomatch' : "KO,{info.time},,,,{info.filesize},\"{info.filename}\"\n",
            'format_files': ['formats.xml', 'format_extensions.xml'],
            'description' : """
    Format Identification for Digital Objects (fido).
    FIDO is a command-line tool to identify the file useformats of digital objects.
    It is designed for simple integration into automated work-flows.
    """,
    'epilog' : """
    Open Planets Foundation (http://www.openplanetsfoundation.org)\n
    See License.txt for license information.  Download from: http://github.com/openplanets/fido/downloads\n
    Author: Adam Farquhar, 2010\n
        
    FIDO uses the UK National Archives (TNA) PRONOM File Format descriptions.
    PRONOM is available from www.tna.gov.uk/pronom.
    """
}

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

class FormatInfo:
    def __init__(self, pronom_files, format_list=[]):
        self.info = {}
        self.formats = []
        self.pronom_files = pronom_files
        for f in format_list:
            self.add_format(f)
                             
    def save_fido_xml(self, dst):
        """Write the fido XML format definitions to @param dst
        """
        print "Saving to "+dst+"..."
        tree = ET.ElementTree(ET.Element('formats', {'version':'0.3',
                                                     'xmlns:xsi' : "http://www.w3.org/2001/XMLSchema-instance",
                                                     'xsi:noNamespaceSchemaLocation': "fido-formats.xsd",
                                                     'xmlns:dc': "http://purl.org/dc/elements/1.1/",
                                                     'xmlns:dcterms': "http://purl.org/dc/terms/"}))
        root = tree.getroot()
        for f in self.formats:
            if f.find('signature'):
                root.append(f)
        self.indent(root)
        with open(dst, 'wb') as out:
                print >> out, ET.tostring(root, encoding='UTF-8')     

    def indent(self, elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
                
    def load_pronom_xml(self):
        """Load the pronom XML from self.pronom_files and convert it to fido XML.
           As a side-effect, set self.useformats to a list of ElementTree.Element
        """
        print "Loading PRONOM data from "+self.pronom_files
        import zipfile
        formats = []
        zip = None
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
            if( zip != None ):
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
            if type == 'PUID':
                puid = get_text_tna(id, 'Identifier')
                ET.SubElement(fido_format, 'puid').text = puid
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
        # Get the Apple format identifier
        for id in pronom_format.findall(TNA('FileFormatIdentifier')):
            type = get_text_tna(id, 'IdentifierType')
            if type == 'Apple Uniform Type Identifier':
                ET.SubElement(fido_format, 'apple_uti').text = get_text_tna(id, 'Identifier')  
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
                regex = convert_pronom_pattern_to_regex(bytes, pos, offset, max_offset)
                ET.SubElement(fido_pat, 'position').text = pos
                ET.SubElement(fido_pat, 'pronom_pattern').text = bytes
                ET.SubElement(fido_pat, 'regex').text = regex

        # Get the format details
        fido_details = ET.SubElement(fido_format,'details')
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
            r = ET.SubElement(fido_details,'reference')
            ET.SubElement(r, 'dc:title').text = get_text_tna(x, 'TitleText')
            ET.SubElement(r, 'dc:creator').text = get_text_tna(x, 'Author/AuthorCompoundName')
            ET.SubElement(r, 'dc:publisher').text = get_text_tna(x, 'Publisher/PublisherCompoundName')
            ET.SubElement(r, 'dcterms:available').text = get_text_tna(x, 'PublicationDate')
            for id in x.findall(TNA('DocumentIdentifier')):
                type = get_text_tna(id, 'IdentifierType')
                if type == 'URL':
                    ET.SubElement(r, 'dc:identifier').text = "http://"+get_text_tna(id, 'Identifier')  
                else:
                    ET.SubElement(r, 'dc:identifier').text = get_text_tna(id, 'IdentifierType')+":"+get_text_tna(id, 'Identifier')  
            ET.SubElement(r, 'dc:description').text = get_text_tna(x, 'DocumentNote')
            ET.SubElement(r, 'dc:type').text = get_text_tna(x, 'DocumentType')
            ET.SubElement(r, 'dcterms:license').text = get_text_tna(x, 'AvailabilityDescription')
            if get_text_tna(x, 'AvailabilityNote') != "":
                ET.SubElement(r, 'dc:source').text = get_text_tna(x, 'AvailabilityNote')
            ET.SubElement(r, 'dc:rights').text = get_text_tna(x, 'DocumentIPR')
        # Examples
        for x in pronom_format.findall(TNA("ReferenceFile")):
            rf = ET.SubElement(fido_details,'example_file')
            ET.SubElement(rf, 'dc:title').text = get_text_tna(x, 'ReferenceFileName')
            ET.SubElement(rf, 'dc:description').text = get_text_tna(x, 'ReferenceFileDescription')
            checksum = ""
            for id in x.findall(TNA('ReferenceFileIdentifier')):
                type = get_text_tna(id, 'IdentifierType')
                if type == 'URL':
                    url = "http://"+get_text_tna(id, 'Identifier')
                    ET.SubElement(rf, 'dc:identifier').text = url  
                    try:
                        # And calculate the checksum of this resource:
                        m = hashlib.md5()
                        sock = urllib.urlopen(url)
                        m.update(sock.read())
                        sock.close()
                        checksum=m.hexdigest()
                    except IOError:
                        print "WARNING! Could not download and calculate checksum for test file."
                else:
                    ET.SubElement(rf, 'dc:identifier').text = get_text_tna(id, 'IdentifierType')+":"+get_text_tna(id, 'Identifier')  
            ET.SubElement(rf, 'dcterms:license').text = ""
            ET.SubElement(rf, 'dc:rights').text = get_text_tna(x, 'ReferenceFileIPR')
            checksumElement = ET.SubElement(rf, 'checksum')
            checksumElement.text = checksum
            checksumElement.attrib['type'] = "md5"
        # Record Metadata
        md = ET.SubElement(fido_details,'record_metadata')
        ET.SubElement(md, 'status').text ='unknown'
        ET.SubElement(md, 'dc:creator').text = get_text_tna(pronom_format, 'ProvenanceName')
        ET.SubElement(md, 'dcterms:created').text = get_text_tna(pronom_format, 'ProvenanceSourceDate')
        ET.SubElement(md, 'dcterms:modified').text = get_text_tna(pronom_format, 'LastUpdatedDate')
        ET.SubElement(md, 'dc:description').text = get_text_tna(pronom_format, 'ProvenanceDescription').encode('utf8')

        return fido_format
        
    #FIXME: I don't think that this quite works yet!
    def _sort_formats(self, formatlist):
        """Sort the format list based on their priority relationships so higher priority
           useformats appear earlier in the list.
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

def escape(string):
    "Escape characters in pattern that are non-printable, non-ascii, or special for regexes."
    return ''.join(c if c in _ordinary else _escape_char(c) for c in string)

def escape_bytes(bytes, ignore=''):
    def _byte_val(c1, c2):
        c1 = '0123456789ABCDEF'.find(c1.upper())
        c2 = '0123456789ABCDEF'.find(c2.upper())
        return chr(16 * c1 + c2)
    result = []
    i = 0
    while i < len(bytes):
        if bytes[i] in ignore:
            result.append(bytes[i])
            i += 1
        else:
            char = _byte_val(bytes[i], bytes[i + 1])
            if char in _ordinary:
                result.append(char)
            else:
                result.append(_escape_char(char))
            i += 2
    return ''.join(result)
            
# \a\b\n\r\t\v
_ordinary = frozenset(' !"#%&\',-/0123456789:;<=>@ABCDEFGHIJKLMNOPQRSTUVWXYZ_`abcdefghijklmnopqrstuvwxyz~')
_special = '$()*+.?[]^\\{|}'
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

def convert_pronom_pattern_to_regex(pronom_pat, pos=None, offset=None, maxoffset=None):
    import string
    _conv_table = string.maketrans('-:[]', ',-()')

    bytes = r'(?P<bytes>\w+)'                   # hex*
    curly = r'(?P<curly>\{([\d\*\-]+)\})'       # {ddd} or {ddd-ddd} or {ddd-*}
    paren = r'(?P<paren>\([|\w]+\))'            # (bbbb|bbbb|bbbb)
    bracket = r'(?P<bracket>\[\w\w:\w\w\])'     # [bb:bb]
    not_pat = r'(?P<not>\[!\w+\])'              # [!bbb]
    specials = r'(?P<specials>([\*\+])|(\?\?))'
    regex = re.compile('|'.join([bytes, curly, paren, bracket, not_pat, specials]))
    result = ['(?s)']
    if offset != None and len(offset) == 0: offset = None
    if maxoffset != None and len(maxoffset) == 0: maxoffset = None
    if pos == 'BOF':
        str = r'\A'
        if maxoffset != None:
            str += '.{%s,%s}' % (offset if offset != None else 0, maxoffset)
        elif offset != None and offset != '0':
            str += '.{' + offset + '}'
        result.append(str)
    for m in regex.finditer(pronom_pat):
        if m != None:
            gd = m.groupdict()
            if gd['bytes'] != None:
                result.append(escape_bytes(m.group(0)))
            elif gd['curly'] != None:
                str = '.' + gd['curly'].translate(_conv_table, '*') 
                result.append(str)
            elif gd['paren'] != None:
                result.append('(?:' + escape_bytes(m.group(0)[1:-1], '|') + ')')
            elif gd['bracket'] != None:
                result.append(escape_bytes(m.group(0), '[:-]').replace(':', '-'))
            elif gd['not'] != None:
                result.append('(?:' + escape_bytes(m.group(0)[1:-1], '!') + ')')
            elif gd['specials'] != None:
                result.append('.' + gd['specials'][0])
        else:
            #if we get here, then, error
            print >> sys.stderr, '***error parsing ', pronom_pat
    if pos == 'EOF':
        str = ''
        if offset == None and maxoffset != None:
            str = '.{0,' + maxoffset + '}'
        elif offset != None and offset != '0' and maxoffset == None:
            str = '.{%s}' % offset
        elif offset != None and maxoffset != None:
            str = '.{%s,%s}' % (offset, maxoffset)
        str += r'\Z'
        result.append(str)
    return ''.join(result)

class Fido:
    def __init__(self, quiet=False, bufsize=None, printnomatch=None, printmatch=None,
                 extension=False, zip=False, handle_matches=None, conf_dir=None, format_files=None):
        global defaults
        self.quiet = quiet
        self.bufsize = (defaults['bufsize'] if bufsize == None else bufsize)
        self.printmatch = (defaults['printmatch'] if printmatch == None else printmatch)
        self.printnomatch = (defaults['printnomatch'] if printnomatch == None else printnomatch)
        self.handle_matches = (self.print_matches if handle_matches == None else handle_matches)
        self.zip = zip
        self.extension = extension
        self.conf_dir = defaults['conf_dir'] if conf_dir == None else conf_dir
        self.format_files = defaults['format_files'] if format_files == None else format_files
        self.formats = []
        self.puid_format_map = {}
        self.puid_has_priority_over_map = {}
        for file in self.format_files:
            self.load_fido_xml(os.path.join(os.path.abspath(self.conf_dir), file))
        self.current_file = ''
        self.current_filesize = 0
        self.current_format = None
        self.current_sig = None
        self.current_pat = None
        self.current_count = 0  # Count of calls to match_formats
        re._MAXCACHE = defaults['regexcachesize']
        self.externalsig = ET.XML('<signature><name>External</name></signature>')

    def load_fido_xml(self, file):
        """Load the fido format information from @param file.
           As a side-effect, set self.useformats
           @return list of ElementTree.Element, one for each format.
        """
        tree = ET.parse(file)
        #print "Loaded format specs in {0:>6.2f}ms".format((t1 - t0) * 1000)
        #TODO: Handle empty regexes properly; perhaps remove from the format list
        for element in tree.getroot().findall('./format'):
            puid = self.get_puid(element)
            # Handle over-writes in multiple file loads
            existing = self.puid_format_map.get(puid, False) 
            if  existing:
                # Already have one, so replace old with new!
                self.formats[self.formats.index(existing)] = element
            else:
                self.formats.append(element)
            self.puid_format_map[puid] = element
            # Build some structures to speed things up
            self.puid_has_priority_over_map[puid] = frozenset([puid_element.text for puid_element in element.findall('has_priority_over')])
        return self.formats

    # To delete a format: (1) remove from self.useformats, (2) remove from puid_format_map, (3) remove from selt.puid_has_pri
    def get_signatures(self, format):
        return format.findall('signature')
    
    def has_priority_over(self, format, possibly_inferior):
        return self.get_puid(possibly_inferior)in self.puid_has_priority_over_map[self.get_puid(format)]
                
    def get_puid(self, format):
        return format.find('puid').text
    
    def get_patterns(self, signature):
        return signature.findall('pattern')
    
    def get_pos(self, pat):        
        return pat.find('position').text
    
    def get_regex(self, pat):
        return pat.find('regex').text
    
    def print_matches(self, fullname, matches, delta_t):
        """The default match handler.  Prints out information for each match in the list.
           @param fullname is name of the file being matched
           @param matches is a list of (format, signature)
           @param delta_t is the time taken for the match.
        """
        class Info:
            pass
        obj = Info()
        obj.count = self.current_count
        obj.group_size = len(matches)
        obj.filename = fullname
        obj.time = int(delta_t * 1000)
        obj.filesize = self.current_filesize
        if len(matches) == 0:
            sys.stdout.write(self.printnomatch.format(info=obj))
        else:
            i = 0
            for (f, s) in matches:
                i += 1
                obj.group_index = i
                obj.puid = self.get_puid(f)
                obj.formatname = f.find('name').text
                obj.signaturename = s.find('name').text
                mime = s.find('mime')
                obj.mimetype = mime.text if mime != None else None
                sys.stdout.write(self.printmatch.format(info=obj))
        
    def print_summary(self, secs):
        """Print summary information on the number of matches and time taken.
        """
        count = self.current_count
        if not self.quiet:
            rate = (int(count / secs) if secs != 0 else 9999)
            print >> sys.stderr, "FIDO: Processed {0:>6d} files in {1:>6.2f} msec, {2:d} files/sec".format(count, secs * 1000, rate)
                                         
    def identify_file(self, filename):
        """Identify the type of @param filename.  
           Call self.handle_matches instead of returning a value.
        """
        self.current_file = filename
        try:
            t0 = time.clock()
            with open(filename, 'rb') as f:
                size = os.stat(filename)[6]
                self.current_filesize = size
                bofbuffer, eofbuffer = self.get_buffers(f, size, seekable=True)
            matches = self.match_formats(bofbuffer, eofbuffer)
            self.handle_matches(filename, matches, time.clock() - t0)
            if self.extension and len(matches) == 0:
                matches = self.match_extensions(filename)
                self.handle_matches(filename, matches, time.clock() - t0)
            if self.zip:
                self.identify_contents(filename, type=self.container_type(matches))
        except IOError:
            print >> sys.stderr, "FIDO: Error in identify_file: Path is {0}".format(filename)

    def identify_contents(self, filename, fileobj=None, type=False):
        """Identify each item in a container (such as a zip or tar file).  Call self.handle_matches on each item.
           @param fileobj could be a file, or a stream.
        """
        if type == False:
            return
        elif type == 'zip':
            self.walk_zip(filename, fileobj)
        elif type == 'tar':
            self.walk_tar(filename, fileobj)
        else:
            raise RuntimeError("Unknown container type: " + repr(type))
                
    def identify_multi_object_stream(self, stream):
        """Does not work!
           Stream may contain one or more objects each with an HTTP style header that must include content-length.
           The headers consist of keyword:value pairs terminated by a newline.  There must be a newline following the headers.
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
            bofbuffer, eofbuffer = self.get_buffers(stream, content_length)
            matches = self.match_formats(bofbuffer, eofbuffer)
            self.handle_matches(self.current_file, matches, time.clock() - t0)
                
    def identify_stream(self, stream):
        """Identify the type of @param stream.  
           Call self.handle_matches instead of returning a value.
           Does not close stream.
        """
        t0 = time.clock()
        bofbuffer, eofbuffer, bytes_read = self.get_buffers(stream, length=None)
        self.current_filesize = bytes_read
        self.current_file = 'STDIN'
        matches = self.match_formats(bofbuffer, eofbuffer)
        self.handle_matches(self.current_file, matches, time.clock() - t0)
                    
    def container_type(self, matches):
        """Determine if one of the @param matches is the format of a container that we can look inside of (e.g., zip, tar).
           @return False, zip, or tar.
        """
        for (format, unused) in matches:
            container = format.find('container')
            if container != None:
                return container.text
        return False
                            
    def get_buffers(self, stream, length=None, seekable=False):
        """Return buffers from the beginning and end of stream and the number of bytes read
           if there may be more bytes in the stream.  
        
           If length is None, return the length as found. 
           If seekable is False, the steam does not support a seek operation.
        """
        
        bofbuffer = stream.read(self.bufsize if length == None else min(length, self.bufsize))
        bytes_read = len(bofbuffer)
        if length == None:
            # A stream with unknown length; have to keep two buffers around
            prevbuffer = bofbuffer
            while True:
                buffer = stream.read(self.bufsize)
                bytes_read += len(buffer)
                if len(buffer) == self.bufsize:
                    prevbuffer = buffer
                else:
                    eofbuffer = prevbuffer if len(buffer) == 0 else prevbuffer[-(self.bufsize - len(buffer)):] + buffer
                    break
            return bofbuffer, eofbuffer, bytes_read
        else:
            bytes_unread = length - len(bofbuffer)
            if bytes_unread == 0:
                eofbuffer = bofbuffer
            elif bytes_unread < self.bufsize:
                # The buffs overlap
                eofbuffer = bofbuffer[bytes_unread:] + stream.read(bytes_unread)
            elif bytes_unread == self.bufsize:
                eofbuffer = stream.read(self.bufsize)
            elif seekable:  # easy case when we can just seek!
                stream.seek(length - self.bufsize)
                eofbuffer = stream.read(self.bufsize)
            else:
                # We have more to read and know how much.    
                # n*bufsize + r = length
                (n, r) = divmod(bytes_unread, self.bufsize)
                # skip n-1*bufsize bytes
                for unused_i in xrange(1, n):
                    stream.read(self.bufsize)
                # skip r bytes
                stream.read(r)
                # and read the remaining bufsize bytes into the eofbuffer
                eofbuffer = stream.read(self.bufsize)
            return bofbuffer, eofbuffer
    
    def walk_zip(self, filename, fileobj=None):
        """Identify the type of each item in the zip 
           @param fileobj.  If fileobj is not provided, open 
           @param filename.
           Call self.handle_matches instead of returning a value.
        """
        # IN 2.7+: with zipfile.ZipFile((fileobj if fileobj != None else filename), 'r') as stream:
        import zipfile, tempfile
        try:
            zipstream = None
            zipstream = zipfile.ZipFile((fileobj if fileobj != None else filename))    
            for item in zipstream.infolist():
                if item.file_size == 0:
                    continue           #TODO: Find a better test for isdir
                t0 = time.clock()
                # with zipstream.open(item) as f:
                f = None
                try:
                    f = zipstream.open(item)
                    item_name = filename + '!' + item.filename
                    self.current_file = item_name
                    self.current_filesize = item.file_size
                    bofbuffer, eofbuffer = self.get_buffers(f, item.file_size)
                finally:
                    if f != None: f.close()
                matches = self.match_formats(bofbuffer, eofbuffer)
                self.handle_matches(item_name, matches, time.clock() - t0)
                if self.container_type(matches):
                    with tempfile.SpooledTemporaryFile(prefix='Fido') as target:
                        #with zipstream.open(item) as source:
                        try:
                            source = zipstream.open(item)
                            self.copy_stream(source, target)
                            #target.seek(0)
                            self.identify_contents(item_name, target, self.container_type(matches))
                        finally:
                            source.close()
        except IOError:
            print >> sys.stderr, "FIDO: Error: ZipError {0}".format(filename)
        except zipfile.BadZipfile:
            print >> sys.stderr, "FIDO: Error: ZipError {0}".format(filename)
            
        finally:
            if zipstream != None: zipstream.close()

    def walk_tar(self, filename, fileobj):
        """Identify the type of each item in the tar 
           @param fileobj.  If fileobj is not provided, open 
           @param filename.
           Call self.handle_matches instead of returning a value.
        """
        import tarfile
        tarstream = None
        try:
            tarstream = tarfile.TarFile(filename, fileobj=fileobj, mode='r')
            for item in tarstream.getmembers():
                if item.isfile():
                    t0 = time.clock()
                    f = tarstream.extractfile(item)
                    tar_item_name = filename + '!' + item.name
                    self.current_file = tar_item_name
                    self.current_filesize = item.size
                    bofbuffer, eofbuffer = self.get_buffers(f, item.size)
                    matches = self.match_formats(bofbuffer, eofbuffer)
                    self.handle_matches(tar_item_name, matches, time.clock() - t0)
                    if self.container_type(matches):
                        f.seek(0)
                        self.identify_contents(tar_item_name, f, self.container_type(matches))
                        f.close()
        except tarfile.TarError:
                print >> sys.stderr, "FIDO: Error: TarError {0}".format(filename)
        finally:
            if tarstream != None: tarstream.close()

    def as_good_as_any(self, f1, match_list):
        """Return True if the proposed format is as good as any in the match_list.
           For example, if there is no format in the match_list that has priority over the proposed one"""
        if match_list != []:
            f1_puid = self.get_puid(f1)
            for (f2, unused) in match_list:
                if f1 == f2:
                    continue
                elif f1_puid in self.puid_has_priority_over_map[self.get_puid(f2)]:
                    return False
        return True
    
    def match_formats(self, bofbuffer, eofbuffer):
        """Apply the patterns for useformats to the supplied buffers.
           @return a match list of (format, signature) tuples. 
           The list has inferior matches removed.
        """
        self.current_count += 1
        #t0 = time.clock()
        result = []
        try:
            for format in self.formats:
                self.current_format = format
                if self.as_good_as_any(format, result):
                    for sig in self.get_signatures(format):
                        self.current_sig = sig
                        success = True
                        for pat in self.get_patterns(sig):
                            self.current_pat = pat
                            pos = self.get_pos(pat)
                            regex = self.get_regex(pat)
                            #print 'trying ', regex
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
                        if success:
                            result.append((format, sig))
                            break
        except Exception:
            print '***', self.get_puid(format), regex
            
        #        t1 = time.clock()
        #        if t1 - t0 > 0.02:
        #            print >> sys.stderr, "FIDO: Slow ID", self.current_file
        result = [match for match in result if self.as_good_as_any(match[0], result)]
        return result
    
    def match_extensions(self, filename):
        "Return the list of (format, self.externalsig) for every format whose extension matches the filename."
        myext = os.path.splitext(filename)[1].lower()
        result = []
        if len(myext) > 0:
            for format in self.formats:
                self.current_format = format
                if myext in format.extensions:
                    result.append((format, self.externalsig))
        result = [match for match in result if self.as_good_as_any(match[0], result)]
        return result
    
    def copy_stream(self, source, target):
        while True:
            buf = source.read(self.bufsize)
            if len(buf) == 0:
                break
            target.write(buf)
             
def list_files(roots, recurse=False):
    "Return the files one at a time.  Roots could be a fileobj or a list."
    for root in roots:
        root = (root if root[-1] != '\n' else root[:-1])
        root = os.path.normpath(root)
        if os.path.isfile(root):
            yield root
        else:
            for path, unused, files in os.walk(root):
                for f in files:
                    yield os.path.join(path, f)
                if recurse == False:
                    break
            
def main(arglist=None):
    # The argparse package was introduced in 2.7
    t0 = time.clock() 
    from argparselocal import ArgumentParser  
    if arglist == None:
        arglist = sys.argv[1:]
        
    parser = ArgumentParser(description=defaults['description'], epilog=defaults['epilog'], fromfile_prefix_chars='@')
    parser.add_argument('-v', default=False, action='store_true', help='show version information')
    parser.add_argument('-q', default=False, action='store_true', help='run (more) quietly')
    parser.add_argument('-recurse', default=False, action='store_true', help='recurse into subdirectories')
    parser.add_argument('-zip', default=False, action='store_true', help='recurse into zip and tar files')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-input', default=False, help='file containing a list of files to check, one per line. - means stdin')
    group.add_argument('files', nargs='*', default=[], metavar='FILE', help='files to check.  If the file is -, then read content from stdin. In this case, python must be invoked with -u or it may convert the line terminators.')
    parser.add_argument('-useformats', metavar='INCLUDEPUIDS', default=None, help='comma separated string of useformats to use in identification')
    parser.add_argument('-nouseformats', metavar='EXCLUDEPUIDS', default=None, help='comma separated string of useformats not to use in identification')
    parser.add_argument('-extension', default=False, action='store_true', help='use file extensions if the patterns fail.  May return many matches.')
    parser.add_argument('-matchprintf', metavar='FORMATSTRING', default=None, help='format string (Python style) to use on match. See nomatchprintf, README.txt.')
    parser.add_argument('-nomatchprintf', metavar='FORMATSTRING', default=None, help='format string (Python style) to use if no match. See README.txt')
    parser.add_argument('-bufsize', type=int, default=None, help='size of the buffer to match against')
    parser.add_argument('-show', default=False, help='show "format" or "defaults"')
    
    parser.add_argument('-loadformats', default=None, metavar='XML1,...,XMLn', help='comma separated string of XML format files to add.')
    parser.add_argument('-confdir', default=None, help='configuration directory to load_fido_xml, for example, the format specifications from.')
   
    mydir = os.path.abspath(os.path.dirname(__file__))
    parser.add_argument('-convert', default=False, action='store_true', help='Convert pronom xml to fido xml')
    parser.add_argument('-source', default=os.path.join(mydir, 'conf', 'pronom-xml.zip'),
                        help='import from a zip file containing only Pronom xml files')
    parser.add_argument('-target', default=os.path.join(mydir, 'conf', 'useformats.xml'), help='export fido xml output file')
         
    # PROCESS ARGUMENTS
    args = parser.parse_args(arglist)
    
    if args.convert:
        # print os.path.abspath(args.input), os.path.abspath(args.output)
        info = FormatInfo(args.source)
        info.load_pronom_xml()
        info.save_fido_xml(args.target)
        delta_t = time.clock() - t0
        if not args.q:
            print >> sys.stderr, 'FIDO: Converted {0} useformats in {1}s'.format(len(info.formats), delta_t)
    
    if args.v :
        print "fido/" + version
        exit(0)
    if args.show == 'defaults':
        for (k, v) in defaults.iteritems():
            print k, '=', repr(v)
        exit(0)
    if args.matchprintf != None:
        args.matchprintf = args.matchprintf.decode('string_escape')
    if args.nomatchprintf != None:
        args.nomatchprintf = args.nomatchprintf.decode('string_escape')
    fido = Fido(quiet=args.q, bufsize=args.bufsize, extension=args.extension,
                printmatch=args.matchprintf, printnomatch=args.nomatchprintf, zip=args.zip, conf_dir=args.confdir)
    
    #TODO: Allow conf options to be dis-included
    if args.loadformats:
        for file in args.loadformats.split(','):
            fido.load_fido_xml(file)
        
    #TODO: remove from maps
    if args.useformats:
        args.useformats = args.useformats.split(',')
        fido.formats = [f for f in fido.formats if f.find('puid').text in args.useformats]
    elif args.nouseformats:
        args.nouseformats = args.nouseformats.split(',')
        fido.formats = [f for f in fido.formats if f.find('puid') not in args.nouseformats]
    
    if args.show == 'useformats':
        for format in fido.formats:
            print ET.tostring(format, encoding='UTF-8')
        exit(0)
        
    if args.input == '-':
        args.files = sys.stdin
    elif args.input:
        args.files = open(args.input, 'r')
    
    # RUN
    try:
        if (not args.input) and len(args.files) == 1 and args.files[0] == '-':
            if fido.zip == True:
                raise RuntimeError("Multiple content read from stdin not yet supported.")
                exit(1)
                fido.identify_multi_object_stream(sys.stdin)
            else:
                fido.identify_stream(sys.stdin)
        else:
            for file in list_files(args.files, args.recurse):
                fido.identify_file(file)
    except KeyboardInterrupt:
        msg = "FIDO: Interrupt during:\n  File: {0}\n  Format: Puid={1.Identifier} [{1.FormatName}]\n  Sig: ID={2.SignatureID} [{2.SignatureName}]\n  Pat={3.ByteSequenceID} {3.regexstring!r}"
        print >> sys.stderr, msg.format(fido.current_file, fido.current_format, fido.current_sig, fido.current_pat)
        exit(1)
        
    if not args.q:
        sys.stdout.flush()
        fido.print_summary(time.clock() - t0)

if __name__ == '__main__':
    main()
    
