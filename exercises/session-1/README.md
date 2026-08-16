# Session 1 — Exercises

> Make sure you're **inside the devcontainer** (see [SETUP.md](../../SETUP.md)).
> Work from this folder: `cd exercises/session-1`

You'll write and run your very first module — no Ansible playbook needed yet.
A module is just a program that reads JSON args and prints one JSON object.

---

## Exercise 1 — Run the `hello` module

The file `hello.py` is a working (if boring) module. `args.json` holds its input.

1. Run it:
   ```bash
   python hello.py args.json
   ```
   You should get a single line of JSON with a `greeting`.

2. Edit `args.json` so it greets **you** by name. Re-run. Confirm the greeting changes.

3. Open `hello.py` and find where `changed` is set. Notice it's `False` — this module
   never alters the system, so it honestly reports no change.

**✅ Acceptance:** `python hello.py args.json` prints `"greeting": "Hello, <your-name>!"`.

---

## Exercise 2 — Add a `shout` option

Make the module able to SHOUT.

1. In `hello.py`, add a new key to `argument_spec`:
   - name: `shout`
   - type: `bool`
   - default: `false`

2. In the logic, if `shout` is true, uppercase the greeting.

3. Add `"shout": true` to `args.json` and run it:
   ```bash
   python hello.py args.json
   ```

**✅ Acceptance:**
- With `shout: true` → `"greeting": "HELLO, <NAME>!"`
- With `shout: false` (or omitted) → normal case
- Running with a bad type (e.g. `"shout": "banana"`)... try it! Ansible's
  `argument_spec` validation rejects it for you with a clear error. That's the point.

---

## Stretch — see the raw contract

Run the module with **no** args file to see what it expects:

```bash
echo '{"ANSIBLE_MODULE_ARGS": {"name": "world"}}' | python hello.py /dev/stdin
```

That `ANSIBLE_MODULE_ARGS` envelope is exactly what Ansible sends. `args.json`
already wraps your args this way — open it and see.

---

## Done?

Compare with [`../../solutions/session-1/`](../../solutions/session-1/). The
solution's `hello.py` includes the `shout` option and comments explaining each line.
