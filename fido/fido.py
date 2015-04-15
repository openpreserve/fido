#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, re, os, time, math
import hashlib, urllib, urlparse, csv, getopt
from xml.etree import cElementTree as ET
from xml.etree import ElementTree as CET
from xml.etree import ElementTree as VET # versions.xml

version = '1.3.1'
defaults = {'bufsize': 128 * 1024, # (bytes)
            'regexcachesize' :2084, # (bytes)
            'conf_dir' : os.path.join(os.path.dirname(__file__), 'conf'),
            'printmatch': "OK,%(info.time)s,%(info.puid)s,\"%(info.formatname)s\",\"%(info.signaturename)s\",%(info.filesize)s,\"%(info.filename)s\",\"%(info.mimetype)s\",\"%(info.matchtype)s\"\n",
            'printnomatch' : "KO,%(info.time)s,,,,%(info.filesize)s,\"%(info.filename)s\",,\"%(info.matchtype)s\"\n",
            'format_files': ['formats-v75.xml', 'format_extensions.xml'],
            'containersignature_file' : 'container-signature-20130501.xml',
            # versions.xml is where fido.py reads version information
            # about which xml to load
            'versions_file' : 'versions.xml',
            'container_bufsize' : 512 * 1024, # (bytes)
            'description' : """
    Format Identification for Digital Objects (fido).
    FIDO is a command-line tool to identify the file formats of digital objects.
    It is designed for simple integration into automated work-flows.
    """,
    'epilog' : """
    Open Planets Foundation (http://www.openplanetsfoundation.org)
    See License.txt for license information.
    Download from: https://github.com/openplanets/fido/releases
    Usage guide: http://wiki.opf-labs.org/display/KB/FIDO+usage+guide 
    Author: Adam Farquhar (BL), 2010
    Maintainer: Maurice de Rooij (OPF/NANETH), 2011, 2012, 2013
    FIDO uses the UK National Archives (TNA) PRONOM File Format
    and Container descriptions.
    PRONOM is available from http://www.nationalarchives.gov.uk/pronom/"""
}

class Fido:
    def __init__(self, quiet=False, bufsize=None, container_bufsize = None, printnomatch=None, printmatch=None, zip=False, nocontainer=False, handle_matches=None, conf_dir=None, format_files=None, containersignature_file=None):
        global defaults
        self.quiet = quiet
        self.bufsize = (defaults['bufsize'] if bufsize == None else bufsize)
        self.container_bufsize = (defaults['container_bufsize'] if container_bufsize == None else container_bufsize)
        self.printmatch = (defaults['printmatch'] if printmatch == None else printmatch)
        self.printnomatch = (defaults['printnomatch'] if printnomatch == None else printnomatch)
        self.handle_matches = (self.print_matches if handle_matches == None else handle_matches)
        self.zip = zip
        self.nocontainer = (defaults['nocontainer'] if nocontainer == None else nocontainer)
        self.conf_dir = defaults['conf_dir'] if conf_dir == None else conf_dir
#        print defaults
#        sys.exit()
        self.format_files = defaults['format_files'] if format_files == None else format_files
        #self.containersignature_file = defaults['containersignature_file'] if containersignature_file == None else containersignature_file
        self.containersignature_file = defaults['containersignature_file'] #if containersignature_file == None else containersignature_file
        self.formats = []
        self.puid_format_map = {}
        self.puid_has_priority_over_map = {}
        # load signatures
        for xml_file in self.format_files:
            self.load_fido_xml(os.path.join(os.path.abspath(self.conf_dir), xml_file))
        self.load_container_signature(os.path.join(os.path.abspath(self.conf_dir), self.containersignature_file))
        self.current_file = ''
        self.current_filesize = 0
        self.current_format = None
        self.current_sig = None
        self.current_pat = None
        self.current_count = 0  # Count of calls to match_formats
        re._MAXCACHE = defaults['regexcachesize']
        self.externalsig = ET.XML('<signature><name>External</name></signature>')

    _ordinary = frozenset(' "#%&\',-/0123456789:;=@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz~')
    #_special = '$*+.?![]^\\{|}'
    _special = '$()*+.?![]^\\{|}'
    _hex = '0123456789abcdef'
    def _escape_char(self,c):
        if c in '\n':
            return '\\n'
        elif c == '\r':
            return '\\r'
        elif c in self._special:
            return '\\' + c
        else:
            (high, low) = divmod(ord(c), 16)
            return '\\x' + self._hex[high] + self._hex[low]
    
    def escape(self,string):
        "Escape characters in pattern that are non-printable, non-ascii, or special for regexes."
        escaped = ''.join(c if c in self._ordinary else self._escape_char(c) for c in string)
        return escaped

    def convert_container_sequence(self,sig):
        """Parse the PRONOM container sequences
        and convert to regular expressions
        """
        seq = '(?s)'
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
                    seq += "("
                    rng = True
                    continue
                if not byt:
                    seq += "\\x" + sig[i].lower()
                    byt = True
                    continue
                if byt:
                    seq += sig[i].lower()
                    byt = False
                    continue
            if inq:
                if sig[i] == "'" and not rng:
                    inq = False
                    continue
                seq += self.escape(sig[i])
                continue
            if rng:
                if sig[i] == "]":
                    seq += ")"
                    rng = False
                    continue
                if sig[i] != "-" and sig[i] != "'" and ror:
                    seq += self.escape(sig[i])
                    continue
                if sig[i] != "-" and sig[i] != "'" and sig[i] != " " and sig[i] != ":" and not ror and not byt:
                    seq += "\\x" + sig[i].lower()
                    byt = True
                    continue
                if sig[i] != "-" and sig[i] != "'" and sig[i] != " " and not ror and byt:
                    seq += sig[i].lower()
                    byt = False
                    continue
                if sig[i] == "-" or sig[i] == " ":
                    seq += "|"
                    continue
                if sig[i] == "'" and not ror:
                    ror = True
                    continue
                if sig[i] == "'" and ror:
                    ror = False
                    continue
        #print seq
        return seq
    
    def load_container_signature(self, containersignature_file):
        """Load the PRONOM container-signature file
        and convert sequences to regular expressions
        """
        tree = CET.parse(containersignature_file)
        # load and have container signatures converted
        self.sequenceSignature = {}
        for signature in tree.getroot().findall('ContainerSignatures/ContainerSignature'):
            signatureId = signature.get('Id')
            signatureSequence = signature.findall('Files/File/BinarySignatures/InternalSignatureCollection/InternalSignature/ByteSequence/SubSequence')
            self.sequenceSignature[signatureId] = []
            for sequence in signatureSequence:
                self.sequenceSignature[signatureId].append(self.convert_container_sequence(sequence[0].text))
        # find PUIDs which trigger container matching
        self.puidTriggers = {}
        triggers = tree.find('TriggerPuids')
        for puid in triggers.findall('TriggerPuid'):
            self.puidTriggers[puid.get('Puid')] = True
        # map PUID to container signatureId
        self.puidMapping = {}
        mappings = tree.find('FileFormatMappings')
        for mapping in mappings.findall('FileFormatMapping'):
            if mapping.get('signatureId') not in self.puidMapping:
                self.puidMapping[mapping.get('signatureId')] = []
            self.puidMapping[mapping.get('signatureId')].append(mapping.get('Puid'))
#        print "sequences:\n",self.sequenceSignature
#        print "trigger:\n",self.puidTriggers
#        print "mapping:\n",self.puidMapping
#        exit()

    def load_fido_xml(self, file):
        """Load the fido format information from @param file.
           As a side-effect, set self.formats
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

    # To delete a format: (1) remove from self.formats, (2) remove from puid_format_map, (3) remove from selt.puid_has_priority_over_map
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
    
    def get_extension(self, format):
        return format.find('extension').text
    
    def print_matches(self, fullname, matches, delta_t, matchtype=''):
        """The default match handler.  Prints out information for each match in the list.
           @param fullname is name of the file being matched
           @param matches is a list of (format, signature)
           @param delta_t is the time taken for the match.
           @param matchtype is the type of match (signature, containersignature, extension, fail)
        """
        class Info:
            pass
        obj = Info()
        obj.count = self.current_count
        obj.group_size = len(matches)
        obj.filename = fullname
        obj.time = int(delta_t * 1000)
        obj.filesize = self.current_filesize
        obj.matchtype = matchtype
        if len(matches) == 0:
            sys.stdout.write(self.printnomatch % { "info.time" : obj.time, "info.filesize" : obj.filesize, "info.filename" : obj.filename, "info.count"
            : obj.count, "info.matchtype" : "fail" } )
        else:
            i = 0
            for (f, s) in matches:
                i += 1
                obj.group_index = i
                obj.puid = self.get_puid(f)
                obj.formatname = f.find('name').text
                obj.signaturename = s.find('name').text
                mime = f.find('mime')
                obj.mimetype = mime.text if mime != None else None
                version = f.find('version')
                obj.version = version.text if version != None else None
                alias = f.find('alias')
                obj.alias = alias.text if alias != None else None
                apple_uti = f.find('apple_uid')
                obj.apple_uti = apple_uti.text if apple_uti != None else None
                sys.stdout.write(self.printmatch % { "info.time" : obj.time, "info.puid" : obj.puid, "info.formatname" : obj.formatname, "info.signaturename" : obj.signaturename, "info.filesize" : obj.filesize, "info.filename" : obj.filename, "info.mimetype" : obj.mimetype, "info.matchtype" : obj.matchtype, "info.version" : obj.version, "info.alias" : obj.alias, "info.apple_uti" : obj.apple_uti, "info.group_size" : obj.group_size, "info.group_index" : obj.group_index, "info.count" : obj.count })
        
    def print_summary(self, secs):
        """Print summary information on the number of matches and time taken.
        """
        count = self.current_count
        if not self.quiet:
            rate = (int(round(count / secs)) if secs != 0 else 9999)
            #print >> sys.stderr, 'FIDO: Processed %6d files in %6.2f msec, %2d files/sec' %  (count, secs * 1000, rate)
            sys.stderr.write('FIDO: Processed %6d files in %6.2f msec, %2d files/sec\n' %  (count, secs * 1000, rate))
                    
    def identify_file(self, filename):
        """Identify the type of @param filename.  
           Call self.handle_matches instead of returning a value.
        """
        self.current_file = filename
        self.matchtype = "signature"
        try:
            t0 = time.clock()
            f = open(filename, 'rb')
            size = os.stat(filename)[6]
            self.current_filesize = size
            if self.current_filesize == 0:
                sys.stderr.write("FIDO: Zero byte file (empty): Path is: {0}\n".format(filename))
            bofbuffer, eofbuffer = self.get_buffers(f, size, seekable=True)
            matches = self.match_formats(bofbuffer, eofbuffer)               
            # from here is also repeated in walk_zip
            # we should make this uniform in a next version!
            #
            # filesize is made conditional because files with 0 bytes
            # are falsely characterised being 'rtf' (due to wacky sig)
            # in these cases we try to match the extension instead
            if len(matches) > 0 and self.current_filesize > 0:
                self.handle_matches(filename, matches, time.clock() - t0, self.matchtype)
            elif len(matches) == 0 or self.current_filesize == 0:
                matches = self.match_extensions(filename)
                self.handle_matches(filename, matches, time.clock() - t0, "extension")
            # till here matey!
            if self.zip:
                self.identify_contents(filename, type=self.container_type(matches))
        except IOError:
            #print >> sys.stderr, "FIDO: Error in identify_file: Path is {0}".format(filename)
            sys.stderr.write("FIDO: Error in identify_file: Path is {0}\n".format(filename))

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
        else: # TODO: ouch!
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
            # MdR: this needs attention
            if len(matches) > 0:
                self.handle_matches(self.current_file, matches, time.clock() - t0, "signature")
            elif len(matches) == 0 or self.current_filesize == 0:
                matches = self.match_extensions(self.current_file)
                self.handle_matches(self.current_file, matches, time.clock() - t0, "extension")
                
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
        if len(matches) > 0:
            self.handle_matches(self.current_file, matches, time.clock() - t0, "signature")
        elif len(matches) == 0 or self.current_filesize == 0:
            # we can only determine the filename from the STDIN stream
            # on Linux, on Windows there is not a (simple) way to do that
            if (os.name != "nt"):
                try:
                    self.current_file = os.readlink("/proc/self/fd/0")
                except:
                    if filename is not None:
                        self.current_file = filename
                    else:
                        self.current_file = 'STDIN'
            else:
                if filename is not None:
                    self.current_file = filename
            matches = self.match_extensions(self.current_file)
            # we have to reset self.current_file if not on Windows
            if (os.name != "nt"):
                self.current_file = 'STDIN'
            self.handle_matches(self.current_file, matches, time.clock() - t0, "extension")
                    
    def container_type(self, matches):
        """Determine if one of the @param matches is the format of a container that we can look inside of (e.g., zip, tar).
           @return False, zip, or tar.
        """
        for (format, unused) in matches:
            container = format.find('container')
            if container != None:
                return container.text
        return False
    
    def blocking_read(self, file, bytes_to_read):
        bytes_read = 0
        buffer = ''
        while bytes_read < bytes_to_read:
            readbuffer = file.read(bytes_to_read - bytes_read)
            buffer += readbuffer
            bytes_read = len(buffer)
            # break out if EOF is reached.
            if readbuffer == '':
                break
        return buffer
                                  
    def get_buffers(self, stream, length=None, seekable=False):
        """Return buffers from the beginning and end of stream and the number of bytes read
           if there may be more bytes in the stream.  
        
           If length is None, return the length as found. 
           If seekable is False, the steam does not support a seek operation.
        """
        bytes_to_read = self.bufsize if length == None else min(length, self.bufsize)
        bofbuffer = self.blocking_read(stream, bytes_to_read)
        bytes_read = len(bofbuffer)
        if length == None:
            # A stream with unknown length; have to keep two buffers around
            prevbuffer = bofbuffer
            while True:
                buffer = self.blocking_read(stream, self.bufsize)
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
                eofbuffer = bofbuffer[bytes_unread:] + self.blocking_read(stream, bytes_unread)
            elif bytes_unread == self.bufsize:
                eofbuffer = self.blocking_read(stream, self.bufsize)
            elif seekable:  # easy case when we can just seek!
                stream.seek(length - self.bufsize)
                eofbuffer = self.blocking_read(stream, self.bufsize)
            else:
                # We have more to read and know how much.    
                # n*bufsize + r = length
                (n, r) = divmod(bytes_unread, self.bufsize)
                # skip n-1*bufsize bytes
                for unused_i in xrange(1, n):
                    self.blocking_read(stream, self.bufsize)
                # skip r bytes
                self.blocking_read(stream, r)
                # and read the remaining bufsize bytes into the eofbuffer
                eofbuffer = self.blocking_read(stream, self.bufsize)
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
            zipstream = zipfile.ZipFile((fileobj if fileobj != None else filename), 'r')    
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
                    if self.current_filesize == 0:
                        sys.stderr.write("FIDO: Zero byte file (empty): Path is: {0}\n".format(item_name))
                    bofbuffer, eofbuffer = self.get_buffers(f, item.file_size)
                finally:
                    if f != None: f.close()
                matches = self.match_formats(bofbuffer, eofbuffer)
                if len(matches) > 0 and self.current_filesize > 0:
                    self.handle_matches(item_name, matches, time.clock() - t0, "signature")
                elif len(matches) == 0 or self.current_filesize == 0:
                    matches = self.match_extensions(item_name)
                    self.handle_matches(item_name, matches, time.clock() - t0, "extension")
                if self.container_type(matches):
                        target = tempfile.SpooledTemporaryFile(prefix='Fido')
                        #with zipstream.open(item) as source:
                        try:
                            source = zipstream.open(item)
                            self.copy_stream(source, target)
                            #target.seek(0)
                            self.identify_contents(item_name, target, self.container_type(matches))
                        finally:
                            source.close()
        except IOError:
            sys.stderr.write("FIDO: ZipError {0}\n".format(filename))
        except zipfile.BadZipfile:
            sys.stderr.write("FIDO: ZipError {0}\n".format(filename))
            
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
                sys.stderr.write("FIDO: Error: TarError {0}\n".format(filename))
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
    
    def buffered_read(self, file_pos, overlap):
        """Buffered read of data chunks
        """
        buf = ""
        if not overlap:
            bufsize = self.container_bufsize
        else:
            bufsize = self.container_bufsize + self.overlap_range
        file_end = self.current_filesize
        file_handle = file(self.current_file, 'rb')
        file_handle.seek(file_pos)
        if file_end - file_pos < bufsize:
            file_read = file_end - file_pos
        else:
            file_read = self.bufsize
        buf = file_handle.read(file_read)
        return buf

    def read_container(self,parent_buffer,parent_result):
        """Header of compound containers can be further away than default 128 KB buffer 
           especially with big files containing binary objects.
           This function reads containers in chunks of 512 KB (defaults['container_bufsize'])
           Each chunk is inspected with the PRONOM container sequences.
           Each chunk smuggles in a piece from the previous chunk to prevent 
           cutting off patterns we are looking for in the middle.
           This method is somewhat slower than reading the complete file at once.
           This is to prevent Fido to potentially crash in the midst of scanning a very big file.
           NOTE (MdR): this piece of code is still a bit quirky
           as it does not yet takes byte positions into account which
           are available in the DROID container signature file
        """
        container_result = []
        nobuffer = False
        overlap = False
        self.overlap_range = 512 # bytes
        container_hit = False
        passes = 1
        container_buffer = ""
        # TODO: find better way to handle zip contents
        # for now: ugly hack, but working
        # this slows down because the zip is re-opened on each item
        # if "!" is in filename, it is a zip item
#        if "!" in self.current_file:
#            import zipfile, tempfile
#            zip, item = self.current_file.split("!")
#            zipitem = tempfile.SpooledTemporaryFile(prefix='Fido')
            #with zipstream.open(item) as source:
#            try:
#                source = zipstream.open(item)
#                self.copy_stream(source, target)
#                target.seek(0)
#                self.identify_contents(item_name, target, self.container_type(matches))
#            finally:
#                source.close()
        #exit()
        # in case argument 'nocontainer' is set
        # read default bofbuffer
        if self.nocontainer or self.current_filesize <= self.bufsize or self.current_file == "STDIN":
            passes = 1
            nobuffer = True
        else:
            passes = int(float(self.current_filesize / self.container_bufsize) + 1)
        pos = 0
        for i in xrange(passes):
            if nobuffer is True:
                container_buffer = parent_buffer
            else:
                if i == 0:
                    pos = 0
                else:
                    pos = ((self.container_bufsize * i) - self.overlap_range)
                    overlap = True
                container_buffer = self.buffered_read(pos, overlap)
            for (container_id,container_regexes) in self.sequenceSignature.iteritems():
                # set hitcounter in case a container entry
                # has more than one regex
                hitcounter = 0
                if len(container_regexes) > 0:
                    for container_regex in container_regexes:
                        if re.search(container_regex, container_buffer):
                            hitcounter += 1
                            # if the hitcounter matches the number of regexes
                            # then it must be a positive hit, else continue
                            # to match the rest of the sequences
                            if hitcounter < len(container_regexes):
                                continue
                            self.matchtype = "container"
                            for container_puid in self.puidMapping[container_id]:
                                for container_format in self.formats:
                                    if container_format.find('puid').text == container_puid:
                                        if self.as_good_as_any(container_format, parent_result):
                                            for container_sig in self.get_signatures(container_format):
                                                container_result.append((container_format, container_sig))
                                            break
        return container_result

    def match_formats(self, bofbuffer, eofbuffer):
        """Apply the patterns for formats to the supplied buffers.
           @return a match list of (format, signature) tuples. 
           The list has inferior matches removed.
        """
        self.current_count += 1
        #t0 = time.clock()
        result = []
        container_result = []
        for format in self.formats:
            try:
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
                            elif pos == 'IFB':
                                if not re.search(regex, bofbuffer):
                                    success = False 
                                    break
                        if success:
                            result.append((format, sig))
                            # check if file needs to be parsed with container signature
                            # we skip files with extension "zip" (x-fmt/263)
                            ext = os.path.splitext(self.current_file)[1].lower().lstrip(".")
                            if format.find('puid').text in self.puidTriggers and ext != "zip":
                                container_result = self.read_container(bofbuffer,result)
                                if len(container_result) != 0:
                                    for (k,v) in container_result:
                                        result.append((k,v))
                            break
            except Exception as e:
                sys.stderr.write(str(e)+"\n")
                continue
            # TODO: MdR: needs some <3
            #print "Unexpected error:", sys.exc_info()[0], e
            #sys.stdout.write('***', self.get_puid(format), regex)
            
        #        t1 = time.clock()
        #        if t1 - t0 > 0.02:
        #            print >> sys.stderr, "FIDO: Slow ID", self.current_file
        result = [match for match in result if self.as_good_as_any(match[0], result)]
        result = list(set(result)) # remove duplicate results, this is due to ??? in self.read_container(), needs fix
        return result
    
    def match_extensions(self, filename):
        "Return the list of (format, self.externalsig) for every format whose extension matches the filename."
        myext = os.path.splitext(filename)[1].lower().lstrip(".")
        result = []
        if len(myext) > 0:
            for element in self.formats:
                if element.findall('extension') != None:
                    for format in element.findall('extension'):
                        if myext == format.text:
                            result.append((element, self.externalsig))
                            break
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
    from argparselocal import ArgumentParser, RawTextHelpFormatter    
    if arglist == None:
        arglist = sys.argv[1:]
    if len(arglist) == False:
        arglist.append("-h")        
    parser = ArgumentParser(description=defaults['description'], epilog=defaults['epilog'], fromfile_prefix_chars='@', formatter_class=RawTextHelpFormatter)
    parser.add_argument('-v', default=False, action='store_true', help='show version information')
    parser.add_argument('-q', default=False, action='store_true', help='run (more) quietly')
    parser.add_argument('-recurse', default=False, action='store_true', help='recurse into subdirectories')
    parser.add_argument('-zip', default=False, action='store_true', help='recurse into zip and tar files')
    parser.add_argument('-nocontainer', default=False, action='store_true', help='disable deep scan of container documents, increases speed but may reduce accuracy with big files')
    parser.add_argument('-pronom_only', default=False, action='store_true', help='disables loading of format extensions file, only PRONOM signatures are loaded, may reduce accuracy of results')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-input', default=False, help='file containing a list of files to check, one per line. - means stdin')
    group.add_argument('files', nargs='*', default=[], metavar='FILE', help='files to check. If the file is -, then read content from stdin. In this case, python must be invoked with -u or it may convert the line terminators.')
    parser.add_argument('-filename', default=None, help='filename if file contents passed through STDIN')
    parser.add_argument('-useformats', metavar='INCLUDEPUIDS', default=None, help='comma separated string of formats to use in identification')
    parser.add_argument('-nouseformats', metavar='EXCLUDEPUIDS', default=None, help='comma separated string of formats not to use in identification')
    parser.add_argument('-matchprintf', metavar='FORMATSTRING', default=None, help='format string (Python style) to use on match. See nomatchprintf, README.txt.')
    parser.add_argument('-nomatchprintf', metavar='FORMATSTRING', default=None, help='format string (Python style) to use if no match. See README.txt')
    parser.add_argument('-bufsize', type=int, default=None, help='size (in bytes) of the buffer to match against (default='+str(defaults['bufsize'])+' bytes)')
    parser.add_argument('-container_bufsize', type=int, default=None, help='size (in bytes) of the buffer to match against (default='+str(defaults['container_bufsize'])+' bytes)')
    
    parser.add_argument('-loadformats', default=None, metavar='XML1,...,XMLn', help='comma separated string of XML format files to add.')
    parser.add_argument('-confdir', default=None, help='configuration directory to load_fido_xml, for example, the format specifications from.')
    
    # what is this doing here only once?   
    #mydir = os.path.abspath(os.path.dirname(__file__))

    # PROCESS ARGUMENTS
    args = parser.parse_args(arglist)
#    print args
#    sys.exit()
    # process confdir
    # load versions.xml
    # and stick it in defaults
    if args.confdir:
        versionsFile = os.path.join(os.path.abspath(args.confdir), defaults['versions_file'])
    else:
        versionsFile = os.path.join(os.path.abspath(defaults['conf_dir']), defaults['versions_file'])
    try:
        versions = VET.parse(versionsFile)
    except Exception, e:
        sys.stderr.write("An error occured loading versions.xml:\n{0}".format(e))
        sys.exit()
    defaults['xml_pronomSignature'] = versions.find("pronomSignature").text
#    defaults['xml_pronomContainerSignature'] = versions.find("pronomContainerSignature").text
    defaults['containersignature_file'] = versions.find("pronomContainerSignature").text
    defaults['xml_fidoExtensionSignature'] = versions.find("fidoExtensionSignature").text
    defaults['format_files'] = []
    defaults['format_files'].append(defaults['xml_pronomSignature'])
    if args.pronom_only:
        versionHeader = "FIDO v{0} ({1}, {2})\n".format(version,defaults['xml_pronomSignature'],defaults['containersignature_file'])
    else:
        versionHeader = "FIDO v{0} ({1}, {2}, {3})\n".format(version,defaults['xml_pronomSignature'],defaults['containersignature_file'],defaults['xml_fidoExtensionSignature'])
        defaults['format_files'].append(defaults['xml_fidoExtensionSignature'])
    
    if args.v :
        sys.stdout.write(versionHeader)
        sys.exit(0)
    if args.matchprintf != None:
        args.matchprintf = args.matchprintf.decode('string_escape')
    if args.nomatchprintf != None:
        args.nomatchprintf = args.nomatchprintf.decode('string_escape')
    fido = Fido(quiet=args.q, bufsize=args.bufsize, container_bufsize=args.container_bufsize,
                printmatch=args.matchprintf, printnomatch=args.nomatchprintf, zip=args.zip, nocontainer = args.nocontainer, conf_dir=args.confdir)
    
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
        fido.formats = [f for f in fido.formats if f.find('puid').text not in args.nouseformats]
 
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
            if fido.zip == True:
                raise RuntimeError("Multiple content read from stdin not yet supported.")
                sys.exit(1)
                fido.identify_multi_object_stream(sys.stdin)
            else:
                fido.identify_stream(sys.stdin, args.filename)
        else:
            for file in list_files(args.files, args.recurse):
                fido.identify_file(file)
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
