import codecs
import os
import re
import sys

from setuptools import setup


def read(*parts):
    path = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(path, encoding='utf-8') as fobj:
        return fobj.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


install_requires = [
    'olefile >= 0.4, < 1',
    'setuptools',
    'six == 1.10.0',
]


setup_requires = [
    'pytest-runner',
]


tests_require = [
    'pytest',
]


setup(
    name='fido',
    version=find_version('fido', '__init__.py'),
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    description='Format Identification for Digital Objects (FIDO)',
    packages=['fido'],
    package_data={'fido': ['*.*', 'conf/*.*']},
    entry_points={'console_scripts': [
        'fido = fido.fido:main',
        'fido-prepare = fido.prepare:main',
        'fido-update-signatures = fido.update_signatures:main',
        'fido-toxml = fido.toxml:main',
    ]}
)
