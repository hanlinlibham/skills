# Playbook: Deploy Scripts

You are generating deployment scripts for a service. Follow these phases strictly.

## Phase 1: Analyze

1. Understand the service:
   ```bash
   # Find the main entry point
   find . -maxdepth 2 -name "main.*" -o -name "app.*" -o -name "server.*" | head -10

   # Check for existing deployment artifacts
   ls -la Dockerfile docker-compose.yml Makefile Procfile 2>/dev/null

   # Check package manager
   ls -la package.json requirements.txt Cargo.toml go.mod pyproject.toml 2>/dev/null
   ```

2. Identify:
   - Language/runtime (Python, Node, Go, etc.)
   - How to install dependencies
   - How to start the service
   - What port(s) it listens on
   - What environment variables it needs
   - How to check if it's healthy

3. Write findings to `plan.md`:
   ```markdown
   ## Service Analysis
   - Runtime: <language/version>
   - Entry: <main file/command>
   - Port: <port number>
   - Dependencies: <how to install>
   - Health endpoint: <URL or check method>
   ```

## Phase 2: Generate Scripts

Generate three scripts in the project root (or a `scripts/` directory if one exists).

### run.sh

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"  # adjust if scripts/ exists

# Environment defaults
export PORT="${PORT:-<default_port>}"

# Install dependencies if needed
<dependency_install_command>

# Start the service
echo "[run.sh] Starting service on port $PORT..."
<start_command>
```

**Rules for run.sh**:
- Must be idempotent (safe to run multiple times).
- Use environment variable defaults with `${VAR:-default}`.
- Print what it's doing to stderr.
- Foreground by default (no daemonization).

### healthcheck.sh

```bash
#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-<default_port>}"
URL="http://localhost:$PORT/<health_endpoint>"
MAX_RETRIES=5
RETRY_INTERVAL=2

for i in $(seq 1 $MAX_RETRIES); do
    if curl -sf "$URL" > /dev/null 2>&1; then
        echo "[healthcheck] OK (attempt $i)"
        exit 0
    fi
    echo "[healthcheck] Waiting... (attempt $i/$MAX_RETRIES)"
    sleep "$RETRY_INTERVAL"
done

echo "[healthcheck] FAILED after $MAX_RETRIES attempts"
exit 1
```

**Rules for healthcheck.sh**:
- Must exit 0 on success, non-zero on failure.
- Include retry logic with configurable attempts.
- Timeout after reasonable duration (default: 10s total).

### stop.sh

```bash
#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-<default_port>}"

# Find process on the port
PID=$(lsof -ti :"$PORT" 2>/dev/null || true)

if [ -z "$PID" ]; then
    echo "[stop.sh] No process found on port $PORT"
    exit 0
fi

echo "[stop.sh] Stopping PID $PID on port $PORT..."
kill "$PID"

# Wait for graceful shutdown
for i in $(seq 1 5); do
    if ! kill -0 "$PID" 2>/dev/null; then
        echo "[stop.sh] Process stopped"
        exit 0
    fi
    sleep 1
done

echo "[stop.sh] Force killing PID $PID..."
kill -9 "$PID" 2>/dev/null || true
echo "[stop.sh] Done"
```

**Rules for stop.sh**:
- Graceful shutdown first (SIGTERM), force kill after timeout.
- Idempotent (no error if already stopped).
- Clean up PID files if used.

## Phase 3: Verify

1. Make scripts executable:
   ```bash
   chmod +x scripts/run.sh scripts/healthcheck.sh scripts/stop.sh
   ```

2. Syntax check:
   ```bash
   bash -n scripts/run.sh
   bash -n scripts/healthcheck.sh
   bash -n scripts/stop.sh
   ```

3. If safe to test (non-production environment):
   ```bash
   # Start in background
   bash scripts/run.sh &
   sleep 3

   # Health check
   bash scripts/healthcheck.sh

   # Stop
   bash scripts/stop.sh
   ```

4. Log all results to `actions.log`.

## Phase 4: Summarize

1. Write `summary.md`:
   - What scripts were generated
   - Service configuration detected
   - Verification results

2. Write `next.md`:
   - `DONE` if all three scripts work.
   - Follow-up: production hardening, Docker, systemd unit, etc.
