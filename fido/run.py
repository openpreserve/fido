#!python
#TODO: Yield matches deltaT
#Caller can do print_matches and use the current_ info from fido.
#Make printmatch take named arguments
import sys, re, os, time
import signature, formats
    
version = '0.8.0'
defaults = {'bufsize': 32 * 4096,
            'regexcachesize' : 1024,
            'printmatch': "OK,{info.time},{format.Identifier},{format.FormatName},{sig.SignatureName},{info.size},\"{info.name}\"\n",
            'printnomatch' : "KO,{info.time},,,,{info.size},\"{info.name}\"\n",
            'description' : """
    Format Identification for Digital Objects (fido).
    FIDO is a command-line tool to identify the file formats of digital objects.
    It is designed for simple integration into automated work-flows.
    """,
    'epilog' : """
    Open Planets Foundation (www.openplanetsfoundation.org)
    See License.txt for license information.  Download from: http://github.com/openplanets/fido
    Author: Adam Farquhar, 2010
        
    FIDO uses the UK National Archives (TNA) PRONOM File Format descriptions.
    PRONOM is available from www.tna.gov.uk/pronom.
    """
}

class Fido:
    def __init__(self, quiet=False, bufsize=None, printnomatch=None, printmatch=None, extension=False, zip=False, match_handler=None):
        global defaults
        self.quiet = quiet
        self.bufsize = (defaults['bufsize'] if bufsize == None else bufsize)
        self.printmatch = (defaults['printmatch'] if printmatch == None else printmatch)
        self.printnomatch = (defaults['printnomatch'] if printnomatch == None else printnomatch)
        self.match_handler = (self.print_matches if match_handler == None else match_handler)
        self.zip = zip
        self.extension = extension
        self.formats = formats.all_formats[:]
        self.current_file = ''
        self.current_filesize = 0
        self.current_format = None
        self.current_sig = None
        self.current_pat = None
        self.current_count = 0  # Count of calls to match_formats
        re._MAXCACHE = defaults['regexcachesize']
        self.externalsig = signature.InternalSignature(SignatureID=u'-1', SignatureName=u'FILE EXTENSION', bytesequences=[])

    def print_matches(self, fullname, matches, delta_t):
        class Group:
            pass
        obj = Group()
        obj.count = len(matches)
        obj.name = fullname
        obj.time = int(delta_t * 1000)
        obj.size = self.current_filesize
        if obj.count == 0:
            sys.stdout.write(self.printnomatch.format(info=obj))
        else:
            for (f, s) in matches:
                sys.stdout.write(self.printmatch.format(info=obj, format=f, sig=s))
        
    def print_summary(self, secs):
        count = self.current_count
        if not self.quiet:
            rate = (int(count / secs) if secs != 0 else 9999)
            print >> sys.stderr, "FIDO: Processed {0:>6d} files in {1:>6.2f} msec, {2:d} files/sec".format(count, secs * 1000, rate)
                                         
    def identify_file(self, filename):
        "Yield (effective_name, matches, delta_t).  Perhaps look at its contents if it is a zip file."
        self.current_file = filename
        try:
            t0 = time.clock()
            with open(filename, 'rb') as f:
                size = os.stat(filename)[6]
                self.current_filesize = size
                bofbuffer = f.read(self.bufsize)
                eofbuffer = self.eof_buffer(f, bofbuffer, size, seek=True)
            matches = self.match_formats(bofbuffer, eofbuffer)
            self.match_handler(filename, matches, time.clock() - t0)
            if self.extension and len(matches) == 0:
                matches = self.match_extensions(filename)
                self.match_handler(filename, matches, time.clock() - t0)
            if self.zip:
                self.identify_contents(filename, type=self.container_type(matches))
        except IOError:
            print >> sys.stderr, "FIDO: Error in identify_file: Path is {0}".format(filename)
        
    def identify_multi_object_stream(self, stream):
        """Stream may contain one or more objects each with an HTTP style header that must include content-length.
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
            nbytes = min(self.bufsize, content_length)
            bofbuffer = stream.read(nbytes)
            eofbuffer = self.eof_buffer(stream, bofbuffer, content_length)
            self.current_filesize = content_length
            matches = self.match_formats(bofbuffer, eofbuffer)
            self.match_handler(self.current_file, matches, time.clock() - t0)
                
    def identify_stream(self, stream):
        """Name is the name to use when providing results. 
           Stream is a file-like object, but it may only support the read(nbytes) method, not seek. 
           Returns the list of matches.  Does not close the stream."""
        t0 = time.clock()
        bofbuffer = stream.read(self.bufsize)
        (eofbuffer, bytes_read) = self.eof_buffer(stream, bofbuffer, length=None)
        self.current_filesize = bytes_read
        self.current_file = 'STDIN'
        matches = self.match_formats(bofbuffer, eofbuffer)
        self.match_handler(self.current_file, matches, time.clock() - t0)
                    
    def container_type(self, matches):
        "Return True if one of the matches is a zip file (x-fmt/263)."
        for m in matches:
            if m[0].Identifier == 'x-fmt/263':
                return 'zip'
            if m[0].Identifier == 'x-fmt/265':
                return 'tar'
        return False
                        
    def identify_contents(self, filename, fileobj=None, type=False):
        "Output the format identifications for the contents of a zip or tar file."
        if type == False:
            return
        elif type == 'zip':
            self.walk_zip(filename, fileobj)
        elif type == 'tar':
            self.walk_tar(filename, fileobj)
        else:
            raise RuntimeError("Unknown container type: " + repr(type))
        
    def eof_buffer(self, stream, bofbuffer, length=None, seek=False):
        "Return the EOF Buffer and len if it was None where EOF is at length-len(bofbuffer) bytes down.  If length is None, return the length as found."
        bytes_read = 0
        if length == None:
            # A stream with unknown length; have to keep two buffers around
            prevbuffer = bofbuffer
            while True:
                buffer = stream.read(self.bufsize)
                bytes_read += len(buffer)
                if len(buffer) == self.bufsize:
                    prevbuffer = buffer
                else:
                    eofbuffer = prevbuffer[-(self.bufsize - len(buffer)):] + buffer
                    break
        else:
            bytes_unread = length - len(bofbuffer)
            if bytes_unread == 0:
                eofbuffer = bofbuffer
            elif bytes_unread < self.bufsize:
                # The buffs overlap
                eofbuffer = bofbuffer[bytes_unread:] + stream.read(bytes_unread)
            elif bytes_unread == self.bufsize:
                eofbuffer = stream.read(self.bufsize)
            elif seek:  # easy case when we can just seek!
                stream.seek(length - self.bufsize)
                eofbuffer = stream.read(self.bufsize)
            else:
                # we have more to read and know how much.    
                # Need to read file_size%bufsize-1 buffers, 
                # then the remainder, then we have a full left.
                (n, r) = divmod(bytes_unread, self.bufsize)
                # skip n-2 buffers
                for unused_i in xrange(1, n):
                    stream.read(self.bufsize)
                # skip the remainder, r
                stream.read(r)
                # and grab the n
                eofbuffer = stream.read(self.bufsize)
        if length == None:
            return eofbuffer, bytes_read + len(bofbuffer)
        else:
            return eofbuffer
    
    def walk_zip(self, filename, fileobj=None):
        "Output the format identifications for the contents of a zip file."
        # IN 2.7+: with zipfile.ZipFile((fileobj if fileobj != None else filename), 'r') as stream:
        import zipfile, tempfile
        try:
            zipstream = zipfile.ZipFile((fileobj if fileobj != None else filename))    
            for item in zipstream.infolist():
                if item.file_size == 0:
                    continue           #TODO: Find a better test for isdir
                t0 = time.clock()
                # with zipstream.open(item) as f:
                try:
                    f = zipstream.open(item)
                    item_name = filename + '!' + item.filename
                    self.current_file = item_name
                    self.current_filesize = item.file_size
                    bofbuffer = f.read(self.bufsize)
                    eofbuffer = self.eof_buffer(f, bofbuffer, item.file_size)
                finally:
                    f.close()
                matches = self.match_formats(bofbuffer, eofbuffer)
                self.match_handler(item_name, matches, time.clock() - t0)
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
        finally:
            zipstream.close()

    def walk_tar(self, filename, fileobj):
        "Output the format identification for the contents of a tar file."
        import tarfile
        try:
            tarstream = tarfile.TarFile(filename, fileobj=fileobj, mode='r')
            for item in tarstream.getmembers():
                if item.isfile():
                    t0 = time.clock()
                    f = tarstream.extractfile(item)
                    tar_item_name = filename + '!' + item.name
                    self.current_file = tar_item_name
                    self.current_filesize = item.size
                    bofbuffer = f.read(self.bufsize)
                    eofbuffer = self.eof_buffer(f, bofbuffer, item.size)
                    matches = self.match_formats(bofbuffer, eofbuffer)
                    self.match_handler(tar_item_name, matches, time.clock() - t0)
                    if self.container_type(matches):
                        f.seek(0)
                        self.identify_contents(tar_item_name, f, self.container_type(matches))
                        f.close()
        except tarfile.TarError:
                print >> sys.stderr, "FIDO: Error: TarError {0}".format(filename)
        finally:
            tarstream.close()

    def as_good_as_any(self, f1, match_list):
        """Return True if the proposed format is as good as any in the match_list.
        For example, if there is no format in the match_list that has priority over the proposed one"""
        for (f2, unused) in match_list:
            if f1 == f2:
                continue
            for (rel, fID) in getattr(f2, u'relatedformat', []):
                if rel == u'Has priority over' and fID == f1.FormatID:
                    #print (f2.FormatID, f2.Identifier, f2.FormatName), 'is better than', (f1.FormatID, f1.Identifier, f1.FormatName)
                    # Then f2 is better, so f1 is worse
                    return False
        return True
        
    def match_formats(self, bofbuffer, eofbuffer):
        """Apply the patterns for formats to the supplied buffers.
        Return a match list of (format, signature) tuples. The list has inferior matches removed."""
        self.current_count += 1
        result = []
        for format in self.formats:
            self.current_format = format
            # we can prune out formats that are worse than the current match, but for every 3, well test 300, so it has to be efficient. 
            if self.as_good_as_any(format, result):
                sig = self.match_signatures(format, bofbuffer, eofbuffer)
                if sig != None:
                    result.append((format, sig))
        # Remove any inferior formats
        # This is very inefficient, but doesn't happen often
        # So far, I've seen max 7, a couple of 4, 2, almost all 0 or 1 matches
        # There are few better-than me, and more worse-than me relations
        result = [match for match in result if self.as_good_as_any(match[0], result)]
        return result
    
    def match_extensions(self, filename):
        "Return the list of (format, externalsig) for every format whose extension matches the filename."
        myext = os.path.splitext(filename)[1].lower()
        result = []
        if len(myext) > 0:
            for format in self.formats:
                self.current_format = format
                if myext in format.extensions:
                    result.append((format, self.externalsig))
        result = [match for match in result if self.as_good_as_any(match[0], result)]
        return result
                    
    def match_signatures(self, format, bofbuffer, eofbuffer):
        "Return the first of Format's signatures to match against the buffers or None."
        result = None  
        for s in format.signatures:
            self.current_sig = s
            if self.match_patterns(s, bofbuffer, eofbuffer):
                # only need one match for each format
                return s          
    
    def match_patterns(self, sig, bofbuffer, eofbuffer):
        "Return the True if this signature matches the buffers or False."
        for b in sig.bytesequences:
            self.current_pat = b
            t_beg = time.clock()
            if b.FidoPosition == 'BOF':
                if not re.match(b.regexstring, bofbuffer):
                    return False
            elif b.FidoPosition == 'EOF':
                if not re.search(b.regexstring, eofbuffer):
                    return False
            elif b.FidoPosition == 'VAR':
                #FIXME: Perhaps this should apply to both buffers?
                if not re.search(b.regexstring, bofbuffer):
                    return False
            else:
                raise Exception("bad positionType")
            t_end = time.clock()
            if not self.quiet and t_end - t_beg > 0.05:
                print >> sys.stderr, "FIDO: Slow Signature {0:>6.2f}s: {3.current_format.Identifier} SigID={1.SignatureID} PatID={2.ByteSequenceID} {1.SignatureName}\n  File:{3.current_file}\n  Regex:{2.regexstring!r}".format(t_end - t_beg, sig, b, self)
        # Should fall through to here if everything matched
        return True
    
    def copy_stream(self, source, target):
        while True:
            buf = source.read(self.bufsize)
            if len(buf) == 0:
                break
            target.write(buf)
            
def show_formats(format_list):
    "Write out a CSV file if information about all of the current formats, signatures, and byte sequences"
    #print'#Identifier,FormatName,MimeType,MimeType'
    for f in sorted(format_list, key=lambda x: x.Identifier):
        mimetypes = ",".join(getattr(f, 'MimeType', ['None']))
        print "{0},\"{1}\",{2!s}".format(f.Identifier, f.FormatName, mimetypes)
        for s in f.signatures:
            print ",,,{0.SignatureID},{0.SignatureName}".format(s)
            for b in s.bytesequences:
                print ",,,,,{b.ByteSequenceID},{b.FidoPosition},{b.Offset},{b.MaxOffset},{b.regexstring!r},{b.ByteSequenceValue}".format(b=b)    
   
def list_files(roots, recurse=False):
    "Return the files one at a time.  Roots could be a fileobj or a list."
    for root in roots:
        root = (root if root[-1] != '\n' else root[:-1])
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
    try:
        from argparse import ArgumentParser
    except ImportError:
        # Were in Python2.6 land
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
    parser.add_argument('-matchprintf', metavar='FORMATSTRING', default=None, help='format string (Python style) to use on match. See nomatchprintf.  You also have access to info.count, the number of matches; format; and sig.')
    parser.add_argument('-nomatchprintf', metavar='FORMATSTRING', default=None, help='format string (Python style) to use if no match. You have access to info with attributes name, size, time.')
    parser.add_argument('-bufsize', type=int, default=None, help='size of the buffer to match against')
    parser.add_argument('-show', default=False, help='show "format" or "defaults"')
        
    # PROCESS ARGUMENTS
    args = parser.parse_args(arglist)
    if args.v :
        print "fido/" + version
        exit(1)
    if args.show == 'defaults':
        for (k, v) in defaults.iteritems():
            print k, '=', repr(v)
        exit(1)
    
    t0 = time.clock()
    fido = Fido(quiet=args.q, bufsize=args.bufsize, extension=args.extension,
                printmatch=args.matchprintf, printnomatch=args.nomatchprintf, zip=args.zip)
       
    if args.formats:
        args.formats = args.formats.split(',')
        fido.formats = [f for f in fido.formats if f.Identifier in args.formats]
    elif args.excludeformats:
        args.excludeformats = args.excludeformats.split(',')
        fido.formats = [f for f in fido.formats if f.Identifier not in args.excludeformats]
    
    if args.show == 'formats':
        show_formats(fido.formats)
        exit(1)
        
    if args.input == '-':
        args.files = sys.stdin
    elif args.input:
        args.files = open(args.input, 'r')
    
    # RUN
    try:
        if (not args.input) and len(args.files) == 1 and args.files[0] == '-':
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
    
