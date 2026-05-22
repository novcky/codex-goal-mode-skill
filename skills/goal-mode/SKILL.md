---
name: goal-mode
description: Unattended goal workflow for Codex. Use only when the user explicitly includes `/goal` or asks to enter goal mode. Initializes goal-N files before edits, registers available goal/task tools, runs one task per session, stops on red flags, verifies concrete evidence, updates tasks.md, and continues until complete.
---

# Goal Mode

## Trigger Guard

Use this skill only when the user explicitly includes `/goal` or explicitly says to enter goal mode. Do not trigger it for ordinary planning, task lists, or long implementation requests that do not ask for goal mode.

Goal mode is designed for unattended execution. Avoid asking the user questions. When information is uncertain, choose a reasonable default assumption, write it in `plan.md` or `tasks.md`, and keep working on parts that do not depend on the missing detail.

## Runtime Contract

Write this short contract at the top of each generated `tasks.md` so the workflow survives context compaction and new sessions:

```text
Runtime Contract:
- At the start of every session, read input.md, plan.md, and tasks.md in full.
- Execute only the first incomplete task or required checkpoint.
- Do not ask the user questions; record assumptions and continue safely.
- Before closing a task, verify with concrete evidence.
- Update this tasks.md with work, evidence, risk, and next step.
- Briefly report, then stop so the client can auto-advance.
- If a Red Flag appears, stop task execution and repair the workflow state first.
```

Keep this contract short. It is a guardrail for the next agent, not a second copy of the full skill.

## Initialization Turn

On the first goal-mode turn, initialize the goal and then stop. Do not modify project code before these files exist.

1. Determine the current project root. Prefer the active repository root, then the current workspace directory. If there is no project, create a new project directory in the current writable workspace and use it as the root.
2. Create the next available `goal-N/` directory under the project root. Use the lowest positive integer that does not already exist, and never overwrite an existing goal directory.
3. Create exactly these files:

```text
goal-N/
  input.md
  plan.md
  tasks.md
```

4. Write `input.md` with the user's original prompt verbatim. Preserve wording, punctuation, whitespace, and line breaks as much as the interface allows.
5. Write `plan.md` with the goal analysis, relevant context, risks, implementation approach, validation approach, rollback approach, and necessary default assumptions.
6. Start `tasks.md` with the Runtime Contract block above.
7. Continue `tasks.md` with small independently verifiable tasks. Prefer about 10 tasks for medium-sized work, fewer for very small work, and more for large work. Each task must reserve space for:
   - completion status
   - work performed
   - verification evidence
   - remaining risk
   - next step
8. Mark a major check/debug checkpoint after every third task in `tasks.md`.
9. Register the goal with built-in goal tooling when available, such as `create_goal`. Register the current todo/checklist with available task tooling when appropriate.
10. End the first turn with exactly:

```text
GOAL_INIT_DONE
```

Do not output anything else on the initialization turn.

## Session Loop

At the start of every later session, and after every context compaction, fully read:

```text
goal-N/input.md
goal-N/plan.md
goal-N/tasks.md
```

Then:

1. List a small todo/checklist for the current session and register it with available task tooling.
2. Execute only the first incomplete non-checkpoint task in `tasks.md`, unless the next required item is a major checkpoint or final review.
3. Keep the work narrowly scoped to that task. Do not execute multiple tasks in one session.
4. Before ending the task, ask internally: "Am I factually confident in the current implementation?"
5. If confidence is not backed by evidence, inspect, test, review diffs/logs/types/build output, and fix issues until confidence is supported by concrete evidence.
6. Run the Task Closure Protocol before reporting.
7. Commit code changes when a commit is appropriate and code was modified.
8. Update `tasks.md` for the completed task with work performed, verification evidence, remaining risk, and next step.
9. Briefly report progress to the user, then stop output so the client can auto-advance.

Do not claim confidence without evidence. Evidence can include tests, builds, type checks, diffs, logs, manual UI checks, static analysis, or other concrete verification artifacts.

## Task Closure Protocol

Before closing a task, verify and record:

- Scope check: only the intended task was executed.
- Evidence check: validation evidence exists and is named in `tasks.md`.
- State check: code changes, commits, and `tasks.md` agree with each other.
- Risk check: remaining risk and next step are explicit.
- AAR check: record any new trap, missing rule, outdated assumption, or repeated failure pattern discovered during the task.

If any check fails, fix the workflow state or implementation before reporting completion.

## Checkpoints

After every three completed tasks, run a major check/debug loop before continuing. Record the result in `tasks.md`. The checkpoint must inspect at least:

- requirement drift
- code bugs
- type checks
- builds
- tests
- UI/UX behavior when relevant
- security risks
- data consistency
- rollback needs
- documentation sync

Fix high-risk issues discovered by the checkpoint before moving on, staying within the goal scope.

## Final Review

When all tasks are complete, run the largest final review before marking the goal complete. Review the user-facing behavior, code quality, security, data consistency, permissions, error handling, tests, build, documentation, and rollback path.

Fix known high-risk issues, rerun relevant validation, update `tasks.md`, and then mark the registered goal complete with available goal tooling such as `update_goal`. After the final report, stop output. The client should not continue advancing after the goal is complete.

## Red Flags - STOP

Stop task execution and repair the workflow state first if you notice:

- you are about to skip validation or rely on a verbal confidence claim
- you are about to execute a second task in the same session
- you are about to ask the user a question instead of recording an assumption
- you started a new session or resumed after compaction without rereading all three goal files
- you changed code but did not update `tasks.md`
- `tasks.md` is missing the Runtime Contract, task status, evidence, risk, or next step fields
- the current task requires production secrets, payment/auth changes, data deletion, or another high-risk action without explicit authorization

Do not continue normal task work until the red flag is resolved or recorded as a blocking condition through the available goal tooling.

## Safety Rules

In goal mode, do not:

- steal Windows focus or open intrusive GUI windows
- reboot the machine
- ask the user questions
- break network connectivity
- edit code before initialization files exist
- execute more than one task per session
- expand scope without recording a default assumption and rationale
- delete important data without an explicit requirement and safe rollback plan
- modify production configuration, secrets, authentication, payments, or other high-risk systems without explicit authorization

If a required built-in goal or task tool is unavailable, continue with the file-based workflow and record the limitation in `tasks.md`.
