#!/usr/bin/env bash
# Self-verification, run INSIDE the container (via `./run.sh --check` / `--full`).
# Exercises the reference solutions end to end.
#   (no args)  smoke: module runs (S1, S2) + pytest (S3, S4)   — fast, offline
#   --full     also: ansible-test sanity (S3, S4) + galaxy build/install +
#                    live mock-API round-trip  — slower, needs internet once
# Exits non-zero if anything fails, so it's CI-friendly too.
set -uo pipefail

cd /workshop 2>/dev/null || cd "$(dirname "${BASH_SOURCE[0]}")/.."

FULL=0
[ "${1:-}" = "--full" ] && FULL=1

pass=0
fail=0
ok()   { printf '  \033[32m✅ %s\033[0m\n' "$1"; pass=$((pass + 1)); }
no()   { printf '  \033[31m❌ %s\033[0m\n' "$1"; fail=$((fail + 1)); }
head() { printf '\n\033[1m== %s ==\033[0m\n' "$1"; }

# ============================================================================
# Fast checks (always run)
# ============================================================================

# --- Session 1: hello module ------------------------------------------------
head "Session 1 — hello module"
out=$(python solutions/session-1/hello.py solutions/session-1/args.json 2>&1) || true
if grep -q '"greeting": "Hello, world!"' <<<"$out"; then
    ok "hello module greets correctly"
else
    no "hello module output unexpected"; echo "     $out"
fi

# --- Session 2: config_setting idempotency ----------------------------------
head "Session 2 — config_setting idempotency"
conf=$(mktemp -u /tmp/smoke_app.XXXX.conf)
args=$(mktemp /tmp/smoke_args.XXXX.json)
cat >"$args" <<JSON
{"ANSIBLE_MODULE_ARGS": {"path": "$conf", "key": "debug", "value": "true"}}
JSON

r1=$(python solutions/session-2/config_setting.py "$args" 2>&1) || true
r2=$(python solutions/session-2/config_setting.py "$args" 2>&1) || true
grep -q '"changed": true'  <<<"$r1" && ok "first run reports changed"          || { no "first run not changed"; echo "     $r1"; }
grep -q '"changed": false' <<<"$r2" && ok "second run is a no-op (idempotent)" || { no "second run not idempotent"; echo "     $r2"; }
rm -f "$conf" "$args"

# --- Session 3: unit tests --------------------------------------------------
head "Session 3 — pytest (config_setting)"
if ( cd solutions/session-3/ansible_collections/workshop/demo \
        && python -m pytest tests/unit/plugins/modules/test_config_setting.py -q ); then
    ok "session 3 unit tests pass"
else
    no "session 3 unit tests failed"
fi

# --- Session 4: unit tests (fetch_url mocked, no network) -------------------
head "Session 4 — pytest (webhook_resource)"
if ( cd solutions/session-4/ansible_collections/workshop/web \
        && python -m pytest tests/unit/plugins/modules/test_webhook_resource.py -q ); then
    ok "session 4 unit tests pass"
else
    no "session 4 unit tests failed"
fi

# ============================================================================
# Full checks (--full only): sanity + galaxy round-trip
# ============================================================================
if [ "$FULL" -eq 1 ]; then
    printf '\n\033[1m### FULL mode: sanity + galaxy round-trip (needs internet, slower) ###\033[0m\n'

    # --- Sanity: both modules ------------------------------------------------
    head "Session 3 — ansible-test sanity (config_setting)"
    if ( cd solutions/session-3/ansible_collections/workshop/demo \
            && ansible-test sanity --test validate-modules \
                 plugins/modules/config_setting.py >/tmp/s3_sanity.log 2>&1 ); then
        ok "config_setting passes validate-modules"
    else
        no "config_setting sanity failed"; tail -n 15 /tmp/s3_sanity.log | sed 's/^/     /'
    fi

    head "Session 4 — ansible-test sanity (webhook_resource)"
    if ( cd solutions/session-4/ansible_collections/workshop/web \
            && ansible-test sanity --test validate-modules \
                 plugins/modules/webhook_resource.py >/tmp/s4_sanity.log 2>&1 ); then
        ok "webhook_resource passes validate-modules"
    else
        no "webhook_resource sanity failed"; tail -n 15 /tmp/s4_sanity.log | sed 's/^/     /'
    fi

    # --- Collection build + install -----------------------------------------
    head "Session 4 — collection build + install"
    if (
        set -e
        cd solutions/session-4/ansible_collections/workshop/web
        export ANSIBLE_COLLECTIONS_PATH=/tmp/ws-check
        ansible-galaxy collection build --force >/tmp/galaxy.log 2>&1
        ansible-galaxy collection install workshop-web-1.0.0.tar.gz \
            -p /tmp/ws-check --force >>/tmp/galaxy.log 2>&1
        rm -f workshop-web-1.0.0.tar.gz
    ); then
        ok "collection builds and installs (workshop.web)"
    else
        no "collection build/install failed"; tail -n 15 /tmp/galaxy.log | sed 's/^/     /'
    fi

    # --- Live round-trip against the mock API --------------------------------
    head "Session 4 — live mock-API round-trip (by FQCN)"
    python exercises/session-4/mock_api.py >/tmp/mockapi.log 2>&1 &
    api_pid=$!
    sleep 1
    export ANSIBLE_COLLECTIONS_PATH=/tmp/ws-check
    inv=(-m workshop.web.webhook_resource)
    a1=$(ansible localhost "${inv[@]}" -a "base_url=http://127.0.0.1:8000 name=chk state=present" 2>/dev/null) || true
    a2=$(ansible localhost "${inv[@]}" -a "base_url=http://127.0.0.1:8000 name=chk state=present" 2>/dev/null) || true
    a3=$(ansible localhost "${inv[@]}" -a "base_url=http://127.0.0.1:8000 name=chk state=absent"  2>/dev/null) || true
    kill "$api_pid" 2>/dev/null || true
    if grep -q '"changed": true'  <<<"$a1" \
       && grep -q '"changed": false' <<<"$a2" \
       && grep -q '"changed": true'  <<<"$a3"; then
        ok "present→changed, present→unchanged, absent→changed"
    else
        no "round-trip result unexpected"
        printf '     present #1: %s\n' "$(grep -o '"changed": [a-z]*' <<<"$a1" | head -1)"
        printf '     present #2: %s\n' "$(grep -o '"changed": [a-z]*' <<<"$a2" | head -1)"
        printf '     absent:     %s\n' "$(grep -o '"changed": [a-z]*' <<<"$a3" | head -1)"
    fi
    rm -rf /tmp/ws-check
fi

# ============================================================================
# Summary
# ============================================================================
printf '\n\033[1m== Summary ==\033[0m\n'
printf '  passed: %s   failed: %s\n' "$pass" "$fail"
if [ "$fail" -eq 0 ]; then
    printf '\033[32mAll checks passed — you are ready for Session 1. 🎉\033[0m\n'
    exit 0
else
    printf '\033[31mSome checks failed (see above).\033[0m\n'
    exit 1
fi
