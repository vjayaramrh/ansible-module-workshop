---
marp: true
title: "Session 2 — Idempotency, Check Mode & Return Values"
paginate: true
theme: default
---

# Session 2
## Idempotency, Check Mode & Return Values

*Making `changed` tell the truth.*

---

## Today's goals

- Understand **idempotency** and get `changed` right
- Support **check mode** (`--check`) — predict without doing
- Support **diff mode** (`--diff`) — show what changed
- Return **clean, documented** data (`DOCUMENTATION` / `EXAMPLES` / `RETURN`)
- Handle **errors** the Ansible way

---

## New concepts this session

idempotency · check mode (`supports_check_mode`, `module.check_mode`) ·
diff mode · `DOCUMENTATION`/`EXAMPLES`/`RETURN` · module boilerplate
(GPL header, `__future__`) · `author` format · `no_log=False` · `fetch_url`

*New to any of these? See [`GLOSSARY.md`](../GLOSSARY.md).*

---

## Idempotency: the one idea that matters

> Running the module twice should change the system **at most once**.

The second run should report `changed=false` because there's nothing left to do.

This is what makes Ansible **declarative**: you describe the desired state,
the module figures out whether reality already matches.

---

## The idempotency pattern

```python
current = read_current_state()      # 1. observe
desired = module.params["value"]    # 2. desired
if current == desired:
    module.exit_json(changed=False) # 3a. already correct → done
# 3b. differs → change it
write_new_state(desired)
module.exit_json(changed=True)
```

**Observe → compare → act only if needed.** Memorize this shape.

---

## Anti-pattern: the liar module

```python
# ❌ Always claims it changed something
subprocess.run(["do-the-thing"])
module.exit_json(changed=True)
```

Why it's harmful:
- Breaks `--check` (can't predict)
- Fires **handlers** every run (restarts, reloads…)
- Erodes trust: `changed` becomes noise

---

## Check mode: predict, don't do

`--check` asks: *"What would happen?"* — without touching anything.

```python
if current == desired:
    module.exit_json(changed=False)

if module.check_mode:
    module.exit_json(changed=True)   # would change, but don't

write_new_state(desired)             # only reached when NOT check mode
module.exit_json(changed=True)
```

Declare support: `AnsibleModule(..., supports_check_mode=True)`

---

## Diff mode: show the change

When the user passes `--diff`, return a `diff` dict:

```python
result_diff = {
    "before": current + "\n",
    "after":  desired + "\n",
}
module.exit_json(changed=True, diff=result_diff)
```

Ansible renders a familiar `before/after` diff. Cheap to add, users love it.

---

## Return values: be tidy

- Always return `changed`.
- Return useful facts the next task can use (e.g. the final value, a path, an id).
- Don't dump internal junk. Return what a *user* would want.

```python
module.exit_json(
    changed=True,
    path=path,
    value=desired,
)
```

---

## Error handling

Use `fail_json` — never raise raw exceptions or `sys.exit`.

```python
try:
    write_new_state(desired)
except OSError as e:
    module.fail_json(msg="Could not write %s: %s" % (path, e))
```

`fail_json(msg=...)` prints `{"failed": true, "msg": ...}` and exits non-zero.
`msg` is **required** and should be actionable.

---

## The three documentation blocks

Every real module has these as module-level strings:

```python
DOCUMENTATION = r'''
module: config_setting
short_description: Manage a key=value line in a config file
options:
  path: { description: File to manage, required: true, type: str }
  key:  { description: Setting name, required: true, type: str }
'''
EXAMPLES = r'''
- name: Ensure debug is on
  config_setting: { path: /etc/app.conf, key: debug, value: "true" }
'''
RETURN = r'''
value: { description: The value that is now set, type: str, returned: always }
'''
```

---

## Why the docs matter (beyond being nice)

- `ansible-doc your_module` renders them.
- **Sanity tests (Session 3) fail if `options` don't match `argument_spec`.**
  The docs are *checked*, not decorative.
- They force you to design your interface before coding.

---

## Exercise time 🧑‍💻

Open **`exercises/session-2/README.md`**.

Build **`config_setting`**: ensure `key=value` exists in a file.
- Idempotent (re-run → `changed=false`)
- `supports_check_mode=True`
- Returns a `diff`
- Has `DOCUMENTATION` / `EXAMPLES` / `RETURN`

Acceptance checks included. This module comes back in Session 3 for testing.

---

## Recap

- **Observe → compare → act** = idempotency
- `changed` must be honest
- `supports_check_mode=True` + guard writes behind `if not module.check_mode`
- Add a `diff` for free UX
- `fail_json(msg=...)` for errors; three doc blocks for the interface

**Next time:** proving it works — `ansible-test` sanity, unit, and integration tests.
