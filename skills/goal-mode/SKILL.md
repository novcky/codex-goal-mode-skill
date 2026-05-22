---
name: goal-mode
description: Unattended goal workflow for Codex. Use only when the user explicitly includes `/goal` or asks to enter goal mode. Initializes goal-N files before edits, registers available goal/task tools, runs one task per session, stops on red flags, verifies concrete evidence, updates tasks.md, and continues until complete.
---

# Goal Mode

## Trigger Guard

Use this skill only when the user explicitly includes `/goal` or explicitly says to enter goal mode. Do not trigger it for ordinary planning, task lists, or long implementation requests that do not ask for goal mode.

Goal mode is designed for unattended execution. Avoid asking the user questions. When information is uncertain, choose a reasonable default assumption, write it in `plan.md` or `tasks.md`, and keep working on parts that do not depend on the missing detail.

## Required Load

Before any initialization or task execution, read [references/goal-workflow.md](references/goal-workflow.md) in full.

## Core Contract

The detailed session loop, task closure protocol, checkpoints, final review, rejected rationalizations, and AAR questions live in the reference file.

- On the first goal-mode turn, initialize the goal and end with `GOAL_INIT_DONE`.
- Start each generated `tasks.md` with the runtime contract block from the reference file.
- Execute only one task per session.
- Verify with concrete evidence before closing a task.
- Update `tasks.md` with work, evidence, risk, and next step.
- Stop on red flags instead of pushing ahead.

## Red Flags - STOP

Stop task execution and repair the workflow state first if you notice:

- you are about to skip validation or rely on a verbal confidence claim
- you are about to execute a second task in the same session
- you are about to ask the user a question instead of recording an assumption
- you started a new session or resumed after compaction without rereading all three goal files
- you changed code but did not update `tasks.md`
- `tasks.md` is missing the Runtime Contract, task status, evidence, risk, or next step fields
- the current task requires production secrets, payment/auth changes, data deletion, or another high-risk action without explicit authorization
- you caught a Rationalization to Reject from the reference file

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
