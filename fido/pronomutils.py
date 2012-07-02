# -*- coding: utf-8 -*-
#
# PRONOM UTILS  
#
# PYTHON FUNCTION TO QUERY PRONOM VERSION 
# AND DOWNLOAD SIGNATUREFILE
# USES PRONOM SOAP SERVICE
#
# Open Planets Foundation (http://www.openplanetsfoundation.org)
# See License.txt for license information.
# Download from: http://github.com/openplanets/fido/downloads
# Author: Maurice de Rooij (OPF/NANETH), 2012
# 
# PRONOM UTILS is a library used by FIDO 
# FIDO uses the UK National Archives (TNA) PRONOM File Format and Container descriptions.
# PRONOM is available from http://www.nationalarchives.gov.uk/pronom/
#
import sys
from xml.dom import minidom
__pronomutils__ = {'version' : '1.0.1'}

def checkWellFormedness(filename,error=False):
    """
        usage: checkWellFormedness(filename)
        arguments:
        "filename": returns true if filename is a valid XML file
        "error": whether or not print to stderr upon error
    """
    import xml.parsers.expat
    parser = xml.parsers.expat.ParserCreate()
    try:
        parser.ParseFile(open(filename, "r"))
    except Exception, e:
        if error is not False:
            sys.stderr.write("checkWellFormedness: %s: %s;\n" % (filename, e))
        return False
    return True

def getPronomSignature(type):
    """
        usage: getPronomSignature(version|file)
        arguments:
        "version": returns latest signature file version number as int
        "file": returns latest signature XML file as string
        upon error: writes to stderr and returns false
    """
    try:
        import httplib
        import re
        import os
        soapVersionContainer = """<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><getSignatureFileVersionV1 xmlns="http://pronom.nationalarchives.gov.uk" /></soap:Body></soap:Envelope>"""
        soapFileContainer = """<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><getSignatureFileV1 xmlns="http://pronom.nationalarchives.gov.uk" /></soap:Body></soap:Envelope>"""
        soapVersionHeader = """\"http://pronom.nationalarchives.gov.uk:getSignatureFileVersionV1In\""""
        soapFileHeader = """\"http://pronom.nationalarchives.gov.uk:getSignatureFileV1In\""""
        if type == "version":
            soapAction = soapVersionHeader
            soapStr = soapVersionContainer
        elif type == "file":
            soapAction = soapFileHeader
            soapStr = soapFileContainer
        else:
            sys.stderr.write("getPronomSignature(): unknown type: "+type)
            return False
        webservice = httplib.HTTP("www.nationalarchives.gov.uk")
        webservice.putrequest("POST", "/pronom/service.asmx")
        webservice.putheader("Host", "www.nationalarchives.gov.uk")
        webservice.putheader("User-Agent", "PRONOM UTILS v{0} (OPF)".format(__pronomutils__['version']))
        webservice.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
        webservice.putheader("Content-length", "%d" % len(soapStr))
        webservice.putheader("SOAPAction", soapAction)
        try:
            webservice.endheaders()
        except Exception, e:
            sys.stderr.write("getPronomSignature(): failed to contact PRONOM;\n%s\n" % (e))
            sys.exit()
        webservice.send(soapStr)
        statuscode, statusmessage, header = webservice.getreply()
        if statuscode == 200:
            xml = webservice.getfile()
            if type == "version":
                exp = re.compile("\<Version\>([0-9]{1,4})\<\/Version\>")
                sigxml = exp.search(xml.read())
                if len(sigxml.group(1)) > 0:
                    return int(sigxml.group(1))
                else:
                    sys.stderr.write("getPronomSignature(): could not parse VERSION from SOAP response: "+type)
                    return False
            if type == "file":
                exp = re.compile("\<SignatureFile\>.*\<\/SignatureFile\>")
                sigxml = exp.search(xml.read())
                sigtxt = sigxml.group(0)
                if len(sigtxt) > 0:
                    tmpfile = "./tmp_getPronomSignature.xml"
                    tmp = open(tmpfile,'wb')
                    tmp.write("""<?xml version="1.0" encoding="UTF-8"?>"""+"\n")
                    tmp.write(sigtxt)
                    tmp.close()
                    if not checkWellFormedness(tmpfile):
                        os.unlink(tmpfile)
                        sys.stderr.write("getPronomSignature(): signaturefile not well formed")
                        return False
                    else:
                        os.unlink(tmpfile)
                        return """<?xml version="1.0" encoding="UTF-8"?>"""+"\n"+sigtxt
                else:
                    sys.stderr.write("getPronomSignature(): could not parse XML from SOAP response: "+type)
                    return False
        else:
            sys.stderr.write("getPronomSignature(): webservice error: '"+str(statuscode)+" "+statusmessage+"'\n")
            return False
        print sys.stderr.write("getPronomSignature(): unexpected return")
        return False
    except Exception, e:
        print sys.stderr.write("getPronomSignature(): unknown error:",e)
        return False
