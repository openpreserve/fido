"""Support for containers."""

import re
import zipfile

import olefile
from six import iteritems


class Package(object):
    """Base class for container support."""

    def _process_puid_map(self, data, puid_map):
        results = []
        for puid, signatures in iteritems(puid_map):
            results.extend(self._process_matches(data, puid, signatures))

        return results

    def _process_matches(self, data, puid, signatures):
        results = []
        for signature in signatures:
            if re.search(signature["signature"], data):
                results.append(puid)

        return results


class OlePackage(Package):
    """OlePackage supports OLE containers."""

    def __init__(self, ole, signatures):
        """Instantiate OlePackage object given the location of its file and signatures."""
        self.ole = ole
        self.signatures = signatures

    def detect_formats(self):
        """Detect available formats inside the OLE container."""
        try:
            ole = olefile.OleFileIO(self.ole)
        except IOError:
            return []

        results = []
        for path, puid_map in iteritems(self.signatures):
            # Each OLE container signature lists the path of the file inside the OLE
            # on which it operates; if the file is missing, there can be no match.
            # This is not a precise match because the name of the stream may slightly
            # differ; for example, \x01CompObj instead of CompObj
            filepath = None
            for paths in ole.listdir():
                p = '/'.join(paths)
                if p == path or p[1:] == path:
                    filepath = p
                    break

            # Path to match isn't in the container at all
            if filepath is None:
                continue

            with ole.openstream(filepath) as stream:
                contents = stream.read()
                results.extend(self._process_puid_map(contents, puid_map))

        return results


class ZipPackage(Package):
    """ZipPackage supports Zip containers."""

    def __init__(self, zip_, signatures):
        """Instantiate ZipPackage object given the location of its file and signatures."""
        self.zip = zip_
        self.signatures = signatures

    def detect_formats(self):
        """Detect available formats inside the ZIP container."""
        try:
            zip_ = zipfile.ZipFile(self.zip)
        except zipfile.BadZipfile:
            return []

        results = []
        for path, puid_map in iteritems(self.signatures):
            # Each ZIP container signature lists the path of the file inside the ZIP
            # on which it operates; if the file is missing, there can be no match.
            if path not in zip_.namelist():
                continue

            # Extract the requested file from the ZIP only once, and pass the same
            # data to each signature that requires it.
            with zip_.open(path) as id_file:
                contents = id_file.read()
                results.extend(self._process_puid_map(contents, puid_map))

        return results
