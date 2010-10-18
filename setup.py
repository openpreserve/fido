#!python
from distutils.core import setup
import py2exe

setup(name='fido',
      version='0.3.2',
      options={"py2exe": { }},
      package_dir={'': 'src'},
      url="http://www.openplanetsfoundation.org",
      packages=['fido'],
      package_data={'fido':['conf/*.*']},
      description='Format Identification for Digital Objects (FIDO).',
      author='Adam Farquhar',
      author_email='adam.farquhar@bl.uk',
      license='Apache 2'
      )
