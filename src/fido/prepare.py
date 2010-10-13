#!python
#
# Format Identification for Digital Objects

import xml.parsers.expat
import glob, time, re
import cStringIO
from signature import FileFormat, InternalSignature, ByteSequence, time_msg

def convert(srcdir='.\\conf\\xml\\puid.*.xml', dst="formats.py"):
    """
    Convert the pronom xml in srcdir and write result into dst in the fido source directory.
    """
    t = [time.clock()]
    specs = []
    for srcfile in glob.glob(srcdir):
        #print srcfile
        for spec in parsePronomReport(srcfile):
            if spec.signatures != []:
                specs.append(spec)
    t.append(time.clock())
    with open(dst, 'wb') as out:
        out.write('from signature import FileFormat, InternalSignature, ByteSequence\n')
        out.write('all_formats = [\n    ')
        for s in sort_formats(specs):
            out.write(repr(s))
            out.write(',\n    ')
        out.write(']\n')
    t.append(time.clock())
    time_msg("Load and parse signature xml,Write fido format file", t)

def sort_formats(formatlist):
    def compare_formats(f1, f2):
        f1ID = f1.FormatID
        f2ID = f2.FormatID
        for (rel, val) in getattr(f1, 'relatedformat', []):
            if rel == 'Has priority over' and val == f2ID:
                return - 1
            elif rel == 'Has lower priority than' and val == f2ID:
                return 1
            elif rel == 'Is supertype of':
                return 1
        return int(f1ID) - int(f2ID)
    return sorted(formatlist, cmp=compare_formats)

def print_graph(formatlist):
    for format in formatlist:
        print format.FormatID, format.FormatName
        for (rel, val) in getattr(format, 'relatedformat', []):
            print '  ', rel, val

def parsePronomReport(file):
    """
    Parse the pronom XML file for a file format.
    Return a list of Signature instances, one for each InternalSignature in the file.
    Signature [SignaturePattern ... ]
    """
    stack = []
    results = []
    info = {'data':''}
    
    def set(prop, val):
        if   getattr(results[-1], prop, None) == None:
            setattr(results[-1], prop, val)
        else:
            raise Exception("Value {} of {} in {} already set".format(val, prop, results[-1]))
        
    def add(prop, val):
        current = getattr(results[-1], prop, None)
        if   current == None:
            setattr(results[-1], prop, [val])
        else:
            current.append(val)        

    def start(tag, attrs):
        stack.append(tag)
        if tag == "FileFormat":
            e = FileFormat(signatures=[])
            results.append(e)
        elif tag == "InternalSignature":
            e = InternalSignature(bytesequences=[])
            results[-1].signatures.append(e)
            results.append(e)
        elif tag == "ByteSequence":
            e = ByteSequence()
            results[-1].bytesequences.append(e)
            results.append(e)

    def end(tag):
        # FileFormat properties
        if tag in ["FormatName", "FormatID"]:
            set(tag, info['data'])
        elif tag == "Identifier" and stack[-2] == "FileFormatIdentifier":
            info['identifier'] = info['data']
        elif tag == "IdentifierType" and info['data'] == "PUID" and stack[-2] == "FileFormatIdentifier":
            set('Identifier', info['identifier'])
            info['identifier'] = None
        elif tag == "IdentifierType" and info['data'] == "MIME" and stack[-2] == "FileFormatIdentifier":
            add('MimeType', info['identifier'])
        elif tag == "RelationshipType" and stack[-2] == "RelatedFormat":
            info['reltype'] = info['data']
        elif tag == "RelatedFormatID" and  stack[-2] == "RelatedFormat":
            spec = results[-1]
            if getattr(spec, 'relatedformat', None) == None:
                spec.relatedformat = []
            spec.relatedformat.append((info['reltype'], info['data']))
            info['reltype'] = None
        # ExternalSignature properties
        # InternalSignature properties
        elif tag in ["SignatureName", "SignatureID"]:
            set(tag, info['data'])
        # ByteSequence properties
        elif tag in ["ByteSequenceID", "PositionType", "Offset",
                     "MaxOffset", "IndirectOffsetLocation", "Endianness", "ByteSequenceValue"]:
            set(tag, info['data'])

        if tag == 'ByteSequenceValue':
            spec = results[-1]
            spec.regexstring = convertToRegex(spec.ByteSequenceValue,
                                              spec.Endianness, spec.PositionType, spec.Offset, spec.MaxOffset)
        # Cleanup
        # When done, the results list should only contain FileFormat
        info['data'] = ''
        stack.pop()
        if tag in [ "InternalSignature" , "ByteSequence"]:
            results.pop()

    def data(str):
        info['data'] += str.strip()
    
    p = xml.parsers.expat.ParserCreate()
    p.buffer_text = True
    p.StartElementHandler = start
    p.EndElementHandler = end
    p.CharacterDataHandler = data
    
    with open(file, 'rb') as f:
        p.ParseFile(f)
    return results

def err(msg, c, i, chars):
    return "Conversion: {}: char='{}', at pos {} in \n  {}\n  {}^".format(msg, c, i, chars, i * ' ')

def doByte(chars, i, littleendian):
    c1 = '0123456789ABCDEF'.find(chars[i].upper())
    c2 = '0123456789ABCDEF'.find(chars[i + 1].upper())
    if (c1 < 0 or c2 < 0):
        raise Exception(err('bad byte sequence', chars[i:i + 2], i, chars))
    if littleendian:
        val = chr(16 * c1 + c2)
    else:
        val = chr(c1 + 16 * c2)
    return (re.escape(val), 2)

# Have to escape any regex special stuff like []*. and so on with re.escape()
def convertToRegex(chars, endianness='', pos='BOF', offset='0', maxoffset=None):
    if 'Big' in endianness:
        littleendian = False
    else:
        littleendian = True
    if len(offset) == 0:
        offset = '0'
    if len(maxoffset) == 0:
        maxoffset = None
    buf = cStringIO.StringIO()
    i = 0
    state = 'start'
    # HACK
    if 'EOF' in pos:
        buf.write('.*')
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
        #print err(state,chars[i],i,chars)
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
                raise Exception(err('Illegal character in start', chars[i], i, chars))
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
                print err('Illegal character in bracket', chars[i], i, chars)
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
                    raise Exception(err('Illegal character in paren', chars[i], i, chars))
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
                    raise Exception(err('Illegal character in curly', chars[i], i, chars))
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
                    raise Exception(err('Illegal character after ?', chars[i + 1], i + 1, chars))
                buf.write('.?')
                i += 2
            state = 'start'
        else:
            raise Exception('Illegal state {}'.format(state))
    if 'EOF' in pos:
        if offset != '0':
            buf.write('.*{' + offset)
            if maxoffset != None:
                buf.write(',' + maxoffset)
            buf.write('}')
        elif maxoffset != None:
            buf.write('.{0,' + maxoffset + '}')
        buf.write('\\Z')
    val = buf.getvalue()
    buf.close()
    return val

def test1():
    return parsePronomReport("e:/Code/droid/fetch/xml/puid.fmt.1.xml")

def test2():
    tests = [('3132(3333|343434)35??36*{250-*}37{10-20}', '\\A12(?:33|444)5.?6.*.{250,}7.{10,20}'),
           ('31[3233:3435]36', 'x'),
           ('31[09:0B]36', '^1[\\\t-\\\x0b]6')
           ]
    for (a, b) in tests:
        assert(convertToRegex(a) == b)

# convert('.\\conf\\xml\\puid.fmt.276.xml')

if __name__ == '__main__':
    convert()
