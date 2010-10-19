#!python
from distutils.core import setup
import run

setup(name='fido',
      version=run.version,
      #options={"py2exe": { }},
      package_dir={'': 'src'},
      url="http://www.openplanetsfoundation.org",
      packages=['fido'],
      package_data={'fido':['conf/*.*']},
      description='Format Identification for Digital Objects (FIDO).',
      author='Adam Farquhar',
      author_email='adam.farquhar@bl.uk',
      license='''
This module is part of the Fido Format Identifier for Digital Objects tool

Copyright 2010 The British Library

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
      )
