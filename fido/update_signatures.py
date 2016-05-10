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
from shutil import rmtree
import sys
import time
from xml.etree import ElementTree as CET
import zipfile

from six.moves.urllib.request import urlopen

from . import __version__, CONFIG_DIR, query_yes_no
from .prepare import main as prepare_pronom_to_fido
from .pronomutils import check_well_formedness, get_local_pronom_versions, get_pronom_signature


defaults = {
    'tmp_dir': os.path.join(CONFIG_DIR, 'tmp'),
    'signatureFileName': 'DROID_SignatureFile-v{0}.xml',
    'pronomZipFileName': 'pronom-xml-v{0}.zip',
    'fidoSignatureVersion': 'format_extensions.xml',
    'http_throttle': 0.5,  # in secs, to prevent DoS of PRONOM server
    'containerVersion': 'container-signature-20160121.xml',  # container version is frozen and needs human attention before updating
}


def main(defaults=defaults):
    """
    Update PRONOM signatures.

    Interactive script, requires keyboard input.
    """
    print("FIDO signature updater v{}".format(__version__))

    try:
        print("Contacting PRONOM...")
        currentVersion = get_pronom_signature("version")
        if not currentVersion:
            sys.exit('Failed to obtain PRONOM signature file version number, please try again.')

        print("Querying latest signaturefile version...")
        signatureFile = os.path.join(CONFIG_DIR, defaults['signatureFileName'].format(currentVersion))
        if os.path.isfile(signatureFile):
            print("You already have the latest PRONOM signature file, version", currentVersion)
            if not query_yes_no("Update anyway?"):
                sys.exit('Aborting update...')

        print("Downloading signature file version {}...".format(currentVersion))
        currentFile = get_pronom_signature("file")
        if not currentFile:
            sys.exit('Failed to obtain PRONOM signature file, please try again.')
        print("Writing {0}...".format(defaults['signatureFileName'].format(currentVersion)))
        with open(signatureFile, 'wb') as file_:
            file_.write(currentFile)

        print("Extracting PRONOM PUID's from signature file...")
        tree = CET.parse(signatureFile)
        puids = []
        for node in tree.iter("{http://www.nationalarchives.gov.uk/pronom/SignatureFile}FileFormat"):
            puids.append(node.get("PUID"))
        numberPuids = len(puids)
        print("Found {} PRONOM PUID's".format(numberPuids))

        print("Downloading signatures can take a while")
        if not query_yes_no("Continue and download signatures?"):
            sys.exit('Aborting update...')
        tmpdir = defaults['tmp_dir']
        if os.path.isdir(tmpdir):
            print("Found previously created temporary folder for download:", tmpdir)
            resume_download = query_yes_no('Do you want to resume download (yes) or start over (no)?')
            if resume_download:
                print("Resuming download...")
        else:
            print("Creating temporary folder for download:", tmpdir)
            try:
                os.mkdir(tmpdir)
            except:
                pass
        if not os.path.isdir(tmpdir):
            print("Failed to create temporary folder for PUID's, using", tmpdir)

        print("Downloading signatures, one moment please...")
        one_percent = (float(numberPuids) / 100)
        numfiles = 0
        for puid in puids:
            puidType, puidNum = puid.split("/")
            puidFileName = "puid." + puidType + "." + puidNum + ".xml"
            filename = os.path.join(tmpdir, puidFileName)
            if os.path.isfile(filename) and check_well_formedness(filename) and resume_download:
                numfiles += 1
                continue
            puid_url = "http://www.nationalarchives.gov.uk/pronom/{}.xml".format(puid)
            try:
                filehandle = urlopen(puid_url)
            except Exception as e:
                print("Failed to download signature file:", puid_url)
                print("Error:", str(e))
                sys.exit('Please restart and resume download.')
            with open(filename, 'wb') as file_:
                for lines in filehandle.readlines():
                    file_.write(lines)
            filehandle.close()
            if not check_well_formedness(filename):
                os.unlink(filename)
                continue
            numfiles += 1
            percent = int(float(numfiles) / one_percent)
            print(r"{}/{} files [{}%]".format(numfiles, numberPuids, percent))
            time.sleep(defaults['http_throttle'])
        print("100%")

        print("Creating PRONOM zip...")
        compression = zipfile.ZIP_DEFLATED if 'zlib' in sys.modules else zipfile.ZIP_STORED
        modes = {zipfile.ZIP_DEFLATED: 'deflated', zipfile.ZIP_STORED: 'stored'}
        zf = zipfile.ZipFile(os.path.join(CONFIG_DIR, defaults['pronomZipFileName'].format(currentVersion)), mode='w')
        print("Adding files with compression mode", modes[compression])
        for puid in puids:
            puidType, puidNum = puid.split("/")
            puidFileName = "puid.{}.{}.xml".format(puidType, puidNum)
            filename = os.path.join(tmpdir, puidFileName)
            if os.path.isfile(filename):
                zf.write(filename, arcname=puidFileName, compress_type=compression)
                os.unlink(filename)
        zf.close()

        print("Deleting temporary folder and files...")
        rmtree(tmpdir, ignore_errors=True)

        print('Updating versions.xml...')
        versions = get_local_pronom_versions()
        versions.pronom_version = str(currentVersion)
        versions.pronom_signature = "formats-v" + str(currentVersion) + ".xml"
        versions.pronom_container_signature = defaults['containerVersion']
        versions.fido_extension_signature = defaults['fidoSignatureVersion']
        versions.update_script = __version__
        versions.write()

        # TODO: there should be a check here to handle prepare.main exit() signal (-1/0/1/...)
        print("Preparing to convert PRONOM formats to FIDO signatures...")
        prepare_pronom_to_fido()
        print("FIDO signatures successfully updated")

    except KeyboardInterrupt:
        sys.exit('Aborting update...')


if __name__ == '__main__':
    main(defaults)
