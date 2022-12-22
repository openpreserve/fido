# -*- coding: utf-8 -*-

"""
Format Identification for Digital Objects (FIDO).

FIDO is a command-line tool to identify the file formats of digital objects.
It is designed for simple integration into automated work-flows.
"""

from __future__ import print_function

from os.path import abspath, dirname, join

from six.moves import input as rinput


__version__ = '1.6.1'


CONFIG_DIR = join(abspath(dirname(__file__)), 'conf')


def query_yes_no(question, default='yes'):
    """
    Ask a yes/no question via input() and return their answer.

    `question` is a string that is presented to the user. `default` is the
    presumed answer if the user just hits <Enter>. It must be "yes" (the
    default), "no" or None (meaning an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {'yes': True, 'y': True, 'no': False, 'n': False}
    if default is None:
        prompt = ' [y/n] '
    elif default == 'yes':
        prompt = ' [Y/n] '
    elif default == 'no':
        prompt = ' [y/N] '
    else:
        raise ValueError('Invalid default answer: "%s"' % default)
    while True:
        print(question + prompt, end='')
        choice = rinput().lower()
        if default is not None and choice == '':
            return valid[default]
        if choice in valid:
            return valid[choice]
        print('Please respond with "yes" or "no" (or "y" or "n").')
