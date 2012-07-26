#!/usr/bin/env python

from unittest import main, TestCase

from fido.fido import Fido

class FidoTests(TestCase):

    def test_ok(self):
        self.assertTrue(True)

    def test_pdf(self):
        # OK,229,fmt/18,"Acrobat PDF 1.4 - Portable Document Format","PDF 1.4",267449,"test-data/fido.pdf","application/pdf","signature"
        f = Fido()
        f.identify_file("test-data/fido.pdf")

if __name__ == "__main__":
    main()
