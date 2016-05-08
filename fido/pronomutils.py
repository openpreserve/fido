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
from xml.parsers.expat import ExpatError, ParserCreate

from six.moves import http_client

from . import __version__


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
