"""Complete unit tests for config_setting (reference solution)."""
import pytest

from ansible_helpers import (
    AnsibleExitJson,
    AnsibleFailJson,
    set_module_args,
    patch_ansible,
)

from ansible_collections.workshop.demo.plugins.modules import config_setting


@pytest.fixture(autouse=True)
def _patch(monkeypatch):
    patch_ansible(monkeypatch)


def test_creates_setting(tmp_path):
    conf = tmp_path / "app.conf"
    set_module_args({"path": str(conf), "key": "debug", "value": "true"})

    with pytest.raises(AnsibleExitJson) as exc:
        config_setting.run_module()

    assert exc.value.result["changed"] is True
    assert conf.read_text().strip() == "debug=true"


def test_idempotent_second_run(tmp_path):
    conf = tmp_path / "app.conf"
    args = {"path": str(conf), "key": "debug", "value": "true"}

    set_module_args(args)
    with pytest.raises(AnsibleExitJson) as first:
        config_setting.run_module()
    assert first.value.result["changed"] is True

    set_module_args(args)
    with pytest.raises(AnsibleExitJson) as second:
        config_setting.run_module()
    assert second.value.result["changed"] is False


def test_updates_existing_value(tmp_path):
    conf = tmp_path / "app.conf"
    conf.write_text("debug=false\n")

    set_module_args({"path": str(conf), "key": "debug", "value": "true"})
    with pytest.raises(AnsibleExitJson) as exc:
        config_setting.run_module()

    assert exc.value.result["changed"] is True
    assert conf.read_text().strip() == "debug=true"


def test_check_mode_does_not_write(tmp_path):
    conf = tmp_path / "app.conf"
    set_module_args({
        "path": str(conf),
        "key": "debug",
        "value": "true",
        "_ansible_check_mode": True,
    })

    with pytest.raises(AnsibleExitJson) as exc:
        config_setting.run_module()

    assert exc.value.result["changed"] is True
    assert not conf.exists()


def test_preserves_other_lines(tmp_path):
    conf = tmp_path / "app.conf"
    conf.write_text("keep=me\ndebug=false\n")

    set_module_args({"path": str(conf), "key": "debug", "value": "true"})
    with pytest.raises(AnsibleExitJson):
        config_setting.run_module()

    text = conf.read_text()
    assert "keep=me" in text
    assert "debug=true" in text
