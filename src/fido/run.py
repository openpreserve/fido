#!python
'''
This module is part of the Fido Format Identifier for Digital Objects tool

Copyright 2010 The British Library

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import argparse, sys, re, os, io, time, zipfile, datetime
import formats

version = '0.5.1'
defaults = {'bufsize': 16 * io.DEFAULT_BUFFER_SIZE,
            #OK/KO,msec,puid,format name,file size,file name            
            'printmatch': "OK,{5},{1.Identifier},{1.FormatName},{6.current_filesize},\"{0}\"\n",
            'printnomatch' : "KO,{2},,,{3.current_filesize},{0}\n",
            'description' : """
    Format Identification for Digital Objects (fido).
    FIDO is a command-line tool to identify the file formats of digital objects.
    It is designed for simple integration into automated work-flows.
    """,
    'epilog' : """
    Open Planets Foundation (www.openplanetsfoundation.org)
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
        self.time_sigs = {'name':'Sig'}
        self.time_formats = {'name':'Format'}
        t = time.clock()
        self.formats = formats.all_formats[:]
        self.compile_signatures()
        self.t_compile = time.clock() - t
        # current_* for helpful messages on interrupt, etc
        self.current_file = ''
        self.current_filesize = 0
        self.current_format = None
        self.current_sig = None
        self.current_pat = None
        self.current_count = 0  # Count of files with attempted identifies
        
    def compile_signatures(self):
        for f in self.formats:
            for s in f.signatures:
                for b in s.bytesequences:
                    b.regex = re.compile(b.regexstring, re.DOTALL | re.MULTILINE)

    def print_matches(self, fullname, matches, start, end):
        count = len(matches)
        if count == 0:
            sys.stdout.write(self.printnomatch.format(fullname, datetime.datetime.now(), int(1000 * (end - start)), self))
        else:
            for (f, s) in matches:
                sys.stdout.write(self.printmatch.format(fullname, f, s, count, datetime.datetime.now(), int(1000 * (end - start)), self))
        
    def print_times(self, attr, dict):
        for (k, v) in sorted(dict.items(), key=lambda x: x[1])[0:10]:
            print >> sys.stderr, "{:>6} {:>15} {:>6d}msec".format(dict['name'], getattr(k, attr)[0:15], int(v * 1000))
        
    def print_summary(self, secs, diagnose=False):
        count = self.current_count
        if not self.quiet:
            print >> sys.stderr, "FIDO: Compiled    {:>6d} formats in {:>6.2f} msec".format(len(self.formats), 1000 * self.t_compile)
            print >> sys.stderr, "FIDO: Processed {:>6d} files in {:>6.2f} msec, {:d} files/sec".format(count, secs * 1000, int(count / secs))
            if diagnose:
                self.print_times('FormatName', self.time_formats)
                self.print_times('SignatureName', self.time_sigs)
                
    def check(self, roots, recurse=False, zip=False):
        for root in roots:
            if os.path.isfile(root):
                self.check_file_or_zip(root, zip)
            else:
                for path, unused, files in os.walk(root):
                    for f in files:
                        self.check_file_or_zip(os.path.join(path, f), zip)
                    if recurse == False:
                        break
        
    def is_zip(self, matches):
        if len(matches) == 1 and matches[0][0].Identifier == 'x-fmt/263':
            return True
        else:
            return False
    
    def check_file_or_zip(self, filename, zip=False):
        self.current_file = filename
        t0 = self.time_check_file = time.clock()
        try:
            matches = self.check_file(filename)
            self.print_matches(filename, matches, start=t0, end=time.clock())
            if zip and self.is_zip(matches):
                self.check_zipfile(filename, matches)
        except IOError as (errno, strerror):
            print >> sys.stderr, "FIDO: Error: I/O error ({0}): {1} Path is {2}".format(errno, strerror, filename)
        
    def check_zipfile(self, zipfilename, matches):
        if zipfile.is_zipfile(zipfilename):
            with zipfile.ZipFile(zipfilename, 'r') as zip:
                for item in zip.infolist():
                    if item.file_size == 0:
                        #TODO: Find a correct test for zip items that are just directories
                        continue
                    t0 = time.clock()
                    with zip.open(item) as f:
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
                        #FIXME: Need to recurse into the zips
                        #self.check_zipfile(path, name, matches)
                        if not self.quiet:
                            print >> sys.stderr, 'FIDO: Skipping recursive zip processing: ' + zipfilename + '!' + item.filename 
        else:
            raise Exception('Not a valid zipfile: {}'.format(zipfilename))
    
    def check_file(self, file):
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
        #return True
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
        # Collect matches for each format
        self.current_count += 1
        result = []
        for format in self.formats:
            self.current_format = format
            # we can prune out formats that are worse than the current match, but for every 3, well test 300, so it has to be efficient. 
            if self.as_good_as_any(format, result):
                match = self.check_format(format, bofbuffer, eofbuffer)
                if match != None:
                    result.append(match)
        # Remove any non-preferred formats
        # This is very inefficient, but doesn't happen often
        # So far, I've seen max 7, a couple of 4, 2, almost all 0 or 1 matches
        # There are few better-than me, and more worse-than me relations
        result = [(f, s) for (f, s) in result if self.as_good_as_any(f, result)]
        return result
    
    def check_format(self, format, bofbuffer, eofbuffer):
        #t = time.clock()
        result = None  
        for s in format.signatures:
            self.current_sig = s
            if self.check_sig(s, bofbuffer, eofbuffer):
                # only need one match for each format
                result = (format, s)
                break
        #self.time_formats[format] = time.clock() - t + self.time_formats.get(format, 0.0)
        return result
    
    #TODO: use an efficient test for BOF/EOF/VAR
    def check_sig(self, sig, bofbuffer, eofbuffer):
        for b in sig.bytesequences:
            #print "try", sig.SignatureName, b.PositionType, b.regexstring
            self.current_pat = b
            t_beg = time.clock()
            if b.FidoPosition == 'BOF':
                if not re.match(b.regex, bofbuffer):
                    return False
            elif b.FidoPosition == 'EOF':
                if not re.search(b.regex, eofbuffer):
                    return False
            elif b.FidoPosition == 'VAR':
                if not re.search(b.regex, bofbuffer):
                    return False
            else:
                raise Exception("bad positionType")
            t_end = time.clock()
            if t_end - t_beg > 0.05:
                print >> sys.stderr, "FIDO: {3.current_format.Identifier} {3.current_file}: Slow sig {0}s  - sig:{1.SignatureID} {1.SignatureName} pat:{2.ByteSequenceID} {2.regexstring!r}".format(t_end - t_beg, sig, b, self)
        # Should fall through to here if everything matched
        #self.time_sigs[sig] = time.clock() - t + self.time_sigs.get(sig, 0.0)
        return True

def show_formats(format_list):
    #print'#Identifier,FormatName,MimeType,MimeType'
    for f in sorted(format_list, key=lambda x: x.Identifier):
        mimetypes = ",".join(getattr(f, 'MimeType', ['None']))
        print "{0},\"{1}\",{2!s}".format(f.Identifier, f.FormatName, mimetypes)
            
def main(arglist=None):
    if arglist == None:
        arglist = sys.argv[1:]
    parser = argparse.ArgumentParser(description=defaults['description'], epilog=defaults['epilog'])
    parser.add_argument('-v', default=False, action='store_true', help='show version information')
    parser.add_argument('-q', default=False, action='store_true', help='run (more) quietly')
    parser.add_argument('-bufsize', type=int, default=None, help='size of the buffer to match against')
    parser.add_argument('-recurse', default=False, action='store_true', help='recurse into subdirectories')
    parser.add_argument('-zip', default=False, action='store_true', help='recurse into zip files')
    parser.add_argument('-diagnose', default=False, action='store_true', help='show some diagnostic information')
    parser.add_argument('-matchprintf', metavar='FORMATSTRING', default=None, help='format string (Python style) to use on match. {0}=path, {1}=format object, {2}=signature, {3}=match count, {4}=now.')
    parser.add_argument('-nomatchprintf', metavar='FORMATSTRING', default=None, help='format string (Python style) to use if no match. {0}=path, {1}=now.')
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
   
    if args.formats:
        args.formats = args.formats.split(',')
        formats.all_formats = [f for f in formats.all_formats if f.Identifier in args.formats]
    elif args.excludeformats:
        args.excludeformats = args.excludeformats.split(',')
        print args.excludeformats
        formats.all_formats = [f for f in formats.all_formats if f.Identifier not in args.excludeformats]
    
    t0 = time.clock()     
    fido = Fido(quiet=args.q, bufsize=args.bufsize, printmatch=args.matchprintf, printnomatch=args.nomatchprintf)
    if args.input == '-':
        args.files = sys.stdin
    elif args.input:
        args.files = open(args.input, 'r')
    for filename in args.files:
        if filename[-1] == '\n':
            filename = filename[:-1]
        try:
            fido.check([filename], recurse=args.recurse, zip=args.zip)
        except KeyboardInterrupt:
            try:
                print >> sys.stderr, "FIDO: Interrupt during:\n  File: {0}\n  Format: Puid={1.Identifier} [{1.FormatName}]\n  Sig: ID={2.SignatureID} [{2.SignatureName}]\n  Pat={3.ByteSequenceID} {3.regexstring!r}".format(fido.current_file, fido.current_format,
                                                           fido.current_sig, fido.current_pat)
            except AttributeError:
                # the things may not be set yet.
                print >> sys.stderr, "FIDO: Aborted during: File: {}".format(fido.current_file)
            # TODO: Is this a good thing to do?
            exit(1)
        except IOError:
            exit(1)
    t1 = time.clock()
    if not args.q:
        fido.print_summary(t1 - t0, args.diagnose)
       
if __name__ == '__main__':
    #main(['-r', r'e:\Code\fidotests\corpus\Buckland -- Concepts of Library Goodness.htm' ])
    #check(r'e:\Code\fidotests',True,True)
    #main(['-r', '-b 3000', r'e:/Code/fidotests/corpus/b.ppt'])
    #main(['-r', '-z', r'e:/Code/fidotests/corpus/'])
    #main(['-r',r'c:/Documents and Settings/afarquha/My Documents'])
    #main(['-r', r'c:\Documents and Settings\afarquha\My Documents\Proposals'])
    #main(['-h'])
    #main(['-s'])
    #main(['-f', "fmt/50,fmt/99,fmt/100,fmt/101", r'e:/Code/fidotests/corpus/'])
    #main(['-n', '', '-f', "fmt/50,fmt/99,fmt/100,fmt/101", r'e:/Code/fidotests/corpus/'])
    #main(['-ex', "fmt/50,fmt/99,fmt/100,fmt/101,fmt/199", r'e:/Code/fidotests/corpus/'])
    main()
    
