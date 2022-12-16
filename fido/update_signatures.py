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

from . import __version__, CONFIG_DIR, query_yes_no
from .prepare import run as prepare_pronom_to_fido
from .versions import get_local_versions
from .pronom.soap import get_pronom_sig_version, get_droid_signatures, NS
from .pronom.http import get_sig_xml_for_puid

ABORT_MSG = 'Aborting update...'

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
    'version': 'latest',
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
        latest, sig_file = sig_version_check(defaults.get('version'))
        download_sig_file(latest, sig_file)
        print("Extracting PRONOM PUID's from signature file...")
        tree = CET.parse(sig_file)
        format_eles = tree.findall('.//sig:FileFormat', NS)
        print("Found {} PRONOM FileFormat elements".format(len(format_eles)))
        tmpdir, resume = init_sig_download(defaults)
        download_signatures(defaults, format_eles, resume, tmpdir)
        create_zip_file(defaults, format_eles, latest, tmpdir)
        if defaults['deleteTempDirectory']:
            print("Deleting temporary folder and files...")
            rmtree(tmpdir, ignore_errors=True)
        update_versions_xml(latest)

        # TODO: there should be a check here to handle prepare.main exit() signal (-1/0/1/...)
        print("Preparing to convert PRONOM formats to FIDO signatures...")
        prepare_pronom_to_fido()
        print("FIDO signatures successfully updated")

    except KeyboardInterrupt:
        sys.exit(ABORT_MSG)


def sig_version_check(version='latest'):
    """Return a tuple consisting of current sig file version and the derived file name."""
    print('Sig version check for version:', version)
    if version == 'latest':
        print('Getting latest version number from PRONOM...')
        version = get_pronom_sig_version()
        if not version:
            sys.exit('Failed to obtain PRONOM signature file version number, please try again.')

    print('Querying PRONOM for signaturefile version {}.'.format(version))
    sig_file_name = _sig_file_name(version)
    if os.path.isfile(sig_file_name):
        print("You already have the PRONOM signature file, version", version)
        if not query_yes_no("Update anyway?"):
            sys.exit(ABORT_MSG)
    return version, sig_file_name


def _sig_file_name(version):
    return os.path.join(CONFIG_DIR, DEFAULTS['signatureFileName'].format(version))


def download_sig_file(version, sig_file):
    """Download the latest version of the PRONOM sigs to signatureFile."""
    print("Downloading signature file version {}...".format(version))
    sig_xml, _ = get_droid_signatures(version)
    if not sig_xml:
        sys.exit('Failed to obtain PRONOM signature file, please try again.')
    print("Writing {0}...".format(DEFAULTS['signatureFileName'].format(version)))
    with open(sig_file, 'w') as file_:
        file_.write(sig_xml)


def init_sig_download(defaults):
    """
    Initialise the download of individual PRONOM signatures.

    Handles user input and resumption of interupted downloads.
    Return a tuple of the temp directory for writing and a boolean resume flag.
    """
    print("Downloading signatures can take a while")
    if not query_yes_no("Continue and download signatures?"):
        sys.exit(ABORT_MSG)
    tmpdir = defaults['tmp_dir']
    resume = False
    if os.path.isdir(tmpdir):
        print("Found previously created temporary folder for download:", tmpdir)
        resume = query_yes_no('Do you want to resume download (yes) or start over (no)?')
        if resume:
            print("Resuming download...")
    else:
        print("Creating temporary folder for download:", tmpdir)
        try:
            os.mkdir(tmpdir)
        except OSError:
            pass
    if not os.path.isdir(tmpdir):
        sys.stderr.write("Failed to create temporary folder for PUID's, using: " + tmpdir)
    return tmpdir, resume


def download_signatures(defaults, format_eles, resume, tmpdir):
    """Download PRONOM signatures and write to individual files."""
    print("Downloading signatures, one moment please...")
    puid_count = len(format_eles)
    one_percent = (float(puid_count) / 100)
    numfiles = 0
    for format_ele in format_eles:
        download_sig(format_ele, tmpdir, resume, defaults)
        numfiles += 1
        print(r"Downloaded {}/{} files [{}%]".format(numfiles, puid_count, int(float(numfiles) / one_percent)), end="\r")
    print("100%")


def download_sig(format_ele, tmpdir, resume, defaults):
    """
    Download an individual PRONOM signature.

    The signature to be downloaded is identified by the FileFormat element
    parameter format_ele. The downloaded signature is written to tmpdir.
    """
    puid, puid_filename = get_puid_file_name(format_ele)
    filename = os.path.join(tmpdir, puid_filename)
    if os.path.isfile(filename) and resume:
        return
    try:
        xml = get_sig_xml_for_puid(puid)
    except Exception as e:
        sys.stderr.write("Failed to download signature file:" + puid)
        sys.stderr.write("Error:" + str(e))
        sys.exit('Please restart and resume download.')
    with open(filename, 'wb') as file_:
        file_.write(xml)
    time.sleep(defaults['http_throttle'])


def create_zip_file(defaults, format_eles, version, tmpdir):
    """Create zip file of signatures."""
    print("Creating PRONOM zip...")
    compression = zipfile.ZIP_DEFLATED if 'zlib' in sys.modules else zipfile.ZIP_STORED
    modes = {zipfile.ZIP_DEFLATED: 'deflated', zipfile.ZIP_STORED: 'stored'}
    zf = zipfile.ZipFile(os.path.join(CONFIG_DIR, DEFAULTS['pronomZipFileName'].format(version)), mode='w')
    print("Adding files with compression mode", modes[compression])
    for format_ele in format_eles:
        _, puid_filename = get_puid_file_name(format_ele)
        filename = os.path.join(tmpdir, puid_filename)
        if os.path.isfile(filename):
            zf.write(filename, arcname=puid_filename, compress_type=compression)
            if defaults['deleteTempDirectory']:
                os.unlink(filename)
    zf.close()


def get_puid_file_name(format_ele):
    """Return a tupe of PUID and PUID file name derived from format_ele."""
    puid = format_ele.get('PUID')
    type_part, num_part = puid.split("/")
    return puid, 'puid.{}.{}.xml'.format(type_part, num_part)


def update_versions_xml(version):
    """Create new versions identified sig XML file."""
    print('Updating versions.xml...')
    versions = get_local_versions()
    versions.pronom_version = str(version)
    versions.pronom_signature = "formats-v" + str(version) + ".xml"
    versions.pronom_container_signature = DEFAULTS['containerVersion']
    versions.fido_extension_signature = DEFAULTS['fidoSignatureVersion']
    versions.update_script = __version__
    versions.write()


def main():
    """Main CLI entrypoint."""
    parser = ArgumentParser(description='Download and convert the latest PRONOM signatures')
    parser.add_argument('-tmpdir', default=OPTIONS['tmp_dir'], help='Location to store temporary files', dest='tmp_dir')
    parser.add_argument('-keep_tmp', default=OPTIONS['deleteTempDirectory'], help='Do not delete temporary files after completion', dest='deleteTempDirectory', action='store_false')
    parser.add_argument('-http_throttle', default=OPTIONS['http_throttle'], help='Time (in seconds) to wait between downloads', type=float, dest='http_throttle')
    parser.add_argument('-version', default=OPTIONS['version'], help='Download and convert a specific signature file by version', dest='version')
    args = parser.parse_args()
    opts = DEFAULTS.copy()
    opts.update(vars(args))
    run(opts)


if __name__ == '__main__':
    main()
