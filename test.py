#!/usr/bin/env python

from unittest import main, TestCase

from fido.fido import Fido

class FidoTests(TestCase):

    def test_pdf(self):
        f = Fido()
        i = list(f.identify_file("test-data/fido.pdf"))[0]
        self.assertEqual(i.mimetype, "application/pdf")
        self.assertEqual(i.version, "1.4")

if __name__ == "__main__":
    main()
