"""Unit-test helpers (args + exit/fail capture)."""
import json

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes


class AnsibleExitJson(Exception):
    def __init__(self, result):
        self.result = result
        super().__init__(result.get("msg", "exit_json"))


class AnsibleFailJson(Exception):
    def __init__(self, result):
        self.result = result
        super().__init__(result.get("msg", "fail_json"))


def set_module_args(args):
    serialized = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(serialized)


def exit_json(self, **kwargs):
    kwargs.setdefault("changed", False)
    raise AnsibleExitJson(kwargs)


def fail_json(self, **kwargs):
    kwargs["failed"] = True
    raise AnsibleFailJson(kwargs)


def patch_ansible(monkeypatch):
    monkeypatch.setattr(basic.AnsibleModule, "exit_json", exit_json)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", fail_json)
