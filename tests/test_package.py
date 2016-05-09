import os
import zipfile

import pytest

from fido.package import ZipPackage


FIXTURES_DIR = os.path.normpath(os.path.join(__file__, '..', 'fixtures'))


def test_bad_zip():
    p = ZipPackage(os.path.join(FIXTURES_DIR, 'bad.zip'), {})
    r = p.detect_formats()
    assert isinstance(r, list) and len(r) == 0
