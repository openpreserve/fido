'''
Modify the definition of fixup to add or correct the format definitions.
'''

def fixup(info):
    """Fixup pronom definitions and extend with local modifications.
    info is a prepare.FormatInfo object.  Use the methods such as add_format, remove, modify
    to correct things.
    """
    #info.add_format()
    # Fix the PDF EOF matches that don't cover all the options: 
    for id in [59, 61, 114, 117, 120, 186, 249, 250, 251, 248]:
        info.modify('ByteSequence', str(id), regexstring='.*\\%\\%EOF.{1,2}\\Z')
    # Fix the horrible fmt/134 EOF signatures that require massive backtracking
    for id in [340, 341, 342, 343]:
        info.modify('ByteSequence', str(id),
                regexstring='.*\\\xff[\\\xf2|\\\xf3|\\\xfa|\\\xfb][\\\x10-\\\xeb].{7,500}\\000\\000\\000.{36,1426}\\Z')
    # Fix the  PPT that looks deep into the file looking for p o w e r p o i n t
    