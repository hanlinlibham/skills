# Playbook: Bug Fix

You are fixing a bug. Follow these phases strictly in order.

## Phase 1: Reproduce

1. Read the bug description carefully. Identify:
   - Expected behavior
   - Actual behavior
   - Steps to reproduce (if given)

2. Find the relevant test file or entry point.
   ```bash
   grep -rn "function_name\|ClassName" --include="*.py" .
   grep -rn "function_name\|ClassName" --include="*.{ts,tsx,js}" .
   ```

3. Attempt to reproduce the bug:
   - Run the existing test suite first to see current state.
   - If no test covers the bug, create a minimal reproduction script.
   - Log the reproduction result to `actions.log`.

4. If you **cannot** reproduce:
   - Document what you tried in `actions.log`.
   - Write the blocker to `next.md` with reproduction details.
   - Set summary status to BLOCKED.
   - Stop.

## Phase 2: Locate

1. Starting from the reproduction, trace the code path to the root cause.
   ```bash
   grep -rn "error_pattern" --include="*.py" .
   ```

2. Read the relevant source files with bounded reads:
   ```bash
   sed -n '20,60p' path/to/source.py
   ```

3. Identify the **exact line(s)** causing the bug.

4. Log your finding:
   ```
   [HH:MM:SS] LOCATE: Root cause at path/to/file.py:42
     <explanation of why this line is wrong>
   ```

## Phase 3: Minimal Patch

1. Make the **smallest change** that fixes the bug. Do not refactor surrounding code.

2. Before editing, show the diff:
   ```
   [HH:MM:SS] EDIT: path/to/file.py line 42
     Before: offset = page * size
     After:  offset = (page - 1) * size
   ```

3. Apply the change.

4. If the fix requires changes in multiple files, list all changes in `plan.md` before applying any.

## Phase 4: Verify

1. Run the reproduction from Phase 1 again. Confirm the bug is fixed.

2. Run the full test suite (or the relevant subset):
   ```bash
   python -m pytest tests/ -v 2>&1 | tee -a .agent/runs/$RUN_ID/actions.log
   # or
   npm test 2>&1 | tee -a .agent/runs/$RUN_ID/actions.log
   ```

3. Log results:
   ```
   [HH:MM:SS] VERIFY: Bug reproduction now passes
   [HH:MM:SS] TEST: Full suite: X passed, Y failed
   ```

4. If new test failures appear that are **unrelated** to your fix, note them in `next.md` but do not fix them.

5. If your fix causes new test failures, revert and try a different approach (retry budget: 2).

## Phase 5: Summarize

1. Write `summary.md` with:
   - Root cause explanation
   - What was changed and why
   - Test results before and after

2. Write `next.md`:
   - `DONE` if the fix is complete and tests pass.
   - Follow-up items if you noticed related issues.
