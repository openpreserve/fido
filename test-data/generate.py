#!/usr/bin/env python

"""
Writes out a unittest.TestCase using fido.* files and an existing fido.
"""

import os, subprocess

fido = '/home/ed/Projects/fido-openplanets/fido/fido.py'
results = open("results.txt", "w")
fmt = '''-matchprintf='%(info.puid)s,%(info.formatname)s,%(info.signaturename)s,%(info.mimetype)s,%(info.matchtype)s,%(info.version)s,%(info.alias)s,%(info.apple_uti)s\n''' 

print """#!/usr/bin/env python

from unittest import main, TestCase

from fido.fido import Fido

class FidoTests(TestCase):

    def setUp(self):
        self.fido = Fido()"""

for file in os.listdir("."):
    if not file.startswith("fido."):
        continue
    output = subprocess.check_output([fido, file, fmt]).split("\n")[-2]
    parts = output.split(",")
    if parts[0] == "KO":
        continue
    size = os.path.getsize(file)
    ext = file.split(".")[-1]

    print \
"""
    def test_%s(self):
        i = self.fido.identify_file("test-data/%s")
        self.assertEqual(i.puid, "%s")
        self.assertEqual(i.formatname, "%s")
        self.assertEqual(i.signaturename, "%s")
        self.assertEqual(i.filesize, %i)
        self.assertEqual(i.filename, "test-data/%s")
        self.assertEqual(i.mimetype, "%s")
        self.assertEqual(i.matchtype, "%s")
        self.assertEqual(i.version, "%s")
        self.assertEqual(i.alias, "%s")
        self.assertEqual(i.apple_uti, "%s")
        self.assertEqual(i.group_size, 1)
        self.assertEqual(i.group_index, 1)
        self.assertEqual(i.count, 1)""" % (ext, file, parts[0], parts[1], parts[2], size, file, parts[3], parts[4], parts[5], parts[6], parts[7])


print """\ 
if __name__ == "__main__":
    main()
"""
