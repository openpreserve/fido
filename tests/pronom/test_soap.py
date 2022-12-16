#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FIDO: Format Identifier for Digital Objects

Copyright 2010 The Open Preservation Foundation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

PRONOM SOAP call test cases.
"""
from fido.pronom import soap


def test_pronom_version():
    """Test that the returned PRONOM sig version is an integer > 90."""
    version = soap.get_pronom_sig_version()
    assert version > 90


def test_pronom_signature():
    """Test that retrieving signatures gets something with length and no errors are thrown."""
    version = soap.get_pronom_sig_version()
    xml, count = soap.get_droid_signatures(version)
    assert len(xml) > 1000, 'Expected more than 1000 XML lines, got %s' % len(xml)
    assert count > 1000, 'Expected more than 1000 signatures, got %s' % count
