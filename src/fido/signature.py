class FileFormat:
    """
    FileFormat: Class to implement the Pronom FileFormat.  The XML
    element names are simply reused as attribute names. 

    FileFormat 1-n InternalSignature
    """
    def __init__(self,**kwargs):
        for k in kwargs.keys():
            setattr(self,k,kwargs[k])

    def __repr__(self):
        return "FileFormat(" + dict_repr(self.__dict__) + ")"

class InternalSignature:
    """
    InternalSignature: Class to implement the Pronom InternalSignature.  The
    XML element names are simply reused as attribute names.


    InternalSignature 0-1 ByteSignature PositionType Absolute from BOF
    InternalSignature 0-1 ByteSignature PositionType Absolute from EOF
    """
    def __init__(self,**kwargs):
        for k in kwargs.keys():
            setattr(self,k,kwargs[k])

    def __repr__(self):
        return "InternalSignature(" + dict_repr(self.__dict__) + ")"

class ByteSequence:
    """
    ByteSequence: Class to implement the Pronom ByteSequence.
    """
    def __init__(self,**kwargs):
        for k in kwargs.keys():
            setattr(self,k,kwargs[k])

    def __repr__(self):
        return "ByteSequence(" + dict_repr(self.__dict__) + ")"
    
def dict_repr(dict):
    first = True
    s = ""
    keys = dict.keys()[:]
    keys.sort()
    for k in keys:
        if first:
            first=False
        else:
            s+=','
        s+= "{}={}".format(k,repr(dict[k]))
    return s


def time_msg(messages, times):
    i=0
    for msg in messages.split(','):
        print "FIDO: {: >10.2f}ms {}".format((times[i+1]-times[i])*1000,msg)
        i+=1
