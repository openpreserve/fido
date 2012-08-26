#!/usr/bin/env python

from unittest import main, TestCase

from fido.fido import Fido

class FidoTests(TestCase):

    def setUp(self):
        self.fido = Fido()

    def test_text(self):
        i = list(self.fido.identify_file("test-data/fido.txt"))[0]
        self.assertEqual(i.mimetype, "text/plain")

    def test_pdf(self):
        i = list(self.fido.identify_file("test-data/fido.pdf"))[0]
        self.assertEqual(i.mimetype, "application/pdf")
        self.assertEqual(i.version, "1.4")

if __name__ == "__main__":
    main()
