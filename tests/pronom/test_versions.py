import socket
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest

from fido.pronom import versions

DEADLINE_SECONDS = 5


class DummyResponse:
    def __init__(self, status_code=200, content=b"", text=""):
        self.status_code = status_code
        self.content = content
        self.text = text


@pytest.mark.parametrize(
    "value, expected",
    [("104", "104"), ("v104", "104"), ("V205", "V205")],
)
def test_get_version_accepts_valid_values(value, expected):
    assert versions._get_version(value) == expected


@pytest.mark.parametrize("value", ["", "foo", "v", "104a", "v-1"])
def test_get_version_rejects_invalid_values(value):
    with pytest.raises(SystemExit):
        versions._get_version(value)


def test_local_versions_write_and_reload(tmp_path):
    versions_file = tmp_path / "versions.xml"
    versions_file.write_text(
        """<?xml version='1.0' encoding='utf-8'?>
<versions>
  <pronomVersion>100</pronomVersion>
  <pronomSignature>formats-v100.xml</pronomSignature>
  <pronomContainerSignature>container-signature-20200101.xml</pronomContainerSignature>
  <fidoExtensionSignature>format_extensions.xml</fidoExtensionSignature>
  <updateScript>0.0.1</updateScript>
  <updateSite>https://example.test</updateSite>
</versions>""",
        encoding="utf-8",
    )
    local = versions.LocalVersions(str(versions_file))

    local.pronom_version = "116"
    local.pronom_signature = "formats-v116.xml"
    local.pronom_container_signature = "container-signature-20231127.xml"
    local.fido_extension_signature = "format_extensions.xml"
    local.update_script = "1.0.0"
    local.update_site = "https://example.test"
    local.write()

    reloaded = versions.LocalVersions(str(versions_file))
    assert reloaded.pronom_version == "116"
    assert reloaded.get_zip_file().endswith("pronom-xml-v116.zip")
    assert reloaded.get_signature_file().endswith("formats-v116.xml")


def test_local_versions_write_requires_all_fields(tmp_path):
    versions_file = tmp_path / "versions.xml"
    versions_file.write_text("<?xml version='1.0' encoding='utf-8'?><versions></versions>", encoding="utf-8")
    local = versions.LocalVersions(str(versions_file))

    with pytest.raises(ValueError):
        local.write()


def test_version_check_returns_newer_version(monkeypatch):
    monkeypatch.setattr(
        versions.requests,
        "get",
        lambda _url, **_kwargs: DummyResponse(status_code=200, text='<signature version="v117" />'),
    )

    is_new, latest = versions._version_check("116", "https://example.test/")
    assert is_new is True
    assert latest == "117"


def test_version_check_returns_not_new(monkeypatch):
    monkeypatch.setattr(
        versions.requests,
        "get",
        lambda _url, **_kwargs: DummyResponse(status_code=200, text='<signature version="116" />'),
    )

    is_new, latest = versions._version_check("116", "https://example.test/")
    assert is_new is False
    assert latest == "116"


def test_version_check_exits_on_http_error(monkeypatch):
    monkeypatch.setattr(
        versions.requests,
        "get",
        lambda _url, **_kwargs: DummyResponse(status_code=500, text=""),
    )

    with pytest.raises(SystemExit):
        versions._version_check("116", "https://example.test/")


def test_write_sigs_downloads_when_target_missing(monkeypatch, tmp_path):
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir()

    class FakeFiles:
        def __init__(self, base):
            self.base = Path(base)

        def joinpath(self, *parts):
            return self.base.joinpath(*parts)

    monkeypatch.setattr(versions.importlib.resources, "files", lambda _pkg: FakeFiles(tmp_path))
    monkeypatch.setattr(
        versions.requests,
        "get",
        lambda _url, **_kwargs: DummyResponse(status_code=200, content=b"<xml>payload</xml>"),
    )

    versions._write_sigs("116", "https://example.test/", "fido", "formats-v{}.xml")

    assert (conf_dir / "formats-v116.xml").read_bytes() == b"<xml>payload</xml>"


def test_write_sigs_skips_when_target_exists(monkeypatch, tmp_path):
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir()
    existing = conf_dir / "formats-v116.xml"
    existing.write_text("present", encoding="utf-8")

    class FakeFiles:
        def __init__(self, base):
            self.base = Path(base)

        def joinpath(self, *parts):
            return self.base.joinpath(*parts)

    called = {"http": 0}
    monkeypatch.setattr(versions.importlib.resources, "files", lambda _pkg: FakeFiles(tmp_path))
    monkeypatch.setattr(versions.requests, "get", lambda _url, **_kwargs: called.__setitem__("http", called["http"] + 1))

    versions._write_sigs("116", "https://example.test/", "fido", "formats-v{}.xml")

    assert existing.read_text(encoding="utf-8") == "present"
    assert called["http"] == 0


def test_list_available_versions_prints_all(monkeypatch, capsys):
    payload = b"<root><signature version='116'/><signature version='117'/></root>"
    monkeypatch.setattr(versions.requests, "get", lambda _url, **_kwargs: DummyResponse(status_code=200, content=payload))

    versions._list_available_versions("https://example.test/")

    output = capsys.readouterr().out
    assert "Available signature versions:" in output
    assert "116" in output
    assert "117" in output


@pytest.mark.parametrize(
    "sig_act, expected_call, expected_update_flag",
    [
        ("list", "list", None),
        ("check", "check", False),
        ("update", "check", True),
        ("116", "download", None),
    ],
)
def test_sig_file_actions_dispatches(monkeypatch, sig_act, expected_call, expected_update_flag):
    calls = {}
    fake_versions = SimpleNamespace(pronom_version="116", update_site="https://example.test")

    monkeypatch.setattr(versions, "get_local_versions", lambda: fake_versions)
    monkeypatch.setattr(versions, "_list_available_versions", lambda update_url: calls.__setitem__("list", update_url))
    monkeypatch.setattr(
        versions,
        "_check_update_signatures",
        lambda sig_vers, update_url, vers, is_update: calls.__setitem__(
            "check", (sig_vers, update_url, vers, is_update)
        ),
    )
    monkeypatch.setattr(
        versions,
        "_download_sig_version",
        lambda action, update_url, vers: calls.__setitem__("download", (action, update_url, vers)),
    )

    with pytest.raises(SystemExit) as exc:
        versions.sig_file_actions(sig_act)

    assert exc.value.code == 0
    if expected_call == "list":
        assert calls["list"] == "https://example.test/"
    elif expected_call == "check":
        sig_vers, update_url, vers, is_update = calls["check"]
        assert sig_vers == "116"
        assert update_url == "https://example.test/"
        assert vers is fake_versions
        assert is_update is expected_update_flag
    else:
        action, update_url, vers = calls["download"]
        assert action == "116"
        assert update_url == "https://example.test/"
        assert vers is fake_versions


def test_check_update_signatures_emits_update_message(monkeypatch, capsys):
    calls = {"details": 0}
    monkeypatch.setattr(versions, "_version_check", lambda _s, _u: (True, "117"))
    monkeypatch.setattr(versions, "_output_details", lambda *_a: calls.__setitem__("details", calls["details"] + 1))

    with pytest.raises(SystemExit) as exc:
        versions._check_update_signatures("116", "https://example.test/", object(), is_update=False)

    assert exc.value.code == 0
    output = capsys.readouterr().out
    assert "Updated signatures v117 are available" in output
    assert calls["details"] == 0


def test_check_update_signatures_updates_when_requested(monkeypatch):
    calls = {"details": 0}
    monkeypatch.setattr(versions, "_version_check", lambda _s, _u: (True, "117"))
    monkeypatch.setattr(versions, "_output_details", lambda *_a: calls.__setitem__("details", calls["details"] + 1))

    with pytest.raises(SystemExit):
        versions._check_update_signatures("116", "https://example.test/", object(), is_update=True)

    assert calls["details"] == 1


def test_check_update_signatures_emits_up_to_date_message(monkeypatch, capsys):
    monkeypatch.setattr(versions, "_version_check", lambda _s, _u: (False, "116"))

    with pytest.raises(SystemExit) as exc:
        versions._check_update_signatures("116", "https://example.test/", object(), is_update=False)

    assert exc.value.code == 0
    assert "up to date" in capsys.readouterr().out


def test_download_sig_version_normalizes_number(monkeypatch):
    calls = {}
    monkeypatch.setattr(versions.requests, "get", lambda _url, **_kwargs: DummyResponse(status_code=200, content=b"", text=""))
    monkeypatch.setattr(
        versions,
        "_output_details",
        lambda version, update_url, vers: calls.__setitem__("out", (version, update_url, vers)),
    )
    target = object()

    versions._download_sig_version("104", "https://example.test/", target)

    assert calls["out"] == ("104", "https://example.test/", target)


def test_download_sig_version_exits_on_http_error(monkeypatch):
    monkeypatch.setattr(versions.requests, "get", lambda _url, **_kwargs: DummyResponse(status_code=404, content=b"", text=""))

    with pytest.raises(SystemExit) as exc:
        versions._download_sig_version("104", "https://example.test/", object())

    assert "No signature files found" in str(exc.value)


def test_output_details_sets_versions_and_downloads(monkeypatch):
    calls = []
    target = SimpleNamespace(pronom_version="", pronom_signature="")
    target.write = lambda: calls.append("write")
    monkeypatch.setattr(versions, "_write_sigs", lambda *args: calls.append(args))

    versions._output_details("117", "https://example.test/", target)

    assert target.pronom_version == "117"
    assert target.pronom_signature == "formats-v117.xml"
    assert calls[0][2] == "fido"
    assert calls[1][2] == "droid"
    assert calls[2][2] == "pronom"
    assert calls[3] == "write"


def test_local_versions_getattr_unknown_returns_none(tmp_path):
    versions_file = tmp_path / "versions.xml"
    versions_file.write_text("<?xml version='1.0' encoding='utf-8'?><versions></versions>", encoding="utf-8")
    local = versions.LocalVersions(str(versions_file))

    assert local.unknown_attribute is None


def test_sig_file_actions_keeps_trailing_slash(monkeypatch):
    calls = {}
    fake_versions = SimpleNamespace(pronom_version="116", update_site="https://example.test/")

    monkeypatch.setattr(versions, "get_local_versions", lambda: fake_versions)
    monkeypatch.setattr(versions, "_list_available_versions", lambda update_url: calls.__setitem__("list", update_url))

    with pytest.raises(SystemExit):
        versions.sig_file_actions("list")

    assert calls["list"] == "https://example.test/"


def test_download_sig_version_rejects_invalid_input():
    with pytest.raises(SystemExit) as exc:
        versions._download_sig_version("v104beta", "https://example.test/", object())

    assert "not a valid version number" in str(exc.value)


def test_download_sig_version_accepts_prefixed_version(monkeypatch):
    calls = {}
    monkeypatch.setattr(versions.requests, "get", lambda _url, **_kwargs: DummyResponse(status_code=200, content=b"", text=""))
    monkeypatch.setattr(
        versions,
        "_output_details",
        lambda version, update_url, vers: calls.__setitem__("out", (version, update_url, vers)),
    )
    target = object()

    versions._download_sig_version("v104", "https://example.test/", target)

    assert calls["out"] == ("104", "https://example.test/", target)


def test_get_local_versions_uses_config_dir(monkeypatch):
    captured = {}
    marker = object()

    def fake_local_versions(path):
        captured["path"] = path
        return marker

    monkeypatch.setattr(versions, "LocalVersions", fake_local_versions)

    result = versions.get_local_versions("/tmp/custom-conf")

    assert result is marker
    assert captured["path"] == "/tmp/custom-conf/versions.xml"


def test_local_versions_init_fallback_uses_empty_root(monkeypatch, tmp_path):
    versions_file = tmp_path / "missing-versions.xml"

    monkeypatch.setattr(versions, "parse", lambda _path: (_ for _ in ()).throw(IOError("missing")))

    local = versions.LocalVersions(str(versions_file))

    assert local.root.tag == versions.LocalVersions.ROOT_ELEMENT


def test_local_versions_setattr_creates_missing_field(monkeypatch, tmp_path):
    versions_file = tmp_path / "versions.xml"
    versions_file.write_text("<?xml version='1.0' encoding='utf-8'?><versions></versions>", encoding="utf-8")

    local = versions.LocalVersions(str(versions_file))

    local.pronom_version = "116"

    assert local.root.find("pronomVersion") is not None
    assert local.root.find("pronomVersion").text == "116"


def test_get_passes_the_timeout(monkeypatch):
    seen = {}

    def record(url, **kwargs):
        seen.update(url=url, **kwargs)
        return DummyResponse()

    monkeypatch.setattr(versions.requests, "get", record)

    versions._get("https://example.test/format/")

    assert seen == {"url": "https://example.test/format/", "timeout": versions.HTTP_TIMEOUT_SECONDS}


@pytest.mark.parametrize(
    "call",
    [
        lambda: versions._version_check("116", "https://example.test/"),
        lambda: versions._list_available_versions("https://example.test/"),
        lambda: versions._download_sig_version("104", "https://example.test/", object()),
    ],
    ids=["version check", "list versions", "download version"],
)
def test_every_signature_service_request_has_a_timeout(monkeypatch, call):
    timeouts = []

    def record(url, **kwargs):
        timeouts.append(kwargs.get("timeout"))
        return DummyResponse(status_code=200, content=b"<format/>", text='<signature version="116" />')

    monkeypatch.setattr(versions.requests, "get", record)
    monkeypatch.setattr(versions, "_output_details", lambda *_args: None)

    call()

    assert timeouts == [versions.HTTP_TIMEOUT_SECONDS]


@pytest.mark.parametrize(
    "error",
    [versions.requests.exceptions.Timeout("slow"), versions.requests.exceptions.ConnectionError("refused")],
    ids=["timeout", "connection refused"],
)
def test_get_exits_naming_the_url_when_the_service_cannot_be_reached(monkeypatch, error):
    def fail(_url, **_kwargs):
        raise error

    monkeypatch.setattr(versions.requests, "get", fail)

    with pytest.raises(SystemExit) as exc:
        versions._get("https://example.test/format/latest/")

    assert "Could not reach https://example.test/format/latest/" in str(exc.value)


@pytest.mark.parametrize(
    "url, shown",
    [
        ("https://alice:hunter2@example.test/format/", "https://example.test/format/"),
        ("https://alice:hunter2@example.test:8443/format/", "https://example.test:8443/format/"),
        ("https://alice@example.test/format/", "https://example.test/format/"),
        ("https://alice:hunter2@[::1]:8443/format/", "https://[::1]:8443/format/"),
        ("https://alice:p@ss@example.test/format/", "https://example.test/format/"),
    ],
    ids=["password", "port", "user only", "ipv6", "at sign in password"],
)
def test_get_does_not_print_the_credentials_of_the_url(monkeypatch, url, shown):
    def fail(requested, **_kwargs):
        raise versions.requests.exceptions.ConnectionError(f"could not reach {requested}")

    monkeypatch.setattr(versions.requests, "get", fail)

    with pytest.raises(SystemExit) as exc:
        versions._get(url)

    message = str(exc.value)
    assert message == f"Could not reach {shown}: could not reach {shown}", message
    assert "alice" not in message and "hunter2" not in message and "ss@" not in message, message


def test_get_does_not_print_the_credentials_of_an_unsupported_url():
    with pytest.raises(SystemExit) as exc:
        versions._get("ftp://alice:hunter2@example.test/format/")

    message = str(exc.value)
    assert "ftp://example.test/format/" in message, message
    assert "alice" not in message and "hunter2" not in message, message


def test_get_gives_up_on_a_service_that_accepts_the_connection_and_never_answers(monkeypatch):
    for name in ("http_proxy", "https_proxy", "all_proxy"):
        monkeypatch.delenv(name, raising=False)
        monkeypatch.delenv(name.upper(), raising=False)
    monkeypatch.setenv("NO_PROXY", "127.0.0.1,localhost")
    monkeypatch.setenv("no_proxy", "127.0.0.1,localhost")
    monkeypatch.setattr(versions, "HTTP_TIMEOUT_SECONDS", 0.5)
    outcome = {}

    def request(url):
        try:
            versions._get(url)
        except SystemExit as exit_request:
            outcome["exit"] = exit_request

    with socket.socket() as silent_server:
        silent_server.bind(("127.0.0.1", 0))
        silent_server.listen(1)
        worker = threading.Thread(target=request, args=(f"http://127.0.0.1:{silent_server.getsockname()[1]}/",))
        worker.daemon = True
        worker.start()
        worker.join(DEADLINE_SECONDS)

        assert not worker.is_alive(), f"the request was not abandoned within {DEADLINE_SECONDS} seconds"

    assert "exit" in outcome, "the request ended without giving up through an exit message"
    message = str(outcome["exit"])
    assert "Could not reach" in message and "timed out" in message, message


@pytest.fixture
def conf_dir(monkeypatch, tmp_path):
    directory = tmp_path / "conf"
    directory.mkdir()

    class FakeFiles:
        def joinpath(self, *parts):
            return tmp_path.joinpath(*parts)

    monkeypatch.setattr(versions.importlib.resources, "files", lambda _pkg: FakeFiles())
    return directory


@pytest.mark.parametrize("status_code", [404, 500])
def test_write_sigs_saves_nothing_when_the_server_answers_with_an_error(monkeypatch, conf_dir, status_code):
    error_page = b"<html><body>error</body></html>"
    monkeypatch.setattr(
        versions.requests,
        "get",
        lambda _url, **_kwargs: DummyResponse(status_code=status_code, content=error_page),
    )

    with pytest.raises(SystemExit) as exc:
        versions._write_sigs("116", "https://alice:hunter2@example.test/", "fido", "formats-v{}.xml")

    message = str(exc.value)
    assert f"Could not download https://example.test/format/116/fido/: HTTP status {status_code}" == message, message
    assert list(conf_dir.iterdir()) == [], "a failed download left a file behind"


@pytest.mark.parametrize("status_code", [404, 500])
def test_list_available_versions_exits_when_the_server_answers_with_an_error(monkeypatch, capsys, status_code):
    error_page = b"<html><body>error</body></html>"
    monkeypatch.setattr(
        versions.requests,
        "get",
        lambda _url, **_kwargs: DummyResponse(status_code=status_code, content=error_page),
    )

    with pytest.raises(SystemExit) as exc:
        versions._list_available_versions("https://alice:hunter2@example.test/")

    message = str(exc.value)
    assert f"Could not download https://example.test/format/: HTTP status {status_code}" == message, message
    assert capsys.readouterr().out == "", "an error page was listed as signature versions"


def test_write_sigs_passes_the_timeout(monkeypatch, tmp_path):
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir()
    timeouts = []

    class FakeFiles:
        def joinpath(self, *parts):
            return tmp_path.joinpath(*parts)

    def record(_url, **kwargs):
        timeouts.append(kwargs.get("timeout"))
        return DummyResponse(status_code=200, content=b"<xml/>")

    monkeypatch.setattr(versions.importlib.resources, "files", lambda _pkg: FakeFiles())
    monkeypatch.setattr(versions.requests, "get", record)

    versions._write_sigs("116", "https://example.test/", "fido", "formats-v{}.xml")

    assert timeouts == [versions.HTTP_TIMEOUT_SECONDS]
