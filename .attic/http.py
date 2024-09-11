#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FIDO: Format Identifier for Digital Objects.

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

PRONOM format signatures HTTP calls.
"""
from six.moves import urllib

# NOTE: from fido/pronom/


def get_sig_xml_for_puid(puid):
    """Return the full PRONOM signature XML for the passed PUID."""
    req = urllib.request.Request("http://www.nationalarchives.gov.uk/pronom/{}.xml".format(puid))
    response = urllib.request.urlopen(req)
    xml = response.read()
    return xml
