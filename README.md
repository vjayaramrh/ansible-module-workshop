# Writing Ansible Modules — A Beginner Workshop

A hands-on, four-session workshop that takes you from *Ansible user* to *Ansible
module author*. Everything runs in a container — **Docker or Podman, nothing else
on your laptop** — so there is no "works on my machine." Examples are
vendor-neutral: no cloud account, and (after the one-time image build) no internet.

> **Quick start:** `./run.sh` builds the image and drops you into a shell —
> it auto-detects Docker or Podman. Verify your setup with `./run.sh --check`
> (module smoke tests + a pytest pass), or `./run.sh --full` for a deep
> pre-workshop check (adds `ansible-test sanity` + the collection build/install
> round-trip). See [SETUP.md](SETUP.md) for details.

> **Who this is for:** People who can already write basic playbooks (tasks,
> variables, `hosts`) and now want to write their own modules in Python.
> If playbooks are new to you, do an intro-to-Ansible session first.

---

## The four sessions

| # | Title | You'll leave able to... | Slides | Exercises |
|---|-------|-------------------------|--------|-----------|
| 1 | **Foundations & your first module** | Explain what a module is (and when *not* to write one); run a minimal module standalone | [slides/session-1.md](slides/session-1.md) | [exercises/session-1](exercises/session-1) |
| 2 | **Idempotency, check mode & return values** | Write a module that is safe to re-run, supports `--check` and `--diff`, and returns clean data | [slides/session-2.md](slides/session-2.md) | [exercises/session-2](exercises/session-2) |
| 3 | **Testing with `ansible-test`** | Write sanity, unit, and integration tests and run them | [slides/session-3.md](slides/session-3.md) | [exercises/session-3](exercises/session-3) |
| 4 | **Packaging into a collection + capstone** | Ship a module inside a Galaxy collection and build a real one end-to-end | [slides/session-4.md](slides/session-4.md) | [exercises/session-4](exercises/session-4) |

Each session is ~90 minutes: ~40 min presentation, ~40 min hands-on, ~10 min
wrap-up. See [facilitator-guide.md](facilitator-guide.md) for timing and talking points.

---

## Repository layout

```
ansible-module-workshop/
├── README.md               ← you are here
├── SETUP.md                ← get your environment running (do this BEFORE session 1)
├── facilitator-guide.md    ← for the person running the workshop
├── .devcontainer/          ← Docker environment (VS Code Dev Containers or plain docker)
│   ├── devcontainer.json
│   └── Dockerfile
├── slides/                 ← Marp markdown decks (render to HTML/PDF, or read as text)
│   ├── session-1.md … session-4.md
├── exercises/              ← what attendees work through (no answers)
│   ├── session-1/ … session-4/
└── solutions/              ← reference answers (facilitator / self-check)
    ├── session-1/ … session-4/
```

---

## How to use this package

**Attendees:**
1. Read [SETUP.md](SETUP.md) and get the container running (`./run.sh`) *before* session 1.
2. Each session: skim the slides, then open that session's `exercises/` folder and follow its `README.md`.
3. Peek at `solutions/` only after you've attempted the exercise (or if you're stuck for >10 min).

**Facilitators:**
1. Read [facilitator-guide.md](facilitator-guide.md).
2. Render slides with Marp (see below) or present them straight from Markdown.
3. Distribute this whole folder (git repo or zip). Everything is self-contained.

---

## Rendering the slides

The decks are [Marp](https://marp.app/) markdown. Three ways to view them:

- **Read as-is** — they're valid Markdown; `---` separates slides.
- **VS Code** — install the "Marp for VS Code" extension, open a deck, click preview.
- **CLI → PDF/HTML/PPTX:**
  ```bash
  npx @marp-team/marp-cli slides/session-1.md -o session-1.pdf
  npx @marp-team/marp-cli slides/session-1.md -o session-1.html
  ```

---

## License

Distribute freely for your own workshops. Attribution appreciated but not required.
