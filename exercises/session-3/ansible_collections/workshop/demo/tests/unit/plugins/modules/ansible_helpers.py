"""Tiny helpers for unit-testing modules.

This is the standard community pattern, trimmed to the essentials:
  * set_module_args(dict) puts args where AnsibleModule reads them
  * exit_json / fail_json are patched to raise, so tests can catch the result
"""
import json

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes


class AnsibleExitJson(Exception):
    """Raised (instead of sys.exit) when the module calls exit_json."""
    def __init__(self, result):
        self.result = result
        super().__init__(result.get("msg", "exit_json"))


class AnsibleFailJson(Exception):
    """Raised (instead of sys.exit) when the module calls fail_json."""
    def __init__(self, result):
        self.result = result
        super().__init__(result.get("msg", "fail_json"))


def set_module_args(args):
    """Feed args to the next AnsibleModule() construction in this process."""
    serialized = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(serialized)


def exit_json(self, **kwargs):
    kwargs.setdefault("changed", False)
    raise AnsibleExitJson(kwargs)


def fail_json(self, **kwargs):
    kwargs["failed"] = True
    raise AnsibleFailJson(kwargs)


def patch_ansible(monkeypatch):
    """Call from a fixture/test to swap in the raising versions."""
    monkeypatch.setattr(basic.AnsibleModule, "exit_json", exit_json)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", fail_json)
