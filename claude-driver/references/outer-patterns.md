# Outer Orchestration Patterns

How the outer layer (you, a script, or OpenClaw) invokes the inner Claude.

## 1. Single-Shot Invocation

The simplest pattern: one task, one run, check results.

```bash
#!/usr/bin/env bash
set -euo pipefail

WORKDIR="/path/to/project"
SKILL_DIR="$WORKDIR/.claude/skills/claude-driver"

bash "$SKILL_DIR/scripts/run-task.sh" \
  --workdir "$WORKDIR" \
  --playbook bugfix \
  --task "Fix the TypeError in src/parser.py line 42 when input is empty string"

# Check outcome
RUN_DIR=$(ls -td "$WORKDIR/.agent/runs/"*/ | head -1)
echo "=== Summary ==="
cat "$RUN_DIR/summary.md"
echo "=== Next ==="
cat "$RUN_DIR/next.md"
```

## 2. Multi-Turn Loop

Read `next.md` after each run. If it's not `DONE`, feed the follow-ups back in.

```bash
#!/usr/bin/env bash
set -euo pipefail

WORKDIR="/path/to/project"
SKILL_DIR="$WORKDIR/.claude/skills/claude-driver"
MAX_TURNS=5
PLAYBOOK="bugfix"

TASK="Fix the TypeError in src/parser.py line 42 when input is empty string"

for turn in $(seq 1 $MAX_TURNS); do
    echo ">>> Turn $turn / $MAX_TURNS"

    bash "$SKILL_DIR/scripts/run-task.sh" \
      --workdir "$WORKDIR" \
      --playbook "$PLAYBOOK" \
      --task "$TASK"

    # Find latest run
    RUN_DIR=$(ls -td "$WORKDIR/.agent/runs/"*/ | head -1)
    NEXT=$(cat "$RUN_DIR/next.md")

    if [ "$NEXT" = "DONE" ]; then
        echo ">>> Completed in $turn turn(s)"
        cat "$RUN_DIR/summary.md"
        exit 0
    fi

    echo ">>> Follow-up needed, continuing..."
    TASK="Continue from previous run. Follow-up tasks:\n\n$NEXT"
done

echo ">>> Reached max turns ($MAX_TURNS) without completion"
exit 1
```

## 3. Prompt Assembly Rules

The `run-task.sh` script assembles the prompt in this order:

```
┌─────────────────────────────────────┐
│  1. Constitution (always included)  │  ← references/constitution.md
├─────────────────────────────────────┤
│  2. Playbook (selected by flag)     │  ← references/playbook-*.md
├─────────────────────────────────────┤
│  3. Run Metadata                    │  ← generated: RUN_ID, WORKDIR
├─────────────────────────────────────┤
│  4. Task Description                │  ← --task or --task-file content
└─────────────────────────────────────┘
```

**Assembly in bash**:
```bash
{
    cat "$SKILL_DIR/references/constitution.md"
    echo ""
    echo "---"
    echo ""
    cat "$SKILL_DIR/references/playbook-${PLAYBOOK}.md"
    echo ""
    echo "---"
    echo ""
    echo "## Run Metadata"
    echo "- Run ID: $RUN_ID"
    echo "- Working directory: $WORKDIR"
    echo "- Artifact directory: .agent/runs/$RUN_ID/"
    echo ""
    echo "---"
    echo ""
    echo "## Task"
    echo "$TASK"
} | claude -p --workdir "$WORKDIR" $EXTRA_ARGS
```

## 4. OpenClaw Integration

For an OpenClaw agent that delegates coding tasks to an inner Claude:

```yaml
# In the coding agent's configuration
name: coding-agent
tools:
  - Bash
  - Read
  - Write
  - Edit

# The agent uses run-task.sh via Bash tool:
# bash .claude/skills/claude-driver/scripts/run-task.sh \
#   --workdir /project \
#   --playbook mvp \
#   --task-file /tmp/task-from-orchestrator.md
```

The outer OpenClaw agent:
1. Writes the task description to a temp file.
2. Calls `run-task.sh` with `--task-file`.
3. Reads `summary.md` and `next.md` from the run directory.
4. Decides whether to dispatch another run or report back.

## 5. CLI Parameter Reference

### Core Parameters

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `-p` | — | — | Headless mode (required). Read prompt from stdin. |
| `--workdir PATH` | string | cwd | Set working directory for the session. |
| `--model MODEL` | string | default | Model override (e.g., `claude-sonnet-4-6`). |
| `--max-budget-usd N` | float | none | Hard spending cap per session. |
| `--allowedTools TOOLS` | string | all | Comma-separated tool allowlist. |
| `--disallowedTools TOOLS` | string | none | Comma-separated tool denylist. |

### Permission Control

| Flag | Effect |
|------|--------|
| (default) | Inner Claude asks for permission on risky actions. |
| `--dangerously-skip-permissions` | Skip all permission checks. **Use only in sandboxed environments.** |

### Output Control

| Flag | Effect |
|------|--------|
| `--output-format text` | Plain text output (default for `-p`). |
| `--output-format json` | Structured JSON output. |
| `--output-format stream-json` | Streaming JSON lines. |
| `--verbose` | Include tool call details in output. |

### Example with All Options

```bash
echo "$PROMPT" | claude -p \
  --workdir /path/to/project \
  --model claude-sonnet-4-6 \
  --max-budget-usd 2.00 \
  --allowedTools "Bash,Read,Write,Edit,Glob,Grep" \
  --output-format text
```
