# Setup — do this before Session 1

Everything runs in a **container**, so everyone has the same Ansible, Python, and
tooling. **All you need on your laptop is Docker _or_ Podman** — no host Python,
no host Ansible. Every exercise (including Session 4's mock REST API) runs
entirely inside the container.

Budget 15–20 minutes; do it the day *before* the workshop so a slow first build
doesn't eat session time. The **build step needs internet once** (to pull the
base image + pip packages); after that everything is offline.

---

## Fastest path — `./run.sh` (Docker or Podman, auto-detected)

From the repo root:

```bash
./run.sh
```

It picks whichever runtime you have, builds the image the first time, and drops
you into a shell inside the repo at `/workshop`. That's it.

Run a one-off command without opening a shell:

```bash
./run.sh python solutions/session-1/hello.py /workshop/solutions/session-1/args.json
```

Prefer to drive things yourself? Use one of the explicit paths below.

---

## What you need

- **A container runtime — one of:**
  - **Docker** (Docker Desktop on macOS/Windows, or Docker Engine on Linux), or
  - **Podman** (`podman` CLI; on macOS/Windows it runs a small VM via `podman machine`).
- **Optional:** **VS Code** + the *Dev Containers* extension for an in-editor experience.

Verify your runtime: `docker --version` **or** `podman --version`.

---

## Option A — VS Code Dev Containers

1. Open this folder in VS Code.
2. Command Palette (`Cmd/Ctrl+Shift+P`) → **Dev Containers: Reopen in Container**.
3. Wait for the first build. A terminal opens *inside* the container.

**Using Podman with VS Code?** Point the extension at podman first:
Settings → search `dev.containers.dockerPath` → set it to `podman`
(and on macOS/Windows run `podman machine start` once beforehand).

## Option B — Docker CLI

```bash
docker build -t ansible-module-workshop .devcontainer
docker run --rm -it -v "$PWD":/workshop -w /workshop -e HOME=/tmp \
  ansible-module-workshop bash
```

## Option C — Podman CLI

```bash
# macOS/Windows only: start the VM once
podman machine init && podman machine start        # skip on Linux

podman build -t ansible-module-workshop .devcontainer

# --userns=keep-id → files you create in the repo stay owned by you (rootless)
# :Z on the mount   → SELinux relabel (Fedora/RHEL); harmless elsewhere
podman run --rm -it --userns=keep-id \
  -v "$PWD":/workshop:Z -w /workshop -e HOME=/tmp \
  ansible-module-workshop bash
```

> Tip (any CLI): add an alias so you don't retype it, e.g.
> `alias wsh='./run.sh'`

Inside the container, verify:

```bash
ansible --version
ansible-test --help >/dev/null && echo "ansible-test OK"
python -c "import pytest; print('pytest', pytest.__version__)"
```

---

## Smoke test (proves the whole toolchain works)

**Easiest — one command, from the repo root on your host:**

```bash
./run.sh --check
```

This builds the image (if needed) and runs the fast self-verification suite inside
the container: the Session 1 & 2 module smoke tests plus a `pytest` pass on the
Session 3 and 4 solutions. You should end with:

```
== Summary ==
  passed: 5   failed: 0
All checks passed — you are ready for Session 1. 🎉
```

Exit code is `0` on success, so this also works in CI.

**Deep pre-workshop check — `./run.sh --full`:** everything `--check` does, *plus*
`ansible-test sanity` on both modules, the full Session 4 collection
build → install → live mock-API round-trip, and the Session 3 `ansible-test
integration` target. Slower and needs internet once (it bootstraps the sanity
test's own venv), so it's meant for the facilitator before the workshop rather
than every attendee. Ends with `passed: 10   failed: 0`.

**Manual version** — inside the container, from the repo root:

```bash
python solutions/session-1/hello.py /workshop/solutions/session-1/args.json
```

Expected output (JSON on one line):

```json
{"changed": false, "greeting": "Hello, world!", "invocation": {"module_args": {"name": "world"}}}
```

If you see that, you're ready. 🎉

---

## A note on Session 4 (the mock API)

Session 4 needs a mock REST API running *and* Ansible calling it. Both run in the
**same** container, so `127.0.0.1` connects them — no extra container, no
published ports. Two easy ways:

```bash
# (a) background it in your one shell:
python exercises/session-4/mock_api.py &
#     ...then run your ansible / pytest commands, and later: kill %1

# (b) or open a SECOND shell into the same running container:
docker exec -it <container> bash      # or: podman exec -it <container> bash
```

The unit tests don't need the API at all — they mock `fetch_url`, so they run
offline regardless.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `need either 'podman' or 'docker'` | Install one of them and reopen your shell. |
| `Cannot connect to Podman` / hangs (macOS/Win) | `podman machine start` (the VM isn't running). `run.sh` tries this for you. |
| Permission denied writing files (Linux + rootless podman) | Use `--userns=keep-id` (already in `run.sh`/Option C). |
| `Permission denied` on the docker socket (Linux) | `sudo usermod -aG docker $USER`, then log out/in. |
| Build is slow the first time | It's the one-time base image + pip download; later runs are cached. |
| `ModuleNotFoundError: ansible` | You're on your host, not in the container. Re-check the shell prompt. |
| VS Code won't "Reopen in Container" with podman | Set `dev.containers.dockerPath` to `podman`. |

---

## Local fallback (no container at all)

Not recommended for the workshop (versions drift), but if you must:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install "ansible-core>=2.16" pytest pytest-mock
```

Everything in the exercises works the same; you just skip the container.
