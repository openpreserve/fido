#!python

import sys, re, os, time
from xml.etree import cElementTree as ET
config_dir = os.path.realpath(sys.path[0]) #os.path.dirname(__file__)
version = '0.9.2'
defaults = {'bufsize': 32 * 4096,
            'regexcachesize' : 2084,
            'printmatch': "OK,{info.time},{info.puid},{info.formatname},{info.signaturename},{info.filesize},\"{info.filename}\"\n",
            'printnomatch' : "KO,{info.time},,,,{info.filesize},\"{info.filename}\"\n",
            'format_files': [os.path.join(config_dir, 'conf', 'formats.xml'),
                             os.path.join(config_dir, 'conf', 'format_extensions.xml')],
            'description' : """
    Format Identification for Digital Objects (fido).
    FIDO is a command-line tool to identify the file formats of digital objects.
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

class memoized(object):
    """Decorator that caches a function's return value each time it is called.
       If called later with the same arguments, the cached value is returned, and
       not re-evaluated.
       Usage: @memoize before def of thing.
       function = memoized(function)
       """
    def __init__(self, func):
        self.func = func
        self.cache = {}
    def __call__(self, *args):
        try:
            return self.cache[args]
        except KeyError:
            value = self.func(*args)
            self.cache[args] = value
            return value
        except TypeError:
        # uncachable -- for instance, passing a list as an argument.
        # Better to not cache than to blow up entirely.
            return self.func(*args)
    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__
    #    def __get__(self, obj, objtype):
    #        """Support instance methods."""
    #        return functools.partial(self.__call__, obj)


class Fido:
    def __init__(self, quiet=False, bufsize=None, printnomatch=None, printmatch=None,
                 extension=False, zip=False, handle_matches=None, format_files=None):
        global defaults
        self.quiet = quiet
        self.bufsize = (defaults['bufsize'] if bufsize == None else bufsize)
        self.printmatch = (defaults['printmatch'] if printmatch == None else printmatch)
        self.printnomatch = (defaults['printnomatch'] if printnomatch == None else printnomatch)
        self.handle_matches = (self.print_matches if handle_matches == None else handle_matches)
        self.zip = zip
        self.extension = extension
        self.format_files = defaults['format_files'] if format_files == None else format_files
        self.formats = []
        self.puid_format_map = {}
        for file in self.format_files:
            self.load(file)
        self.current_file = ''
        self.current_filesize = 0
        self.current_format = None
        self.current_sig = None
        self.current_pat = None
        self.current_count = 0  # Count of calls to match_formats
        re._MAXCACHE = defaults['regexcachesize']
        self.externalsig = ET.XML('<signature><name>External</name></signature>')

    def load(self, file):
        """Load the fido format information from @param file.
           As a side-effect, set self.formats
           @return list of ElementTree.Element, one for each format.
        """
        tree = ET.parse(file)
        root = tree.getroot()
        for element in root.getiterator():
            if element.text == None:
                pass
            else:
                if element.tag == 'regex':
                    #print element.text
                    element.text = element.text.decode('string_escape')
                    # but if the end char is a backslash, we lost the whitespace in the strip.
                else:
                    element.text = element.text.strip()
        #print "Loaded format specs in {0:>6.2f}ms".format((t1 - t0) * 1000)
        for element in root.findall('format'):
            puid = element.find('puid').text
            existing = self.puid_format_map.get(puid, False) 
            if  existing:
                # Already have one, so delete it!
                self.formats[self.formats.index(existing)] = element
            else:
                self.formats.append(element)
            self.puid_format_map[puid] = element
        return self.formats
            
    def print_matches(self, fullname, matches, delta_t):
        """The default match handler.  Prints out information for each match in the list.
           @param fullname is name of the file being matched
           @param matches is a list of (format, signature)
           @param delta_t is the time taken for the match.
        """
        class Group:
            pass
        obj = Group()
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
                obj.puid = f.find('puid').text
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
                try:
                    f = None
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
        try:
            tarstream = None
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
        f1_puid = f1.find('puid').text
        for (f2, unused) in match_list:
            if f1 == f2:
                continue
            for puid_element in f2.findall('has_priority_over'):
                puid = puid_element.text
                if puid == f1_puid:
                    # f2 has priority over me, so we are not that good!
                    return False
        return True
    
    def match_formats(self, bofbuffer, eofbuffer):
        """Apply the patterns for formats to the supplied buffers.
           @return a match list of (format, signature) tuples. 
           The list has inferior matches removed.
        """
        cache = {}
        def memo(*args):
            try:
                return cache[args]
            except KeyError:
                value = args[0](*args[1:])
                cache[args] = value
                return value
        self.current_count += 1
        result = []
        for format in self.formats:
            self.current_format = format
            if self.as_good_as_any(format, result):
                for sig in format.findall('signature'):
                    #t0 = time.clock()
                    self.current_sig = sig
                    success = True
                    for pat in sig.findall('pattern'):
                        self.current_pat = pat
                        pos = pat.find('position').text
                        regex = pat.find('regex').text
                        #print 'trying ', regex
                        if pos == 'BOF':
                            if not memo(re.match, regex, bofbuffer):
                                success = False
                                break
                        elif pos == 'EOF':
                            if not memo(re.search, regex, eofbuffer):
                                success = False
                                break
                        elif pos == 'VAR':
                            if not memo(re.search, regex, bofbuffer):
                                success = False 
                                break
                    if success:
                        result.append((format, sig))
                        break
                    #                t1 = time.clock()
                    #                if t1 - t0 > 0.02:
                    #                    print >> sys.stderr, "FIDO: Slow Signature", self.current_file, format.find('puid').text, format.find('name').text, sig.find('name').text
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

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    from xml.dom import minidom
    rough_string = ET.tostring(elem, 'UTF-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
             
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
    from argparselocal import ArgumentParser  
    if arglist == None:
        arglist = sys.argv[1:]
        
    parser = ArgumentParser(description=defaults['description'], epilog=defaults['epilog'])
    parser.add_argument('-v', default=False, action='store_true', help='show version information')
    parser.add_argument('-q', default=False, action='store_true', help='run (more) quietly')
    parser.add_argument('-recurse', default=False, action='store_true', help='recurse into subdirectories')
    parser.add_argument('-zip', default=False, action='store_true', help='recurse into zip files')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-input', default=False, help='file containing a list of files to check, one per line. - means stdin')
    group.add_argument('files', nargs='*', default=[], metavar='FILE', help='files to check.  If the file is -, then read content from stdin. In this case, python must be invoked with -u or it may convert the line terminators.')
    parser.add_argument('-formats', metavar='PUIDS', default=None, help='comma separated string of formats to use in identification')
    parser.add_argument('-excludeformats', metavar='PUIDS', default=None, help='comma separated string of formats not to use in identification')
    parser.add_argument('-extension', default=False, action='store_true', help='use file extensions if the patterns fail.  May return many matches.')
    parser.add_argument('-matchprintf', metavar='FORMATSTRING', default=None, help='format string (Python style) to use on match. See nomatchprintf, README.txt.')
    parser.add_argument('-nomatchprintf', metavar='FORMATSTRING', default=None, help='format string (Python style) to use if no match. See README.txt')
    parser.add_argument('-bufsize', type=int, default=None, help='size of the buffer to match against')
    parser.add_argument('-show', default=False, help='show "format" or "defaults"')
    parser.add_argument('-xmlformats', default=None, metavar='XML1,...,XMLn', help='comma separated string of XML format specifications to add.')
        
    # PROCESS ARGUMENTS
    args = parser.parse_args(arglist)
    
    if args.v :
        print "fido/" + version
        exit(1)
    if args.show == 'defaults':
        for (k, v) in defaults.iteritems():
            print k, '=', repr(v)
        exit(1)
    if args.matchprintf != None:
        args.matchprintf = args.matchprintf.decode('string_escape')
    if args.nomatchprintf != None:
        args.nomatchprintf = args.nomatchprintf.decode('string_escape')
    t0 = time.clock()
    fido = Fido(quiet=args.q, bufsize=args.bufsize, extension=args.extension,
                printmatch=args.matchprintf, printnomatch=args.nomatchprintf, zip=args.zip)
    
    if args.xmlformats:
        for file in args.xmlformats.split(','):
            fido.load(file)
        
    if args.formats:
        args.formats = args.formats.split(',')
        fido.formats = [f for f in fido.formats if f.find('puid').text in args.formats]
    elif args.excludeformats:
        args.excludeformats = args.excludeformats.split(',')
        fido.formats = [f for f in fido.formats if f.find('puid') not in args.excludeformats]
    
    if args.show == 'formats':
        for format in fido.formats:
            print prettify(format)
        exit(1)
        
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
    #main(['-r', '-z', r'e:/Code/fidotests/corpus/nested1.zip', r'e:/Code/fidotests/corpus/test.tar'])
    main()
    
