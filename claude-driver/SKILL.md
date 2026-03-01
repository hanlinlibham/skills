---
name: claude-driver
description: >
  Drive an inner Claude Code instance via `claude` CLI to execute coding tasks autonomously.
  Use when orchestrating Claude-to-Claude workflows, automated coding pipelines, or
  multi-agent task delegation through the CLI protocol.
  Triggers: claude driver, inner claude, claude cli, delegate task, run claude, orchestrate claude
---

# Claude Driver

Drive an inner Claude Code via `claude -p` to execute coding tasks with structured artifacts.

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Outer Orchestrator (you / OpenClaw / script)    │
│                                                  │
│  1. Pick a playbook                              │
│  2. Assemble prompt = constitution + playbook    │
│     + task description                           │
│  3. Pipe into: claude -p --workdir <project>     │
│  4. Read .agent/runs/<run_id>/summary.md         │
│  5. If next.md has follow-ups → loop             │
└──────────────────────┬──────────────────────────┘
                       │ stdin pipe
                       ▼
┌─────────────────────────────────────────────────┐
│  Inner Claude Code (headless, -p mode)           │
│                                                  │
│  - Follows constitution (safety + workflow)       │
│  - Writes plan → executes → logs → summarizes    │
│  - All artifacts land in .agent/runs/<run_id>/   │
└─────────────────────────────────────────────────┘
```

## Prerequisites

1. `claude` CLI installed and on `$PATH`
2. Authenticated (`claude` can respond to prompts)
3. Target project directory exists

Run `bash scripts/healthcheck.sh` to verify all three.

## Quick Start

```bash
SKILL_DIR=".claude/skills/claude-driver"

# 1. Verify environment
bash "$SKILL_DIR/scripts/healthcheck.sh"

# 2. Run a task
bash "$SKILL_DIR/scripts/run-task.sh" \
  --workdir /path/to/project \
  --playbook bugfix \
  --task "Fix the off-by-one error in pagination.py"

# 3. Check results
cat /path/to/project/.agent/runs/*/summary.md
```

## Artifact Directory

Every run creates `.agent/runs/<YYYYMMDD-HHMMSS>/` with:

| File | Purpose | Written |
|------|---------|---------|
| `plan.md` | Step-by-step plan before any code changes | First |
| `actions.log` | Append-only log of commands and observations | During |
| `summary.md` | What was done, what changed, verification result | Last |
| `next.md` | Follow-up tasks or `DONE` if nothing remains | Last |

See [artifact-spec.md](references/artifact-spec.md) for full specification.

## Constitution (Summary)

The inner Claude operates under a constitution injected as prompt prefix:

- **Safety**: Work only inside `--workdir`, diff before overwrite, never `cat` large files
- **Workflow**: Must produce all 4 artifact files, log evidence for every claim
- **Failure convergence**: Max 2 retries on same error class, then write blockers to `next.md`

Full text: [constitution.md](references/constitution.md)

## Playbook Selection

| Scenario | Playbook | Steps |
|----------|----------|-------|
| Bug to fix | `bugfix` | Reproduce → Locate → Minimal patch → Verify → Summarize |
| New feature | `mvp` | Acceptance criteria → Find entry point → Implement + test → Summarize |
| Deploy scripts | `deploy` | Analyze service → Generate run/healthcheck/stop → Verify |

Playbook files: [playbook-bugfix.md](references/playbook-bugfix.md) | [playbook-mvp.md](references/playbook-mvp.md) | [playbook-deploy.md](references/playbook-deploy.md)

## CLI Parameters Quick Reference

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--workdir` | (required) | Project root for inner Claude |
| `--playbook` | `bugfix` | Which playbook to use: `bugfix`, `mvp`, `deploy` |
| `--task` | — | Task description as string |
| `--task-file` | — | Path to file containing task description |
| `--max-budget` | `1.00` | Max spend in USD per run |
| `--model` | (claude default) | Model override for inner Claude |
| `--allowed-tools` | (none) | Comma-separated tool allowlist |

## Standard Toolbox (Inner Claude)

Common patterns the inner Claude uses, documented in the constitution:

```
# Search
grep -rn "pattern" --include="*.py" .
find . -name "*.test.*" -type f

# Safe file reading (never cat entire large files)
head -100 path/to/file
sed -n '50,80p' path/to/file

# Evidence capture
command 2>&1 | tee -a .agent/runs/$RUN_ID/actions.log

# Diff before overwrite
diff <(cat original) <(cat modified) || true
```

## Outer Orchestration Patterns

See [outer-patterns.md](references/outer-patterns.md) for:
- Single-shot invocation (bash one-liner)
- Multi-turn loop (read `next.md`, decide whether to continue)
- OpenClaw integration (agent config)
- Prompt assembly rules

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Prompt delivery | stdin pipe to `claude -p` | Avoids shell escaping issues with long prompts |
| Permission skip | Off by default | Safety first; user opts in explicitly |
| Budget cap | $1.00/run default | Prevents runaway inner Claude spending |
| Artifact dir | `.agent/` not `.claude/` | Avoids conflict with Claude Code config |
| Dependencies | Pure bash, zero Python | Maximum portability |
