# Artifact Specification

## Directory Structure

All run artifacts live under `.agent/runs/` in the target project:

```
<project-root>/
└── .agent/
    └── runs/
        ├── 20260301-143022/
        │   ├── plan.md
        │   ├── actions.log
        │   ├── summary.md
        │   └── next.md
        └── 20260301-150510/
            ├── plan.md
            ├── actions.log
            ├── summary.md
            └── next.md
```

## Run ID Format

```
YYYYMMDD-HHMMSS
```

- Generated from local time at run start.
- Example: `20260301-143022` = March 1, 2026 at 14:30:22.
- Used as the directory name under `.agent/runs/`.
- Passed to the inner Claude as `$RUN_ID` environment context.

## File Specifications

### plan.md

**When**: Written FIRST, before any code changes.

**Contents**:
```markdown
# Plan

## Task
<one-line task description>

## Steps
1. <step>
2. <step>
...

## Files to Read
- path/to/file (reason)

## Files to Modify
- path/to/file (what changes)

## Success Criteria
- <criterion 1>
- <criterion 2>
```

**Rules**:
- Must be written before executing any step.
- Steps should be concrete and verifiable.
- If the plan changes mid-execution, append a `## Plan Update` section (do not delete original).

### actions.log

**When**: Appended to continuously during execution.

**Format**:
```
[HH:MM:SS] ACTION: <description>
<optional output or evidence, indented 2 spaces>

[HH:MM:SS] ACTION: <description>
<optional output or evidence, indented 2 spaces>
```

**Example**:
```
[14:31:05] READ: src/pagination.py (42 lines)
  Contains paginate() function with off-by-one on line 28

[14:31:12] SEARCH: grep -rn "paginate" --include="*.py" .
  Found 3 references: src/pagination.py:28, tests/test_pagination.py:15, app.py:92

[14:31:30] EDIT: src/pagination.py line 28
  Changed: offset = page * size  →  offset = (page - 1) * size

[14:31:45] TEST: python -m pytest tests/test_pagination.py -v
  3 passed, 0 failed (0.2s)
```

**Rules**:
- Append only. Never delete or overwrite earlier entries.
- Every command that produces output should have output captured.
- Use action verbs: READ, SEARCH, EDIT, CREATE, DELETE, TEST, RUN, VERIFY.

### summary.md

**When**: Written LAST, after all work is complete.

**Contents**:
```markdown
# Summary

## Status
<COMPLETED | BLOCKED | PARTIAL>

## Task
<what was asked>

## What Was Done
- <change 1>
- <change 2>

## Files Changed
- `path/to/file` -- <what changed>

## Verification
<test results, reproduction check, or other evidence>

## Caveats
- <any known limitations or edge cases>
```

**Rules**:
- Status must be one of: COMPLETED, BLOCKED, PARTIAL.
- Every claim must have corresponding evidence in `actions.log`.
- If BLOCKED, explain what blocked progress and cross-reference `next.md`.

### next.md

**When**: Written LAST, alongside summary.md.

**If done**:
```markdown
DONE
```

**If follow-up needed**:
```markdown
# Next Steps

## Task 1: <title>
<description with enough context for a fresh Claude to execute>

## Task 2: <title>
<description>
```

**Rules**:
- Write `DONE` (single line) if nothing remains.
- Each follow-up task must be self-contained -- a fresh Claude reading only this file should understand what to do.
- Include file paths, error messages, and context from the current run.
- The outer orchestrator reads this file to decide whether to launch another run.

## .gitignore Recommendation

Add to the project's `.gitignore`:
```
.agent/
```

The `.agent/` directory is ephemeral run data, not source code.
