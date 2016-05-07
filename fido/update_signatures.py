#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FIDO SIGNATURE UPDATER.

Open Planets Foundation (http://www.openplanetsfoundation.org)
See License.txt for license information.
Download from: https://github.com/openplanets/fido/releases
Author: Maurice de Rooij (NANETH), 2012

FIDO uses the UK National Archives (TNA) PRONOM File Format and Container descriptions.
PRONOM is available from http://www.nationalarchives.gov.uk/pronom/.
"""

from __future__ import print_function

import os
import sys
import time
import urllib
from xml.etree import ElementTree as CET
import zipfile

from six.moves import input

from . import __version__
from .prepare import main as prepare_main
from .pronomutils import get_pronom_signature, check_well_formedness


defaults = {
    'version': __version__,
    'conf_dir': os.path.join(os.path.dirname(__file__), 'conf'),
    'tmp_dir': 'tmp',
    'signatureFileName': 'DROID_SignatureFile-v{0}.xml',
    'pronomZipFileName': 'pronom-xml-v{0}.zip',
    'fidoSignatureVersion': 'format_extensions.xml',
    'versionsFileName': 'versions.xml',
    'http_throttle': 0.5,  # in secs, to prevent DoS of PRONOM server
    'containerVersion': 'container-signature-20160121.xml',  # container version is frozen and needs human attention before updating
    'versionXML': """<?xml version="1.0" encoding="UTF-8"?>\n<versions>\n\t<pronomVersion>{0}</pronomVersion>\n\t<pronomSignature>{1}</pronomSignature>\n\t<pronomContainerSignature>{2}</pronomContainerSignature>\n\t<fidoExtensionSignature>{3}</fidoExtensionSignature>\n\t<updateScript>{4}</updateScript>\n</versions>"""
}


def main(defaults=defaults):
    """
    Update PRONOM signatures.

    Interactive script, requires keyboard input.
    """
    try:
        resume_download = False
        answers = ['y', 'yes']
        versionXML = defaults['versionXML'].format("{0}", "{1}", defaults['containerVersion'], defaults['fidoSignatureVersion'], defaults['version'])
        print("FIDO signature updater v{}".format(defaults['version']))
        print("Contacting PRONOM...")
        currentVersion = get_pronom_signature("version")
        if not currentVersion:
            print("Failed to obtain PRONOM signature file version number, please try again")
            sys.exit()
        print("Querying latest signaturefile version...")
        signatureFile = os.path.join(os.path.abspath(defaults['conf_dir']), defaults['signatureFileName'].format(currentVersion))
        if os.path.isfile(signatureFile):
            print("You already have the latest PRONOM signature file, version", currentVersion)
            ask = input("Update anyway? (yes/no): ")
            if ask.lower() not in answers:
                sys.exit()
        print("Downloading signature file version {}...".format(currentVersion))
        currentFile = get_pronom_signature("file")
        if not currentFile:
            print("Failed to obtain PRONOM signature file, please try again")
            exit()
        with open(signatureFile, 'wb') as file_:
            file_.write(currentFile)
        print("Writing {0}...".format(defaults['signatureFileName'].format(currentVersion)))
        print("Extracting PRONOM PUID's from signature file...")
        tree = CET.parse(signatureFile)
        puids = []
        for node in tree.iter("{http://www.nationalarchives.gov.uk/pronom/SignatureFile}FileFormat"):
            puids.append(node.get("PUID"))
        numberPuids = len(puids)
        print("Found {} PRONOM PUID's".format(numberPuids))
        print("Downloading signatures can take a while")
        ask = input("Continue and download signatures? (yes/no): ")
        if ask.lower() not in answers:
            print("Aborting update...")
            sys.exit()
        tmpdir = os.path.join(os.path.abspath(defaults['conf_dir']), defaults['tmp_dir'])
        if os.path.isdir(tmpdir):
            print("Found previously created temporary folder for download:", tmpdir)
            ask = input("Resume download (yes) or start over (no)?: ")
            if ask.lower() in answers:
                print("Resuming download...")
                resume_download = True
            else:
                resume_download = False
        else:
            print("Creating temporary folder for download:", tmpdir)
            try:
                os.mkdir(tmpdir)
            except:
                pass
        if not os.path.isdir(tmpdir):
            tmpdir = os.path.join(os.path.abspath(defaults['conf_dir']))
            print("Failed to create temporary folder for PUID's, using", tmpdir)
        print("Downloading signatures, one moment please...")
        one_percent = (float(numberPuids) / 100)
        numfiles = 0
        for puid in puids:
            puidType, puidNum = puid.split("/")
            puidFileName = "puid." + puidType + "." + puidNum + ".xml"
            filename = os.path.join(tmpdir, puidFileName)
            if os.path.isfile(filename) and check_well_formedness(filename) and resume_download is not False:
                numfiles += 1
                continue
            puidUrl = "http://www.nationalarchives.gov.uk/pronom/{}.xml".format(puid)
            try:
                filehandle = urllib.urlopen(puidUrl)
            except Exception as e:
                print("Failed to download signature file:", puidUrl)
                print("Error:", str(e))
                print("Please restart and resume download")
                sys.exit()
            with open(filename, 'wb') as file_:
                for lines in filehandle.readlines():
                    file_.write(lines)
            filehandle.close()
            if not check_well_formedness(filename):
                os.unlink(filename)
                continue
            numfiles += 1
            percent = int(float(numfiles) / one_percent)
            status = r"{}/{} files [{}%]".format(numfiles, numberPuids, percent)
            print(status)
            time.sleep(defaults['http_throttle'])

        print("100%")
        compression = zipfile.ZIP_DEFLATED if 'zlib' in sys.modules else zipfile.ZIP_STORED
        modes = {zipfile.ZIP_DEFLATED: 'deflated', zipfile.ZIP_STORED: 'stored'}
        print("Creating PRONOM zip...")
        zf = zipfile.ZipFile(os.path.join(os.path.abspath(defaults['conf_dir']), defaults['pronomZipFileName'].format(currentVersion)), mode='w')
        print("Adding files with compression mode '{}'", modes[compression])
        for puid in puids:
            puidType, puidNum = puid.split("/")
            puidFileName = "puid.{}.{}.xml".format(puidType, puidNum)
            filename = os.path.join(os.path.abspath(defaults['conf_dir']), defaults['tmp_dir'], puidFileName)
            if os.path.isfile(filename):
                zf.write(filename, arcname=puidFileName, compress_type=compression)
                os.unlink(filename)
        zf.close()
        print("Deleting temporary folder and files...")
        try:
            for root, dirs, files in os.walk(tmpdir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
                os.rmdir(tmpdir)
        except:
            pass
        # update versions.xml
        versionsFile = os.path.join(os.path.abspath(defaults['conf_dir']), defaults['versionsFileName'])
        print("Updating {0}...".format(defaults['versionsFileName']))
        with open(versionsFile, 'wb') as file_:
            file_.write(versionXML.format(str(currentVersion), "formats-v" + str(currentVersion) + ".xml"))
        print("Preparing to convert PRONOM formats to FIDO signatures...")
        # there should be a check here to handle prepare.main exit() signal (-1/0/1/...)
        prepare_main()
        print("FIDO signatures successfully updated")
        sys.exit()
    except KeyboardInterrupt:
        print("Aborting update!")
        sys.exit()


if __name__ == '__main__':
    main(defaults)
