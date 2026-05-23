#!/usr/bin/env python3
"""Scenario regression checks for the goal-mode workflow contract."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_REF = ROOT / "skills" / "goal-mode" / "references" / "goal-workflow.md"


@dataclass(frozen=True)
class Decision:
    action: str
    must_stop: bool
    forbidden_next: frozenset[str]


class GoalModePolicy:
    """Tiny executable model of the workflow states that failed in real runs."""

    def after_initialization(self) -> Decision:
        return Decision("GOAL_INIT_DONE", True, frozenset({"execute_task_1", "commit", "final_review"}))

    def after_compaction_without_full_read(self) -> Decision:
        return Decision("read_goal_files", True, frozenset({"touch_implementation", "close_task"}))

    def after_task_boundary(self) -> Decision:
        return Decision("report_and_stop", True, frozenset({"checkpoint", "final_review", "next_task"}))

    def after_checkpoint_tracking(self) -> Decision:
        return Decision("report_and_stop", True, frozenset({"final_review", "next_task"}))

    def final_review_completion(
        self,
        *,
        tracking_committed: bool,
        latest_commit_verified: bool,
        high_risk_issue: bool,
    ) -> Decision:
        if tracking_committed and latest_commit_verified and not high_risk_issue:
            return Decision(
                "mark_goal_complete_and_stop",
                True,
                frozenset({"checkpoint", "next_task", "task_work"}),
            )
        return Decision(
            "record_blocker_or_insert_repair_task",
            True,
            frozenset({"final_report", "mark_goal_complete"}),
        )


@dataclass(frozen=True)
class Scenario:
    name: str
    decision: Decision
    expected_action: str
    expected_must_stop: bool
    expected_forbidden_next: frozenset[str]
    required_reference_phrase: str


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def assert_decision(scenario: Scenario, reference_text: str) -> None:
    if scenario.required_reference_phrase not in reference_text:
        fail(f"{scenario.name}: missing reference phrase: {scenario.required_reference_phrase}")
    if scenario.decision.action != scenario.expected_action:
        fail(
            f"{scenario.name}: action {scenario.decision.action!r} "
            f"!= {scenario.expected_action!r}"
        )
    if scenario.decision.must_stop != scenario.expected_must_stop:
        fail(
            f"{scenario.name}: must_stop {scenario.decision.must_stop!r} "
            f"!= {scenario.expected_must_stop!r}"
        )
    if scenario.decision.forbidden_next != scenario.expected_forbidden_next:
        fail(
            f"{scenario.name}: forbidden_next {sorted(scenario.decision.forbidden_next)!r} "
            f"!= {sorted(scenario.expected_forbidden_next)!r}"
        )


def main() -> None:
    reference_text = WORKFLOW_REF.read_text(encoding="utf-8")
    policy = GoalModePolicy()

    scenarios = [
        Scenario(
            "goal_context initialization stops before Task 1",
            policy.after_initialization(),
            "GOAL_INIT_DONE",
            True,
            frozenset({"commit", "execute_task_1", "final_review"}),
            "Do not combine initialization with task execution, even for tiny goals.",
        ),
        Scenario(
            "compaction requires full goal-file reread",
            policy.after_compaction_without_full_read(),
            "read_goal_files",
            True,
            frozenset({"close_task", "touch_implementation"}),
            "At the start of every later session, and after every context compaction:",
        ),
        Scenario(
            "task boundary commit stops before checkpoint",
            policy.after_task_boundary(),
            "report_and_stop",
            True,
            frozenset({"checkpoint", "final_review", "next_task"}),
            "Do not run a checkpoint or final review in the same session that completed a task boundary",
        ),
        Scenario(
            "checkpoint tracking commit stops before final review",
            policy.after_checkpoint_tracking(),
            "report_and_stop",
            True,
            frozenset({"final_review", "next_task"}),
            "After the checkpoint tracking commit succeeds or is skipped, stop immediately; final review must wait for the next goal-mode session.",
        ),
        Scenario(
            "final review requires verified tracking commit before completion",
            policy.final_review_completion(
                tracking_committed=True,
                latest_commit_verified=True,
                high_risk_issue=False,
            ),
            "mark_goal_complete_and_stop",
            True,
            frozenset({"checkpoint", "next_task", "task_work"}),
            "After final-review tracking is committed or skipped, mark the registered goal complete",
        ),
        Scenario(
            "final review blocks completion when tracking commit is missing",
            policy.final_review_completion(
                tracking_committed=False,
                latest_commit_verified=True,
                high_risk_issue=False,
            ),
            "record_blocker_or_insert_repair_task",
            True,
            frozenset({"final_report", "mark_goal_complete"}),
            "After final-review tracking is committed or skipped, mark the registered goal complete",
        ),
        Scenario(
            "final review blocks completion when verification is missing",
            policy.final_review_completion(
                tracking_committed=True,
                latest_commit_verified=False,
                high_risk_issue=False,
            ),
            "record_blocker_or_insert_repair_task",
            True,
            frozenset({"final_report", "mark_goal_complete"}),
            "If there is no git repository, record `Commit skipped: not a git repository`; if the commit fails or the latest commit does not match, record the failure in `tasks.md` and stop before marking the goal complete.",
        ),
        Scenario(
            "final review blocks completion when high-risk issue remains",
            policy.final_review_completion(
                tracking_committed=True,
                latest_commit_verified=True,
                high_risk_issue=True,
            ),
            "record_blocker_or_insert_repair_task",
            True,
            frozenset({"final_report", "mark_goal_complete"}),
            "Fix known high-risk issues by inserting follow-up repair tasks in `tasks.md` and stopping",
        ),
    ]

    for scenario in scenarios:
        assert_decision(scenario, reference_text)

    print("goal-mode scenario regression checks passed")


if __name__ == "__main__":
    main()
