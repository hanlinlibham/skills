# Playbook: MVP Feature

You are implementing a new feature with minimal viable scope. Follow these phases strictly.

## Phase 1: Define Acceptance Criteria

1. Read the task description. Extract or infer:
   - What the feature does (user-visible behavior)
   - What inputs it accepts
   - What outputs it produces
   - Edge cases mentioned

2. Write acceptance criteria in `plan.md`:
   ```markdown
   ## Acceptance Criteria
   - [ ] <criterion 1>
   - [ ] <criterion 2>
   - [ ] <criterion 3>
   ```

3. If the task description is ambiguous, pick the **simplest** interpretation and note alternatives in `plan.md`.

## Phase 2: Find Entry Point

1. Understand the project structure:
   ```bash
   find . -maxdepth 2 -type f -name "*.py" | head -30
   # or
   find . -maxdepth 2 -type f -name "*.ts" | head -30
   ```

2. Identify where the new feature should live:
   - Which existing module/package does it belong to?
   - What naming conventions does the project use?
   - Are there similar features to use as a pattern?

3. Log the entry point decision:
   ```
   [HH:MM:SS] LOCATE: Feature will be added to src/features/
     Following pattern of existing src/features/auth.py
   ```

## Phase 3: Implement

1. Write the **minimum code** that satisfies the acceptance criteria. Do not:
   - Add configuration options not requested
   - Build abstractions for hypothetical future needs
   - Add logging/monitoring unless requested
   - Refactor existing code

2. For each file you create or modify, log in `actions.log`:
   ```
   [HH:MM:SS] CREATE: src/features/new_feature.py (45 lines)
     Implements <brief description>

   [HH:MM:SS] EDIT: src/app.py line 15
     Added import and route registration for new_feature
   ```

3. If the implementation requires a dependency not already in the project, **stop** and write it to `next.md` as a blocker. Do not install dependencies.

## Phase 4: Test

1. Write a test for each acceptance criterion:
   ```bash
   # Create test file following project conventions
   ```

2. Run the tests:
   ```bash
   python -m pytest tests/test_new_feature.py -v 2>&1 | tee -a .agent/runs/$RUN_ID/actions.log
   ```

3. Run the full test suite to check for regressions:
   ```bash
   python -m pytest tests/ -v 2>&1 | tee -a .agent/runs/$RUN_ID/actions.log
   ```

4. If tests fail:
   - Fix the implementation (not the test, unless the test is wrong).
   - Retry up to 2 times.
   - After 2 failures, write BLOCKED status.

## Phase 5: Summarize

1. Write `summary.md`:
   - What was implemented
   - Files created/modified
   - Test results
   - How to use the new feature (one-line example)

2. Write `next.md`:
   - `DONE` if all acceptance criteria are met and tests pass.
   - Follow-up items: polish, documentation, edge cases deferred.

3. Check off acceptance criteria in `plan.md` that were met.
