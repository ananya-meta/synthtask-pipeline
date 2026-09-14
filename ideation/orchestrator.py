"""High-level task-generation orchestration.

This module turns the lifecycle primitives into an end-to-end controller. It is allowed
to stop at explicit external boundaries: incomplete contracts, missing builder prompts,
local verification failures, and manual Smoldata upload.
"""

from __future__ import annotations

import json
import shlex
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import db, lifecycle, smoldata

STAGES = (
    "contract",
    "ready",
    "scaffold",
    "build",
    "verify",
    "audit",
    "promote",
    "smoldata",
    "learn",
)


class OrchestratorError(RuntimeError):
    pass


@dataclass
class PipelineRunConfig:
    idea_id: int | None = None
    contract_id: int | None = None
    scaffold_run_id: int | None = None
    bundle_id: int | None = None
    builder: str = "codex"
    model: str = ""
    build_prompt_file: Path | None = None
    verify_commands: list[list[str]] = field(default_factory=list)
    canonical_root: Path | None = None
    smoldata_task_name: str = ""
    smoldata_site: str = "default"
    source_repo: str = ""
    stop_after: str = "learn"
    force_contract: bool = False
    allow_draft_scaffold: bool = False
    contract_overrides: dict[str, str] = field(default_factory=dict)


@dataclass
class PipelineRunResult:
    completed: list[str] = field(default_factory=list)
    blocked_at: str = ""
    reason: str = ""
    ids: dict[str, Any] = field(default_factory=dict)
    next_action: str = ""

    def as_dict(self) -> dict:
        return {
            "completed": self.completed,
            "blocked_at": self.blocked_at,
            "reason": self.reason,
            "ids": self.ids,
            "next_action": self.next_action,
        }


def parse_command(value: str) -> list[str]:
    command = shlex.split(value)
    if not command:
        raise OrchestratorError("verification command cannot be empty")
    return command


def run(conn, config: PipelineRunConfig) -> PipelineRunResult:
    if config.stop_after not in STAGES:
        raise OrchestratorError(f"unknown stop stage {config.stop_after!r}")

    result = PipelineRunResult()
    target_index = STAGES.index(config.stop_after)

    def should_continue(stage: str) -> bool:
        return STAGES.index(stage) <= target_index

    contract_id = config.contract_id
    if should_continue("contract") and contract_id is None:
        if config.idea_id is None:
            return _blocked(result, "contract", "missing idea or contract", "pass --idea-id or --contract-id")
        try:
            contract_id = lifecycle.create_contract(
                conn,
                config.idea_id,
                discovery_bundle_id=config.bundle_id,
                force=config.force_contract,
                **config.contract_overrides,
            )
        except lifecycle.LifecycleError as exc:
            return _blocked(result, "contract", str(exc), f"ideation contract create {config.idea_id}")
        result.ids["contract_id"] = contract_id
        result.completed.append("contract")

    if contract_id is None:
        return result
    result.ids.setdefault("contract_id", contract_id)

    if should_continue("ready"):
        try:
            missing = lifecycle.mark_contract_ready(conn, contract_id)
        except lifecycle.LifecycleError as exc:
            return _blocked(result, "ready", str(exc), f"ideation contract ready {contract_id}")
        if missing:
            return _blocked(
                result,
                "ready",
                f"contract is incomplete: {', '.join(missing)}",
                f"fill contract #{contract_id}, then run `ideation contract ready {contract_id}`",
            )
        result.completed.append("ready")

    scaffold_run_id = config.scaffold_run_id
    if should_continue("scaffold") and scaffold_run_id is None:
        try:
            scaffold_run_id, root = lifecycle.start_scaffold(
                conn,
                contract_id,
                builder=config.builder,
                model=config.model,
                allow_draft=config.allow_draft_scaffold,
            )
        except lifecycle.LifecycleError as exc:
            return _blocked(result, "scaffold", str(exc), f"ideation scaffold start {contract_id}")
        result.ids["scaffold_run_id"] = scaffold_run_id
        result.ids["workspace_root"] = str(root)
        result.completed.append("scaffold")

    if scaffold_run_id is None:
        return result
    result.ids.setdefault("scaffold_run_id", scaffold_run_id)

    if should_continue("build"):
        scaffold = db.get_scaffold_run(conn, scaffold_run_id)
        built_states = {"built", "verified", "reviewed", "promoted", "submitted", "accepted"}
        if scaffold is not None and scaffold["state"] in built_states:
            result.completed.append("build")
        elif config.build_prompt_file is None:
            return _blocked(
                result,
                "build",
                "builder prompt file is required for automated scaffold generation",
                f"ideation scaffold run {scaffold_run_id} --prompt-file /path/to/build_prompt.md",
            )
        else:
            try:
                rc = lifecycle.run_scaffold_worker(
                    conn,
                    scaffold_run_id,
                    config.build_prompt_file,
                )
            except lifecycle.LifecycleError as exc:
                return _blocked(result, "build", str(exc), f"ideation scaffold run {scaffold_run_id}")
            if rc != 0:
                return _blocked(result, "build", f"builder exited {rc}", "inspect worker_stderr.log")
            result.completed.append("build")

    if should_continue("verify"):
        passing = conn.execute(
            "SELECT id FROM verification_runs WHERE scaffold_run_id = ? AND status = 'pass'",
            (scaffold_run_id,),
        ).fetchone()
        if passing is not None:
            result.completed.append("verify")
        elif not config.verify_commands:
            return _blocked(
                result,
                "verify",
                "at least one local verifier command is required",
                f"ideation verify run {scaffold_run_id} --cwd task -- <command>",
            )
        else:
            for command in config.verify_commands:
                verify_id = lifecycle.run_verification(conn, scaffold_run_id, command, cwd_choice="task")
                row = conn.execute(
                    "SELECT status FROM verification_runs WHERE id = ?", (verify_id,)
                ).fetchone()
                if row["status"] != "pass":
                    result.ids["verification_id"] = verify_id
                    return _blocked(result, "verify", f"verification #{verify_id} {row['status']}", "fix scaffold or verifier")
            result.completed.append("verify")

    if should_continue("audit"):
        approved = conn.execute(
            "SELECT id FROM review_records WHERE scaffold_run_id = ? AND verdict = 'approve'",
            (scaffold_run_id,),
        ).fetchone()
        if approved is None:
            return _blocked(
                result,
                "audit",
                "no approving adversarial review is recorded",
                f"ideation audit record {scaffold_run_id} --reviewer <name> --verdict approve",
            )
        result.completed.append("audit")

    if should_continue("promote"):
        scaffold = db.get_scaffold_run(conn, scaffold_run_id)
        if scaffold is None:
            return _blocked(result, "promote", "scaffold disappeared", "inspect scaffold list")
        if scaffold["canonical_root"]:
            result.completed.append("promote")
        elif config.canonical_root is None:
            return _blocked(
                result,
                "promote",
                "canonical output directory is required",
                f"ideation scaffold promote {scaffold_run_id} /path/to/canonical-task-root",
            )
        else:
            try:
                lifecycle.promote_scaffold(conn, scaffold_run_id, config.canonical_root)
            except lifecycle.LifecycleError as exc:
                return _blocked(result, "promote", str(exc), f"ideation scaffold promote {scaffold_run_id}")
            result.completed.append("promote")

    if should_continue("smoldata"):
        if not config.smoldata_task_name:
            return _blocked(
                result,
                "smoldata",
                "Smoldata upload is external; record the resulting task name once uploaded",
                f"ideation submission record {scaffold_run_id} --platform smoldata --external-id <task> --status pending",
            )
        try:
            watched = smoldata.watch_task(
                config.smoldata_task_name,
                site=config.smoldata_site,
            )
            review = smoldata.agentic_review(
                config.smoldata_task_name,
                site=config.smoldata_site,
                source_repo=config.source_repo,
                wait=False,
            )
        except smoldata.SmoldataError as exc:
            return _blocked(result, "smoldata", str(exc), f"codimango api tasks show {config.smoldata_task_name}")
        record = smoldata.submission_record(
            config.smoldata_task_name,
            status=review["status"] or watched["status"],
            payload={"watch": watched.get("payload"), "review": review.get("payload")},
        )
        submission_id = lifecycle.record_submission(conn, scaffold_run_id, **record)
        result.ids["submission_id"] = submission_id
        result.completed.append("smoldata")

    if should_continue("learn"):
        summary = lifecycle.pipeline_summary(conn)
        event_id = lifecycle.record_learning(
            conn,
            scope_type="scaffold",
            scope_id=scaffold_run_id,
            label="pipeline-run",
            detail="Recorded end-to-end pipeline state after run.",
            payload={"summary": summary},
        )
        result.ids["learning_event_id"] = event_id
        result.completed.append("learn")

    return result


def _blocked(result: PipelineRunResult, stage: str, reason: str, next_action: str) -> PipelineRunResult:
    result.blocked_at = stage
    result.reason = reason
    result.next_action = next_action
    return result
