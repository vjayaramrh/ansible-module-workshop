#!/usr/bin/python
# Session 1 starter module. Run it with:  python hello.py args.json
from ansible.module_utils.basic import AnsibleModule


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=False, default="world"),
            # TODO (Exercise 2): add a `shout` boolean option here,
            #   type="bool", default=False
        ),
    )

    greeting = "Hello, %s!" % module.params["name"]

    # TODO (Exercise 2): if module.params["shout"] is True, uppercase `greeting`.

    # This module never changes the target, so changed is honestly False.
    module.exit_json(changed=False, greeting=greeting)


if __name__ == "__main__":
    run_module()
