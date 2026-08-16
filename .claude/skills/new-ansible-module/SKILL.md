---
name: new-ansible-module
description: Scaffold a new, convention-correct Ansible module in this workshop repo — module file with the required GPL header + DOCUMENTATION/EXAMPLES/RETURN + an idempotent, check-mode-aware run_module skeleton, plus a unit test (with an idempotency case) and the conftest/helpers. Use when the user wants to add a new module or start a new collection module and wants it to pass `ansible-test sanity` on the first try.
---

# Scaffold a new Ansible module

Follow the conventions in this repo's `CLAUDE.md`. The goal: a module that passes
`./run.sh --full` (pytest + `ansible-test sanity`) without rework.

## 1. Gather the essentials

Ask the user (or infer from their request) — keep it to what you can't guess:

- **Module name** (snake_case), e.g. `config_setting`, `webhook_resource`.
- **Collection** as `namespace.name` (default to an existing one in the repo, e.g.
  `workshop.demo`, unless they want a new collection).
- **Arguments**: for each, the name, type (`str`/`bool`/`int`/`list`/`dict`), whether
  required, default, and choices.
- **Shape**: is it **state-based** (`state: present/absent`, create/delete a thing) or
  **value-based** (ensure some setting/content equals a desired value)? This picks the
  idempotency skeleton.

If a collection doesn't exist yet, also create `galaxy.yml` (namespace/name MUST match
the directory path) and a `README.md`.

## 2. Create the files

Target layout (create dirs as needed):

```
ansible_collections/<namespace>/<name>/
├── plugins/modules/<module>.py
└── tests/unit/plugins/modules/
    ├── ansible_helpers.py     # copy from an existing collection in this repo
    ├── conftest.py            # copy from an existing collection in this repo
    └── test_<module>.py
```

Copy `ansible_helpers.py` and `conftest.py` verbatim from
`solutions/session-3/ansible_collections/workshop/demo/tests/unit/plugins/modules/`
— they're already correct (the conftest walks up to `ansible_collections/`; do not
hardcode `../` counts).

## 3. Module template

Fill this in. Keep every convention from `CLAUDE.md` (header, matching docs, valid
author, `no_log=False` for secret-looking-but-not-secret args, check mode, honest
`changed`, `exit_json`/`fail_json` only).

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Workshop Team
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: <module>
short_description: <one line, no trailing period>
description:
  - <what it does>
options:
  <arg>:
    description: <...>
    required: <true|false>
    type: <str|bool|int|list|dict>
    # choices: [a, b]        # if applicable
    # default: <...>         # if applicable
author:
  - Workshop Team (@workshop)
'''

EXAMPLES = r'''
- name: <example>
  <namespace>.<name>.<module>:
    <arg>: <value>
'''

RETURN = r'''
<key>:
  description: <...>
  returned: always
  type: <str|bool|...>
'''

from ansible.module_utils.basic import AnsibleModule
# from ansible.module_utils.urls import fetch_url   # if the module talks HTTP


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            # arg=dict(type="str", required=True),
            # secret_looking_but_not=dict(type="str", required=True, no_log=False),
        ),
        supports_check_mode=True,
    )

    # 1. OBSERVE current state
    # current = ...

    # 2. COMPARE to desired; honest no-op if already correct
    # if current == desired:
    #     module.exit_json(changed=False, ...)

    # 3. CHECK MODE: we know a change is needed, but must not act
    # if module.check_mode:
    #     module.exit_json(changed=True, ...)

    # 4. ACT (wrap real side effects; use fail_json on error)
    # try:
    #     ...
    # except Exception as e:
    #     module.fail_json(msg="...: %s" % e)

    module.exit_json(changed=True)


if __name__ == "__main__":
    run_module()
```

**State-based idempotency** (`present`/`absent`): observe existence → `need_change =
(not exists) if state == "present" else exists` → no-op if `not need_change` → check
mode → create/delete. See `solutions/session-4/.../webhook_resource.py`.

**Value-based idempotency**: read current value → no-op if it already equals desired →
check mode → write. See `solutions/session-2/config_setting.py`.

## 4. Unit test template

Always include a **create/act** test AND an **idempotency** test (and a **check-mode**
test that asserts no side effect). Mock any network with `monkeypatch.setattr(<module>,
"fetch_url", ...)`.

```python
import pytest
from ansible_helpers import (
    AnsibleExitJson, AnsibleFailJson, set_module_args, patch_ansible,
)
from ansible_collections.<namespace>.<name>.plugins.modules import <module>


@pytest.fixture(autouse=True)
def _patch(monkeypatch):
    patch_ansible(monkeypatch)


def test_makes_change(...):
    set_module_args({...})
    with pytest.raises(AnsibleExitJson) as exc:
        <module>.run_module()
    assert exc.value.result["changed"] is True


def test_idempotent_second_run(...):
    # run twice with same args; assert first changed True, second False
    ...


def test_check_mode_no_side_effect(...):
    set_module_args({..., "_ansible_check_mode": True})
    with pytest.raises(AnsibleExitJson) as exc:
        <module>.run_module()
    assert exc.value.result["changed"] is True
    # assert the side effect did NOT happen
```

## 5. Verify

Run the fast suite, then the deep one:

```bash
./run.sh --check
# and, for the new module's collection:
./run.sh bash -lc "cd ansible_collections/<namespace>/<name> && \
  ansible-test sanity --test validate-modules plugins/modules/<module>.py && \
  python -m pytest tests/unit/plugins/modules/test_<module>.py -q"
```

Fix anything sanity reports (see the findings→fixes table in
`exercises/session-3/README.md`). Don't consider the module done until sanity + pytest
are green. Optionally add it to `scripts/smoke.sh` so CI covers it too.
