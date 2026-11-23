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

import http.client
import sys
import urllib.request
from xml.etree import ElementTree as ET

from defusedxml.ElementTree import fromstring

from fido import __version__
from fido.pronom import HTTP_TIMEOUT_SECONDS

ENCODING = "utf-8"
XML_PROC = '<?xml version="1.0" encoding="{}"?>'.format(ENCODING)
TNA_DOMAIN = "nationalarchives.gov.uk"
PRONOM_HOST = "www.{}".format(TNA_DOMAIN)
PRONOM_NS = "http://pronom.{}".format(TNA_DOMAIN)
SIG_NS = "http://{}/pronom/SignatureFile".format(PRONOM_HOST)

NS = {
    "soap": "http://schemas.xmlsoap.org/soap/envelope/",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "xsd": "http://www.w3.org/2001/XMLSchema",
    "pronom": PRONOM_NS,
    "sig": SIG_NS,
}

HEADERS = {
    "Host": PRONOM_HOST,
    "User-Agent": "PRONOM UTILS v{0} (OPF)".format(__version__),
    "Content-type": 'text/xml; charset="UTF-8"',
}


def get_sig_xml_for_puid(puid):
    """Return the full PRONOM signature XML for the passed PUID."""
    req = urllib.request.Request("http://www.nationalarchives.gov.uk/pronom/{}.xml".format(puid))
    response = urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS)  # nosec B310  # fixed TNA URL
    xml = response.read()
    return xml


def get_pronom_sig_version():
    """
    Get PRONOM signature version.

    Return latest signature file version number as an int.
    Exits with a message naming the service URL if it cannot be reached.
    """
    tree = _get_soap_ele_tree("getSignatureFileVersionV1")
    ver_ele = tree.find(".//pronom:Version/pronom:Version", NS)
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
        with urllib.request.urlopen(  # nosec B310  # fixed TNA URL
            "https://www.nationalarchives.gov.uk/documents/DROID_SignatureFile_V{}.xml".format(version),
            timeout=HTTP_TIMEOUT_SECONDS,
        ) as f:
            xml = f.read().decode("utf-8")
            root_ele = fromstring(xml)
            format_count = len(
                root_ele.findall(".//{http://www.nationalarchives.gov.uk/pronom/SignatureFile}FileFormat")
            )
    except (OSError, http.client.HTTPException) as err:
        sys.stderr.write(
            "get_droid_signatures(): could not download signature file v{} due to exception: {}\n".format(
                version, err
            )
        )
    return xml, format_count


def _get_soap_ele_tree(soap_action):
    soap_string = '{}<soap:Envelope xmlns:xsi="{}" xmlns:xsd="{}" xmlns:soap="{}"><soap:Body><{} xmlns="{}" /></soap:Body></soap:Envelope>'.format(
        XML_PROC, NS.get("xsi"), NS.get("xsd"), NS.get("soap"), soap_action, PRONOM_NS
    ).encode(ENCODING)
    soap_action = '"{}:{}In"'.format(PRONOM_NS, soap_action)
    xml = _get_soap_response(soap_action, soap_string)
    for prefix, uri in NS.items():
        ET.register_namespace(prefix, uri)
    return fromstring(xml)


def _get_soap_response(soap_action, soap_string):
    url = f"https://{PRONOM_HOST}/pronom/service.asmx"
    req = urllib.request.Request(url, data=soap_string)
    for key, value in HEADERS.items():
        req.add_header(key, value)
    req.add_header("Content-length", "%d" % len(soap_string))
    req.add_header("SOAPAction", soap_action)
    try:
        response = urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS)  # nosec B310  # fixed TNA URL
        return response.read().decode(ENCODING)
    except (OSError, http.client.HTTPException) as err:
        sys.exit(
            f"There was a problem contacting the PRONOM service at {url}: {err}\n"
            "Please check your network connection and try again."
        )
