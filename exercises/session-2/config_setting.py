#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Workshop Team
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

# Session 2 starter. Fill in the TODOs to make it idempotent + check-mode aware.
# (The license header above + __future__ lines are standard boilerplate every
#  real module carries; sanity tests in Session 3 require the GPL header.)
# Run with:  python config_setting.py args.json

DOCUMENTATION = r'''
---
module: config_setting
short_description: Ensure a key=value line exists in a config file
description:
  - Manages a single C(key=value) line in a simple config file.
options:
  path:
    description: Path to the config file to manage.
    required: true
    type: str
  key:
    description: The setting name.
    required: true
    type: str
  value:
    description: The desired value for the setting.
    required: true
    type: str
author:
  - Workshop Team (@workshop)
# TODO: make sure every option above matches your argument_spec exactly.
'''

EXAMPLES = r'''
- name: Ensure debug is enabled
  config_setting:
    path: /etc/app.conf
    key: debug
    value: "true"
'''

RETURN = r'''
value:
  description: The value now set for the key.
  returned: always
  type: str
'''

from ansible.module_utils.basic import AnsibleModule


def find_current_value(lines, key):
    """Return the current value for key, or None if not present."""
    prefix = key + "="
    for line in lines:
        if line.strip().startswith(prefix):
            return line.strip()[len(prefix):]
    return None


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            # TODO: declare path, key, value (all type="str", required=True)
        ),
        supports_check_mode=True,
    )

    path = module.params["path"]
    key = module.params["key"]
    value = module.params["value"]
    desired_line = "%s=%s" % (key, value)

    # 1. OBSERVE ------------------------------------------------------------
    try:
        with open(path, "r") as fh:
            lines = fh.read().splitlines()
    except FileNotFoundError:
        lines = []
    except OSError as e:
        module.fail_json(msg="Could not read %s: %s" % (path, e))

    before = "\n".join(lines)
    current = find_current_value(lines, key)

    # 2. COMPARE ------------------------------------------------------------
    # TODO: if current == value, nothing to do → exit_json(changed=False, value=value)

    # 3. Build the desired file content (replace existing key or append) -----
    new_lines = []
    replaced = False
    for line in lines:
        if line.strip().startswith(key + "="):
            new_lines.append(desired_line)
            replaced = True
        else:
            new_lines.append(line)
    if not replaced:
        new_lines.append(desired_line)
    after = "\n".join(new_lines)

    # 4. CHECK MODE ---------------------------------------------------------
    # TODO: if module.check_mode: exit_json(changed=True, ...) WITHOUT writing.

    # 5. ACT ----------------------------------------------------------------
    try:
        with open(path, "w") as fh:
            fh.write(after + "\n")
    except OSError as e:
        module.fail_json(msg="Could not write %s: %s" % (path, e))

    # 6. RETURN (with diff) -------------------------------------------------
    module.exit_json(
        changed=True,
        value=value,
        diff={"before": before + "\n", "after": after + "\n"},
    )


if __name__ == "__main__":
    run_module()
