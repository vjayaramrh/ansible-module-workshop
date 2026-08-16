---
marp: true
title: "Session 3 — Testing with ansible-test"
paginate: true
theme: default
---

# Session 3
## Testing with `ansible-test`

*Proving your module works — and keeps working.*

---

## Today's goals

- Understand the **testing pyramid** for modules
- Run **sanity** tests (docs/spec/style)
- Write and run **unit** tests (fast, Python-level)
- See an **integration** test (real playbook against the module)
- Learn the **collection layout** `ansible-test` requires

---

## The testing pyramid for modules

```
        /  integration  \     few, slow, high-confidence
       /------------------\    (run the module in a real play)
      /       unit         \   many, fast
     /----------------------\  (call run_module with fake args)
    /        sanity          \ automatic, cheap
   /--------------------------\ (docs match spec, imports, style)
```

Start at the bottom. Sanity is nearly free and catches real bugs.

---

## `ansible-test` runs *inside a collection*

This trips up everyone once. `ansible-test` expects this layout:

```
<collections_root>/ansible_collections/<namespace>/<name>/
├── plugins/modules/config_setting.py
└── tests/
    ├── unit/plugins/modules/test_config_setting.py
    └── integration/targets/config_setting/tasks/main.yml
```

You run `ansible-test` **from the collection directory**. The exercise gives you
this skeleton so you don't fight layout first.

---

## Sanity tests

```bash
ansible-test sanity --test validate-modules plugins/modules/config_setting.py
```

Catches, among other things:
- `DOCUMENTATION` options that don't match `argument_spec`
- Missing `RETURN` docs
- Python that won't import / bad shebang

*This is why we wrote the doc blocks in Session 2 — now they're enforced.*

---

## Unit tests: the idea

Call the module's `main()` with fake args, capture how it exits.

Two helper patterns (provided for you):
- `set_module_args({...})` — stuff args where `AnsibleModule` reads them
- Catch `exit_json` / `fail_json` via exceptions so the test can assert on the result

```python
def test_greets_by_name():
    set_module_args({"name": "ada"})
    with pytest.raises(AnsibleExitJson) as exc:
        hello.main()
    assert exc.value.result["greeting"] == "Hello, ada!"
```

---

## Unit tests: idempotency is testable!

The best part — you can *prove* idempotency in a unit test:

```python
def test_second_run_reports_unchanged(tmp_path):
    conf = tmp_path / "app.conf"
    args = {"path": str(conf), "key": "debug", "value": "true"}

    set_module_args(args)
    with pytest.raises(AnsibleExitJson) as first:
        config_setting.main()
    assert first.value.result["changed"] is True

    set_module_args(args)                      # run again, same args
    with pytest.raises(AnsibleExitJson) as second:
        config_setting.main()
    assert second.value.result["changed"] is False   # ← idempotent!
```

---

## Running unit tests

Two ways:

```bash
# Via ansible-test (uses its managed environment)
ansible-test units --python 3.12 tests/unit/plugins/modules/test_config_setting.py

# Or plain pytest during development (fast inner loop)
pytest tests/unit/plugins/modules/test_config_setting.py -v
```

Use `pytest` while iterating; `ansible-test units` for the "official" run.

---

## Integration tests (a peek)

An integration **target** is just a role's worth of tasks that *use* your module
and assert on the result:

```yaml
# tests/integration/targets/config_setting/tasks/main.yml
- name: set a value
  config_setting: { path: /tmp/app.conf, key: debug, value: "true" }
  register: first

- name: run again
  config_setting: { path: /tmp/app.conf, key: debug, value: "true" }
  register: second

- assert:
    that:
      - first is changed
      - second is not changed        # idempotency, end to end
```

Run: `ansible-test integration config_setting`

---

## Exercise time 🧑‍💻

Open **`exercises/session-3/README.md`**.

Using the provided collection skeleton (with your Session 2 module dropped in):
1. Run **sanity** — fix anything it flags.
2. Complete the **unit tests**, including the idempotency test.
3. **Stretch:** flesh out the **integration** target.

---

## Recap

- Sanity → unit → integration; start at the bottom
- `ansible-test` runs from inside the collection dir
- Unit tests feed fake args and catch `exit_json`/`fail_json`
- You can *unit-test idempotency* — do it
- Integration = your module in a real play, asserting behavior

**Next time:** packaging it into a real collection and a full capstone.
