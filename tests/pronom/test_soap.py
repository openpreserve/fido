"""Offline contract tests for PRONOM SOAP helpers."""

import socket
import unittest.mock
import urllib.error

import pytest

import fido.pronom


class FakeResponse:
    """Small response shim used to mock urllib responses."""

    def __init__(self, payload):
        self.payload = payload

    def read(self):
        return self.payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeRequest:
    """Simple urllib Request shim with header support."""

    def __init__(self, url, data=None):
        self.url = url
        self.data = data
        self.headers = {}

    def add_header(self, key, value):
        self.headers[key] = value


@unittest.mock.patch("fido.pronom.soap.urllib.request", create=True)
def test_pronom_version_from_mocked_soap_response(mock_request):
    """Parse signature version from a mocked SOAP payload."""
    xml = b"""<?xml version=\"1.0\" encoding=\"utf-8\"?>
<soap:Envelope xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">
  <soap:Body>
  <getSignatureFileVersionV1Response xmlns=\"http://pronom.nationalarchives.gov.uk\">
    <getSignatureFileVersionV1Result>
    <Version><Version>116</Version></Version>
    </getSignatureFileVersionV1Result>
  </getSignatureFileVersionV1Response>
  </soap:Body>
</soap:Envelope>
"""

    mock_request.Request.side_effect = lambda url, data=None: FakeRequest(
        url, data=data
    )
    mock_request.urlopen.return_value = FakeResponse(xml)

    assert fido.pronom.soap.get_pronom_sig_version() == 116


@unittest.mock.patch("fido.pronom.soap.urllib.request", create=True)
def test_get_droid_signatures_counts_file_formats(mock_request):
    """Count FileFormat elements from a mocked DROID signature XML file."""
    sig_xml = b"""<?xml version=\"1.0\" encoding=\"utf-8\"?>
<SignatureFile xmlns=\"http://www.nationalarchives.gov.uk/pronom/SignatureFile\">
  <FileFormatCollection>
  <FileFormat ID=\"1\" PUID=\"fmt/1\" />
  <FileFormat ID=\"2\" PUID=\"fmt/2\" />
  </FileFormatCollection>
</SignatureFile>
"""

    mock_request.urlopen.return_value = FakeResponse(sig_xml)

    xml, count = fido.pronom.soap.get_droid_signatures(116)
    assert "SignatureFile" in xml
    assert count == 2


@unittest.mock.patch("fido.pronom.soap.urllib.request", create=True)
def test_get_droid_signatures_handles_http_error(mock_request, capsys):
    """Return fallback values and log an error when download fails."""

    mock_request.urlopen.side_effect = urllib.error.HTTPError(
        url="http://example.test", code=500, msg="boom", hdrs=None, fp=None
    )

    xml, count = fido.pronom.soap.get_droid_signatures(116)
    captured = capsys.readouterr()
    assert xml == []
    assert count is False
    assert "could not download signature file v116" in captured.err


@unittest.mock.patch("fido.pronom.soap.urllib.request", create=True)
def test_get_sig_xml_for_puid_returns_raw_xml(mock_request):
    """Return unmodified PRONOM XML bytes for a PUID."""
    payload = b"<root><foo>bar</foo></root>"
    mock_request.urlopen.return_value = FakeResponse(payload)

    assert fido.pronom.soap.get_sig_xml_for_puid("fmt/18") == payload


@unittest.mock.patch("fido.pronom.soap.urllib.request", create=True)
def test_get_soap_response_exits_on_request_error(mock_request, capsys):
    """Exit with code 1 when creating the request fails."""

    mock_request.Request.side_effect = urllib.error.URLError("offline")

    with pytest.raises(SystemExit) as exc:
        fido.pronom.soap._get_soap_response('"action"', b"<soap/>")

    captured = capsys.readouterr()
    assert exc.value.code == 1
    assert "There was a problem contacting the PRONOM service" in captured.out


@unittest.mock.patch("fido.pronom.soap.urllib.request", create=True)
def test_get_sig_xml_for_puid_sets_a_timeout(mock_request):
    mock_request.urlopen.return_value = FakeResponse(b"<root/>")

    fido.pronom.soap.get_sig_xml_for_puid("fmt/18")

    assert mock_request.urlopen.call_args.kwargs["timeout"] == fido.pronom.HTTP_TIMEOUT_SECONDS


@unittest.mock.patch("fido.pronom.soap.urllib.request", create=True)
def test_get_droid_signatures_sets_a_timeout(mock_request):
    mock_request.urlopen.return_value = FakeResponse(b"<SignatureFile/>")

    fido.pronom.soap.get_droid_signatures(116)

    assert mock_request.urlopen.call_args.kwargs["timeout"] == fido.pronom.HTTP_TIMEOUT_SECONDS


@unittest.mock.patch("fido.pronom.soap.urllib.request", create=True)
def test_get_soap_response_sets_a_timeout(mock_request):
    mock_request.urlopen.return_value = FakeResponse(b"<soap/>")

    fido.pronom.soap._get_soap_response('"action"', b"<soap/>")

    assert mock_request.urlopen.call_args.kwargs["timeout"] == fido.pronom.HTTP_TIMEOUT_SECONDS


@pytest.mark.parametrize(
    "error",
    [socket.timeout("timed out"), urllib.error.URLError("connection refused")],
    ids=["timeout", "connection refused"],
)
@unittest.mock.patch("fido.pronom.soap.urllib.request", create=True)
def test_get_droid_signatures_reports_an_unreachable_service(mock_request, error, capsys):
    mock_request.urlopen.side_effect = error

    xml, count = fido.pronom.soap.get_droid_signatures(116)

    assert xml == []
    assert count is False
    assert "could not download signature file v116" in capsys.readouterr().err
