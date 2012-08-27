from setuptools import setup

from fido.fido import version

setup( 
    name             = 'fido',
    version          = version,
    url              = 'http://github.com/openplanets/fido',
    license          = 'http://www.apache.org/licenses/LICENSE-2.0.html',
    py_modules       = ['fido'],
    test_suite       = 'test',
    description      = "Format Identification for Digital Objects (FIDO) is a Python command-line tool to identify the file formats of digital objects. It is designed for simple integration into automated work-flows.",
)
