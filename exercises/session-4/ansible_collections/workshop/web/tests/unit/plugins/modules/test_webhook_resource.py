"""Unit tests for webhook_resource — fetch_url is mocked, so NO network.

Key idea: patch `fetch_url` in the module's namespace to return canned
(response, info) tuples. Then assert your module's decisions and `changed`.
"""
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
    """Return a fake fetch_url that yields the given statuses in order.

    Each call returns (None, {"status": <next status>}).
    """
    statuses = list(status_sequence)

    def fake_fetch(module, url, **kwargs):
        status = statuses.pop(0)
        return None, {"status": status}

    return fake_fetch


def test_present_creates_when_missing(monkeypatch):
    # GET -> 404 (missing), then POST -> 201 (created)
    monkeypatch.setattr(webhook_resource, "fetch_url", make_fetch([404, 201]))
    set_module_args({"base_url": "http://x", "name": "demo", "state": "present"})

    with pytest.raises(AnsibleExitJson) as exc:
        webhook_resource.run_module()

    assert exc.value.result["changed"] is True


def test_present_is_idempotent_when_exists(monkeypatch):
    # GET -> 200 (already exists); no POST expected
    monkeypatch.setattr(webhook_resource, "fetch_url", make_fetch([200]))
    set_module_args({"base_url": "http://x", "name": "demo", "state": "present"})

    with pytest.raises(AnsibleExitJson) as exc:
        webhook_resource.run_module()

    assert exc.value.result["changed"] is False


def test_absent_deletes_when_present(monkeypatch):
    # TODO: GET -> 200 (exists), DELETE -> 204. Assert changed is True.
    raise NotImplementedError("complete me")


def test_absent_is_idempotent_when_missing(monkeypatch):
    # TODO: GET -> 404 (already gone). Assert changed is False.
    raise NotImplementedError("complete me")


def test_check_mode_does_not_create(monkeypatch):
    # GET -> 404; even though a change is needed, check mode must not POST.
    # If your module wrongly POSTs, make_fetch([404]) will raise IndexError -> test fails.
    monkeypatch.setattr(webhook_resource, "fetch_url", make_fetch([404]))
    set_module_args({
        "base_url": "http://x", "name": "demo",
        "state": "present", "_ansible_check_mode": True,
    })

    with pytest.raises(AnsibleExitJson) as exc:
        webhook_resource.run_module()

    assert exc.value.result["changed"] is True
