---
marp: true
title: "Session 4 — Packaging into a Collection + Capstone"
paginate: true
theme: default
---

# Session 4
## Packaging into a Collection + Capstone

*Shipping something real.*

---

## Today's goals

- Understand **FQCN** and why collections exist
- Know the **collection structure** and `galaxy.yml`
- **Build & install** a collection (the round-trip)
- **Capstone:** a module that talks to a (mock) REST API — idempotent, documented, tested, packaged

---

## New concepts this session

collection · FQCN (`namespace.collection.module`) · collection structure ·
`galaxy.yml` · `ansible-galaxy collection build` / `install` ·
`ANSIBLE_COLLECTIONS_PATH`

*New to any of these? See [`GLOSSARY.md`](../GLOSSARY.md).*

---

## Why collections?

Before collections, modules were loose files in a global namespace — name clashes,
no versioning, no clear ownership.

Collections give you:
- **Namespacing:** `community.general.hostname` vs `ansible.builtin.hostname`
- **Versioning & distribution** via Ansible Galaxy / Automation Hub
- A home for modules **+** roles **+** plugins **+** docs **+** tests together

---

## FQCN — fully-qualified collection name

```
namespace . collection . module
   │           │            │
community  .  general  .  hostname
```

In a playbook:

```yaml
- name: use it by full name
  community.general.hostname:
    name: web01
```

`ansible.builtin.*` is just the collection that ships with `ansible-core`.

---

## Collection structure

```
ansible_collections/<namespace>/<name>/
├── galaxy.yml               # metadata: namespace, name, version, deps
├── plugins/
│   └── modules/
│       └── webhook_resource.py
├── roles/                   # optional
├── tests/
│   ├── unit/…
│   └── integration/…
└── README.md
```

The path **must** match `namespace`/`name` in `galaxy.yml`.

---

## `galaxy.yml`

```yaml
namespace: workshop
name: demo
version: 1.0.0
readme: README.md
authors:
  - Your Name <you@example.com>
description: Workshop demo collection
license:
  - GPL-3.0-or-later
```

`namespace` + `name` → the first two parts of every FQCN in this collection.

---

## Build & install: the round-trip

```bash
# From inside the collection directory:
ansible-galaxy collection build            # → workshop-demo-1.0.0.tar.gz

# Install it (into your configured collections path):
ansible-galaxy collection install workshop-demo-1.0.0.tar.gz -p ./collections

# Use it:
ANSIBLE_COLLECTIONS_PATH=./collections \
  ansible localhost -m workshop.demo.webhook_resource -a "name=demo state=present"
```

**Rebuild after every change** before re-installing.

---

## Distribution options

- **Ansible Galaxy** — public, `ansible-galaxy collection publish`
- **Automation Hub** — Red Hat, curated/certified
- **Private:** a git repo (`ansible-galaxy collection install git+https://…`)
  or an internal Galaxy/Artifactory

For a team, a git URL is often the simplest start.

---

## Capstone: `webhook_resource`

Manage a resource on a REST API idempotently.

- `state: present` → create if missing (GET then POST)
- `state: absent`  → delete if present (GET then DELETE)
- Idempotent, `supports_check_mode=True`
- Uses Ansible's own HTTP helper: `ansible.module_utils.urls.fetch_url`
- Full doc blocks + one unit test (API mocked — no network!)

We provide a **mock API** so nobody needs an account or internet.

---

## Why mock the API in tests?

- Tests must be **fast**, **deterministic**, **offline**
- You're testing *your logic*, not the remote service
- Pattern: patch `fetch_url` to return canned responses, assert your module
  made the right calls and reported the right `changed`

Session 3's unit-test helpers carry straight over.

---

## Exercise time 🧑‍💻

Open **`exercises/session-4/README.md`**.

1. Complete `webhook_resource` (create/delete + idempotency + check mode).
2. Wire up `galaxy.yml`; **build & install** the collection.
3. Invoke it by **FQCN** against the mock API.
4. Complete the mocked **unit test**.

The solution is a full, working collection you can keep as a template.

---

## Where to go next

- **Contribute** a fix to a `community.*` collection — best way to learn the real workflow
- Explore **plugins** (lookup, filter, connection) — modules are just the start
- Read the **Ansible dev_guide** end to end now that it'll make sense
- Add **CI** (GitHub Actions) running `ansible-test` on every PR
- **Share code across modules** — when you write your 2nd/3rd API module, factor
  auth, URL-building, and the HTTP call into `plugins/module_utils/` instead of
  copy-pasting
- **Real auth** — a `no_log` token param that also reads an env var via
  `env_fallback`, and *fail fast* with a clear `msg` instead of sending
  `Authorization: Bearer None`

---

## Series recap 🎓

1. A module = JSON in → work → JSON out; `AnsibleModule` + `exit_json`/`fail_json`
2. **Idempotency**: observe → compare → act; check mode; diff; docs
3. **Testing**: sanity → unit → integration; test idempotency
4. **Packaging**: collections, FQCN, build/install; a real capstone

**You are now an Ansible module author.** Go build something.
