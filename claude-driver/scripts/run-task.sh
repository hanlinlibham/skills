#!/usr/bin/env bash
# Claude Driver: assemble prompt and run inner Claude Code on a task.
set -euo pipefail

# ---------- defaults ----------
WORKDIR=""
PLAYBOOK="bugfix"
TASK=""
TASK_FILE=""
MAX_BUDGET="1.00"
MODEL=""
ALLOWED_TOOLS=""
EXTRA_ARGS=""

# ---------- resolve skill dir ----------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
REF_DIR="$SKILL_DIR/references"

# ---------- usage ----------
usage() {
    cat <<'EOF'
Usage: run-task.sh --workdir DIR [OPTIONS]

Required:
  --workdir DIR          Target project directory for inner Claude

Task (one required):
  --task TEXT            Task description as inline string
  --task-file PATH       Path to file containing task description

Options:
  --playbook NAME        Playbook: bugfix (default), mvp, deploy
  --max-budget USD       Max spend per run (default: 1.00)
  --model MODEL          Model override for inner Claude
  --allowed-tools LIST   Comma-separated tool allowlist
  -h, --help             Show this help
EOF
    exit 1
}

# ---------- parse args ----------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --workdir)      WORKDIR="$2";        shift 2 ;;
        --playbook)     PLAYBOOK="$2";       shift 2 ;;
        --task)         TASK="$2";           shift 2 ;;
        --task-file)    TASK_FILE="$2";      shift 2 ;;
        --max-budget)   MAX_BUDGET="$2";     shift 2 ;;
        --model)        MODEL="$2";          shift 2 ;;
        --allowed-tools) ALLOWED_TOOLS="$2"; shift 2 ;;
        -h|--help)      usage ;;
        *)
            echo "Error: unknown option: $1" >&2
            usage
            ;;
    esac
done

# ---------- validate ----------
if [ -z "$WORKDIR" ]; then
    echo "Error: --workdir is required" >&2
    usage
fi

if [ ! -d "$WORKDIR" ]; then
    echo "Error: workdir does not exist: $WORKDIR" >&2
    exit 1
fi

if [ -z "$TASK" ] && [ -z "$TASK_FILE" ]; then
    echo "Error: --task or --task-file is required" >&2
    usage
fi

PLAYBOOK_FILE="$REF_DIR/playbook-${PLAYBOOK}.md"
if [ ! -f "$PLAYBOOK_FILE" ]; then
    echo "Error: unknown playbook: $PLAYBOOK (file not found: $PLAYBOOK_FILE)" >&2
    exit 1
fi

CONSTITUTION_FILE="$REF_DIR/constitution.md"
if [ ! -f "$CONSTITUTION_FILE" ]; then
    echo "Error: constitution.md not found at $CONSTITUTION_FILE" >&2
    exit 1
fi

# ---------- resolve task text ----------
if [ -n "$TASK_FILE" ]; then
    if [ ! -f "$TASK_FILE" ]; then
        echo "Error: task file not found: $TASK_FILE" >&2
        exit 1
    fi
    TASK=$(cat "$TASK_FILE")
fi

# ---------- create run directory ----------
RUN_ID=$(date +"%Y%m%d-%H%M%S")
RUN_DIR="$WORKDIR/.agent/runs/$RUN_ID"
mkdir -p "$RUN_DIR"

echo ">>> Claude Driver"
echo "    Run ID:   $RUN_ID"
echo "    Workdir:  $WORKDIR"
echo "    Playbook: $PLAYBOOK"
echo "    Budget:   \$$MAX_BUDGET"
echo "    Run dir:  $RUN_DIR"
echo ""

# ---------- build claude args ----------
CLAUDE_ARGS="-p --workdir $WORKDIR"

if [ -n "$MAX_BUDGET" ]; then
    CLAUDE_ARGS="$CLAUDE_ARGS --max-budget-usd $MAX_BUDGET"
fi

if [ -n "$MODEL" ]; then
    CLAUDE_ARGS="$CLAUDE_ARGS --model $MODEL"
fi

if [ -n "$ALLOWED_TOOLS" ]; then
    CLAUDE_ARGS="$CLAUDE_ARGS --allowedTools $ALLOWED_TOOLS"
fi

# ---------- assemble prompt and run ----------
{
    cat "$CONSTITUTION_FILE"
    echo ""
    echo "---"
    echo ""
    cat "$PLAYBOOK_FILE"
    echo ""
    echo "---"
    echo ""
    echo "## Run Metadata"
    echo "- Run ID: $RUN_ID"
    echo "- Working directory: $WORKDIR"
    echo "- Artifact directory: .agent/runs/$RUN_ID/"
    echo "- Write all artifact files (plan.md, actions.log, summary.md, next.md) to: .agent/runs/$RUN_ID/"
    echo ""
    echo "---"
    echo ""
    echo "## Task"
    echo ""
    echo "$TASK"
} | claude $CLAUDE_ARGS

echo ""
echo ">>> Run complete: $RUN_ID"

# ---------- show results if available ----------
if [ -f "$RUN_DIR/summary.md" ]; then
    echo ""
    echo "=== summary.md ==="
    cat "$RUN_DIR/summary.md"
fi

if [ -f "$RUN_DIR/next.md" ]; then
    echo ""
    echo "=== next.md ==="
    cat "$RUN_DIR/next.md"
fi
