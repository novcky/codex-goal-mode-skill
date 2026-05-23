# Goal Workflow Reference

Read this file after `SKILL.md` and before any goal-mode initialization or task execution.

## Runtime Contract

```text
Runtime Contract:
- Resolve the active goal through goal-current before choosing work.
- If this session created goal-current or goal-N files, stop with exactly GOAL_INIT_DONE.
- At the start of every session, read input.md, plan.md, and tasks.md in full.
- Before task, checkpoint, or final-review work in a git repository, block on unrelated dirty worktree changes.
- Execute only the first incomplete task or required checkpoint.
- Commit code changes at the task boundary when the project is a git repository.
- Commit checkpoint-only tracking updates as `goal-N checkpoint after task M: complete` when the project is a git repository.
- Commit final-review-only tracking updates as `goal-N final review: complete` when the project is a git repository.
- After any task-boundary commit, task commit skip, or task commit failure, stop immediately; checkpoint and final review must wait for a later session.
- Commit-status text in tasks.md must remain true after the commit; do not commit pending, ready-to-commit, or to-be-created wording.
- Do not ask the user questions; record assumptions and continue safely.
- Before closing a task, verify with concrete evidence.
- Update this tasks.md with work, evidence, risk, and next step.
- Briefly report, then stop so the client can auto-advance.
- If a Red Flag appears, stop task execution and repair the workflow state first.
```

Keep this block short. It is a guardrail for the next agent, not a second copy of the whole skill.

## Initialization Turn

On the first goal-mode turn:

1. Determine the current project root. Prefer the active repository root, then the current workspace directory. If there is no project, create a new project directory in the current writable workspace and use it as the root.
2. Create the next available `goal-N/` directory under the project root. Use the lowest positive integer that does not already exist, and never overwrite an existing goal directory.
3. Create exactly these files and update the project-root `goal-current` file to contain only the active directory name, such as `goal-3`:

```text
goal-current
goal-N/
  input.md
  plan.md
  tasks.md
```

4. Write `input.md` with the user's original prompt verbatim. If Codex transformed the original `/goal` command into a `goal_context` message, write the `objective` text as the goal prompt and note `Source: Codex goal_context`.
5. Write `plan.md` with the goal analysis, relevant context, risks, implementation approach, validation approach, rollback approach, necessary default assumptions, and commit approach.
6. Start `tasks.md` with the Runtime Contract block above.
7. Add `Goal status: active` and `Commit policy: commit code changes at the task boundary when the project is a git repository` to `tasks.md`.
8. Continue `tasks.md` with small independently verifiable tasks. Split explicitly named deliverables into separate tasks: if the user names separate files, docs, scripts, screens, APIs, or validation artifacts, create one task per deliverable or per tightly coupled deliverable group instead of merging them into a single broad task. For a goal that names three or more deliverables, create at least three implementation tasks so the Task 3 checkpoint can run. Prefer about 10 tasks for medium-sized work, fewer for very small single-deliverable work, and more for large work. Each task must reserve space for:
   - completion status
   - work performed
   - verification evidence
   - remaining risk
   - next step
9. Mark a major check/debug checkpoint after every third task in `tasks.md`.
10. Register the goal with built-in goal tooling when available, such as `create_goal`, unless Codex `goal_context` already created an active goal. Register the current todo/checklist with available task tooling when appropriate. If the tooling is unavailable, continue the file workflow and record the limitation.
11. End the first turn with exactly:

```text
GOAL_INIT_DONE
```

Do not output anything else on the initialization turn.

Do not combine initialization with task execution, even for tiny goals. During the initialization turn, do not edit target project files, run task validation, close tasks, perform final review, create commits, or mark the goal complete.

In a git repository, initialization files are not committed during the initialization turn. Include `goal-current`, `input.md`, `plan.md`, and the initial `tasks.md` in the first task-boundary commit together with that task's implementation changes.

## Session Loop

At the start of every later session, and after every context compaction:

1. Resolve the active goal directory:
   - Read project-root `goal-current` when it exists and points to a `goal-N/` directory whose `tasks.md` is not complete.
   - If `goal-current` is missing or invalid, choose the highest-numbered `goal-N/` whose `tasks.md` does not say `Goal status: complete`, update `goal-current`, and record the repair in `tasks.md`.
   - If no incomplete goal can be determined uniquely, stop and record the blocker instead of guessing.
2. Fully read:

```text
goal-N/input.md
goal-N/plan.md
goal-N/tasks.md
```

3. In a git repository, inspect the worktree with `git status --short` before task, checkpoint, or final-review work. Use `pwsh -NoProfile` or `powershell -NoProfile` for PowerShell checks and scripts on Windows.
   - Allowed dirty state is limited to active goal-mode tracking leftovers that the workflow explicitly knows how to repair: uncommitted initialization files before Task 1, uncommitted active `goal-N/tasks.md` checkpoint/final-review tracking updates, or `goal-current` pointing at the active goal.
   - If any other modified, deleted, or untracked file is present, treat it as user or unrelated work. Record a blocker in `tasks.md`, do not edit implementation files, do not stage or commit the unrelated files, and stop.
   - If the dirty state is an allowed tracking leftover, repair that boundary first and stop when the repair rule says to stop.

Then:

1. List a small todo/checklist for the current session and register it with available task tooling.
2. Execute only the first incomplete non-checkpoint task in `tasks.md`, unless the next required item is a major checkpoint or final review.
3. Execute only one task per session. Keep the work narrowly scoped to that task.
4. Before ending the task, ask internally: "Am I factually confident in the current implementation?"
5. If confidence is not backed by evidence, inspect, test, review diffs/logs/types/build output, and fix issues until confidence is supported by concrete evidence.
6. Run the Task Closure Protocol before reporting.
7. Update `tasks.md` for the completed task with work performed, verification evidence, remaining risk, next step, and commit status.
8. If task execution changed code inside a git repository, create one task-boundary commit after validation and the `tasks.md` update. Use commit message `goal-N task M: <task title>` and include only task-related implementation files plus the relevant goal tracking update. For the first task commit, also include the untracked initialization files from the initialization turn. Before committing, write durable commit-status text such as `Commit status: included in task-boundary commit message "goal-N task M: <task title>"`; do not commit wording like pending, ready to commit, or to be created. If there is no git repository, record `Commit skipped: not a git repository` in `tasks.md`. If the commit fails, record the failure in `tasks.md` and stop instead of asking the user.
9. After the task-boundary commit succeeds, the non-git task skip is recorded, or the commit failure is recorded, stop immediately. Do not run a checkpoint or final review in the same session that completed a task boundary, even if this was the last incomplete implementation task. The next required checkpoint or final review must wait for the next goal-mode continuation.
10. If a previous checkpoint is already marked complete in `tasks.md` but its tracking update is uncommitted, create the checkpoint tracking commit and stop immediately. Use commit message `goal-N checkpoint after task M: complete`, where `M` is the completed task count that triggered the checkpoint. Final review must wait for the next goal-mode session.
11. Briefly report progress to the user, then stop output so the client can auto-advance.

Do not claim confidence without evidence. Evidence can include tests, builds, type checks, diffs, logs, manual UI checks, static analysis, or other concrete verification artifacts.

## Principles and Checks

- Principle: One task per session. Check: Did this session modify, verify, or close a second incomplete task? If yes, stop and repair `tasks.md`.
- Principle: Stop after task boundary. Check: Did this session complete a task-boundary commit, commit skip, or commit failure and then start checkpoint or final review? If yes, stop and repair `tasks.md`.
- Principle: Deliverable splitting. Check: Did `tasks.md` merge multiple files, docs, scripts, screens, APIs, or validation artifacts that the user explicitly named? If yes, split them before executing Task 1.
- Principle: Evidence before closure. Check: Is there named concrete evidence for the claimed result? If no, inspect, test, or review before reporting.
- Principle: State synchronization. Check: Do code changes, commits, and `tasks.md` describe the same work? If no, fix the mismatch.
- Principle: Scope control. Check: Did new scope appear that was not in `input.md` or `plan.md`? If yes, record an assumption before continuing.
- Principle: Goal resolution. Check: Did this session resolve the active goal from `goal-current`, or repair it by selecting the highest-numbered incomplete goal? If no, stop before touching implementation.
- Principle: Initialization boundary. Check: Did this session create goal files and also execute Task 1? If yes, stop and repair the workflow state.
- Principle: Dirty worktree guard. Check: Did `git status --short` show unrelated work before this session changed files? If yes, record a blocker and stop without staging or committing it.
- Principle: Commit control. Check: Did this session change code or complete a checkpoint/final-review tracking update in a git repo without the matching tracking commit or recorded commit failure? If yes, stop and repair the workflow state.
- Principle: Durable commit status. Check: Would the committed `tasks.md` still say the commit is pending, ready to commit, or to be created after the commit succeeds? If yes, fix the wording before committing.
- Principle: Compaction resilience. Check: Did this session read `input.md`, `plan.md`, and `tasks.md` in full? If no, read them before touching implementation.

## Task Closure Protocol

Before closing a task, verify and record:

- Scope check: only the intended task was executed.
- Evidence check: validation evidence exists and is named in `tasks.md`.
- State check: code changes, commits, and `tasks.md` agree with each other.
- Risk check: remaining risk and next step are explicit.
- AAR check: record any new trap, missing rule, outdated assumption, or repeated failure pattern discovered during the task.

If any check fails, fix the workflow state or implementation before reporting completion.

## Checkpoints

After every three completed tasks, run a major check/debug loop before continuing. Record the result in `tasks.md`. Inspect at least:

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

If the checkpoint finds a bug, requirement drift, documentation mismatch, high-risk issue, or stale context outside `tasks.md`, do not fix implementation files in the checkpoint session. Insert the next repair task in `tasks.md`, record the evidence and risk, create the checkpoint tracking commit, and stop. The next goal-mode session must execute that repair as an ordinary task-boundary commit.

If the checkpoint only updates `tasks.md` inside a git repository, create one checkpoint tracking commit before moving on. Use message `goal-N checkpoint after task M: complete`, where `M` is the completed task count that triggered the checkpoint. Before committing, write durable checkpoint commit-status text such as `Commit status: included in checkpoint tracking commit message "goal-N checkpoint after task M: complete"`; do not commit pending, ready-to-commit, or to-be-created wording. If there is no git repository, record `Commit skipped: not a git repository`; if the commit fails, record the failure in `tasks.md` and stop before moving on. After the checkpoint tracking commit succeeds or is skipped, stop immediately; final review must wait for the next goal-mode session.

During a checkpoint-only session, do not edit `plan.md`, `input.md`, or implementation files. If a checkpoint discovers tracking drift, stale project paths, or documentation mismatch outside `tasks.md`, record the finding and next action in `tasks.md` instead of changing those files. Stage only `goal-N/tasks.md` for the checkpoint tracking commit. After committing, verify `git log -1 --oneline` shows `goal-N checkpoint after task M: complete` before reporting success. If the commit is missing, update `tasks.md` to record the commit failure and stop; do not leave `tasks.md` claiming the checkpoint commit exists.

## Final Review

When all tasks are complete, run the largest final review before marking the goal complete. Review the user-facing behavior, code quality, security, data consistency, permissions, error handling, tests, build, documentation, and rollback path.

Fix known high-risk issues by inserting follow-up repair tasks in `tasks.md` and stopping; do not patch implementation files inside the final-review session. When no high-risk issue remains, rerun relevant validation, update `tasks.md`, and set `Goal status: complete`. If this final review only changed `tasks.md` inside a git repository, create one final-review tracking commit with message `goal-N final review: complete`; do not use `goal-N task final: Final Review`. Before committing, write durable final-review commit-status text such as `Commit status: included in final-review tracking commit message "goal-N final review: complete"`; do not commit pending, ready-to-commit, or to-be-created wording. After committing, verify `git log -1 --oneline` shows `goal-N final review: complete` before reporting success or marking the goal complete. If there is no git repository, record `Commit skipped: not a git repository`; if the commit fails or the latest commit does not match, record the failure in `tasks.md` and stop before marking the goal complete.

After final-review tracking is committed or skipped, mark the registered goal complete with available goal tooling such as `update_goal`. After the final report, stop output. The client should not continue advancing after the goal is complete.

Future directory-layout migration note: this version intentionally keeps project-root `goal-current` and `goal-N/`. If a later version moves state under `.goal-mode/`, it must continue reading and safely resuming existing root-level goals.

## Rationalizations to Reject

Reject these before they turn into drift:

- "It's a tiny change, so tasks.md can wait."
- "I'll verify it later."
- "Tests take too long."
- "I already know it works."
- "Let's just do the next task too."
- "I finished the last task, so I can run final review now."
- "The user named three files, but they are small enough to be one task."
- "The user wants speed, so evidence can be light."
- "This time the red flag does not really count."
- "This is a tiny goal, so I can initialize and execute Task 1 in one session."
- "I can skip the task-boundary commit because the change is small."
- "A checkpoint only changed tasks.md, so it does not need a tracking commit."
- "The checkpoint commit succeeded, so I can run final review in the same session."
- "I can fix plan.md during a checkpoint because it is only tracking metadata."
- "The checkpoint commit probably succeeded, so tasks.md can say it exists."
- "The worktree is dirty, but those changes are probably related."
- "Final review can patch the implementation because the fix is obvious."
- "The final-review commit probably succeeded, so tasks.md can say it exists."
- "Final review is basically a task, so `goal-N task final: Final Review` is fine."
- "I'll leave commit status as pending and fix it after the commit."

## AAR Questions

After each completed task and at checkpoints, answer:

1. What new trap appeared?
2. What missing rule should be added?
3. What assumption is now outdated?
4. What failure pattern repeated?

Record the answer in `tasks.md` as part of the next-step note or checkpoint record.
