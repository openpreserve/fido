#!python

import argparse, sys, re, os, time, signature
import formats
version = '0.6.4'
defaults = {'bufsize': 32 * 4096,
            'regexcachesize' : 1024,
            #OK/KO,msec,puid,format name,file size,file name            
            'printmatch': "OK,{1},{4.Identifier},{4.FormatName},{5.SignatureName},{2.current_filesize},\"{0}\"\n",
            'printnomatch' : "KO,{1},,,,{2.current_filesize},{0}\n",
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
    def __init__(self, quiet=False, bufsize=None, printnomatch=None, printmatch=None, extension=False, zip=False):
        global defaults
        self.quiet = quiet
        self.bufsize = (defaults['bufsize'] if bufsize == None else bufsize)
        self.printmatch = (defaults['printmatch'] if printmatch == None else printmatch)
        self.printnomatch = (defaults['printnomatch'] if printnomatch == None else printnomatch)
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

    def count_formats(self):
        "Return a tuple (num_formats, num_signatures, num_bytesequences)"
        count = [0, 0, 0]
        for f in self.formats:
            count[0] += 1
            for s in f.signatures:
                count[1] += 1
                count[2] += len(s.bytesequences)
        return count

    def print_matches(self, fullname, matches, start, end):
        count = len(matches)
        delta = int(1000 * (end - start))
        if count == 0:
            sys.stdout.write(self.printnomatch.format(fullname, delta, self))
        else:
            for (f, s) in matches:
                sys.stdout.write(self.printmatch.format(fullname, delta, self, count, f, s))
        
    def print_summary(self, secs):
        count = self.current_count
        if not self.quiet:
            print >> sys.stderr, "FIDO: Processed {:>6d} files in {:>6.2f} msec, {:d} files/sec".format(count, secs * 1000, int(count / secs))
    
    def run(self, generator):
        for filename in generator:
            self.identify_file(filename)
                                        
    def container_type(self, matches):
        "Return True if one of the matches is a zip file (x-fmt/263)."
        for m in matches:
            if m[0].Identifier == 'x-fmt/263':
                return 'zip'
            if m[0].Identifier == 'x-fmt/265':
                return 'tar'
        return False
    
    def identify_file(self, filename):
        "Output the format identifications for filename.  Perhaps look at its contents if it is a zip file."
        self.current_file = filename
        try:
            t0 = time.clock()
            self.current_file = filename
            with open(filename, 'rb') as f:
                size = os.stat(filename)[6]
                self.current_filesize = size
                bofbuffer = f.read(self.bufsize)
                if size > self.bufsize:
                    f.seek(-self.bufsize, 2)
                    eofbuffer = f.read(self.bufsize)
                else:
                    eofbuffer = bofbuffer
            matches = self.match_formats(bofbuffer, eofbuffer)
            if self.extension and len(matches) == 0:
                matches = self.match_extensions(filename)
            self.print_matches(filename, matches, start=t0, end=time.clock())
            if self.zip:
                self.identify_contents(filename, type=self.container_type(matches))
        except IOError as (errno, strerror):
            print >> sys.stderr, "FIDO: Error: I/O error ({0}): {1} Path is {2}".format(errno, strerror, filename)
        
    def identify_contents(self, filename, fileobj=None, type=False):
        if type == False:
            return
        import zipfile, tarfile
        if type == 'zip':
            with zipfile.ZipFile((fileobj if fileobj != None else filename), 'r') as stream:
                self.walk_zip(filename, stream)
        elif type == 'tar':
            try:
                stream = tarfile.TarFile(filename, fileobj=fileobj, mode='r')
                self.walk_tar(filename, stream)
            except tarfile.TarError:
                print >> sys.stderr, "FIDO: Error: TarError {0}".format(filename)
            finally:
                stream.close()
        else:
            raise RuntimeError("Unknown container type: " + repr(type))    
        
    def walk_zip(self, zipfilename, zipstream):
        import tempfile
        for item in zipstream.infolist():
            if item.file_size == 0:
                #TODO: Find a correct test for zip items that are just directories
                continue
            t0 = time.clock()
            with zipstream.open(item) as f:
                zip_item_name = zipfilename + '!' + item.filename
                self.current_file = zip_item_name
                self.current_filesize = item.file_size
                bofbuffer = f.read(self.bufsize)
                if item.file_size > self.bufsize:
                    # Need to read file_size%bufsize-1 buffers, 
                    # then the remainder, then we have a full left.
                    (n, r) = divmod(item.file_size, self.bufsize)
                    for unused_i in range(1, n - 1):
                        f.read(self.bufsize)
                    f.read(r)
                    eofbuffer = f.read(self.bufsize)
                else:
                    eofbuffer = bofbuffer
            matches = self.match_formats(bofbuffer, eofbuffer)
            self.print_matches(zip_item_name, matches, start=t0, end=time.clock())
            if self.container_type(matches):
                with tempfile.SpooledTemporaryFile(prefix='Fido') as target:
                    with zipstream.open(item) as source:
                        self.copy_stream(source, target)
                        #target.seek(0)
                        self.identify_contents(zip_item_name, target, self.container_type(matches))

    def walk_tar(self, tarfilename, tarstream=None):
        for item in tarstream.getmembers():
            if item.isfile():
                t0 = time.clock()
                f = tarstream.extractfile(item)
                tar_item_name = tarfilename + '!' + item.name
                self.current_file = tar_item_name
                self.current_filesize = item.size
                bofbuffer = f.read(self.bufsize)
                if item.size > self.bufsize:
                    f.seek(item.size - self.bufsize)
                    eofbuffer = f.read(self.bufsize)
                else:
                    eofbuffer = bofbuffer
                matches = self.match_formats(bofbuffer, eofbuffer)
                self.print_matches(tar_item_name, matches, start=t0, end=time.clock())
                if self.container_type(matches):
                    f.seek(0)
                    self.identify_contents(tar_item_name, f, self.container_type(matches))
                    f.close()
  
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
                result = s
                break
        return result          
    
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
    #print'#Identifier,FormatName,MimeType,MimeType'
    for f in sorted(format_list, key=lambda x: x.Identifier):
        mimetypes = ",".join(getattr(f, 'MimeType', ['None']))
        print "{0},\"{1}\",{2!s}".format(f.Identifier, f.FormatName, mimetypes)
        for s in f.signatures:
            print ",,,{0.SignatureID},{0.SignatureName}".format(s)
            for b in s.bytesequences:
                print ",,,,,{0.ByteSequenceID},{0.FidoPosition},{0.Offset},{0.MaxOffset},{0.regexstring!r},{0.ByteSequenceValue}".format(b)    

def dump_formats(format_list):
    "Write out the format definitions in csv as required for loading"
    import csv
    writer = csv.writer(sys.stdout, delimiter=',', quotechar='"')
    #writer.writeheader("FNAME,MIMETYPE,SNAME,BOFREGEX,VARREGEX,EOFREGEX".split())
    for f in format_list:
        for s in f.signatures:
            row = [f.FormatName, ';'.join(getattr(f, 'MimeType', [])), s.SignatureName]
            bof = ''
            eof = ''
            var = ''
            for b in s.bytesequences:
                if b.FidoPosition == 'BOF' and bof == '':
                    bof = repr(b.regexstring)[1:-1]
                if b.FidoPosition == 'EOF' and eof == '':
                    eof = repr(b.regexstring)[1:-1]
                if b.FidoPosition == 'VAR' and var == '':
                    var = repr(b.regexstring)[1:-1]
                row.append(bof)
                row.append(var)
                row.append(eof)
                writer.writerow(row)
        
def load_extensions(file):
    import csv
    #FNAME,MIMETYPE,SNAME,BOFREGEX,VARREGEX,EOFREGEX
    with open(file, 'rb') as stream:
        reader = csv.reader(stream, delimiter=',', quotechar='"')
        for unused_row in reader:
            pass
     
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
    if arglist == None:
        arglist = sys.argv[1:]
    parser = argparse.ArgumentParser(description=defaults['description'], epilog=defaults['epilog'])
    parser.add_argument('-v', default=False, action='store_true', help='show version information')
    parser.add_argument('-q', default=False, action='store_true', help='run (more) quietly')
    parser.add_argument('-bufsize', type=int, default=None, help='size of the buffer to match against')
    parser.add_argument('-recurse', default=False, action='store_true', help='recurse into subdirectories')
    parser.add_argument('-zip', default=False, action='store_true', help='recurse into zip files')
    parser.add_argument('-extension', default=False, action='store_true', help='use file extensions if the patterns fail.  May return many matches.')
    parser.add_argument('-matchprintf', metavar='FORMATSTRING', default=None, help='format string (Python style) to use on match. {0}=path, {1}=delta-t, {2}=fido, {3}=format, {4}=sig, {5}=count.')
    parser.add_argument('-nomatchprintf', metavar='FORMATSTRING', default=None, help='format string (Python style) to use if no match. {0}=path, {1}=delta-t, {2}=fido.')
    parser.add_argument('-formats', metavar='PUIDS', default=None, help='comma separated string of formats to use in identification')
    parser.add_argument('-excludeformats', metavar='PUIDS', default=None, help='comma separated string of formats not to use in identification')
    parser.add_argument('-show', default=False, help='show "format" or "defaults"')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-input', default=False, help='file containing a list of files to check, one per line. - means stdin')
    group.add_argument('files', nargs='*', default=[], metavar='FILE', help='files to check')
        
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
        fido.run(list_files(args.files, args.recurse))
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
    
