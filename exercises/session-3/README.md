# Session 3 — Exercises

> Inside the devcontainer. Work from: `cd exercises/session-3`

Now we test the `config_setting` module from Session 2. A ready-made **collection
skeleton** is provided so you don't fight layout — `ansible-test` only works from
inside a collection.

```
ansible_collections/workshop/demo/
├── galaxy.yml
├── plugins/modules/          ← put your module here (step 1)
└── tests/
    ├── unit/plugins/modules/
    │   ├── ansible_helpers.py         (provided — args + exit/fail capture)
    │   └── test_config_setting.py     (starter with TODOs)
    └── integration/targets/config_setting/tasks/main.yml   (starter)
```

---

## Step 0 — go to the collection

```bash
cd exercises/session-3/ansible_collections/workshop/demo
```

Everything below runs from here.

## Step 1 — drop in your module

Copy your working Session 2 module into place (or use the solution):

```bash
cp ../../../../session-2/config_setting.py plugins/modules/config_setting.py
# stuck? use the reference:
# cp ../../../../../solutions/session-2/config_setting.py plugins/modules/config_setting.py
```

## Step 2 — run sanity tests

```bash
ansible-test sanity --test validate-modules plugins/modules/config_setting.py
```

Fix anything it reports. **This is the tests doing their job.** The findings you're
most likely to see, and their fixes:

| Sanity finding | What it means | Fix |
|----------------|---------------|-----|
| `DOCUMENTATION.xxx` doesn't match spec | Your `options:` don't match `argument_spec` | Make them line up exactly |
| `missing-gplv3-license` | No GPL header in the first 20 lines | Keep the `# GNU General Public License v3.0+...` header from the starter |
| `invalid-documentation ... author` | `author` must be `Name (@handle)` | e.g. `- Workshop Team (@workshop)` |
| `no-log-needed: Argument 'key'...` | An arg *named* like a secret isn't marked | Add `no_log=False` to `key` in `argument_spec` (it's not actually secret) |

That last one is a great lesson: Ansible assumes anything named `key`/`password`/
`token` might be a secret and nags until you *explicitly* say otherwise.

## Step 3 — complete and run the unit tests

Open `tests/unit/plugins/modules/test_config_setting.py` and finish the TODOs.
The star of the show is the **idempotency test**: run the module twice with the
same args and assert the second run is `changed=false`.

```bash
# Fast inner loop while iterating:
pytest tests/unit/plugins/modules/test_config_setting.py -v

# The "official" run via ansible-test:
ansible-test units --python 3.12 tests/unit/plugins/modules/test_config_setting.py
```

## Step 4 (stretch) — integration target

Flesh out `tests/integration/targets/config_setting/tasks/main.yml` so it uses
the module twice and asserts idempotency end-to-end, then:

```bash
ansible-test integration config_setting
```

---

## ✅ Acceptance checks

- `ansible-test sanity --test validate-modules ...` passes.
- `pytest` shows the idempotency test passing (first run changed, second not).
- (Stretch) the integration target passes.

## Done?

Compare with [`../../solutions/session-3/`](../../solutions/session-3/) — a complete,
passing test suite.
