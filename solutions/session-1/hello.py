#!/usr/bin/python
# Session 1 solution — includes the `shout` option from Exercise 2.
# Run with:  python hello.py args.json
from ansible.module_utils.basic import AnsibleModule


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            # `name` is optional and defaults to "world".
            name=dict(type="str", required=False, default="world"),
            # Exercise 2: a boolean flag. Ansible validates the type for us, so
            # passing "banana" here fails with a clear error automatically.
            shout=dict(type="bool", required=False, default=False),
        ),
    )

    greeting = "Hello, %s!" % module.params["name"]

    if module.params["shout"]:
        greeting = greeting.upper()

    # This module never touches the target system, so changed is honestly False.
    module.exit_json(changed=False, greeting=greeting)


if __name__ == "__main__":
    run_module()
