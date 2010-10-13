#!python
#
# FIDO: Format Identifier for Digital Objects
#

import argparse, sys, re, os, io, time, zipfile, tempfile, datetime
import formats

version = 'fido/0.2.2'
bufsize = 16 * io.DEFAULT_BUFFER_SIZE
printmatch = "OK,{4:%H:%M:%S},{1.Identifier},{1.FormatName},{0}\n"
printnomatch = "KO,{1:%H:%M:%S},,,{0}\n"
confdir = 'conf/'
helpdescription="""
Format Identification for Digital Objects (fido).
FIDO is a command-line tool to identify the file formats of digital objects.  It is designed for
simple integration into automated work-flows.
"""
helpepilog="""
Open Planets Foundation (www.openplanetsfoundation.org)
Author: Adam Farquhar, 2010

FIDO uses the UK National Archives (TNA) PRONOM File Format descriptions.
PRONOM is available from www.tna.gov.uk/pronom.
"""

def init():
    for f in formats.all_formats:
        for s in f.signatures:
            for b in s.bytesequences:
                b.regex = re.compile(b.regexstring, re.DOTALL | re.MULTILINE)

def print_matches(fullname, matches):
    global printmatch, printnomatch
    count = len(matches)
    if count==0:
        sys.stdout.write(printnomatch.format(fullname,datetime.datetime.now()))
    else:
        for (f, s) in matches:
            sys.stdout.write(printmatch.format(fullname,f,s,count,datetime.datetime.now()))
    
def print_summary(count, secs):
    print "FIDO: {:>6d} files in {:>6.2f}ms, {:d} files/sec".format(count, secs * 1000, int(count / secs))

def check(roots, recurse=False, zip=False):
    count = 0
    for root in roots:
        if os.path.isfile(root):
            count += check_file_or_zip(root, zip)
        else:
            for path, unused, files in os.walk(root):
                for f in files:
                    count += check_file_or_zip(os.path.join(path, f), zip)
                if recurse == False:
                    break
    return count

def is_zip(matches):
    if len(matches) == 1 and matches[0][0].Identifier == 'x-fmt/263':
        return True
    else:
        return False

def check_file_or_zip(filename, zip=False):
    count = 1
    try:
        matches = check_file(filename)
        print_matches(filename, matches)
        if zip and is_zip(matches):
            count += check_zipfile(os.path.dirname(filename), os.path.basename(filename), matches)
    except IOError as (errno, strerror):
        print "FIDO: Error: I/O error ({0}): {1} Path is {2}".format(errno, strerror, filename)
    return count

def check_zipfile(path, file, matches):
    try:
        zipfullname = os.path.join(path, file)
        if zipfile.is_zipfile(zipfullname):
            dir = tempfile.mkdtemp()
            count = 0
            with zipfile.ZipFile(zipfullname, 'r') as zip:
                for name in zip.namelist():
                    if name.startswith('..') or name.startswith('/'):
                        raise Exception('zip file has unsafe names')
                    zip.extract(name, dir)
                    tempitempath = os.path.join(dir, name)
                    count += 1
                    matches = check_file(tempitempath)
                    print_matches(zipfullname + '!' + name, matches)
                    if is_zip(matches):
                        count += check_zipfile(path, name, matches)
                    os.remove(tempitempath)
        else:
            raise Exception('Not a valid zipfile: {}'.format(zipfullname))
    except IOError:
        print 'Error in check_zipfile'
        raise
    finally:
        pass
        # not quite right - it won't be empty of subdirs.
        # os.rmdir(dir)
    return count

def check_file(file):
    with open(file, 'rb') as f:
        size = os.stat(file)[6]
        bofbuffer = f.read(bufsize)
        if size > bufsize:
            f.seek(-bufsize, 2)
            eofbuffer = f.read(bufsize)
        else:
            eofbuffer = bofbuffer
    return check_formats(formats.all_formats, bofbuffer, eofbuffer)

def as_good_as_any(f1, match_list):
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
    
def check_formats(formatlist, bofbuffer, eofbuffer):
    # Collect matches for each format
    result = []
    for format in formatlist:
        # we can prune out formats that are worse than the current match, but for every 3, well test 300, so it has to be efficient. 
        #if as_good_as_any(format, result):
            match = check_format(format, bofbuffer, eofbuffer)
            if match != None:
                result.append(match)
    #        else:   
    #            print '*** Pruned', format.FormatID, format.FormatName, format.Identifier
    # Remove any non-preferred formats
    # This is very inefficient, but doesn't happen often
    # So far, I've seen max 7, a couple of 4, 2, almost all 0 or 1 matches
    # There are few better-than me, and more worse-than me relations
    result = [(f, s) for (f, s) in result if as_good_as_any(f, result)]
    
    return result


def check_format(format, bofbuffer, eofbuffer):
    for s in format.signatures:
        if check_sig(s, bofbuffer, eofbuffer):
            # only need one match for each format
            return (format, s)

def check_sig(sig, bofbuffer, eofbuffer):
    match = True
    for b in sig.bytesequences:
        #print "try", sig.SignatureName, b.PositionType, b.regexstring 
        if 'BOF' in b.PositionType:
            if not re.match(b.regex, bofbuffer):
                return False
        elif 'EOF' in b.PositionType:
            if not re.match(b.regex, eofbuffer):
                return False
        elif 'Variable' in b.PositionType:
            if not re.search(b.regex, bofbuffer):
                match = False
        else:
            raise Exception("bad positionType")
    # Should fall through to here if everything matched
    return match

def main(arglist=None):
    if arglist == None:
        arglist = sys.argv[1:]
    global bufsize
    parser = argparse.ArgumentParser(description=helpdescription, epilog=helpepilog)
    parser.add_argument('-v', default=False, action='store_true', help='show version information')
    parser.add_argument('-q', default=False, action='store_true', help='run (more) quietly')
    parser.add_argument('-bufsize', type=int, default=bufsize, help='size of the buffer to match against')
    parser.add_argument('-recurse', default=False, action='store_true', help='recurse into subdirectories')
    parser.add_argument('-zip', default=False, action='store_true', help='recurse into zip files')
    parser.add_argument('-matchprintf',metavar='FORMATSTRING',default=None,help='format string (Python style) to use on match. {0}=path, {1}=format object, {2}=signature, {3}=match count, {4}=now. Default=' + printmatch)
    parser.add_argument('-nomatchprintf',metavar='FORMATSTRING',default=None,help='format string (Python style) to use if no match. {0}=path, {1}=now.  Default=' + printnomatch)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-input', default=False, help='file containing a list of files to check, one per line')
    group.add_argument('files', nargs='*', default=[], metavar='FILE', help='files to check')

    args = parser.parse_args(arglist)
        
    if args.v :
        print version
        exit(1)
    t0 = time.clock()
    init()
    t1 = time.clock()
    if not args.q:
        print "FIDO: {:>6.4f}s loading formats".format(t1 - t0)
    bufsize = args.bufsize
    if args.input != False:
        args.files = [os.path.normpath(line[:-1]) for line in open(args.input, 'r').readlines()]
    else:
        args.files = [os.path.normpath(line) for line in args.files]
    t0 = time.clock()
    #print args.files
    print args
    count = check(args.files, recurse=args.recurse, zip=args.zip)
    
    t1 = time.clock()
    if not args.q:
        print_summary(count, t1 - t0)
                    
if __name__ == '__main__':
    #check(r'e:\Code\fidotests',True,True)
    #main(['-r',r'e:/Code/fidotests/corpus'])
    #main(['-r',r'c:/Documents and Settings/afarquha/My Documents'])
    #main(['-r', r'c:\Documents and Settings\afarquha\My Documents\Proposals'])
    #main(['-h'])
    main()
    
