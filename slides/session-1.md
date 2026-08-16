---
marp: true
title: "Session 1 — Foundations & Your First Module"
paginate: true
theme: default
---

# Writing Ansible Modules
## Session 1 — Foundations & Your First Module

*From Ansible **user** to Ansible **author**.*

---

## Where we're going (the whole series)

1. **Foundations & your first module** ← today
2. Idempotency, check mode & return values
3. Testing with `ansible-test`
4. Packaging into a collection + capstone

By the end you'll have written, tested, and *shipped* a real module.

---

## Today's goals

- Know what a module **is** (and isn't)
- Know **when not to write one**
- Understand the **anatomy** of a module: `AnsibleModule`, `argument_spec`, `exit_json`/`fail_json`
- **Run your own module** standalone — twice

---

## What *is* a module?

> A module is just a small program that:
> 1. reads **JSON arguments** on stdin/from a file,
> 2. does one unit of work on the target host,
> 3. prints a **single JSON object** to stdout.

That's the whole contract. Everything else is convenience.

Ansible copies it to the target, runs it, parses the JSON it prints.

---

## Module vs role vs plugin

| Thing | What it is | Runs where |
|-------|-----------|------------|
| **Module** | A task's unit of work (`copy`, `file`, your own) | On the **target** host |
| **Role** | A reusable bundle of tasks/vars/templates | Orchestration (controller) |
| **Plugin** | Extends Ansible itself (lookup, filter, connection…) | Mostly on the **controller** |

Today = **modules**. Plugins are a later adventure.

---

## When should you write a module? 🛑

Write one when:
- You call the same API/tool repeatedly and want **idempotent**, **check-mode-aware** tasks
- `command`/`shell` is getting gnarly and fragile

**Don't** write one when:
- A **role** or existing module already does it
- `command`/`shell` with `creates:`/`removes:` is genuinely enough
- Someone already published it (search Galaxy first!)

*The best module is often the one you didn't have to write.*

---

## Why modules run on the target

The controller **ships the module code** to the managed host and executes it there.

Consequences:
- Keep dependencies minimal (the target may be spartan)
- You can't rely on the controller's filesystem
- stdout is sacred: **print only the final JSON**

---

## Anatomy of a minimal module

```python
#!/usr/bin/python
from ansible.module_utils.basic import AnsibleModule

def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=False, default="world"),
        ),
    )
    greeting = "Hello, %s!" % module.params["name"]
    module.exit_json(changed=False, greeting=greeting)

if __name__ == "__main__":
    run_module()
```

---

## The three pieces you always touch

- **`argument_spec`** — declares your inputs: type, required, default, choices.
  Ansible validates against it *for you*.
- **`module.params`** — the validated inputs, as a dict.
- **`exit_json(...)` / `fail_json(msg=...)`** — the *only* correct way to finish.
  They print the JSON and exit. Never `print()` or `sys.exit()` yourself.

---

## Running a module standalone

Modules expect `{"ANSIBLE_MODULE_ARGS": {...}}`. For example:

```json
{ "ANSIBLE_MODULE_ARGS": { "name": "workshop" } }
```

Run it:

```bash
python hello.py args.json
```

Output (single line):

```json
{"changed": false, "greeting": "Hello, workshop!", ...}
```

*This is exactly how Ansible invokes it — no magic.*

---

## `changed`: your first taste of idempotency

Every module returns `changed` (true/false).

- `changed=false` → "nothing needed doing"
- `changed=true`  → "I altered the system"

Today we hard-code `changed=false`. **Session 2 is entirely about getting this right** —
it's the single most important concept in module authoring.

---

## Exercise time 🧑‍💻

Open **`exercises/session-1/README.md`**.

1. **Exercise 1:** run the provided `hello` module; make it greet *you*.
2. **Exercise 2:** add a `shout` boolean argument (uppercases the greeting) using `argument_spec`.

Acceptance checks are in the exercise. Peek at `solutions/` only if stuck >10 min.

---

## Recap

- A module = reads JSON args → does work → prints one JSON object
- `AnsibleModule(argument_spec=...)` validates inputs for you
- Finish with `exit_json` / `fail_json` — nothing else
- `changed` is a promise about whether you altered the system

**Next time:** making that promise *true* — idempotency, `--check`, and clean returns.
