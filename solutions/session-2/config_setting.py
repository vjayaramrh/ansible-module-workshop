#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Workshop Team
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

# Session 2 solution — idempotent, check-mode aware, with diff and full docs.
# Also passes `ansible-test sanity` (see the header + no_log below).
# Run with:  python config_setting.py args.json

DOCUMENTATION = r'''
---
module: config_setting
short_description: Ensure a key=value line exists in a config file
description:
  - Manages a single C(key=value) line in a simple config file.
  - Idempotent - re-running with the same value reports no change.
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
  sample: "true"
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
            path=dict(type="str", required=True),
            # no_log=False: 'key' looks secret-y to sanity checks; say it isn't.
            key=dict(type="str", required=True, no_log=False),
            value=dict(type="str", required=True),
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
    if current == value:
        # Already in the desired state → honest no-op.
        module.exit_json(changed=False, value=value)

    # 3. Build desired content (replace existing key, else append) ----------
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

    result_diff = {"before": before + "\n", "after": after + "\n"}

    # 4. CHECK MODE ---------------------------------------------------------
    if module.check_mode:
        # We know a change is needed, but must not write anything.
        module.exit_json(changed=True, value=value, diff=result_diff)

    # 5. ACT ----------------------------------------------------------------
    try:
        with open(path, "w") as fh:
            fh.write(after + "\n")
    except OSError as e:
        module.fail_json(msg="Could not write %s: %s" % (path, e))

    # 6. RETURN -------------------------------------------------------------
    module.exit_json(changed=True, value=value, diff=result_diff)


if __name__ == "__main__":
    run_module()
