"""Complete unit tests for webhook_resource (fetch_url mocked, reference)."""
import pytest

from ansible_helpers import (
    AnsibleExitJson,
    AnsibleFailJson,
    set_module_args,
    patch_ansible,
)

from ansible_collections.workshop.web.plugins.modules import webhook_resource


@pytest.fixture(autouse=True)
def _patch(monkeypatch):
    patch_ansible(monkeypatch)


def make_fetch(status_sequence):
    """Fake fetch_url yielding the given HTTP statuses in order."""
    statuses = list(status_sequence)

    def fake_fetch(module, url, **kwargs):
        status = statuses.pop(0)
        return None, {"status": status}

    return fake_fetch


def test_present_creates_when_missing(monkeypatch):
    monkeypatch.setattr(webhook_resource, "fetch_url", make_fetch([404, 201]))
    set_module_args({"base_url": "http://x", "name": "demo", "state": "present"})
    with pytest.raises(AnsibleExitJson) as exc:
        webhook_resource.run_module()
    assert exc.value.result["changed"] is True


def test_present_is_idempotent_when_exists(monkeypatch):
    monkeypatch.setattr(webhook_resource, "fetch_url", make_fetch([200]))
    set_module_args({"base_url": "http://x", "name": "demo", "state": "present"})
    with pytest.raises(AnsibleExitJson) as exc:
        webhook_resource.run_module()
    assert exc.value.result["changed"] is False


def test_absent_deletes_when_present(monkeypatch):
    monkeypatch.setattr(webhook_resource, "fetch_url", make_fetch([200, 204]))
    set_module_args({"base_url": "http://x", "name": "demo", "state": "absent"})
    with pytest.raises(AnsibleExitJson) as exc:
        webhook_resource.run_module()
    assert exc.value.result["changed"] is True


def test_absent_is_idempotent_when_missing(monkeypatch):
    monkeypatch.setattr(webhook_resource, "fetch_url", make_fetch([404]))
    set_module_args({"base_url": "http://x", "name": "demo", "state": "absent"})
    with pytest.raises(AnsibleExitJson) as exc:
        webhook_resource.run_module()
    assert exc.value.result["changed"] is False


def test_check_mode_does_not_create(monkeypatch):
    # Only a GET (404) is provided; if the module tries to POST, make_fetch
    # runs out of statuses and raises IndexError, failing the test.
    monkeypatch.setattr(webhook_resource, "fetch_url", make_fetch([404]))
    set_module_args({
        "base_url": "http://x", "name": "demo",
        "state": "present", "_ansible_check_mode": True,
    })
    with pytest.raises(AnsibleExitJson) as exc:
        webhook_resource.run_module()
    assert exc.value.result["changed"] is True


def test_unexpected_status_fails(monkeypatch):
    monkeypatch.setattr(webhook_resource, "fetch_url", make_fetch([500]))
    set_module_args({"base_url": "http://x", "name": "demo", "state": "present"})
    with pytest.raises(AnsibleFailJson):
        webhook_resource.run_module()
