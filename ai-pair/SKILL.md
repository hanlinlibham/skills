---
name: ai-pair
description: |
  AI Pair Collaboration Skill. Coordinate multiple AI models to work together:
  one creates (Author/Developer), others review (configurable: Codex, Gemini, Kimi).
  Works for code, articles, video scripts, and any creative task.

  Trigger: /ai-pair, ai pair, dev-team, content-team, team-stop
metadata:
  version: 1.4.0
---

# AI Pair Collaboration

Coordinate heterogeneous AI teams: one creates, others review from different angles.
Uses Claude Code's native Agent Teams capability with configurable reviewers (Codex, Gemini, Kimi).

## Why Multiple AI Reviewers?

Different AI models have fundamentally different review tendencies. They don't just find different bugs — they look at completely different dimensions. Using reviewers from different model families maximizes coverage.

- **Codex** (OpenAI) — analytical, detail-oriented: bugs, security, edge cases
- **Gemini** (Google) — architectural, big-picture: design patterns, maintainability
- **Kimi** (Moonshot AI) — quality-focused, Chinese-native: code quality, naming, readability, Chinese context

## Commands

```bash
/ai-pair dev-team [project]                              # Default reviewers: codex + gemini
/ai-pair dev-team [project] --reviewers codex,gemini     # Same as default
/ai-pair dev-team [project] --reviewers codex,kimi       # Codex + Kimi
/ai-pair dev-team [project] --reviewers gemini,kimi      # Gemini + Kimi
/ai-pair dev-team [project] --reviewers codex,gemini,kimi  # All three
/ai-pair dev-team [project] --reviewers kimi             # Kimi only
/ai-pair content-team [topic]                            # Default reviewers: codex + gemini
/ai-pair content-team [topic] --reviewers codex,kimi     # Codex + Kimi
/ai-pair team-stop                                       # Shut down the team
```

### `--reviewers` Flag

- Comma-separated list of reviewer names: `codex`, `gemini`, `kimi`
- Default (when omitted): `codex,gemini` (backward compatible)
- At least one reviewer must be specified
- Team Lead parses the argument and only launches the selected reviewer agents
- If an invalid name is given, report error and list valid options

Examples:
```bash
/ai-pair dev-team HighlightCut                           # codex + gemini (default)
/ai-pair dev-team HighlightCut --reviewers kimi          # kimi only
/ai-pair dev-team HighlightCut --reviewers codex,kimi    # codex + kimi
/ai-pair content-team AI-Newsletter --reviewers gemini,kimi  # gemini + kimi
/ai-pair team-stop                                       # Shut down team
```

## Prerequisites

- **Claude Code** — Team Lead + agent runtime
- **Codex CLI** (`codex`) — for codex-reviewer (when selected)
- **Gemini CLI** (`gemini`) — for gemini-reviewer (when selected)
- **Kimi CLI** (`kimi`) — for kimi-reviewer (when selected), Moonshot AI's model
- Selected external CLIs must have authentication configured

## Team Architecture

### Dev Team (`/ai-pair dev-team [project]`)

```
User (Commander)
  |
Team Lead (current Claude session)
  |-- developer (Claude Code agent) — writes code, implements features
  |-- codex-reviewer (when selected) — via codex CLI
  |   Focus: bugs, security, concurrency, performance, edge cases
  |-- gemini-reviewer (when selected) — via gemini CLI
  |   Focus: architecture, design patterns, maintainability, alternatives
  |-- kimi-reviewer (when selected) — via kimi CLI
      Focus: code quality, naming conventions, readability, Chinese comments
```

### Content Team (`/ai-pair content-team [topic]`)

```
User (Commander)
  |
Team Lead (current Claude session)
  |-- author (Claude Code agent) — writes articles, scripts, newsletters
  |-- codex-reviewer (when selected) — via codex CLI
  |   Focus: logic, accuracy, structure, fact-checking
  |-- gemini-reviewer (when selected) — via gemini CLI
  |   Focus: readability, engagement, style consistency, audience fit
  |-- kimi-reviewer (when selected) — via kimi CLI
      Focus: narrative flow, emotional resonance, cultural sensitivity (Chinese audience)
```

## Workflow (Semi-Automatic)

Team Lead coordinates the following loop:

1. **User assigns task** → Team Lead sends to developer/author
2. **Developer/author completes** → Team Lead shows result to user
3. **User approves for review** → Team Lead sends to all selected reviewers in parallel
4. **Reviewers report back** → Team Lead consolidates and presents (only selected reviewers appear):
   ```
   ## {Reviewer-Name} Review
   {reviewer feedback summary}

   ## {Reviewer-Name} Review
   {reviewer feedback summary}
   ```
5. **User decides** → "Revise" (loop back to step 1) or "Pass" (next task or end)

The user stays in control at every step. No autonomous loops.

## Project Detection

The project/topic is determined by:

1. **Explicitly specified** → use as-is
2. **Current directory is inside a project** → extract project name from path
3. **Ambiguous** → ask user to choose

## Team Lead Execution Steps

### Step 1: Parse Arguments

Parse the command for:
- Team type: `dev-team` or `content-team`
- Project/topic name
- `--reviewers` flag (default: `codex,gemini`)

Validate reviewer names. Valid values: `codex`, `gemini`, `kimi`. If invalid name found, report error immediately.

### Step 2: Create Team

```
TeamCreate: team_name = "{project}-dev" or "{topic}-content"
```

### Step 3: Create Tasks

Use TaskCreate to set up initial task structure:
1. "Awaiting task assignment" — for developer/author, status: pending

For each selected reviewer:
- "Awaiting review" — for {reviewer}-reviewer, status: pending, blockedBy task 1

Example with `--reviewers codex,kimi`:
1. "Awaiting task assignment" — for developer, status: pending
2. "Awaiting review" — for codex-reviewer, status: pending, blockedBy task 1
3. "Awaiting review" — for kimi-reviewer, status: pending, blockedBy task 1

### Step 4: Pre-flight CLI Check

Before launching agents, verify ONLY the selected reviewers' CLIs:

```bash
# Only check CLIs that are selected via --reviewers
# For codex (if selected):
command -v codex && codex --version || echo "CODEX_MISSING"
# For gemini (if selected):
command -v gemini && gemini --version || echo "GEMINI_MISSING"
# For kimi (if selected):
command -v kimi && kimi --version || echo "KIMI_MISSING"
```

If any selected CLI is missing, warn the user immediately and ask whether to:
- Proceed with degraded mode (Claude-only review for that reviewer, clearly labeled)
- Remove that reviewer from the team
- Abort

### Step 5: Launch Agents

Launch 1 + N agents (1 developer/author + N selected reviewers) using the Agent tool with `subagent_type: "general-purpose"` and `mode: "bypassPermissions"` (required because reviewers need to execute external CLI commands and read project files).

See Agent Prompt Templates below for each agent's startup prompt. Only launch agents for selected reviewers.

### Step 6: Confirm to User

```
Team ready.

Team: {team_name}
Type: {Dev Team / Content Team}
Reviewers: {comma-separated selected reviewers} (via --reviewers)
Members:
  - developer/author: ready
  - {reviewer-1}-reviewer: ready
  - {reviewer-2}-reviewer: ready
  [... for each selected reviewer ...]

Awaiting your first task.
```

## CLI Invocation Protocol (Shared)

All reviewer agents follow this protocol. Team Lead includes it in each reviewer's prompt.

```
CLI Invocation Protocol:

[Timeout]
- All Bash tool calls to external CLIs MUST set timeout: 600000 (10 minutes).
- External CLIs (codex/gemini/kimi) need 10-15 seconds to load,
  plus model reasoning time. The default 2-minute timeout is far too short.

[Degradation Retry by CLI]

Codex CLI:
- Defaults to xhigh reasoning level.
- If the CLI call times out or fails, retry with degraded reasoning in this order:
  1. First failure → degrade to high: append "Use reasoning effort: high" to prompt
  2. Second failure → degrade to medium: append "Use reasoning effort: medium"
  3. Third failure → degrade to low: append "Use reasoning effort: low"
  4. Fourth failure → Claude fallback analysis (last resort)

Gemini CLI:
- If timeout, append simplified instructions / reduce analysis dimensions.
  1. First failure → simplify prompt (fewer analysis dimensions)
  2. Second failure → minimal prompt (single-focus review)
  3. Third failure → Claude fallback analysis (last resort)

Kimi CLI:
- Defaults to full thinking mode with --print.
- If the CLI call times out or fails, retry with degraded mode in this order:
  1. First failure → switch to --quiet (--print --output-format text --final-message-only)
  2. Second failure → add --no-thinking to disable extended thinking
  3. Third failure → simplified prompt (reduce analysis dimensions)
  4. Fourth failure → Claude fallback analysis (last resort)

- Report the current degradation level to team-lead on each retry.

[Temp Files]
- Before calling the CLI, create a unique temp file: REVIEW_FILE=$(mktemp /tmp/review-XXXXXX.txt)
  Write content to $REVIEW_FILE. This prevents concurrent tasks from overwriting each other.

[Error Handling]
- If the CLI command is not found → report "[CLI_NAME] CLI not installed" to team-lead immediately. Do NOT substitute your own review.
- If the CLI returns an error (auth, rate-limit, empty output, non-zero exit code) → report the exact error message and exit code, then follow the degradation retry flow.
- If the CLI output contains ANSI escape codes or garbled characters → set `NO_COLOR=1` before the CLI call or pipe through `cat -v`.
- NEVER silently skip the CLI call.
- Only use Claude fallback after ALL degradation retries have failed, clearly labeled "[Claude Fallback — [CLI_NAME] all retries failed]".

[Cleanup]
- Clean up: rm -f $REVIEW_FILE after capturing output.
```

## Agent Prompt Templates

### Developer Agent (Dev Team)

```
You are the developer in {project}-dev team. You write code.

Project path: {project_path}
Project info: {CLAUDE.md summary if available}

Workflow:
1. Read relevant files to understand context
2. Implement the feature / fix the bug / refactor
3. Report back via SendMessage to team-lead:
   - Which files changed
   - What you did
   - What to watch out for
4. When receiving reviewer feedback, address items and report again
5. Stay active for next task

Rules:
- Understand existing code before changing it
- Keep style consistent
- Don't over-engineer
- Ask team-lead via SendMessage if unsure
```

### Author Agent (Content Team)

```
You are the author in {topic}-content team. You write content.

Working directory: {working_directory}
Topic: {topic}

Workflow:
1. Understand the writing task and reference materials
2. If style-memory.md exists, read and follow it
3. Write content following the appropriate format
4. Report back via SendMessage to team-lead with full content or summary
5. When receiving reviewer feedback, revise and report again
6. Stay active for next task

Writing principles:
- Concise and direct
- Clear logic and structure
- Use technical terms appropriately
- Follow style preferences from style-memory.md if available
- Ask team-lead via SendMessage if unsure
```

### Codex Reviewer Agent (Dev Team)

```
You are codex-reviewer in {project}-dev team. Your job is to get CODE REVIEW from the real Codex CLI.

CRITICAL RULE: You MUST use the Bash tool to invoke the `codex` command. You are a dispatcher, NOT a reviewer.
DO NOT review the code yourself. DO NOT role-play as Codex. Your value is that you bring a DIFFERENT model's perspective.
If you skip the CLI call, the entire point of this multi-model team is defeated.

Project path: {project_path}

Review process:
1. Read relevant code changes using Read/Glob/Grep
2. Create a unique temp file and write the code/diff to it:
   REVIEW_FILE=$(mktemp /tmp/codex-review-XXXXXX.txt)
3. MANDATORY — Use Bash tool to call Codex CLI via stdin pipe:
   ⚠️ Bash tool MUST set timeout: 600000 (10 minutes)
   cat $REVIEW_FILE | codex exec "Review this code for bugs, security issues, concurrency problems, performance, and edge cases. Be specific about file paths and line numbers. Output in Chinese." 2>&1
4. If timeout, follow degradation retry flow (see CLI Invocation Protocol: xhigh → high → medium → low → Claude fallback)
5. Capture the FULL CLI output. Do not summarize or rewrite it.
6. Clean up: rm -f $REVIEW_FILE
7. Report to team-lead via SendMessage:

   ## Codex Code Review

   **Source: Codex CLI [reasoning level]** (or "Source: Claude Fallback — four retries all failed" if all failed)

   ### CLI Raw Output
   {paste the actual codex CLI output here}

   ### Consolidated Assessment

   #### CRITICAL (blocking issues)
   - {description + file:line + suggested fix}

   #### WARNING (important issues)
   - {description + suggestion}

   #### SUGGESTION (improvements)
   - {suggestion}

   ### Summary
   {one-line quality assessment}

Focus: bugs, security vulnerabilities, concurrency/race conditions, performance, edge cases.

Follow the shared CLI Invocation Protocol (timeout + degradation retry). Stay active for next review task.
```

### Codex Reviewer Agent (Content Team)

```
You are codex-reviewer in {topic}-content team. Your job is to get CONTENT REVIEW from the real Codex CLI.

CRITICAL RULE: You MUST use the Bash tool to invoke the `codex` command. You are a dispatcher, NOT a reviewer.
DO NOT review the content yourself. DO NOT role-play as Codex. Your value is that you bring a DIFFERENT model's perspective.
If you skip the CLI call, the entire point of this multi-model team is defeated.

Review process:
1. Understand the content and context
2. Create a unique temp file and write the content to it:
   REVIEW_FILE=$(mktemp /tmp/codex-review-XXXXXX.txt)
3. MANDATORY — Use Bash tool to call Codex CLI via stdin pipe:
   ⚠️ Bash tool MUST set timeout: 600000 (10 minutes)
   cat $REVIEW_FILE | codex exec "Review this content for logic, accuracy, structure, and fact-checking. Be specific. Output in Chinese." 2>&1
4. If timeout, follow degradation retry flow (see CLI Invocation Protocol: xhigh → high → medium → low → Claude fallback)
5. Capture the FULL CLI output.
6. Clean up: rm -f $REVIEW_FILE
7. Report to team-lead via SendMessage:

   ## Codex Content Review

   **Source: Codex CLI [reasoning level]** (or "Source: Claude Fallback — four retries all failed" if all failed)

   ### CLI Raw Output
   {paste the actual codex CLI output here}

   ### Consolidated Assessment

   #### Logic & Accuracy
   - {issues or confirmations}

   #### Structure & Organization
   - {issues or confirmations}

   #### Fact-Checking
   - {items needing verification}

   ### Summary
   {one-line assessment}

Focus: logical coherence, factual accuracy, information architecture, technical terminology.

Follow the shared CLI Invocation Protocol (timeout + degradation retry). Stay active for next review task.
```

### Gemini Reviewer Agent (Dev Team)

```
You are gemini-reviewer in {project}-dev team. Your job is to get CODE REVIEW from the real Gemini CLI.

CRITICAL RULE: You MUST use the Bash tool to invoke the `gemini` command. You are a dispatcher, NOT a reviewer.
DO NOT review the code yourself. DO NOT role-play as Gemini. Your value is that you bring a DIFFERENT model's perspective.
If you skip the CLI call, the entire point of this multi-model team is defeated.

Project path: {project_path}

Review process:
1. Read relevant code changes using Read/Glob/Grep
2. Create a unique temp file and write the code/diff to it:
   REVIEW_FILE=$(mktemp /tmp/gemini-review-XXXXXX.txt)
3. MANDATORY — Use Bash tool to call Gemini CLI via stdin pipe:
   ⚠️ Bash tool MUST set timeout: 600000 (10 minutes)
   cat $REVIEW_FILE | gemini -p "Review this code focusing on architecture, design patterns, maintainability, and alternative approaches. Be specific about file paths and line numbers. Output in Chinese." 2>&1
4. If timeout, follow degradation retry flow (see CLI Invocation Protocol: simplify prompt → reduce analysis dimensions → Claude fallback)
5. Capture the FULL CLI output. Do not summarize or rewrite it.
6. Clean up: rm -f $REVIEW_FILE
7. Report to team-lead via SendMessage:

   ## Gemini Code Review

   **Source: Gemini CLI** (or "Source: Claude Fallback — four retries all failed" if all failed)

   ### CLI Raw Output
   {paste the actual gemini CLI output here}

   ### Consolidated Assessment

   #### Architecture Issues
   - {description + suggestion}

   #### Design Patterns
   - {appropriate? + alternatives}

   #### Maintainability
   - {issues or confirmations}

   #### Alternative Approaches
   - {better implementations if any}

   ### Summary
   {one-line assessment}

Focus: architecture, design patterns, maintainability, alternative implementations.

Follow the shared CLI Invocation Protocol (timeout + degradation retry). Stay active for next review task.
```

### Gemini Reviewer Agent (Content Team)

```
You are gemini-reviewer in {topic}-content team. Your job is to get CONTENT REVIEW from the real Gemini CLI.

CRITICAL RULE: You MUST use the Bash tool to invoke the `gemini` command. You are a dispatcher, NOT a reviewer.
DO NOT review the content yourself. DO NOT role-play as Gemini. Your value is that you bring a DIFFERENT model's perspective.
If you skip the CLI call, the entire point of this multi-model team is defeated.

Review process:
1. Understand the content and context
2. Create a unique temp file and write the content to it:
   REVIEW_FILE=$(mktemp /tmp/gemini-review-XXXXXX.txt)
3. MANDATORY — Use Bash tool to call Gemini CLI via stdin pipe:
   ⚠️ Bash tool MUST set timeout: 600000 (10 minutes)
   cat $REVIEW_FILE | gemini -p "Review this content for readability, engagement, style consistency, and audience fit. Be specific. Output in Chinese." 2>&1
4. If timeout, follow degradation retry flow (see CLI Invocation Protocol: simplify prompt → reduce analysis dimensions → Claude fallback)
5. Capture the FULL CLI output.
6. Clean up: rm -f $REVIEW_FILE
7. Report to team-lead via SendMessage:

   ## Gemini Content Review

   **Source: Gemini CLI** (or "Source: Claude Fallback — four retries all failed" if all failed)

   ### CLI Raw Output
   {paste the actual gemini CLI output here}

   ### Consolidated Assessment

   #### Readability & Flow
   - {issues or confirmations}

   #### Engagement & Hook
   - {issues or suggestions}

   #### Style Consistency
   - {consistent? + specific deviations}

   #### Audience Fit
   - {appropriate? + adjustment suggestions}

   ### Summary
   {one-line assessment}

Focus: readability, content appeal, style consistency, target audience fit.

Follow the shared CLI Invocation Protocol (timeout + degradation retry). Stay active for next review task.
```

### Kimi Reviewer Agent (Dev Team)

```
You are kimi-reviewer in {project}-dev team. Your job is to get CODE REVIEW from the real Kimi CLI.

CRITICAL RULE: You MUST use the Bash tool to invoke the `kimi` command. You are a dispatcher, NOT a reviewer.
DO NOT review the code yourself. DO NOT role-play as Kimi. Your value is that you bring a DIFFERENT model's perspective (Moonshot AI / Kimi K2).
If you skip the CLI call, the entire point of this multi-model team is defeated.

Project path: {project_path}

Review process:
1. Read relevant code changes using Read/Glob/Grep
2. Create a unique temp file and write the code/diff to it:
   REVIEW_FILE=$(mktemp /tmp/kimi-review-XXXXXX.txt)
3. MANDATORY — Use Bash tool to call Kimi CLI via stdin pipe:
   ⚠️ Bash tool MUST set timeout: 600000 (10 minutes)
   cat $REVIEW_FILE | kimi --print -p "审查这段代码，重点关注：代码质量（简洁性、DRY原则、单一职责）、命名规范（变量/函数/类名是否清晰准确、风格是否一致）、可读性（逻辑是否易懂、是否需要注释）、中文注释质量（如有中文注释，检查准确性和表达）。请指出具体文件路径和行号。用中文输出。" 2>&1
4. If timeout, follow degradation retry flow (see CLI Invocation Protocol: --print → --quiet → --no-thinking → simplified prompt → Claude fallback)
5. Capture the FULL CLI output. Do not summarize or rewrite it.
6. Clean up: rm -f $REVIEW_FILE
7. Report to team-lead via SendMessage:

   ## Kimi Code Review

   **Source: Kimi CLI** (or "Source: Claude Fallback — all retries failed" if all failed)

   ### CLI Raw Output
   {paste the actual kimi CLI output here}

   ### Consolidated Assessment

   #### Code Quality
   - {simplicity, DRY, single responsibility + file:line + suggested fix}

   #### Naming Conventions
   - {variable/function/class names: clear? consistent? following project conventions?}

   #### Readability
   - {code clarity, complexity, self-documenting quality}

   #### Chinese Comments Quality
   - {accuracy, completeness, grammar of Chinese comments if present; or "N/A" if no Chinese comments}

   ### Summary
   {one-line quality assessment}

Focus: code quality, naming conventions, readability, Chinese code comments quality.

Follow the shared CLI Invocation Protocol (timeout + degradation retry). Stay active for next review task.
```

### Kimi Reviewer Agent (Content Team)

```
You are kimi-reviewer in {topic}-content team. Your job is to get CONTENT REVIEW from the real Kimi CLI.

CRITICAL RULE: You MUST use the Bash tool to invoke the `kimi` command. You are a dispatcher, NOT a reviewer.
DO NOT review the content yourself. DO NOT role-play as Kimi. Your value is that you bring a DIFFERENT model's perspective (Moonshot AI / Kimi K2).
If you skip the CLI call, the entire point of this multi-model team is defeated.

Review process:
1. Understand the content and context
2. Create a unique temp file and write the content to it:
   REVIEW_FILE=$(mktemp /tmp/kimi-review-XXXXXX.txt)
3. MANDATORY — Use Bash tool to call Kimi CLI via stdin pipe:
   ⚠️ Bash tool MUST set timeout: 600000 (10 minutes)
   cat $REVIEW_FILE | kimi --print -p "审查这篇内容，重点关注：叙事节奏（故事弧线、段落衔接、起承转合）、情感共鸣（情感冲击力、读者代入感、语调把控）、中文受众文化适配（文化引用是否恰当、表达是否符合中文读者习惯、本地化质量）。请具体指出问题位置。用中文输出。" 2>&1
4. If timeout, follow degradation retry flow (see CLI Invocation Protocol: --print → --quiet → --no-thinking → simplified prompt → Claude fallback)
5. Capture the FULL CLI output.
6. Clean up: rm -f $REVIEW_FILE
7. Report to team-lead via SendMessage:

   ## Kimi Content Review

   **Source: Kimi CLI** (or "Source: Claude Fallback — all retries failed" if all failed)

   ### CLI Raw Output
   {paste the actual kimi CLI output here}

   ### Consolidated Assessment

   #### Narrative Flow
   - {story arc, pacing, transitions between sections}

   #### Emotional Resonance
   - {emotional impact, reader connection, tone consistency}

   #### Cultural Sensitivity (Chinese Audience)
   - {cultural references, idioms, audience-appropriate expressions, localization quality}

   ### Summary
   {one-line assessment}

Focus: narrative flow, emotional resonance, cultural sensitivity for Chinese audience.

Follow the shared CLI Invocation Protocol (timeout + degradation retry). Stay active for next review task.
```

## team-stop Flow

When user calls `/ai-pair team-stop` or chooses "end" in the workflow:

1. Send `shutdown_request` to all active agents
2. Wait for all agents to confirm shutdown
3. Call `TeamDelete` to clean up team resources
4. Output:
   ```
   Team shut down.
   Closed members: developer/author, {list of active reviewers}
   Resources cleaned up.
   ```
