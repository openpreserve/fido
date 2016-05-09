# -*- coding: utf-8 -*-

"""
PRONOM UTILS.

PYTHON FUNCTION TO QUERY PRONOM VERSION
AND DOWNLOAD SIGNATUREFILE
USES PRONOM SOAP SERVICE

Open Planets Foundation (http://www.openplanetsfoundation.org)
See License.txt for license information.
Download from: http://github.com/openplanets/fido/downloads
Author: Maurice de Rooij (OPF/NANETH), 2012

PRONOM UTILS is a library used by FIDO.
FIDO uses the UK National Archives (TNA) PRONOM File Format and Container descriptions.
PRONOM is available from http://www.nationalarchives.gov.uk/pronom/
"""

from __future__ import absolute_import

import os
import re
import sys
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import parse, ParseError
from xml.parsers.expat import ExpatError, ParserCreate

import six
from six.moves import http_client

from . import __version__, CONFIG_DIR


def check_well_formedness(filename, error=False):
    """
    Check if a given file contains valid XML.

    :param filename: file from which the XML is read.
    :param error: whether or not print to `stderr` upon error.
    :returns: whether the file contains valid XML.
    """
    parser = ParserCreate()
    try:
        parser.ParseFile(open(filename, "r"))
    except ExpatError as e:
        if error is not False:
            sys.stderr.write("check_well_formedness: %s: %s;\n" % (filename, e))
        return False
    return True


def get_pronom_signature(type_):
    """
    Get PRONOM signature.

    Return latest signature file version number as int when `type_` equals
    "version" or return latest signature XML file as string when `type_` equals
    "file". Upon error, write to `stderr` and returls `False`.
    """
    try:
        soapVersionContainer = """<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><getSignatureFileVersionV1 xmlns="http://pronom.nationalarchives.gov.uk" /></soap:Body></soap:Envelope>"""
        soapFileContainer = """<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><getSignatureFileV1 xmlns="http://pronom.nationalarchives.gov.uk" /></soap:Body></soap:Envelope>"""
        soapVersionHeader = """\"http://pronom.nationalarchives.gov.uk:getSignatureFileVersionV1In\""""
        soapFileHeader = """\"http://pronom.nationalarchives.gov.uk:getSignatureFileV1In\""""
        if type_ == "version":
            soapAction = soapVersionHeader
            soapStr = soapVersionContainer
        elif type_ == "file":
            soapAction = soapFileHeader
            soapStr = soapFileContainer
        else:
            sys.stderr.write("get_pronom_signature(): unknown type: " + type_)
            return False
        webservice = http_client.HTTP("apps.nationalarchives.gov.uk")
        webservice.putrequest("POST", "/pronom/service.asmx")
        webservice.putheader("Host", "www.nationalarchives.gov.uk")
        webservice.putheader("User-Agent", "PRONOM UTILS v{0} (OPF)".format(__version__))
        webservice.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
        webservice.putheader("Content-length", "%d" % len(soapStr))
        webservice.putheader("SOAPAction", soapAction)
        try:
            webservice.endheaders()
        except Exception as e:
            sys.stderr.write("get_pronom_signature(): failed to contact PRONOM;\n%s\n" % (e))
            sys.exit()
        webservice.send(soapStr)
        statuscode, statusmessage, header = webservice.getreply()
        if statuscode == 200:
            xml = webservice.getfile()
            if type_ == "version":
                exp = re.compile("\<Version\>([0-9]{1,4})\<\/Version\>")
                sigxml = exp.search(xml.read())
                if len(sigxml.group(1)) > 0:
                    return int(sigxml.group(1))
                else:
                    sys.stderr.write("get_pronom_signature(): could not parse VERSION from SOAP response: " + type_)
                    return False
            if type_ == "file":
                exp = re.compile("\<SignatureFile\>.*\<\/SignatureFile\>")
                sigxml = exp.search(xml.read())
                sigtxt = sigxml.group(0) if sigxml else ''
                if len(sigtxt) > 0:
                    tmpfile = "./tmp_getPronomSignature.xml"
                    with open(tmpfile, 'wb') as file_:
                        file_.write("""<?xml version="1.0" encoding="UTF-8"?>""" + "\n")
                        file_.write(sigtxt)
                    if not check_well_formedness(tmpfile):
                        os.unlink(tmpfile)
                        sys.stderr.write("get_pronom_signature(): signaturefile not well formed")
                        return False
                    else:
                        os.unlink(tmpfile)
                        return """<?xml version="1.0" encoding="UTF-8"?>""" + "\n" + sigtxt
                else:
                    sys.stderr.write("get_pronom_signature(): could not parse XML from SOAP response: " + type_)
                    return False
        else:
            sys.stderr.write("get_pronom_signature(): webservice error: '" + str(statuscode) + " " + statusmessage + "'\n")
            return False
        sys.stderr.write("get_pronom_signature(): unexpected return")
        return False
    except Exception as e:
        sys.stderr.write("get_pronom_signature(): unknown error: " + str(e))
        return False


class LocalPronomVersions(object):
    """
    Parse local PRONOM signature versions XML file.

    This is how the XML document should look like:

    <?xml version="1.0" encoding="UTF-8"?>
    <versions>
        <pronomVersion>84</pronomVersion>
        <pronomSignature>formats-v84.xml</pronomSignature>
        <pronomContainerSignature>container-signature-20160121.xml</pronomContainerSignature>
        <fidoExtensionSignature>format_extensions.xml</fidoExtensionSignature>
        <updateScript>1.2.2</updateScript>
    </versions>
    """

    PROPS_MAPPING = {
        'pronom_version': 'pronomVersion',
        'pronom_signature': 'pronomSignature',
        'pronom_container_signature': 'pronomContainerSignature',
        'fido_extension_signature': 'fidoExtensionSignature',
        'update_script': 'updateScript',
    }

    ROOT_ELEMENT = 'versions'

    def __init__(self, versions_file):
        """Instantiate class based on the file indicated in `versions_file`."""
        self.versions_file = versions_file
        self.conf_dir = os.path.abspath(os.path.dirname(versions_file))
        try:
            self.tree = parse(versions_file)
            self.root = self.tree.getroot()
        except (ParseError, IOError):
            self.root = ET.Element(self.ROOT_ELEMENT)
            self.tree = ET.ElementTree(self.root)

    def __getattr__(self, name):
        """Extract the element's text content."""
        if name in self.PROPS_MAPPING:
            return self.root.find(self.PROPS_MAPPING[name]).text

    def __setattr__(self, name, value):
        """Update the element's text content."""
        if name in self.PROPS_MAPPING:
            try:
                self.root.find(self.PROPS_MAPPING[name]).text = value
            except AttributeError:
                elem = ET.SubElement(self.root, self.PROPS_MAPPING[name])
                elem.text = value
        else:
            object.__setattr__(self, name, value)

    def get_zip_file(self):
        """Obtain location to the PRONOM XML Zip file based on the current PRONOM version."""
        return os.path.join(self.conf_dir, 'pronom-xml-v{}.zip'.format(self.pronom_version))

    def get_signature_file(self):
        """Obtain location to the current PRONOM signature file."""
        return os.path.join(self.conf_dir, self.pronom_signature)

    def write(self):
        """Update versions.xml."""
        # Check that all the fields are defined
        for key, value in six.iteritems(self.PROPS_MAPPING):
            if self.root.find(value) is None:
                raise ValueError('Field {} has not been defined!'.format(key))
        self.tree.write(self.versions_file, xml_declaration=True, method='xml', encoding='utf-8')


def get_local_pronom_versions(config_dir=CONFIG_DIR):
    """Return an instance of LocalPronomVersions loaded with `conf/versions.xml`."""
    return LocalPronomVersions(os.path.join(config_dir, 'versions.xml'))
