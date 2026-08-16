#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Workshop Team
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

# Reference config_setting module — passes `ansible-test sanity`.

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
    prefix = key + "="
    for line in lines:
        if line.strip().startswith(prefix):
            return line.strip()[len(prefix):]
    return None


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type="str", required=True),
            # no_log=False tells Ansible this arg is NOT a secret. Any arg whose
            # name looks secret-y (key/password/token...) is flagged by sanity
            # unless you say so explicitly.
            key=dict(type="str", required=True, no_log=False),
            value=dict(type="str", required=True),
        ),
        supports_check_mode=True,
    )

    path = module.params["path"]
    key = module.params["key"]
    value = module.params["value"]
    desired_line = "%s=%s" % (key, value)

    try:
        with open(path, "r") as fh:
            lines = fh.read().splitlines()
    except FileNotFoundError:
        lines = []
    except OSError as e:
        module.fail_json(msg="Could not read %s: %s" % (path, e))

    before = "\n".join(lines)
    current = find_current_value(lines, key)

    if current == value:
        module.exit_json(changed=False, value=value)

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

    if module.check_mode:
        module.exit_json(changed=True, value=value, diff=result_diff)

    try:
        with open(path, "w") as fh:
            fh.write(after + "\n")
    except OSError as e:
        module.fail_json(msg="Could not write %s: %s" % (path, e))

    module.exit_json(changed=True, value=value, diff=result_diff)


if __name__ == "__main__":
    run_module()
