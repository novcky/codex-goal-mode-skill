---
name: goal-mode
description: Unattended goal workflow for Codex. Use only when the user explicitly includes `/goal` or explicitly says to enter goal mode. Initialize goal files before code edits, register the goal with available built-in goal/task tools, execute one task per session, verify with concrete evidence, update tasks.md, and continue until the goal is complete.
---

# Goal Mode

## Trigger Guard

Use this skill only when the user explicitly includes `/goal` or explicitly says to enter goal mode. Do not trigger it for ordinary planning, task lists, or long implementation requests that do not ask for goal mode.

Goal mode is designed for unattended execution. Avoid asking the user questions. When information is uncertain, choose a reasonable default assumption, write it in `plan.md` or `tasks.md`, and keep working on parts that do not depend on the missing detail.

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
6. Write `tasks.md` with small independently verifiable tasks. Prefer about 10 tasks for medium-sized work, fewer for very small work, and more for large work. Each task must reserve space for:
   - completion status
   - work performed
   - verification evidence
   - remaining risk
   - next step
7. Mark a major check/debug checkpoint after every third task in `tasks.md`.
8. Register the goal with built-in goal tooling when available, such as `create_goal`. Register the current todo/checklist with available task tooling when appropriate.
9. End the first turn with exactly:

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
6. Commit code changes when a commit is appropriate and code was modified.
7. Update `tasks.md` for the completed task with work performed, verification evidence, remaining risk, and next step.
8. Briefly report progress to the user, then stop output so the client can auto-advance.

Do not claim confidence without evidence. Evidence can include tests, builds, type checks, diffs, logs, manual UI checks, static analysis, or other concrete verification artifacts.

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
