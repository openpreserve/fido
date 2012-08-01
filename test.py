#!/usr/bin/env python

from unittest import main, TestCase

from fido.fido import Fido

class FidoTests(TestCase):

    def test_ok(self):
        self.assertTrue(True)

    def test_pdf(self):
        f = Fido()
        f.identify_file("test-data/fido.pdf")

if __name__ == "__main__":
    main()
