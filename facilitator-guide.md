# Facilitator Guide

How to run the workshop, session by session — timing, talking points, the
mistakes beginners reliably make, and how to unstick people fast.

---

## Before the first session

- Send [SETUP.md](SETUP.md) at least 24h ahead. **Insist** people run the smoke
  test before arriving — environment issues will otherwise eat your first session.
- Have the [solutions/](solutions/) handy but don't share the folder until each
  session's exercise is done (or share the whole repo and rely on the honor system —
  beginners generally *want* to try first).
- Decide on cadence: weekly is ideal (homework sticks); a compressed 2-day format
  works if you keep breaks generous.

## General facilitation tips

- **Live-code the first example each session** rather than just showing slides.
  Type it wrong once on purpose (e.g. forget `argument_spec`) and show the error.
- **Pair people up.** Debugging someone else's module teaches the mental model fast.
- **The #1 time sink is environment drift.** The devcontainer exists to kill this;
  gently enforce "are you inside the container?" as the first debugging question.
- Keep a "parking lot" for advanced questions (plugins, async, connection modules)
  so you don't rabbit-hole. Point them at the dev_guide.

---

## Session 1 — Foundations & your first module (~90 min)

| Time | Segment |
|------|---------|
| 0:00–0:10 | Welcome, agenda, "who's written a playbook?" show of hands |
| 0:10–0:40 | Slides: what a module is, module vs role vs plugin, when NOT to write one, anatomy of `AnsibleModule` |
| 0:40–1:20 | Exercise 1 (hello module) + Exercise 2 (add `argument_spec`) |
| 1:20–1:30 | Wrap-up: recap `exit_json`/`fail_json`, preview idempotency |

**Talking points:**
- Hammer "a module is just a program that reads JSON args and prints JSON." Demystify it.
- The "should you even write one?" slide matters — beginners over-reach. A role or
  `command` with `creates:` often wins.
- Explain *why* modules run on the target host, not the controller.

**Common pitfalls:**
- Running the module inside the container vs on host (import errors).
- Forgetting the args JSON must be `{"ANSIBLE_MODULE_ARGS": {...}}` when run standalone
  — the exercises use a helper wrapper to hide this at first, then reveal it.
- Printing anything other than the final JSON to stdout (breaks the contract).

---

## Session 2 — Idempotency, check mode & return values (~90 min)

| Time | Segment |
|------|---------|
| 0:00–0:10 | Recap S1, homework review |
| 0:10–0:45 | Slides: idempotency & `changed`, check mode, `diff`, return values, `DOCUMENTATION`/`EXAMPLES`/`RETURN`, error handling |
| 0:45–1:20 | Exercise: `config_setting` module (idempotent key=value in a file, check mode + diff) |
| 1:20–1:30 | Wrap-up |

**Talking points:**
- Idempotency is *the* concept. "Report changed only when you actually changed something."
- Check mode = "predict, don't do." Walk the code path where `module.check_mode` is true.
- Show a bad module that always returns `changed=true` and why that's harmful
  (breaks handlers, `--check`, and trust).

**Common pitfalls:**
- Setting `changed=true` unconditionally.
- Doing the write *before* checking whether it's needed.
- Forgetting to guard the actual write behind `if not module.check_mode`.

---

## Session 3 — Testing with `ansible-test` (~90 min)

| Time | Segment |
|------|---------|
| 0:00–0:10 | Recap, homework review |
| 0:10–0:45 | Slides: the testing pyramid for modules, sanity vs unit vs integration, the collection layout `ansible-test` expects |
| 0:45–1:20 | Exercise: unit-test the S2 module; run sanity; (stretch) an integration target |
| 1:20–1:30 | Wrap-up |

**Talking points:**
- `ansible-test` must run from *inside a collection directory*. This trips everyone.
  The exercise provides the collection skeleton so they don't fight layout first.
- Unit tests use a pattern to feed args and capture the `exit_json`/`fail_json` result —
  walk through the provided helper.
- Sanity tests catch doc/spec mismatches — great for beginners because the errors are concrete.

**Common pitfalls:**
- Running `ansible-test` from the wrong directory.
- `DOCUMENTATION` options not matching `argument_spec` (sanity fails — this is a *feature*).

---

## Session 4 — Packaging into a collection + capstone (~90 min)

| Time | Segment |
|------|---------|
| 0:00–0:10 | Recap |
| 0:10–0:40 | Slides: FQCN, collection structure, `galaxy.yml`, build & install, distribution |
| 0:40–1:20 | Capstone: `webhook_resource` module against a mock REST API, packaged + one unit test |
| 1:20–1:30 | Wrap-up, where to go next, contributing to community collections |

**Talking points:**
- Fully-qualified collection names (`namespace.collection.module`) and why they exist.
- `ansible-galaxy collection build` / `install` round-trip.
- Encourage contributing a fix to a community collection as the natural next step.

**Common pitfalls:**
- `namespace`/`name` in `galaxy.yml` not matching the directory path.
- Forgetting to `build` after changes before `install`.

---

## Answer-key policy

`solutions/` mirrors `exercises/` one-to-one. Each solution file has comments
explaining *why*, not just *what*. Encourage attendees to diff their work against it.

## Feedback loop

End each session with one keep / one change on sticky notes (or a shared doc).
The exercises are intentionally modular — cut the stretch goals if you're short on time.
