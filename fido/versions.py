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

import requests
import six
import importlib_resources
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import parse, ParseError

import six

from fido import CONFIG_DIR


class LocalVersions(object):
    """
    Parse local versions XML file.

    This is what the XML document should look like:

    <?xml version="1.0" encoding="UTF-8"?>
    <versions>
        <pronomVersion>84</pronomVersion>
        <pronomSignature>formats-v84.xml</pronomSignature>
        <pronomContainerSignature>container-signature-20160121.xml</pronomContainerSignature>
        <fidoExtensionSignature>format_extensions.xml</fidoExtensionSignature>
        <updateScript>1.2.2</updateScript>
        <updateSite>https://fidosigs.openpreservation.org</updateSite>
    </versions>
    """

    PROPS_MAPPING = {
        'pronom_version': 'pronomVersion',
        'pronom_signature': 'pronomSignature',
        'pronom_container_signature': 'pronomContainerSignature',
        'fido_extension_signature': 'fidoExtensionSignature',
        'update_script': 'updateScript',
        'update_site': 'updateSite',
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

def get_local_versions(config_dir=CONFIG_DIR):
    """Return an instance of LocalVersions loaded with `conf/versions.xml`."""
    return LocalVersions(os.path.join(config_dir, 'versions.xml'))

def sig_file_actions(sig_act):
    versions = get_local_versions()
    sig_vers = versions.pronom_version
    update_url = versions.update_site
    if not update_url.endswith('/'):
        update_url+='/'
    if sig_act == 'check':
        is_new, latest = _version_check(sig_vers, update_url)
        if is_new:
            print('Updated signatures v{} are available, current version is v{}'.format(latest, sig_vers))
        else:
            print('Your signature files are up to date, current version is v{}'.format(sig_vers))
    elif sig_act == 'list':
        resp = requests.get(update_url + 'format/')
        tree = ET.fromstring(resp.content)
        print('Available signature versions')
        for child in tree.iter('signature'):
            print(child.get('version'))
    elif sig_act == 'update':
        is_new, latest = _version_check(sig_vers, update_url)
        if not is_new:
            print('Your signature files are up to date, current version is v{}'.format(sig_vers))
            sys.exit(0)
        print('Updated signatures v{} are available, current version is v{}'.format(latest, sig_vers))
        _output_details(latest, update_url, versions)
    else:
        ver = sig_act
        if not ver.startswith('v'):
            ver = 'v' + sig_act
        resp = requests.get(update_url + 'format/' + ver + '/')
        if resp.status_code != 200:
            print('No signature files found for {}, REST status {}'.format(sig_act, resp.status_code))
            sys.exit(1)
        _output_details(re.search('\d+|$', ver).group(), update_url, versions)


def _output_details(version, update_url, versions):
    print('Updating signatures')
    _write_sigs(version, update_url, 'fido', 'formats-v{}.xml')
    _write_sigs(version, update_url, 'droid', 'DROID_SignatureFile-{}.xml')
    _write_sigs(version, update_url, 'fido', 'pronom-xml-{}.zip')
    versions.pronom_version = '{}'.format(version)
    versions.pronom_signature = 'pronom-xml-{}.zip'.format(version)
    versions.write()

def _version_check(sig_ver, update_url):
    resp = requests.get(update_url + 'format/latest/')
    if resp.status_code != 200:
        print('Error getting latest version info {}'.format(resp.status_code))
        sys.exit(1)
    latest = re.search('\d+|$', resp.text).group()  # noqa: W605
    return int(latest) > int(sig_ver), latest

def _write_sigs(latest, update_url, type, name_template):
    sig_out = str(importlib_resources.files('fido').joinpath('conf', name_template.format(latest)))
    if os.path.exists(sig_out):
        return
    resp = requests.get(update_url + 'format/latest/{}/'.format(type))
    open(sig_out, 'wb').write(resp.content)
