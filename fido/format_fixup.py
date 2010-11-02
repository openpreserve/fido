'''
Modify the definition of fixup to add or correct the format definitions.
'''

def fixup(info):
    """Fixup pronom definitions and extend with local modifications.
    info is a prepare.FormatInfo object.  Use the methods such as add_format, remove, modify
    to correct things.
    """
    #info.add_format()
    # Fix the PDF EOF matches that don't cover all the options. I have observed many PDFs with no bytes after EOF.
    for id in [59, 61, 114, 117, 120, 186, 249, 250, 251, 248]:
        info.modify('ByteSequence', str(id), regexstring='(?s)\\%\\%EOF.{0,2}\\Z')
    # Fix the horrible fmt/134 EOF signatures that require massive backtracking
    for id in [340, 341, 342, 343]:
        info.modify('ByteSequence', str(id),
                regexstring='(?s)\\\xff[\\\xf2|\\\xf3|\\\xfa|\\\xfb][\\\x10-\\\xeb].{7,500}\\000\\000\\000.{36,1426}\\Z')
    # TODO: Fix the  PPT that looks deep into the file looking for p o w e r p o i n t
    # Change the recogniser for the ZIP component of OOXML formats to be more efficient. 
    # The signature for Zip uses an inefficient eof match. Siard: fmt/161, pat 390, Zip: fmt/263 pat 338
    # info.modify('ByteSequence',str(338), '(?s)PK\\\x01.{43,65531}PK\\\x05\\\x06.{18,65531}\\Z')
    
    for id in [331]:
        info.modify('ByteSequence', str(id),
            regexstring='(?s)\\APK\\\x03\\\x04')
