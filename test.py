#!/usr/bin/env python

from unittest import main, TestCase

from fido.fido import Fido

class FidoTests(TestCase):

    def setUp(self):
        self.fido = Fido()

    def test_identify_file(self):
        """checks that identify_file returns a single match
        """
        i = self.fido.identify_file("test-data/fido.txt")
        self.assertEqual(i.mimetype, "text/plain")

    def test_identify_files(self):
        """checks that identify_files returns a generator
        """
        i = list(self.fido.identify_files("test-data/fido.txt"))
        self.assertEqual(len(i), 1)
        self.assertEqual(i[0].mimetype, "text/plain")

    def test_text(self):
        i = self.fido.identify_file("test-data/fido.txt")
        self.assertEqual(i.puid, "x-fmt/111")
        self.assertEqual(i.formatname, "Plain Text File")
        self.assertEqual(i.signaturename, "External")
        self.assertEqual(i.filesize, 11452)
        self.assertEqual(i.filename, "test-data/fido.txt")
        self.assertEqual(i.mimetype, "text/plain")
        self.assertEqual(i.matchtype, "extensions")
        self.assertEqual(i.version, None)
        self.assertEqual(i.alias, None)
        self.assertEqual(i.apple_uti, None)
        self.assertEqual(i.group_size, 1)
        self.assertEqual(i.group_index, 1)
        self.assertEqual(i.count, 1)

    def test_pdf(self):
        i = self.fido.identify_file("test-data/fido.pdf")
        self.assertEqual(i.puid, "fmt/18")
        self.assertEqual(i.formatname, "Acrobat PDF 1.4 - Portable Document Format")
        self.assertEqual(i.signaturename, "PDF 1.4")
        self.assertEqual(i.filesize, 267449)
        self.assertEqual(i.filename, "test-data/fido.pdf")
        self.assertEqual(i.mimetype, "application/pdf")
        self.assertEqual(i.matchtype, "signature")
        self.assertEqual(i.version, "1.4")
        self.assertEqual(i.alias, "PDF (1.4)")
        self.assertEqual(i.apple_uti, "com.adobe.pdf")
        self.assertEqual(i.group_size, 1)
        self.assertEqual(i.group_index, 1)
        self.assertEqual(i.count, 1)

    def test_zip(self):
        f = Fido(zip=True)

        # a zip file should return the identified zip file as well
        # as any of the files it contains
        #i = list(f.identify_files("test-data/fido.zip"))
        i = list(self.fido.identify_files("test-data/fido.zip"))
        self.assertEqual(len(i), 3)

        # first identified file should be the zip itself
        self.assertEqual(i[0].puid, "x-fmt/263")
        self.assertEqual(i[0].formatname, "ZIP Format")
        self.assertEqual(i[0].signaturename, "ZIP format")
        self.assertEqual(i[0].filesize, 261296)
        self.assertEqual(i[0].filename, "test-data/fido.zip")
        self.assertEqual(i[0].mimetype, "application/zip")
        self.assertEqual(i[0].matchtype, "signature")
        self.assertEqual(i[0].version, None)
        self.assertEqual(i[0].alias, None)
        self.assertEqual(i[0].apple_uti, "com.pkware.zip-archive")
        self.assertEqual(i[0].group_size, 1)
        self.assertEqual(i[0].group_index, 1)
        self.assertEqual(i[0].count, 1)

        # check the first identified file in the zip is an application/pdf
        self.assertEqual(i[1].puid, "fmt/18")
        self.assertEqual(i[1].formatname, "Acrobat PDF 1.4 - Portable Document Format")
        self.assertEqual(i[1].signaturename, "PDF 1.4")
        self.assertEqual(i[1].filesize, 267449)
        self.assertEqual(i[1].filename, "test-data/fido.zip!test-data/fido.pdf")
        self.assertEqual(i[1].mimetype, "application/pdf")
        self.assertEqual(i[1].matchtype, "signature")
        self.assertEqual(i[1].version, "1.4")
        self.assertEqual(i[1].alias, "PDF (1.4)")
        self.assertEqual(i[1].apple_uti, "com.adobe.pdf")
        self.assertEqual(i[1].group_size, 1)
        self.assertEqual(i[1].group_index, 1)
        self.assertEqual(i[1].count, 2)

        # check the second identified file in the zip is a text/plain
        self.assertEqual(i[2].puid, "x-fmt/111")
        self.assertEqual(i[2].formatname, "Plain Text File")
        self.assertEqual(i[2].signaturename, "External")
        self.assertEqual(i[2].filesize, 11452)
        self.assertEqual(i[2].filename, "test-data/fido.zip!test-data/todo.txt")
        self.assertEqual(i[2].mimetype, "text/plain")
        self.assertEqual(i[2].matchtype, "extensions")
        self.assertEqual(i[2].version, None)
        self.assertEqual(i[2].alias, None)
        self.assertEqual(i[2].apple_uti, None)
        self.assertEqual(i[2].group_size, 1)
        self.assertEqual(i[2].group_index, 1)
        self.assertEqual(i[2].count, 3)

 
if __name__ == "__main__":
    main()
