#!python
# -*- coding: utf-8 -*-
#
# FIDO SIGNATURE UPDATER  
#
# Open Planets Foundation (http://www.openplanetsfoundation.org)
# See License.txt for license information.
# Download from: http://github.com/openplanets/fido/downloads
# Author: Maurice de Rooij (NANETH), 2012
#        
# FIDO uses the UK National Archives (TNA) PRONOM File Format and Container descriptions .
# PRONOM is available from http://www.nationalarchives.gov.uk/pronom/
#
import sys, os, urllib, time, zipfile
from xml.etree import ElementTree as CET
from opfpronomutils import getPronomSignature, checkWellFormedness
import prepare

defaults = {
    'version': '1.0',
    'conf_dir': os.path.join(os.path.dirname(__file__), 'conf'),
    'tmp_dir': 'tmp', 
    'signatureFileName' : 'DROID_SignatureFile_V{0}.xml',
    'pronomZipFile' : 'pronom-xml.zip',
    'http_throttle' : 0.5 # in secs, to prevent DoS of PRONOM server
    }    

def main():
    """
        Updates PRONOM signatures
    """
    global defaults
    print "FIDO signature updater v"+defaults['version']
    print "Contacting PRONOM..."
    currentVersion = getPronomSignature("version")
    if currentVersion == False:
        exit()
    print "Querying latest signaturefile version..."
    signatureFile = os.path.join(os.path.abspath(defaults['conf_dir']), defaults['signatureFileName'].format(currentVersion))
    if os.path.isfile(signatureFile):
        print "You already have the latest PRONOM signature file, version "+str(currentVersion)
        answers = {'y','yes'}
        ask = raw_input("Update anyway? (yes/no): ")
        if ask.lower() not in answers:
            sys.exit()
    print "Downloading signature file version "+str(currentVersion)+"..."
    currentFile = getPronomSignature("file")
    if currentFile == False:
        exit()
    sigfile = open(signatureFile,'wb')
    sigfile.write(currentFile)
    sigfile.close()
    print "Extracting PRONOM PUID's from signature file..."
    tree = CET.parse(signatureFile)
    puids = []
    for node in tree.iter("{http://www.nationalarchives.gov.uk/pronom/SignatureFile}FileFormat"):
        puids.append(node.get("PUID"))
    numberPuids = len(puids)
    print "Found "+str(numberPuids)+" PRONOM PUID's"
    print "Downloading signatures can take a while"
    answers = {'y','yes'}
    ask = raw_input("Continue and download signatures? (yes/no): ")
    if ask.lower() not in answers:
        print "Aborting update..."
        sys.exit()
    tmpdir = os.path.join(os.path.abspath(defaults['conf_dir']), defaults['tmp_dir'])
    print "Creating temporary folder for download:", tmpdir
    try:
        os.mkdir(tmpdir)
    except:
        pass
    if not os.path.isdir(tmpdir):
        tmpdir = os.path.join(os.path.abspath(defaults['conf_dir']))
        print "Failed to create temporary folder for PUID's, using", tmpdir
    print "Downloading signatures, one moment please..."
    one_percent = (float(numberPuids) / 100)
    numfiles = 0
    for puid in puids:
        puidType, puidNum = puid.split("/")
        filehandle = urllib.urlopen('http://www.nationalarchives.gov.uk/pronom/'+puid+'.xml')
        puidFileName = "puid."+puidType+"."+puidNum+".xml"
        filename = os.path.join(os.path.abspath(defaults['conf_dir']), defaults['tmp_dir'], puidFileName)
        puidfile = open(filename,'wb')
        for lines in filehandle.readlines():
                puidfile.write(lines)
        puidfile.close()
        filehandle.close()
        if not checkWellFormedness(filename):
            os.unlink(filename)
            continue
        numfiles += 1
        percent = int(float(numfiles) / one_percent)
        print "\b\b\b\b\b",
        print str(percent)+"%",
        time.sleep(defaults['http_throttle'])
    print "\b\b\b\b\b",
    print "100%"
    try:
        import zlib
        compression = zipfile.ZIP_DEFLATED
    except:
        compression = zipfile.ZIP_STORED
    modes = {zipfile.ZIP_DEFLATED: 'deflated', zipfile.ZIP_STORED:   'stored'}
    print "Creating PRONOM zip,",
    zf = zipfile.ZipFile(os.path.join(os.path.abspath(defaults['conf_dir']), defaults['pronomZipFile']), mode='w')
    print "adding files with compression mode '"+modes[compression]+"'"
    for puid in puids:
        puidType, puidNum = puid.split("/")
        puidFileName = "puid."+puidType+"."+puidNum+".xml"
        filename = os.path.join(os.path.abspath(defaults['conf_dir']), defaults['tmp_dir'], puidFileName)
        if os.path.isfile(filename):
            zf.write(filename, arcname=puidFileName, compress_type=compression)
            os.unlink(filename)
    zf.close()
    print "Deleting temporary folder and files..."
    try:
        for root, dirs, files in os.walk(tmpdir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
            os.rmdir(tmpdir)
    except:
        pass
    print "Preparing to convert PRONOM formats to FIDO signatures..."
    prepare.main()
    print "FIDO signatures successfully updated"
    sys.exit()

if __name__ == '__main__':
    main()
