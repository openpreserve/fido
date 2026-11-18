"""The -sigs actions must work on the configuration directory they are given, not the packaged one."""

from pathlib import Path

import pytest

from fido import CONFIG_DIR
from fido import fido as fido_mod
from fido.pronom import versions

VERSIONS_XML = """<?xml version='1.0' encoding='utf-8'?>
<versions>
  <pronomVersion>100</pronomVersion>
  <pronomSignature>formats-v100.xml</pronomSignature>
  <pronomContainerSignature>container-signature-20000101.xml</pronomContainerSignature>
  <fidoExtensionSignature>format_extensions.xml</fidoExtensionSignature>
  <updateScript>test</updateScript>
  <updateSite>https://sigs.example.test</updateSite>
</versions>
"""

DOWNLOADS = ("formats-v200.xml", "DROID_SignatureFile-v200.xml", "pronom-xml-v200.zip")


class Response:
    def __init__(self, status_code=200, content=b"", text=""):
        self.status_code = status_code
        self.content = content
        self.text = text


@pytest.fixture
def custom_conf_dir(tmp_path):
    conf_dir = tmp_path / "custom_conf"
    conf_dir.mkdir()
    (conf_dir / "versions.xml").write_text(VERSIONS_XML, encoding="utf-8")
    return conf_dir


@pytest.fixture
def signature_service(monkeypatch):
    """Stand in for the signature service and record every URL requested from it."""
    requested = []

    def get(url, **_kwargs):
        requested.append(url)
        if url.endswith("format/latest/"):
            return Response(text='<signature version="v200" />')
        if url.endswith("format/"):
            return Response(content=b'<format><signatures><signature version="v200" /></signatures></format>')
        return Response(content=b"payload from " + url.encode())

    monkeypatch.setattr(versions.requests, "get", get)
    return requested


@pytest.fixture
def decoy_packaged_conf_dir(monkeypatch, tmp_path):
    """Point the packaged conf directory at an empty one, so a regression cannot write into the real package."""
    decoy = tmp_path / "package"
    (decoy / "conf").mkdir(parents=True)

    class Files:
        def joinpath(self, *parts):
            return decoy.joinpath(*parts)

    monkeypatch.setattr(versions.importlib.resources, "files", lambda _package: Files())
    return decoy / "conf"


def test_list_asks_the_update_site_named_in_the_given_conf_dir(custom_conf_dir, signature_service):
    with pytest.raises(SystemExit) as exc:
        versions.sig_file_actions("list", str(custom_conf_dir))

    assert exc.value.code == 0
    assert signature_service == ["https://sigs.example.test/format/"]


@pytest.mark.parametrize("action", ["update", "v200"], ids=["update to latest", "download a named version"])
def test_new_signature_files_are_installed_into_the_given_conf_dir(
    action, custom_conf_dir, signature_service, decoy_packaged_conf_dir
):
    with pytest.raises(SystemExit) as exc:
        versions.sig_file_actions(action, str(custom_conf_dir))

    assert exc.value.code == 0
    for name in DOWNLOADS:
        assert (custom_conf_dir / name).is_file(), name + " was not written to the given conf dir"
    updated = versions.get_local_versions(str(custom_conf_dir))
    assert updated.pronom_version == "200"
    assert updated.pronom_signature == "formats-v200.xml"
    assert list(decoy_packaged_conf_dir.iterdir()) == [], "something was written to the packaged conf dir"
    assert not (Path(CONFIG_DIR) / "formats-v200.xml").exists()


def test_main_hands_confdir_to_the_sigs_actions(monkeypatch, custom_conf_dir, signature_service):
    monkeypatch.setattr(fido_mod, "defaults", dict(fido_mod.defaults))

    with pytest.raises(SystemExit) as exc:
        fido_mod.main(["-confdir", str(custom_conf_dir), "-sigs", "list"])

    assert exc.value.code == 0
    assert signature_service == ["https://sigs.example.test/format/"]


def test_without_a_conf_dir_the_packaged_one_is_used(signature_service):
    packaged_site = versions.get_local_versions().update_site.rstrip("/")

    with pytest.raises(SystemExit):
        versions.sig_file_actions("list")

    assert signature_service == [packaged_site + "/format/"]
