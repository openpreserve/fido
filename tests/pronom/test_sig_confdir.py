"""The -sigs actions must work on the configuration directory they are given, not the packaged one."""

import os
import re
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


def without(tag):
    return re.sub(rf"\s*<{tag}>[^<]*</{tag}>", "", VERSIONS_XML)


UNUSABLE_VERSIONS = [
    pytest.param(None, id="missing file"),
    pytest.param("", id="empty file"),
    pytest.param("this is not xml", id="not xml"),
    pytest.param("<versions/>", id="empty root"),
    pytest.param(without("updateSite"), id="no updateSite"),
    pytest.param(without("pronomVersion"), id="no pronomVersion"),
    pytest.param(without("pronomSignature"), id="no pronomSignature, which a download rewrites"),
    pytest.param(
        VERSIONS_XML.replace("<pronomVersion>100</pronomVersion>", "<pronomVersion/>"), id="empty pronomVersion"
    ),
    pytest.param(VERSIONS_XML.replace("https://sigs.example.test", " "), id="blank updateSite"),
]


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


def read_files(directory):
    return {path.name: path.read_bytes() for path in Path(directory).iterdir() if path.is_file()}


@pytest.fixture(autouse=True)
def packaged_conf_dir_is_untouched():
    """Fail a test that changes the packaged conf dir, after restoring it from a snapshot taken before the test."""
    packaged = Path(CONFIG_DIR)
    before = read_files(packaged)
    yield
    after = read_files(packaged)
    added = sorted(set(after) - set(before))
    changed = sorted(name for name in before if after.get(name) != before[name])
    for name in added:
        (packaged / name).unlink()
    for name in changed:
        (packaged / name).write_bytes(before[name])
    assert not (added or changed), (
        f"the packaged conf dir was modified (now restored): added {added}, changed {changed}"
    )


@pytest.fixture
def decoy_packaged_conf_dir(monkeypatch, tmp_path):
    """Point importlib.resources at an empty package, so a download that falls back to the package's conf dir shows."""
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


def test_downloads_land_next_to_the_versions_xml_that_was_read_through_a_symlink(
    tmp_path, signature_service, decoy_packaged_conf_dir
):
    config = tmp_path / "srv" / "config"
    (config / "current").mkdir(parents=True)
    (config / "versions.xml").write_text(VERSIONS_XML, encoding="utf-8")
    work = tmp_path / "work"
    work.mkdir()
    try:
        (work / "link").symlink_to(Path("..") / "srv" / "config" / "current", target_is_directory=True)
    except (OSError, NotImplementedError) as error:
        pytest.skip(f"symlinks are not supported here: {error}")
    confdir_through_symlink = f"{work}/link/.."
    assert Path(confdir_through_symlink, "versions.xml").read_text(encoding="utf-8") == VERSIONS_XML, (
        "the layout must make the OS resolve link/.. to the directory holding versions.xml"
    )

    with pytest.raises(SystemExit) as exc:
        versions.sig_file_actions("update", confdir_through_symlink)

    assert exc.value.code == 0
    for name in DOWNLOADS:
        assert (config / name).is_file(), name + " was not written next to the versions.xml that was read"
    assert sorted(path.name for path in work.iterdir()) == ["link"], "files were written to the lexical parent"
    updated = versions.get_local_versions(confdir_through_symlink)
    assert updated.pronom_signature == "formats-v200.xml"
    resolved = os.path.realpath(config)
    assert updated.get_signature_file() == os.path.join(resolved, "formats-v200.xml")
    assert updated.get_zip_file() == os.path.join(resolved, "pronom-xml-v200.zip")


@pytest.mark.parametrize("action", ["list", "check", "update", "v200"])
@pytest.mark.parametrize("content", UNUSABLE_VERSIONS)
def test_an_unusable_versions_xml_stops_the_sigs_actions_before_any_request_or_write(
    content, action, tmp_path, signature_service
):
    conf_dir = tmp_path / "unusable_conf"
    conf_dir.mkdir()
    if content is not None:
        (conf_dir / "versions.xml").write_text(content, encoding="utf-8")
    before = read_files(conf_dir)

    with pytest.raises(SystemExit) as exc:
        versions.sig_file_actions(action, str(conf_dir))

    message = str(exc.value)
    assert message == f"FIDO: {conf_dir / 'versions.xml'} is missing or incomplete, cannot use it with -sigs", message
    assert signature_service == [], "the update site was contacted"
    assert read_files(conf_dir) == before, "something was written to the conf dir"


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
