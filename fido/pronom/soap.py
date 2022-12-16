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

PRONOM format signatures SOAP calls.
"""
import sys
from urllib.error import HTTPError, URLError
import xml.etree.ElementTree as ET
from six.moves import urllib

from fido import __version__
ENCODING = 'utf-8'
XML_PROC = '<?xml version="1.0" encoding="{}"?>'.format(ENCODING)
TNA_DOMAIN = 'nationalarchives.gov.uk'
PRONOM_HOST = 'www.{}'.format(TNA_DOMAIN)
PRONOM_NS = 'http://pronom.{}'.format(TNA_DOMAIN)
SIG_NS = 'http://{}/pronom/SignatureFile'.format(PRONOM_HOST)

NS = {
    'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'xsd': 'http://www.w3.org/2001/XMLSchema',
    'pronom': PRONOM_NS,
    'sig': SIG_NS
}

HEADERS = {
    'Host': PRONOM_HOST,
    'User-Agent': 'PRONOM UTILS v{0} (OPF)'.format(__version__),
    'Content-type': 'text/xml; charset="UTF-8"'
}


def get_pronom_sig_version():
    """
    Get PRONOM signature version.

    Return latest signature file version number as an int.
    Raises an HTTPError if there are problems.
    """
    tree = _get_soap_ele_tree('getSignatureFileVersionV1')
    ver_ele = tree.find('.//pronom:Version/pronom:Version', NS)
    return int(ver_ele.text)


def get_droid_signatures(version):
    """
    Get a DROID signature file by version.

    Return a tuple comprising the requested signature XML file as string
    and a count of the FileFormat elements contained as an integer.
    Upon error, write to `stderr` and return the tuple [], False.
    """
    xml = []
    format_count = False
    try:
        with urllib.request.urlopen('https://www.nationalarchives.gov.uk/documents/DROID_SignatureFile_V{}.xml'.format(version)) as f:
            xml = f.read().decode('utf-8')
            root_ele = ET.fromstring(xml)
            format_count = len(root_ele.findall('.//{http://www.nationalarchives.gov.uk/pronom/SignatureFile}FileFormat'))
    except HTTPError as httpe:
        sys.stderr.write("get_droid_signatures(): could not download signature file v{} due to exception: {}\n".format(version, httpe))
    return xml, format_count


def _get_soap_ele_tree(soap_action):
    soap_string = '{}<soap:Envelope xmlns:xsi="{}" xmlns:xsd="{}" xmlns:soap="{}"><soap:Body><{} xmlns="{}" /></soap:Body></soap:Envelope>'.format(XML_PROC, NS.get('xsi'), NS.get('xsd'), NS.get('soap'), soap_action, PRONOM_NS).encode(ENCODING)
    soap_action = '\"{}:{}In\"'.format(PRONOM_NS, soap_action)
    xml = _get_soap_response(soap_action, soap_string)
    for prefix, uri in NS.items():
        ET.register_namespace(prefix, uri)
    return ET.fromstring(xml)


def _get_soap_response(soap_action, soap_string):
    try:
        req = urllib.request.Request('http://{}/pronom/service.asmx'.format(PRONOM_HOST), data=soap_string)
    except URLError:
        print('There was a problem contacting the PRONOM service at http://{}/pronom/service.asmx.'.format(PRONOM_HOST))
        print('Please check your network connection and try again.')
        sys.exit(1)
    for key, value in HEADERS.items():
        req.add_header(key, value)
    req.add_header('Content-length', '%d' % len(soap_string))
    req.add_header('SOAPAction', soap_action)
    response = urllib.request.urlopen(req)
    return response.read().decode(ENCODING)
