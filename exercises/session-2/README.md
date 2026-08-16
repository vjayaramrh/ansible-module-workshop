# Session 2 — Exercises

> Inside the devcontainer. Work from: `cd exercises/session-2`

Build **`config_setting`**: a module that ensures a `key=value` line exists in a
config file — the beginner's version of `lineinfile`. This is where idempotency
becomes real.

`config_setting.py` is a **skeleton with TODOs**. Fill them in.

---

## The spec

`config_setting` takes:
- `path` (str, required) — the config file
- `key` (str, required) — the setting name
- `value` (str, required) — the desired value

Behavior: after it runs, the file contains a line `key=value`.
- If that exact line already exists → `changed=false`
- If the key exists with a different value → replace it → `changed=true`
- If the key is absent → append it → `changed=true`

---

## Tasks

1. **Declare inputs.** Fill in `argument_spec` (all three, all `required=True`)
   and pass `supports_check_mode=True`.

2. **Observe.** Read the file if it exists; find the current value for `key` (if any).

3. **Compare.** If the current line already equals the desired `key=value`,
   `exit_json(changed=False)`.

4. **Check mode.** If a change *is* needed but `module.check_mode` is true,
   `exit_json(changed=True)` **without writing**.

5. **Act.** Otherwise write the file (replace or append the line), then
   `exit_json(changed=True, ...)`.

6. **Diff.** Include a `diff={"before": ..., "after": ...}` in your final
   `exit_json` so `--diff` works.

7. **Docs.** Fill in the `DOCUMENTATION`, `EXAMPLES`, and `RETURN` strings so they
   match your `argument_spec`. (Session 3's sanity tests will check this!)

---

## Test it by hand

```bash
# First run: creates the file → changed true
python config_setting.py args.json

# Second run, same args: → changed FALSE (idempotent!)
python config_setting.py args.json

# Change the value in args.json, run again → changed true
```

Inspect the file it manages (default `/tmp/app.conf`):

```bash
cat /tmp/app.conf
```

---

## ✅ Acceptance checks

- Running twice with identical args → second run reports `"changed": false`
- Changing `value` and re-running → `"changed": true` and the file is updated
- A run that *would* change something with check mode on doesn't write the file.
  Test it:
  ```bash
  rm -f /tmp/app.conf
  # add "_ansible_check_mode": true inside ANSIBLE_MODULE_ARGS in args.json, run:
  python config_setting.py args.json
  cat /tmp/app.conf   # → should NOT exist / be empty; module still reports changed true
  ```
- `DOCUMENTATION` options list matches `argument_spec` keys exactly.

---

## Done?

Compare with [`../../solutions/session-2/config_setting.py`](../../solutions/session-2/config_setting.py).
Keep your working module — **Session 3 tests this exact module.**
