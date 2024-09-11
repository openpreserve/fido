import os

import pytest

from fido.package import ZipPackage

TEST_DATA_BAD_PACKAGES = os.path.normpath(os.path.join(__file__, "..", "test_data/hard_packages"))


# None of these files should be identified as packages?
@pytest.mark.parametrize("filename", ["bad.zip", "worse.zip", "unicode.zip", "foo.zip", "foo.tar"])
def test_bad_zip(filename):
    p = ZipPackage(os.path.join(TEST_DATA_BAD_PACKAGES, filename), {})
    r = p.detect_formats()
    assert isinstance(r, list) and len(r) == 0
