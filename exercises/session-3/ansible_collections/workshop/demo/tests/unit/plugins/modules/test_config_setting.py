"""Unit tests for the config_setting module — finish the TODOs."""
import pytest

from ansible_helpers import (
    AnsibleExitJson,
    AnsibleFailJson,
    set_module_args,
    patch_ansible,
)

# Import the module under test. (When run via ansible-test the import path is
# resolved for you; pytest uses conftest.py in this dir to add the module path.)
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

    # TODO: run it a SECOND time with the same args and assert changed is False.
    #   set_module_args(args)
    #   with pytest.raises(AnsibleExitJson) as second:
    #       config_setting.run_module()
    #   assert second.value.result["changed"] is False


def test_updates_existing_value(tmp_path):
    conf = tmp_path / "app.conf"
    conf.write_text("debug=false\n")

    # TODO: set args to change debug to "true", run, and assert:
    #   - changed is True
    #   - the file now contains "debug=true"
    raise NotImplementedError("complete me")


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
    # TODO: assert the file was NOT created (check mode must not write).
    #   assert not conf.exists()
