#!python
#
# Format Identification for Digital Objects

import xml.parsers.expat, re, cStringIO, zipfile, os
import format_fixup
from signature import FileFormat, InternalSignature, ByteSequence

class FormatInfo:
    def __init__(self, pronom_files, format_list=[]):
        self.info = {}
        self.formats = []
        self.pronom_files = pronom_files
        for f in format_list:
            self.add_format(f)
                           

    def add_format(self, f):
        self.formats.append(f)
        self.info[('Format', f.FormatID)] = (f, None)
        for s in f.signatures:
            self.info[('Signature', s.SignatureID)] = (s, f)
            for b in s.bytesequences:
                self.info[('ByteSequence', b.ByteSequenceID)] = (b, s)
        
    def remove(self, type, id):
        key = (type, id)
        (child, parent) = self.info[key]
        if type == 'Format':
            list = self.format_list
        elif type == 'Signature':
            list = parent.signatures
        elif type == 'ByteSequence':
            list = parent.bytesequnces
        else:
            raise Exception("Unknown type: " + str(type))
        list.remove(child)
        del self.info[key]
                
    def modify(self, type, id, **kwargs):
        (o, unused_parent) = self.info[(type, id)]
        for (k) in kwargs.keys():
            if getattr(o, k, None) != None:
                print "FIDO: Modifying {} {}\n  Old={}\n  New={}".format(type, id,
                                                                          repr(getattr(o, k)),
                                                                          repr(kwargs[k]))
            setattr(o, k, kwargs[k])   
    
    #TODO: read the pronom-xml from configured location.  This will break in real life.
    def load(self):
        with zipfile.ZipFile(self.pronom_files, 'r') as zip:
            for item in zip.infolist():
                # FIXME: need to scan to the end, as there is no seek.
                with zip.open(item) as stream:
                    for format in parsePronomReport(stream):
                        self.add_format(format)
        self._sort_formats(self.formats)
      
    def save(self, dst):
        with open(dst, 'wb') as out:
            out.write('from signature import FileFormat, InternalSignature, ByteSequence\n')
            out.write('all_formats = [\n    ')
            for format in self.formats:
                if format.signatures != []:
                    out.write(repr(format))
                    out.write(',\n    ')
            out.write(']\n')
    
    def _sort_formats(self, formatlist):
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

def parsePronomReport(stream):
    """
    Parse the pronom XML file for a file format.
    Return a list of Formats.
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
            e = FileFormat(signatures=[], extensions=[])
            results.append(e)
        elif tag == "InternalSignature":
            e = InternalSignature(bytesequences=[])
            if len(results) == 0:
                pass
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
        elif tag == 'Signature': #This is where the extension is held
            results[-1].extensions.append('.' + info['data'].lower())
        # InternalSignature properties
        elif tag in ["SignatureName", "SignatureID"]:
            set(tag, info['data'])
        # ByteSequence properties
        elif tag in ["ByteSequenceID", "PositionType", "Offset",
                     "MaxOffset", "IndirectOffsetLocation", "Endianness", "ByteSequenceValue"]:
            if tag == 'PositionType':
                if 'BOF' in info['data']:
                    set('FidoPosition', 'BOF')
                elif 'EOF' in info['data']:
                    set('FidoPosition', 'EOF')
                elif 'Var' in info['data']:
                    set('FidoPosition', 'VAR')
                else:
                    raise Exception('Bad Position Type')
            set(tag, info['data'])

        if tag == 'ByteSequenceValue':
            spec = results[-1]
            spec.regexstring = convert_to_regex(spec.ByteSequenceValue,
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
        
    p.ParseFile(stream)
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
def convert_to_regex(chars, endianness='', pos='BOF', offset='0', maxoffset=None):
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

def list_find(item, list, key=lambda x: x):
    i = 0
    for e in list:
        if key(e) == item:
            return (e, i)
        i += 1
    return None

if __name__ == '__main__':
    info = FormatInfo(os.path.join(os.path.dirname(__file__), 'conf', 'pronom-xml.zip'))
    info.load()
    format_fixup.fixup(info)
    info.save(os.path.join(os.path.dirname(__file__), 'formats.py'))
    print 'FIDO: {} formats'.format(len(info.formats))
    
