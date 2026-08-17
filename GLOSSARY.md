# Glossary — concepts introduced in this workshop

A beginner-friendly reference for the terms this workshop introduces. Each entry:
a one-line definition, the **session** it first appears in, and a **file** where you
can see it used. 🚩 marks the concepts beginners most often stall on.

> Assumed *before* Session 1 (not taught here): basic playbooks (tasks, `hosts`,
> variables, running `ansible-playbook`), a terminal, and basic Python.

---

## Session 1 — module fundamentals

| Concept | One-line definition | See |
|---|---|---|
| Module | A small program that reads JSON args, does one unit of work, and prints one JSON object. | `exercises/session-1/hello.py` |
| Runs on the target 🚩 | The module's code is shipped to and executed on the *managed host*, not the controller. | `slides/session-1.md` |
| `AnsibleModule` | The base class every module creates; it parses/validates args and formats output. | `exercises/session-1/hello.py` |
| `argument_spec` | Declares your inputs and their rules: `type`, `required`, `default`, `choices`. | `solutions/session-2/config_setting.py` |
| `module.params` | The dict of validated inputs Ansible hands back to you. | `exercises/session-1/hello.py` |
| `exit_json` / `fail_json` 🚩 | The only correct way to finish a module — never `print()` or `sys.exit()`. `fail_json` needs a `msg`. | `exercises/session-1/hello.py` |
| `changed` | A module's promise about whether it actually altered the system. | `exercises/session-1/hello.py` |
| `ANSIBLE_MODULE_ARGS` envelope 🚩 | The JSON wrapper Ansible uses to pass args; how you run a module standalone. | `exercises/session-1/args.json` |
| Module vs role vs plugin | Module = a task's unit of work; role = reusable task bundle; plugin = extends Ansible itself. | `slides/session-1.md` |

## Session 2 — idempotency, check mode, docs

| Concept | One-line definition | See |
|---|---|---|
| Idempotency 🚩 | Running twice changes the system at most once; the pattern is **observe → compare → act**. | `solutions/session-2/config_setting.py` |
| Check mode 🚩 | Dry-run: predict what would change without doing it. Opt in with `supports_check_mode=True`, honor via `module.check_mode`. | `solutions/session-2/config_setting.py` |
| Diff mode | Return a `{"before":..., "after":...}` dict so `--diff` shows the change. | `solutions/session-2/config_setting.py` |
| `DOCUMENTATION` / `EXAMPLES` / `RETURN` | The three module doc blocks; `options:` must match `argument_spec`. 🚩 | `solutions/session-2/config_setting.py` |
| Module boilerplate 🚩 | Standard top-of-file ceremony: GPLv3 header, `from __future__ ...`, `__metaclass__ = type`. | `solutions/session-2/config_setting.py` |
| `author: Name (@handle)` | Author format sanity requires (bare names fail). | `solutions/session-2/config_setting.py` |
| `no_log=False` 🚩 | Tells Ansible a secret-looking arg (e.g. `key`) is *not* secret, silencing a sanity warning. | `solutions/session-2/config_setting.py` |
| `fetch_url` 🚩 | Ansible's built-in HTTP helper — use it instead of `requests` (targets may be minimal). | `solutions/session-4/.../webhook_resource.py` |
| State- vs value-based idempotency | present/absent (does a thing exist?) vs. ensure-a-value (does content equal desired?). | `webhook_resource.py` / `config_setting.py` |

## Session 3 — testing

| Concept | One-line definition | See |
|---|---|---|
| Testing pyramid | Many fast unit tests, fewer integration tests, plus cheap automatic sanity checks. | `slides/session-3.md` |
| `ansible-test` | Ansible's test runner; three modes: `sanity`, `units`, `integration`. Runs from inside a collection. 🚩 | `exercises/session-3/README.md` |
| `validate-modules` | A sanity test that checks docs match the spec, license header, author, etc. | `exercises/session-3/README.md` |
| pytest | The Python test framework used for unit tests. | `.../tests/unit/plugins/modules/test_config_setting.py` |
| Fixture 🚩 | A value/setup pytest injects into a test by name (e.g. `tmp_path`, `monkeypatch`); `autouse=True` applies it automatically. | `.../test_config_setting.py` |
| `tmp_path` | Built-in fixture giving each test a fresh temporary directory. | `.../test_config_setting.py` |
| `monkeypatch` 🚩 | Temporarily replaces code during a test and auto-restores it; patch a name **where it's used**. | `.../test_webhook_resource.py` |
| Mocking | Replacing a real dependency (e.g. `fetch_url`) with a fake so tests are offline and deterministic. | `.../test_webhook_resource.py` |
| `pytest.raises` + `AnsibleExitJson`/`AnsibleFailJson` 🚩 | The trick to *catch* a module's `exit_json`/`fail_json` result as an exception and assert on it. | `.../ansible_helpers.py` |
| `set_module_args` | Helper that stuffs fake args where `AnsibleModule` reads them. | `.../ansible_helpers.py` |
| `conftest.py` / `sys.path` 🚩 | Per-directory pytest setup; here it makes `import ansible_collections...` resolve. | `.../tests/unit/plugins/modules/conftest.py` |
| Namespace packages | Why `ansible_collections.workshop.demo...` imports work without `__init__.py`. | `conftest.py` |
| Integration target | A role's-worth of tasks that *use* your module and assert (`register`, `assert`, `is changed`). | `.../tests/integration/targets/config_setting/tasks/main.yml` |
| Testing idempotency | Run the module twice in a test; assert the second run is `changed=false`. | `.../test_config_setting.py` |
| `pytest-xdist` (`-n auto`) | Plugin `ansible-test units` uses to run tests in parallel (must be installed). | `.devcontainer/Dockerfile` |

## Session 4 — packaging & distribution

| Concept | One-line definition | See |
|---|---|---|
| Collection | A versioned, namespaced bundle of modules/roles/plugins + tests. | `solutions/session-4/ansible_collections/workshop/web/` |
| FQCN 🚩 | Fully-qualified collection name: `namespace.collection.module`. | `solutions/session-4/.../README.md` |
| Collection structure | Directory layout that must match `galaxy.yml` (`ansible_collections/<ns>/<name>/`). | `solutions/session-4/.../` |
| `galaxy.yml` | Collection metadata: namespace, name, version, deps. | `solutions/session-4/.../galaxy.yml` |
| `ansible-galaxy collection build` / `install` | Package a collection to a tarball and install it (the round-trip). | `exercises/session-4/README.md` |
| `ANSIBLE_COLLECTIONS_PATH` | Env var telling Ansible where to find installed collections. | `exercises/session-4/README.md` |

## Environment & tooling (SETUP)

| Concept | One-line definition | See |
|---|---|---|
| Container (Docker/Podman) | An isolated, reproducible environment holding the whole toolchain. | `SETUP.md` |
| Devcontainer / Dockerfile | The recipe + config that builds the workshop's container image. | `.devcontainer/Dockerfile` |
| Bind mount | Mounting your repo into the container so edits are shared live. | `run.sh` |
| Rootless podman quirks 🚩 | `--userns=keep-id`, SELinux `:Z`, UID mapping — why file ownership can behave oddly. | `run.sh` / `SETUP.md` |
| Backgrounding / `exec` | Run the mock API with `&`, or attach a second shell to the same container with `exec`. | `SETUP.md` |

## Python concepts that quietly appear

| Concept | One-line definition |
|---|---|
| `if __name__ == "__main__":` | Run this code only when the file is executed directly. |
| Context manager (`with ...`) | Auto-manages setup/cleanup (e.g. closing a file, catching an exception). |
| Decorator (`@pytest.fixture`) | Wraps a function to give it extra behavior. |
| Exceptions (`try`/`except`, `raise`) | How Python signals and handles errors. |
| Defined vs used name 🚩 | A name imported into a module is looked up *there* — the key to patching correctly. |

## Dev workflow / repo meta (optional, for contributors)

| Concept | One-line definition | See |
|---|---|---|
| git / GitHub | Version control and hosting for the repo. | — |
| CI (GitHub Actions) | Automated verification that runs on every push/PR. | `.github/workflows/ci.yml` |
| YAML | The config format used by galaxy.yml, workflows, doc blocks, and tasks. | `galaxy.yml` |
| Marp | Markdown-to-slides tool used for the decks. | `slides/` |
| `run.sh --check` / `--full` | The workshop's self-verification suite. | `run.sh`, `scripts/smoke.sh` |

---

## If you only pre-brief five things

1. **Idempotency** (observe → compare → act)
2. **Check mode** (`supports_check_mode` + the `module.check_mode` guard)
3. **The `exit_json` / `fail_json` contract**
4. **Docs must match `argument_spec`**
5. **Testing trio: fixtures + `monkeypatch` + catching the exit as an exception**
