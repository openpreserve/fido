#!python
from distutils.core import setup
setup(name='fido',
      version='0.2.1',
      packages=['fido'],
      package_data={'fido':['conf/*.*']},
      description='Format Identification for Digital Objects (FIDO).',
      author='Adam Farquhar',
      author_email='adam.farquhar@bl.uk',
      license='Apache 2'
      )
