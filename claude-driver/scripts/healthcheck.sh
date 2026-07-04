#!/usr/bin/env bash
# Claude Driver healthcheck: verify claude CLI is available and authenticated.
set -euo pipefail

PASS=0
FAIL=0

check() {
    local label="$1"
    shift
    if "$@" > /dev/null 2>&1; then
        echo "[PASS] $label"
        PASS=$((PASS + 1))
    else
        echo "[FAIL] $label"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== Claude Driver Healthcheck ==="
echo ""

# 1. claude CLI on PATH
check "claude CLI found on PATH" command -v claude

# 2. Version check
if command -v claude > /dev/null 2>&1; then
    VERSION=$(claude --version 2>/dev/null || echo "unknown")
    echo "       Version: $VERSION"
fi

# 3. Authentication test (echo a simple prompt and check exit code)
echo -n "[....] Authentication (echo test)..."
if echo "Reply with exactly: OK" | claude -p --output-format text > /dev/null 2>&1; then
    echo -e "\r[PASS] Authentication (echo test)"
    PASS=$((PASS + 1))
else
    echo -e "\r[FAIL] Authentication (echo test)"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
