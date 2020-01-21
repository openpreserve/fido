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

from argparse import ArgumentParser
import os
from shutil import rmtree
import sys
import time
from xml.etree import ElementTree as CET
import zipfile

from six.moves.urllib.request import urlopen
from six.moves.urllib.error import URLError

from . import __version__, CONFIG_DIR, query_yes_no
from .prepare import run as prepare_pronom_to_fido
from .pronomutils import check_well_formedness, get_local_pronom_versions, get_pronom_signature


DEFAULTS = {
    'signatureFileName': 'DROID_SignatureFile-v{0}.xml',
    'pronomZipFileName': 'pronom-xml-v{0}.zip',
    'fidoSignatureVersion': 'format_extensions.xml',
    'containerVersion': 'container-signature-UPDATE-ME.xml',  # container version is frozen and needs human attention before updating,
}

OPTIONS = {
    'http_throttle': 0.5,  # in secs, to prevent DoS of PRONOM server
    'tmp_dir': os.path.join(CONFIG_DIR, 'tmp'),
    'deleteTempDirectory': True,
}


def run(defaults=None):
    """
    Update PRONOM signatures.

    Interactive script, requires keyboard input.
    """
    print("FIDO signature updater v{}".format(__version__))
    defaults = defaults or DEFAULTS
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
        with open(signatureFile, 'w') as file_:
            file_.write(currentFile)

        print("Extracting PRONOM PUID's from signature file...")
        tree = CET.parse(signatureFile)
        puids = []
        for node in tree.iter("{http://www.nationalarchives.gov.uk/pronom/SignatureFile}FileFormat"):
            puids.append(node.get("PUID"))
        print("Found {} PRONOM PUID's".format(len(puids)))

        print("Downloading signatures can take a while")
        if not query_yes_no("Continue and download signatures?"):
            sys.exit('Aborting update...')
        tmpdir = defaults['tmp_dir']
        resume_download = False
        if os.path.isdir(tmpdir):
            print("Found previously created temporary folder for download:", tmpdir)
            resume_download = query_yes_no('Do you want to resume download (yes) or start over (no)?')
            if resume_download:
                print("Resuming download...")
        else:
            print("Creating temporary folder for download:", tmpdir)
            try:
                os.mkdir(tmpdir)
            except OSError:
                pass
        if not os.path.isdir(tmpdir):
            sys.stderr.write("Failed to create temporary folder for PUID's, using: " + tmpdir)

        download_signatures(defaults, puids, resume_download, tmpdir)
        create_zip_file(defaults, puids, currentVersion, tmpdir)
        if defaults['deleteTempDirectory']:
            print("Deleting temporary folder and files...")
            rmtree(tmpdir, ignore_errors=True)

        update_versions_xml(defaults, currentVersion)

        # TODO: there should be a check here to handle prepare.main exit() signal (-1/0/1/...)
        print("Preparing to convert PRONOM formats to FIDO signatures...")
        prepare_pronom_to_fido()
        print("FIDO signatures successfully updated")

    except KeyboardInterrupt:
        sys.exit('Aborting update...')


def download_signatures(defaults, puids, resume_download, tmpdir):
    """Download PRONOM signatures and write to individual files."""
    print("Downloading signatures, one moment please...")
    numberPuids = len(puids)
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
        except URLError as e:
            sys.stderr.write("Failed to download signature file:" + puid_url)
            sys.stderr.write("Error:" + str(e))
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


def create_zip_file(defaults, puids, currentVersion, tmpdir):
    """Create zip file of signatures."""
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
            if defaults['deleteTempDirectory']:
                os.unlink(filename)
    zf.close()


def update_versions_xml(defaults, currentVersion):
    """Create new versions identified sig XML file."""
    print('Updating versions.xml...')
    versions = get_local_pronom_versions()
    versions.pronom_version = str(currentVersion)
    versions.pronom_signature = "formats-v" + str(currentVersion) + ".xml"
    versions.pronom_container_signature = defaults['containerVersion']
    versions.fido_extension_signature = defaults['fidoSignatureVersion']
    versions.update_script = __version__
    versions.write()


def main():
    """Main CLI entrypoint."""
    parser = ArgumentParser(description='Download and convert the latest PRONOM signatures')
    parser.add_argument('-tmpdir', default=OPTIONS['tmp_dir'], help='Location to store temporary files', dest='tmp_dir')
    parser.add_argument('-keep_tmp', default=OPTIONS['deleteTempDirectory'], help='Do not delete temporary files after completion', dest='deleteTempDirectory', action='store_false')
    parser.add_argument('-http_throttle', default=OPTIONS['http_throttle'], help='Time (in seconds) to wait between downloads', type=float, dest='http_throttle')
    args = parser.parse_args()
    opts = DEFAULTS.copy()
    opts.update(vars(args))

    run(opts)


if __name__ == '__main__':
    main()
