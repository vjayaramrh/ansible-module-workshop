# CLAUDE.md

Guidance for Claude Code (and contributors) when working in this repository.

## What this repo is

A hands-on, four-session beginner **workshop for writing Ansible modules**. It is
teaching material, not a production collection. Contents:

- `slides/` — Marp markdown decks (sessions 1–4)
- `exercises/` — starter files with TODOs + step-by-step READMEs (what attendees do)
- `solutions/` — complete, working reference answers (must always pass verification)
- `.devcontainer/` — Docker/Podman image with `ansible-core`, `pytest`, `ansible-test`
- `run.sh` — runtime-agnostic launcher + self-verification (`--check`, `--full`)
- `scripts/smoke.sh` — the verification suite run inside the container

## Golden rule: keep the reference solutions green

Any change touching `solutions/`, `scripts/`, `run.sh`, or the devcontainer MUST
still pass:

```bash
./run.sh --check     # fast: module runs + pytest (offline)
./run.sh --full      # deep: also ansible-test sanity + collection build/install + live round-trip
```

CI (`.github/workflows/ci.yml`) runs `--full` natively and a devcontainer smoke on
every push/PR. Don't merge red.

## Module authoring conventions (these prevent real sanity failures)

Every module under `plugins/modules/` MUST:

1. **Start with the standard header** (GPLv3 line required in the first 20 lines):
   ```python
   #!/usr/bin/python
   # -*- coding: utf-8 -*-

   # Copyright: (c) 2024, Workshop Team
   # GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
   from __future__ import absolute_import, division, print_function
   __metaclass__ = type
   ```
2. **Carry all three doc blocks** — `DOCUMENTATION`, `EXAMPLES`, `RETURN` — and the
   `options:` in `DOCUMENTATION` must match `argument_spec` **exactly**.
3. **Use a valid author** format: `author:\n  - Name (@githubhandle)` (bare names fail sanity).
4. **Mark non-secret args that *look* secret** with `no_log=False` — any arg named
   like `key`/`password`/`token`/`secret` is flagged by sanity unless you say so.
5. **Be idempotent**: observe → compare → act. Return `changed=True` only when the
   system actually changed.
6. **Support check mode**: `supports_check_mode=True`, and guard all writes behind
   `if not module.check_mode` (or exit early in check mode once you know a change is needed).
7. **Finish only via** `module.exit_json(...)` / `module.fail_json(msg=...)` — never
   `print()` or `sys.exit()`. `fail_json` always needs an actionable `msg`.
8. **For HTTP, use** `ansible.module_utils.urls.fetch_url` — never `requests`
   (targets may not have it).

## Collection & test layout

Modules live in a collection tree so `ansible-test` works:

```
ansible_collections/<namespace>/<name>/
├── galaxy.yml                              # namespace/name MUST match the path
├── plugins/modules/<module>.py
└── tests/unit/plugins/modules/
    ├── ansible_helpers.py                  # set_module_args + exit/fail capture
    ├── conftest.py                         # sys.path setup (walks up to ansible_collections/)
    └── test_<module>.py
```

- Unit tests feed args via `set_module_args({...})` and catch `AnsibleExitJson` /
  `AnsibleFailJson` to assert on the result. **Always include an idempotency test**
  (run twice, assert second run is `changed=False`).
- Mock network calls (patch `fetch_url`) — unit tests must be offline and deterministic.
- The `conftest.py` finds the collections root by walking up to the
  `ansible_collections` directory (don't hardcode `../` counts — that broke once).

## Scaffolding a new module

Prefer the **`/new-ansible-module`** skill — it emits a convention-correct module,
doc blocks, unit test, and conftest in one step. See `.claude/skills/new-ansible-module/`.

## Environment notes

- Everything runs in the container; nothing else is needed on the host but Docker
  or Podman. `run.sh` auto-detects the runtime (podman gets `--userns=keep-id` + `:Z`).
- `HOME=/tmp` is set in `run.sh` so caches stay writable regardless of UID mapping.
- `--full` needs internet once (it bootstraps `ansible-test`'s sanity venv).

## Style

- Match the existing code's comment density and idiom. Modules favor clear,
  beginner-readable Python over cleverness — this is teaching material.
- Slides are Marp; `---` separates slides. Keep them terse and example-driven.
