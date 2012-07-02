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
import sys, os, urllib, time, zipfile, shutil

from xml.etree import ElementTree as CET
from xml.etree import ElementTree as VET
from pronomutils import getPronomSignature, checkWellFormedness
import prepare

defaults = {
    'version': '1.2.0',
    'conf_dir': os.path.join(os.path.dirname(__file__), 'conf'),
    'tmp_dir': 'tmp', 
    'signatureFileName' : 'DROID_SignatureFile-v{0}.xml',
    'pronomZipFileName' : 'pronom-xml-v{0}.zip',
    'fidoSignatureVersion' : 'format_extensions.xml', 
    'versionsFileName' : 'versions.xml',
    'http_throttle' : 0.5, # in secs, to prevent DoS of PRONOM server
    'containerVersion' : 'container-signature-20110204.xml', # container version is kind of frozen and needs human attention before updating
    'versionXML' : """<?xml version="1.0" encoding="UTF-8"?>\n<versions>\n\t<pronomVersion>{0}</pronomVersion>\n\t<pronomSignature>{1}</pronomSignature>\n\t<pronomContainerSignature>{2}</pronomContainerSignature>\n\t<fidoExtensionSignature>{3}</fidoExtensionSignature>\n\t<updateScript>{4}</updateScript>\n</versions>"""
    }

def main(defaults):
    """
        Updates PRONOM signatures
        Interactive script, requires keyboard input
    """
    try:
        resume_download = False
        answers = ['y','yes']
        versionXML = defaults['versionXML'].format("{0}","{1}",defaults['containerVersion'],defaults['fidoSignatureVersion'],defaults['version'])
        #print versionXML
        print "FIDO signature updater v"+defaults['version']
        print "Contacting PRONOM..."
        currentVersion = getPronomSignature("version")
        if currentVersion == False:
            print "Failed to obtain PRONOM signature file version number, please try again"
            sys.exit()
        print "Querying latest signaturefile version..."
        signatureFile = os.path.join(os.path.abspath(defaults['conf_dir']), defaults['signatureFileName'].format(currentVersion))
        versionsFile = os.path.join(os.path.abspath(defaults['conf_dir']), defaults['versionsFileName'])
        if os.path.isfile(signatureFile):
            print "You already have the latest PRONOM signature file, version "+str(currentVersion)
            ask = raw_input("Update anyway? (yes/no): ")
            if ask.lower() not in answers:
                sys.exit()
        print "Updating {0}...".format(defaults['versionsFileName'])
        xmlversionsfile = open(versionsFile,'wb')
        xmlversionsfile.write(versionXML.format(str(currentVersion),"formats-v"+str(currentVersion)+".xml"))
        xmlversionsfile.close()
        print "Downloading signature file version "+str(currentVersion)+"..."
        currentFile = getPronomSignature("file")
        if currentFile == False:
            print "Failed to obtain PRONOM signature file, please try again"
            exit()
        sigfile = open(signatureFile,'wb')
        sigfile.write(currentFile)
        sigfile.close()
        print "Writing {0}...".format(defaults['signatureFileName'].format(currentVersion))
        print "Extracting PRONOM PUID's from signature file..."
        tree = CET.parse(signatureFile)
        puids = []
        for node in tree.iter("{http://www.nationalarchives.gov.uk/pronom/SignatureFile}FileFormat"):
            puids.append(node.get("PUID"))
        numberPuids = len(puids)
        print "Found "+str(numberPuids)+" PRONOM PUID's"
        print "Downloading signatures can take a while"
        ask = raw_input("Continue and download signatures? (yes/no): ")
        if ask.lower() not in answers:
            print "Aborting update..."
            sys.exit()
        tmpdir = os.path.join(os.path.abspath(defaults['conf_dir']), defaults['tmp_dir'])
        if os.path.isdir(tmpdir):
            print "Found previously created temporary folder for download:", tmpdir
            ask = raw_input("Resume download (yes) or start over (no)?: ")
            if ask.lower() in answers:
                print "Resuming download..."
                resume_download = True
            else:
                resume_download = False
        else:
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
            puidFileName = "puid."+puidType+"."+puidNum+".xml"
            filename = os.path.join(tmpdir, puidFileName)
            if os.path.isfile(filename) and checkWellFormedness(filename) and resume_download is not False:
                numfiles += 1
                continue
            puidUrl = "http://www.nationalarchives.gov.uk/pronom/"+puid+".xml"
            try:
                filehandle = urllib.urlopen(puidUrl)
            except Exception, e:
                print "Failed to download signaturefile:", puidUrl
                print "Error:", str(e)
                print "Please restart and resume download"
                sys.exit()
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
        zf = zipfile.ZipFile(os.path.join(os.path.abspath(defaults['conf_dir']), defaults['pronomZipFileName'].format(currentVersion)), mode='w')
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
    except KeyboardInterrupt:
        print "\nAborting update"
        sys.exit()

if __name__ == '__main__':
    main(defaults)
