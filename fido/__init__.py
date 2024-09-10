# -*- coding: utf-8 -*-

"""
Format Identification for Digital Objects (FIDO).

FIDO is a command-line tool to identify the file formats of digital objects.
It is designed for simple integration into automated work-flows.
"""

__version__ = "1.8.0dev"

# todo: move this to a conf/conf.py or something rather than init.py. Would require some cascading updates, though
from os.path import abspath, dirname, join

CONFIG_DIR = join(abspath(dirname(__file__)), "conf")
