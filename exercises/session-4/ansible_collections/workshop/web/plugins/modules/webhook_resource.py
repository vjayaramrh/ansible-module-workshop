#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Workshop Team
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

# Capstone starter. Manage a resource on a REST API, idempotently.
# Fill in the TODOs. Use fetch_url (NOT requests) so it works on any target.

DOCUMENTATION = r'''
---
module: webhook_resource
short_description: Manage a named resource on a REST API
description:
  - Ensures a named resource exists (or is absent) on a simple REST API.
options:
  base_url:
    description: Root URL of the API, e.g. http://127.0.0.1:8000
    required: true
    type: str
  name:
    description: Name of the resource to manage.
    required: true
    type: str
  state:
    description: Whether the resource should exist.
    type: str
    choices: [present, absent]
    default: present
author:
  - Workshop Team (@workshop)
# TODO: keep these options in sync with argument_spec below.
'''

EXAMPLES = r'''
- name: Ensure the resource exists
  workshop.web.webhook_resource:
    base_url: http://127.0.0.1:8000
    name: demo
    state: present
'''

RETURN = r'''
name:
  description: The resource name that was managed.
  returned: always
  type: str
'''

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url


def resource_exists(module, base_url, name):
    """Return True if GET /resources/<name> is 200, False if 404."""
    url = "%s/resources/%s" % (base_url.rstrip("/"), name)
    resp, info = fetch_url(module, url, method="GET")
    status = info["status"]
    if status == 200:
        return True
    if status == 404:
        return False
    module.fail_json(msg="Unexpected status %s from GET %s" % (status, url))


def create_resource(module, base_url, name):
    url = "%s/resources" % base_url.rstrip("/")
    body = json.dumps({"name": name})
    resp, info = fetch_url(
        module, url, method="POST", data=body,
        headers={"Content-Type": "application/json"},
    )
    if info["status"] not in (200, 201):
        module.fail_json(msg="Create failed: status %s" % info["status"])


def delete_resource(module, base_url, name):
    url = "%s/resources/%s" % (base_url.rstrip("/"), name)
    resp, info = fetch_url(module, url, method="DELETE")
    if info["status"] not in (200, 204):
        module.fail_json(msg="Delete failed: status %s" % info["status"])


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            base_url=dict(type="str", required=True),
            name=dict(type="str", required=True),
            state=dict(type="str", choices=["present", "absent"], default="present"),
        ),
        supports_check_mode=True,
    )

    base_url = module.params["base_url"]
    name = module.params["name"]
    state = module.params["state"]

    exists = resource_exists(module, base_url, name)

    # Decide whether a change is needed.
    if state == "present":
        need_change = not exists
    else:  # absent
        need_change = exists

    # No change needed → idempotent no-op.
    if not need_change:
        module.exit_json(changed=False, name=name)

    # Change needed but check mode → report without acting.
    if module.check_mode:
        module.exit_json(changed=True, name=name)

    # TODO: perform the actual change:
    #   if state == "present": create_resource(module, base_url, name)
    #   else:                  delete_resource(module, base_url, name)

    module.exit_json(changed=True, name=name)


if __name__ == "__main__":
    run_module()
