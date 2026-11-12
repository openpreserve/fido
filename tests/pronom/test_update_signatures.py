import importlib
import os
import subprocess
import sys
from types import SimpleNamespace

import pytest


@pytest.fixture
def update_signatures_module():
    module = importlib.import_module("fido.pronom.update_signatures")
    return importlib.reload(module)


@pytest.mark.parametrize(
    "code",
    (
        # the fido-update-signatures entry point
        "from fido.pronom.update_signatures import run",
        # soap.py must import urllib.request itself, not rely on another module having done it
        "import fido.pronom.soap as soap; soap.urllib.request.Request",
    ),
)
def test_imports_work_in_a_fresh_interpreter(code):
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_get_puid_file_name(update_signatures_module):
    element = SimpleNamespace(get=lambda key: "fmt/18" if key == "PUID" else None)

    puid, filename = update_signatures_module.get_puid_file_name(element)

    assert puid == "fmt/18"
    assert filename == "puid.fmt.18.xml"


def test_sig_version_check_latest_uses_service(update_signatures_module, monkeypatch, tmp_path):
    monkeypatch.setattr(update_signatures_module, "CONFIG_DIR", str(tmp_path))
    monkeypatch.setattr(update_signatures_module, "get_pronom_sig_version", lambda: 116)
    monkeypatch.setattr(update_signatures_module.os.path, "isfile", lambda _p: False)

    version, sig_file_name = update_signatures_module.sig_version_check("latest")

    assert version == 116
    assert sig_file_name.endswith("DROID_SignatureFile-v116.xml")


def test_sig_version_check_exits_when_existing_file_not_confirmed(update_signatures_module, monkeypatch, tmp_path):
    monkeypatch.setattr(update_signatures_module, "CONFIG_DIR", str(tmp_path))
    monkeypatch.setattr(update_signatures_module.os.path, "isfile", lambda _p: True)
    monkeypatch.setattr(update_signatures_module, "query_yes_no", lambda _q: False)

    with pytest.raises(SystemExit) as exc:
        update_signatures_module.sig_version_check("116")

    assert str(exc.value) == update_signatures_module.ABORT_MSG


def test_sig_version_check_allows_existing_file_when_confirmed(update_signatures_module, monkeypatch, tmp_path):
    monkeypatch.setattr(update_signatures_module, "CONFIG_DIR", str(tmp_path))
    monkeypatch.setattr(update_signatures_module.os.path, "isfile", lambda _p: True)
    monkeypatch.setattr(update_signatures_module, "query_yes_no", lambda _q: True)

    version, sig_file_name = update_signatures_module.sig_version_check("116")

    assert version == "116"
    assert sig_file_name.endswith("DROID_SignatureFile-v116.xml")


def test_download_sig_file_writes_xml(update_signatures_module, monkeypatch, tmp_path):
    monkeypatch.setattr(update_signatures_module, "get_droid_signatures", lambda _v: ("<xml/>", 1))
    out = tmp_path / "sig.xml"

    update_signatures_module.download_sig_file(116, str(out))

    assert out.read_text(encoding="utf-8") == "<xml/>"


def test_download_sig_file_exits_when_service_returns_empty(update_signatures_module, monkeypatch, tmp_path):
    monkeypatch.setattr(update_signatures_module, "get_droid_signatures", lambda _v: ("", False))

    with pytest.raises(SystemExit):
        update_signatures_module.download_sig_file(116, str(tmp_path / "sig.xml"))


def test_update_versions_xml_assigns_expected_values(update_signatures_module, monkeypatch):
    calls = {"write": 0}
    versions = SimpleNamespace(
        pronom_version=None,
        pronom_signature=None,
        pronom_container_signature=None,
        fido_extension_signature=None,
        update_script=None,
    )
    versions.write = lambda: calls.__setitem__("write", calls["write"] + 1)
    monkeypatch.setattr(update_signatures_module, "get_local_versions", lambda: versions)

    update_signatures_module.update_versions_xml(117)

    assert versions.pronom_version == "117"
    assert versions.pronom_signature == "formats-v117.xml"
    assert versions.pronom_container_signature == update_signatures_module.DEFAULTS["containerVersion"]
    assert versions.fido_extension_signature == update_signatures_module.DEFAULTS["fidoSignatureVersion"]
    assert versions.update_script == update_signatures_module.__version__
    assert calls["write"] == 1


@pytest.mark.parametrize(
    "default, user_inputs, expected",
    [
        ("yes", [""], True),
        ("no", [""], False),
        (None, ["", "y"], True),
    ],
)
def test_query_yes_no_handles_defaults(update_signatures_module, monkeypatch, default, user_inputs, expected):
    answers = iter(user_inputs)
    monkeypatch.setattr("builtins.input", lambda: next(answers))

    assert update_signatures_module.query_yes_no("Proceed?", default=default) is expected


def test_query_yes_no_rejects_invalid_default(update_signatures_module):
    with pytest.raises(ValueError):
        update_signatures_module.query_yes_no("Proceed?", default="maybe")


def test_sig_version_check_exits_when_latest_lookup_fails(update_signatures_module, monkeypatch):
    monkeypatch.setattr(update_signatures_module, "get_pronom_sig_version", lambda: None)

    with pytest.raises(SystemExit) as exc:
        update_signatures_module.sig_version_check("latest")

    assert "Failed to obtain PRONOM signature file version number" in str(exc.value)


def test_init_sig_download_creates_directory(update_signatures_module, monkeypatch, tmp_path):
    target = tmp_path / "tmp_download"
    prompts = iter([True])
    monkeypatch.setattr(update_signatures_module, "query_yes_no", lambda _q: next(prompts))

    tmpdir, resume = update_signatures_module.init_sig_download({"tmp_dir": str(target)})

    assert tmpdir == str(target)
    assert resume is False
    assert target.is_dir()


def test_init_sig_download_exits_when_user_declines(update_signatures_module, monkeypatch, tmp_path):
    monkeypatch.setattr(update_signatures_module, "query_yes_no", lambda _q: False)

    with pytest.raises(SystemExit) as exc:
        update_signatures_module.init_sig_download({"tmp_dir": str(tmp_path / "nope")})

    assert str(exc.value) == update_signatures_module.ABORT_MSG


def test_init_sig_download_resumes_existing_directory(update_signatures_module, monkeypatch, tmp_path):
    target = tmp_path / "tmp_download"
    target.mkdir()
    prompts = iter([True, True])
    monkeypatch.setattr(update_signatures_module, "query_yes_no", lambda _q: next(prompts))

    tmpdir, resume = update_signatures_module.init_sig_download({"tmp_dir": str(target)})

    assert tmpdir == str(target)
    assert resume is True


def test_init_sig_download_start_over_existing_directory(update_signatures_module, monkeypatch, tmp_path):
    target = tmp_path / "tmp_download"
    target.mkdir()
    prompts = iter([True, False])
    monkeypatch.setattr(update_signatures_module, "query_yes_no", lambda _q: next(prompts))

    tmpdir, resume = update_signatures_module.init_sig_download({"tmp_dir": str(target)})

    assert tmpdir == str(target)
    assert resume is False


def test_init_sig_download_reports_failed_mkdir(update_signatures_module, monkeypatch, capsys, tmp_path):
    target = tmp_path / "tmp_download"
    monkeypatch.setattr(update_signatures_module, "query_yes_no", lambda _q: True)
    monkeypatch.setattr(update_signatures_module.os, "mkdir", lambda _p: (_ for _ in ()).throw(OSError("fail")))
    monkeypatch.setattr(update_signatures_module.os.path, "isdir", lambda _p: False)

    tmpdir, resume = update_signatures_module.init_sig_download({"tmp_dir": str(target)})

    assert tmpdir == str(target)
    assert resume is False
    assert "Failed to create temporary folder for PUID's" in capsys.readouterr().err


def test_download_sig_skips_existing_when_resuming(update_signatures_module, monkeypatch, tmp_path):
    called = {"download": 0}
    format_ele = SimpleNamespace(get=lambda key: "fmt/18" if key == "PUID" else None)
    existing = tmp_path / "puid.fmt.18.xml"
    existing.write_text("already", encoding="utf-8")

    monkeypatch.setattr(update_signatures_module, "get_sig_xml_for_puid", lambda _p: called.__setitem__("download", 1))

    update_signatures_module.download_sig(format_ele, str(tmp_path), True, {"http_throttle": 0.0})

    assert called["download"] == 0
    assert existing.read_text(encoding="utf-8") == "already"


def test_download_sig_exits_on_download_error(update_signatures_module, monkeypatch, tmp_path):
    format_ele = SimpleNamespace(get=lambda key: "fmt/18" if key == "PUID" else None)
    monkeypatch.setattr(update_signatures_module, "get_sig_xml_for_puid", lambda _p: (_ for _ in ()).throw(RuntimeError("x")))

    with pytest.raises(SystemExit) as exc:
        update_signatures_module.download_sig(format_ele, str(tmp_path), False, {"http_throttle": 0.0})

    assert "Please restart and resume download" in str(exc.value)


def test_download_sig_writes_xml_and_sleeps(update_signatures_module, monkeypatch, tmp_path):
    format_ele = SimpleNamespace(get=lambda key: "fmt/18" if key == "PUID" else None)
    calls = {"sleep": 0}
    monkeypatch.setattr(update_signatures_module, "get_sig_xml_for_puid", lambda _p: b"<xml/>")
    monkeypatch.setattr(update_signatures_module.time, "sleep", lambda _s: calls.__setitem__("sleep", calls["sleep"] + 1))

    update_signatures_module.download_sig(format_ele, str(tmp_path), False, {"http_throttle": 0.0})

    assert (tmp_path / "puid.fmt.18.xml").read_bytes() == b"<xml/>"
    assert calls["sleep"] == 1


def test_create_zip_file_honors_keep_temp_option(update_signatures_module, monkeypatch, tmp_path):
    monkeypatch.setattr(update_signatures_module, "CONFIG_DIR", str(tmp_path))

    format_ele = SimpleNamespace(get=lambda key: "fmt/18" if key == "PUID" else None)
    source = tmp_path / "puid.fmt.18.xml"
    source.write_bytes(b"<xml/>")

    update_signatures_module.create_zip_file(
        {"deleteTempDirectory": False},
        [format_ele],
        "117",
        str(tmp_path),
    )

    archive = tmp_path / "pronom-xml-v117.zip"
    assert archive.exists()
    assert source.exists()


def test_create_zip_file_deletes_temp_files_when_configured(update_signatures_module, monkeypatch, tmp_path):
    monkeypatch.setattr(update_signatures_module, "CONFIG_DIR", str(tmp_path))

    format_ele = SimpleNamespace(get=lambda key: "fmt/18" if key == "PUID" else None)
    source = tmp_path / "puid.fmt.18.xml"
    source.write_bytes(b"<xml/>")

    update_signatures_module.create_zip_file(
        {"deleteTempDirectory": True},
        [format_ele],
        "117",
        str(tmp_path),
    )

    assert (tmp_path / "pronom-xml-v117.zip").exists()
    assert not source.exists()


def test_create_zip_file_skips_missing_temp_file(update_signatures_module, monkeypatch, tmp_path):
    monkeypatch.setattr(update_signatures_module, "CONFIG_DIR", str(tmp_path))
    format_ele = SimpleNamespace(get=lambda key: "fmt/404" if key == "PUID" else None)

    update_signatures_module.create_zip_file(
        {"deleteTempDirectory": True},
        [format_ele],
        "117",
        str(tmp_path),
    )

    assert (tmp_path / "pronom-xml-v117.zip").exists()


def test_run_calls_expected_pipeline(update_signatures_module, monkeypatch):
    calls = []
    format_eles = [SimpleNamespace(get=lambda key: "fmt/1" if key == "PUID" else None)]

    monkeypatch.setattr(update_signatures_module, "sig_version_check", lambda _v: (calls.append("sig_version_check") or ("116", "sig.xml")))
    monkeypatch.setattr(update_signatures_module, "download_sig_file", lambda _v, _s: calls.append("download_sig_file"))
    monkeypatch.setattr(
        update_signatures_module.CET,
        "parse",
        lambda _sig: SimpleNamespace(findall=lambda _path, _ns: format_eles),
    )
    monkeypatch.setattr(update_signatures_module, "init_sig_download", lambda _d: (calls.append("init_sig_download") or ("tmp", False)))
    monkeypatch.setattr(update_signatures_module, "download_signatures", lambda *_a: calls.append("download_signatures"))
    monkeypatch.setattr(update_signatures_module, "create_zip_file", lambda *_a: calls.append("create_zip_file"))
    monkeypatch.setattr(update_signatures_module, "rmtree", lambda *_a, **_k: calls.append("rmtree"))
    monkeypatch.setattr(update_signatures_module, "update_versions_xml", lambda _v: calls.append("update_versions_xml"))
    monkeypatch.setattr(update_signatures_module, "prepare_pronom_to_fido", lambda: calls.append("prepare_pronom_to_fido"))

    update_signatures_module.run({"version": "latest", "deleteTempDirectory": True})

    assert calls == [
        "sig_version_check",
        "download_sig_file",
        "init_sig_download",
        "download_signatures",
        "create_zip_file",
        "rmtree",
        "update_versions_xml",
        "prepare_pronom_to_fido",
    ]


def test_run_skips_rmtree_when_delete_disabled(update_signatures_module, monkeypatch):
    calls = []
    format_eles = [SimpleNamespace(get=lambda key: "fmt/1" if key == "PUID" else None)]

    monkeypatch.setattr(update_signatures_module, "sig_version_check", lambda _v: (calls.append("sig_version_check") or ("116", "sig.xml")))
    monkeypatch.setattr(update_signatures_module, "download_sig_file", lambda _v, _s: calls.append("download_sig_file"))
    monkeypatch.setattr(
        update_signatures_module.CET,
        "parse",
        lambda _sig: SimpleNamespace(findall=lambda _path, _ns: format_eles),
    )
    monkeypatch.setattr(update_signatures_module, "init_sig_download", lambda _d: (calls.append("init_sig_download") or ("tmp", False)))
    monkeypatch.setattr(update_signatures_module, "download_signatures", lambda *_a: calls.append("download_signatures"))
    monkeypatch.setattr(update_signatures_module, "create_zip_file", lambda *_a: calls.append("create_zip_file"))
    monkeypatch.setattr(update_signatures_module, "rmtree", lambda *_a, **_k: calls.append("rmtree"))
    monkeypatch.setattr(update_signatures_module, "update_versions_xml", lambda _v: calls.append("update_versions_xml"))
    monkeypatch.setattr(update_signatures_module, "prepare_pronom_to_fido", lambda: calls.append("prepare_pronom_to_fido"))

    update_signatures_module.run({"version": "latest", "deleteTempDirectory": False})

    assert "rmtree" not in calls


def test_run_exits_on_keyboard_interrupt(update_signatures_module, monkeypatch):
    monkeypatch.setattr(update_signatures_module, "sig_version_check", lambda _v: (_ for _ in ()).throw(KeyboardInterrupt()))

    with pytest.raises(SystemExit) as exc:
        update_signatures_module.run({"version": "latest", "deleteTempDirectory": True})

    assert str(exc.value) == update_signatures_module.ABORT_MSG


def test_download_signatures_processes_all_entries(update_signatures_module, monkeypatch):
    format_eles = [
        SimpleNamespace(get=lambda key, val=v: val if key == "PUID" else None)
        for v in ["fmt/1", "fmt/2", "fmt/3"]
    ]
    calls = {"count": 0}

    monkeypatch.setattr(update_signatures_module, "download_sig", lambda *_a: calls.__setitem__("count", calls["count"] + 1))

    update_signatures_module.download_signatures({"http_throttle": 0.0}, format_eles, False, os.getcwd())

    assert calls["count"] == 3


def test_main_parses_cli_args_and_calls_run(update_signatures_module, monkeypatch):
    captured = {}
    monkeypatch.setattr(
        update_signatures_module.sys,
        "argv",
        [
            "prog",
            "-tmpdir",
            "/tmp/fido",
            "-keep_tmp",
            "-http_throttle",
            "0.1",
            "-version",
            "116",
        ],
    )
    monkeypatch.setattr(update_signatures_module, "run", lambda opts: captured.__setitem__("opts", opts))

    update_signatures_module.main()

    assert captured["opts"]["tmp_dir"] == "/tmp/fido"
    assert captured["opts"]["deleteTempDirectory"] is False
    assert captured["opts"]["http_throttle"] == 0.1
    assert captured["opts"]["version"] == "116"
    assert captured["opts"]["signatureFileName"] == update_signatures_module.DEFAULTS["signatureFileName"]
