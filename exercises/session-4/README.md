# Session 4 — Capstone Exercise

> Inside the devcontainer. Work from: `cd exercises/session-4`

Build a real module that manages a resource on a REST API — **idempotently** —
then package it in a collection and call it by its fully-qualified name.
No cloud account or internet needed: a **mock API** is included.

```
ansible_collections/workshop/web/
├── galaxy.yml
├── plugins/modules/webhook_resource.py     ← starter with TODOs
└── tests/unit/plugins/modules/
    ├── ansible_helpers.py                   (provided)
    └── test_webhook_resource.py             (starter — API mocked)
mock_api.py                                   (run this for the live demo)
```

---

## The module: `webhook_resource`

Manage a named resource on an HTTP API.

Arguments:
- `base_url` (str, required) — API root, e.g. `http://127.0.0.1:8000`
- `name` (str, required) — the resource name
- `state` (str, choices `present`/`absent`, default `present`)

Behavior (idempotent!):
- `state=present`: `GET /resources/<name>`.
  - 200 → already exists → `changed=false`
  - 404 → `POST /resources` to create → `changed=true`
- `state=absent`: `GET /resources/<name>`.
  - 404 → already gone → `changed=false`
  - 200 → `DELETE /resources/<name>` → `changed=true`
- `supports_check_mode=True`: when a change is needed but check mode is on,
  report the change **without** calling POST/DELETE.

Use Ansible's HTTP helper — **not** `requests`:
```python
from ansible.module_utils.urls import fetch_url
resp, info = fetch_url(module, url, method="GET")
status = info["status"]   # e.g. 200, 404
```

---

## Part A — finish the module

Fill in the TODOs in `plugins/modules/webhook_resource.py` (GET/compare/act for
both states, check-mode guard, doc blocks).

## Part B — try it against the live mock API

In one terminal, start the mock API:
```bash
python exercises/session-4/mock_api.py      # serves on http://127.0.0.1:8000
```

In another (inside the collection dir), install and invoke by FQCN. Export the
collections path *first* so the install and the run agree (avoids a harmless
"not part of the configured paths" warning):
```bash
cd exercises/session-4/ansible_collections/workshop/web
export ANSIBLE_COLLECTIONS_PATH=/tmp/ws-collections
ansible-galaxy collection build --force
ansible-galaxy collection install workshop-web-1.0.0.tar.gz -p /tmp/ws-collections --force

ansible localhost -m workshop.web.webhook_resource \
  -a "base_url=http://127.0.0.1:8000 name=demo state=present"     # changed=true

ansible localhost -m workshop.web.webhook_resource \
  -a "base_url=http://127.0.0.1:8000 name=demo state=present"     # changed=false (idempotent!)

ansible localhost -m workshop.web.webhook_resource \
  -a "base_url=http://127.0.0.1:8000 name=demo state=absent"      # changed=true
```

## Part C — complete the mocked unit test

Open `tests/unit/plugins/modules/test_webhook_resource.py` and finish the TODOs.
The test **patches `fetch_url`** so it never hits the network — fast and deterministic.

```bash
pytest tests/unit/plugins/modules/test_webhook_resource.py -v
```

---

## ✅ Acceptance checks

- Live: second `state=present` run reports `changed=false`; `state=absent` on an
  existing resource reports `changed=true`.
- Collection builds and installs; the module is callable as `workshop.web.webhook_resource`.
- Unit tests pass with `fetch_url` mocked (no network).
- Check mode: a `present` on a missing resource with `--check` reports `changed=true`
  but does not create it.

## Done?

Compare with [`../../solutions/session-4/`](../../solutions/session-4/) — a complete,
buildable collection you can keep as a starter template for your own modules.
