#!python

import argparse, sys, re, os, io, time, zipfile, tempfile
import formats
version = '0.6.0'
defaults = {'bufsize': 16 * io.DEFAULT_BUFFER_SIZE,
            #OK/KO,msec,puid,format name,file size,file name            
            'printmatch': "OK,{1},{4.Identifier},{4.FormatName},{2.current_filesize},\"{0}\"\n",
            'printnomatch' : "KO,{1},,,{2.current_filesize},{0}\n",
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
    def __init__(self, quiet=False, bufsize=None, printnomatch=None, printmatch=None):
        global defaults
        self.quiet = quiet
        self.bufsize = (defaults['bufsize'] if bufsize == None else bufsize)
        self.printmatch = (defaults['printmatch'] if printmatch == None else printmatch)
        self.printnomatch = (defaults['printnomatch'] if printnomatch == None else printnomatch)
        self.formats = formats.all_formats[:]
        self.current_file = ''
        self.current_filesize = 0
        self.current_format = None
        self.current_sig = None
        self.current_pat = None
        self.current_count = 0  # Count of calls to check_formats
        re._MAXCACHE = self.count_formats()[2] + re._MAXCACHE   # Make sure we have room for our patterns

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
        
    def print_times(self, attr, dict):
        for (k, v) in sorted(dict.items(), key=lambda x: x[1])[0:10]:
            print >> sys.stderr, "{:>6} {:>15} {:>6d}msec".format(dict['name'], getattr(k, attr)[0:15], int(v * 1000))
        
    def print_summary(self, secs):
        count = self.current_count
        if not self.quiet:
            print >> sys.stderr, "FIDO: Processed {:>6d} files in {:>6.2f} msec, {:d} files/sec".format(count, secs * 1000, int(count / secs))
                            
    def check(self, root, recurse=False, zip=False):
        "Output the format identifications for root.  Perhaps recurse or look into zip files."
        if os.path.isfile(root):
            self.check_file_or_zip(root, zip)
        else:
            for path, unused, files in os.walk(root):
                for f in files:
                    self.check_file_or_zip(os.path.join(path, f), zip)
                if recurse == False:
                    break

    def is_zip(self, matches):
        "Return True if one of the matches is a zip file (x-fmt/263)."
        return len(matches) == 1 and matches[0][0].Identifier == 'x-fmt/263'
    
    def check_file_or_zip(self, filename, zip=False):
        "Output the format identifications for filename.  Perhaps look at its contents if it is a zip file."
        self.current_file = filename
        t0 = self.time_check_file = time.clock()
        try:
            matches = self.check_file(filename)
            self.print_matches(filename, matches, start=t0, end=time.clock())
            if zip and self.is_zip(matches):
                self.check_zipfile(filename)
        except IOError as (errno, strerror):
            print >> sys.stderr, "FIDO: Error: I/O error ({0}): {1} Path is {2}".format(errno, strerror, filename)
        
    def check_zipfile(self, zipfilename, zipstream=None):
        if zipstream == None:
            with zipfile.ZipFile(zipfilename, 'r') as stream:
                self.check_zipfile(zipfilename, stream)
        else:
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
                matches = self.check_formats(bofbuffer, eofbuffer)
                self.print_matches(zip_item_name, matches, start=t0, end=time.clock())
                if self.is_zip(matches):
                    with tempfile.SpooledTemporaryFile(prefix='Fido') as target:
                        with zipstream.open(item) as source:
                            self.copy_stream(source, target)
                        with zipfile.ZipFile(target, 'r') as internal_zip:
                            self.check_zipfile(zip_item_name, internal_zip) 

    def check_file(self, file):
        "Return a list of matches for FILE."
        self.current_file = file
        with open(file, 'rb') as f:
            size = os.stat(file)[6]
            self.current_filesize = size
            bofbuffer = f.read(self.bufsize)
            if size > self.bufsize:
                f.seek(-self.bufsize, 2)
                eofbuffer = f.read(self.bufsize)
            else:
                eofbuffer = bofbuffer
        return self.check_formats(bofbuffer, eofbuffer)
    
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
        
    def check_formats(self, bofbuffer, eofbuffer):
        """Apply the patterns for formats to the supplied buffers.
        Return a match list of (format, signature) tuples. The list has inferior matches removed."""
        self.current_count += 1
        result = []
        for format in self.formats:
            self.current_format = format
            # we can prune out formats that are worse than the current match, but for every 3, well test 300, so it has to be efficient. 
            if self.as_good_as_any(format, result):
                sig = self.check_format(format, bofbuffer, eofbuffer)
                if sig != None:
                    result.append((format, sig))
        # Remove any inferior formats
        # This is very inefficient, but doesn't happen often
        # So far, I've seen max 7, a couple of 4, 2, almost all 0 or 1 matches
        # There are few better-than me, and more worse-than me relations
        result = [match for match in result if self.as_good_as_any(match[0], result)]
        return result
    
    def check_format(self, format, bofbuffer, eofbuffer):
        "Return the first of Format's signatures to match against the buffers or None."
        result = None  
        for s in format.signatures:
            self.current_sig = s
            if self.check_sig(s, bofbuffer, eofbuffer):
                # only need one match for each format
                result = s
                break
        return result
    
    def check_sig(self, sig, bofbuffer, eofbuffer):
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
            
def main(arglist=None):
    if arglist == None:
        arglist = sys.argv[1:]
    parser = argparse.ArgumentParser(description=defaults['description'], epilog=defaults['epilog'])
    parser.add_argument('-v', default=False, action='store_true', help='show version information')
    parser.add_argument('-q', default=False, action='store_true', help='run (more) quietly')
    parser.add_argument('-bufsize', type=int, default=None, help='size of the buffer to match against')
    parser.add_argument('-recurse', default=False, action='store_true', help='recurse into subdirectories')
    parser.add_argument('-zip', default=False, action='store_true', help='recurse into zip files')
    parser.add_argument('-matchprintf', metavar='FORMATSTRING', default=None, help='format string (Python style) to use on match. {0}=path, {1}=delta-t, {2}=fido, {3}=format, {4}=sig, {5}=count.')
    parser.add_argument('-nomatchprintf', metavar='FORMATSTRING', default=None, help='format string (Python style) to use if no match. {0}=path, {1}=delta-t, {2}=fido.')
    parser.add_argument('-formats', metavar='PUIDS', default=None, help='comma separated string of formats to use in identification')
    parser.add_argument('-excludeformats', metavar='PUIDS', default=None, help='comma separated string of formats not to use in identification')
    parser.add_argument('-showformats', default=False, action='store_true', help='show current format set')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-input', default=False, help='file containing a list of files to check, one per line. - means stdin')
    group.add_argument('files', nargs='*', default=[], metavar='FILE', help='files to check')
        
    args = parser.parse_args(arglist)
   
    if args.v :
        print "fido/" + version
        exit(1)
    if args.showformats:
        show_formats(formats.all_formats)
        exit(1)
    t0 = time.clock()     
    fido = Fido(quiet=args.q, bufsize=args.bufsize, printmatch=args.matchprintf, printnomatch=args.nomatchprintf)
    if args.formats:
        args.formats = args.formats.split(',')
        fido.formats = [f for f in fido.formats if f.Identifier in args.formats]
    elif args.excludeformats:
        args.excludeformats = args.excludeformats.split(',')
        fido.formats = [f for f in fido.formats if f.Identifier not in args.excludeformats]
    
    if args.input == '-':
        args.files = sys.stdin
    elif args.input:
        args.files = open(args.input, 'r')
        
    for filename in args.files:
        if filename[-1] == '\n':
            filename = filename[:-1]
        try:
            fido.check(filename, recurse=args.recurse, zip=args.zip)
        except KeyboardInterrupt:
            print >> sys.stderr, "FIDO: Interrupt during:\n  File: {0}\n  Format: Puid={1.Identifier} [{1.FormatName}]\n  Sig: ID={2.SignatureID} [{2.SignatureName}]\n  Pat={3.ByteSequenceID} {3.regexstring!r}".format(fido.current_file,
                                  fido.current_format, fido.current_sig, fido.current_pat)
        except IOError:
            exit(1)
    if not args.q:
        fido.print_summary(time.clock() - t0)
       
if __name__ == '__main__':
    #main(['-r', '-z', r'e:/Code/fidotests/corpus/nested1.zip'])
    main()
    
