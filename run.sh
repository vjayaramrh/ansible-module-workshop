#!/usr/bin/env bash
# One command to get a workshop shell, whether you have Docker or Podman.
#   ./run.sh            → build (first time) + drop into a shell in the repo
#   ./run.sh --check    → build + fast self-verification (module runs + pytest), exit
#   ./run.sh --full     → --check PLUS ansible-test sanity + galaxy round-trip
#                         (slower, needs internet once), then exit
#   ./run.sh <cmd...>   → run a one-off command in the container instead of a shell
#
# Everything the exercises need is inside the image; nothing else touches your host.
set -euo pipefail

IMAGE="ansible-module-workshop"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- flags --------------------------------------------------------------------
MODE="shell"
case "${1:-}" in
    --check|-c) MODE="check"; shift ;;
    --full|-f)  MODE="full";  shift ;;
esac

# --- pick a runtime -----------------------------------------------------------
if command -v podman >/dev/null 2>&1; then
    RUNTIME="podman"
elif command -v docker >/dev/null 2>&1; then
    RUNTIME="docker"
else
    echo "Need either 'podman' or 'docker' installed and on PATH." >&2
    exit 1
fi
echo ">> Using $RUNTIME"

# On macOS/Windows, Podman needs its VM running.
if [ "$RUNTIME" = "podman" ]; then
    if ! podman info >/dev/null 2>&1; then
        echo ">> Starting podman machine (first run may take a minute)..."
        podman machine init 2>/dev/null || true
        podman machine start 2>/dev/null || true
    fi
fi

# --- build once (cached afterwards) -------------------------------------------
echo ">> Building image (cached after first run)..."
"$RUNTIME" build -t "$IMAGE" "$DIR/.devcontainer"

# --- run ----------------------------------------------------------------------
# HOME=/tmp keeps ansible/pytest caches writable regardless of how the runtime
# maps user IDs, so the bind mount never fights us.
case "$MODE" in
    check)
        COMMON=(--rm -w /workshop -e HOME=/tmp)
        CMD=(bash scripts/smoke.sh)
        echo ">> Running self-verification (scripts/smoke.sh)..." ;;
    full)
        COMMON=(--rm -w /workshop -e HOME=/tmp)
        CMD=(bash scripts/smoke.sh --full)
        echo ">> Running FULL verification (smoke + sanity + galaxy round-trip)..." ;;
    *)
        COMMON=(--rm -it -w /workshop -e HOME=/tmp)
        CMD=("${@:-bash}") ;;
esac

if [ "$RUNTIME" = "podman" ]; then
    # keep-id: your host user owns files created in the mount (rootless podman).
    # :Z relabels the mount for SELinux (Fedora/RHEL); harmless elsewhere.
    set -- podman run "${COMMON[@]}" \
        --userns=keep-id \
        -v "$DIR":/workshop:Z \
        "$IMAGE" "${CMD[@]}"
else
    set -- docker run "${COMMON[@]}" \
        -v "$DIR":/workshop \
        "$IMAGE" "${CMD[@]}"
fi

echo ">> ${*}"
exec "$@"
