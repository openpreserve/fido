import sys
from setuptools import setup

# attempt automatic python2 to python3 conversion if using python3
extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup( name='fido',
       version='1.3.0',
       install_requires=['distribute'],
       description='Format Identification for Digital Objects (FIDO)',
       packages=['fido'],
       package_data={'fido':['*.*', 'conf/*.*']},
       entry_points={'console_scripts':['fido = fido.fido:main']},
       **extra )
