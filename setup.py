import sys
from setuptools import setup

from fido.fido import version

# attempt automatic python2 to python3 conversion if using python3
extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(
    name='fido',
    version=version,
    install_requires    = ['distribute'],
    description         = 'Format Identification for Digital Objects (FIDO)',
    packages            = ['fido'],
    package_data        = {'fido':['*.*', 'conf/*.*']},
    entry_points        = {'console_scripts':['fido = fido.fido:main']},
    test_suite          = 'test',
    **extra
)
