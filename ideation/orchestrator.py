"""High-level task-generation orchestration.

This module turns the lifecycle primitives into an end-to-end controller. It is allowed
to stop at explicit external boundaries: incomplete contracts, missing builder prompts,
local verification failures, publish failures, and pending Smoldata validation.
"""

from __future__ import annotations

import json
import shlex
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import db, lifecycle, publisher, smoldata

DEFAULT_BUILD_PROMPT = db.REPO_ROOT / "prompts" / "build_task.md"

STAGES = (
    "contract",
    "ready",
    "scaffold",
    "build",
    "verify",
    "audit",
    "promote",
    "publish",
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
    publish_task_name: str = ""
    publish_remote: str = ""
    publish_branch: str = publisher.DEFAULT_BRANCH
    publish_message: str = ""
    publish_push: bool = True
    publish_overwrite: bool = False
    publish_method: str = "auto"
    smoldata_task_name: str = ""
    smoldata_site: str = "default"
    source_repo: str = ""
    stop_after: str = "learn"
    force_contract: bool = False
    allow_draft_scaffold: bool = False
    allow_build: bool = True
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


def apply_contract_settings(conn, contract_id: int, config: PipelineRunConfig) -> None:
    """Fill unset config fields from the contract's stored settings.

    Explicit flags always win; this only supplies what the caller left blank, which is
    what lets an unattended sweep advance a task with no per-task arguments.
    """
    row = db.get_contract_settings(conn, contract_id)
    if row is None:
        return

    if not config.verify_commands and row["verify_commands"]:
        try:
            stored = json.loads(row["verify_commands"])
        except json.JSONDecodeError as exc:
            raise OrchestratorError(
                f"contract #{contract_id} has invalid verify_commands JSON"
            ) from exc
        config.verify_commands = [parse_command(cmd) for cmd in stored]

    if config.canonical_root is None and row["canonical_root"]:
        config.canonical_root = Path(row["canonical_root"])

    for attr in ("publish_task_name", "publish_remote", "source_repo"):
        if not getattr(config, attr) and row[attr]:
            setattr(config, attr, row[attr])

    if config.publish_branch == publisher.DEFAULT_BRANCH and row["publish_branch"]:
        config.publish_branch = row["publish_branch"]
    if config.publish_method == "auto" and row["publish_method"]:
        config.publish_method = row["publish_method"]
    if config.smoldata_site == "default" and row["smoldata_site"]:
        config.smoldata_site = row["smoldata_site"]


def run(conn, config: PipelineRunConfig) -> PipelineRunResult:
    if config.stop_after not in STAGES:
        raise OrchestratorError(f"unknown stop stage {config.stop_after!r}")

    result = PipelineRunResult()
    target_index = STAGES.index(config.stop_after)

    def should_continue(stage: str) -> bool:
        return STAGES.index(stage) <= target_index

    contract_id = config.contract_id
    if contract_id is None and config.scaffold_run_id is not None:
        scaffold = db.get_scaffold_run(conn, config.scaffold_run_id)
        if scaffold is None:
            return _blocked(
                result,
                "contract",
                f"no scaffold run #{config.scaffold_run_id}",
                "synthtask scaffold list",
            )
        contract_id = scaffold["contract_id"]

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
            return _blocked(result, "contract", str(exc), f"synthtask contract create {config.idea_id}")
        result.ids["contract_id"] = contract_id
        result.completed.append("contract")

    if contract_id is None:
        return result
    result.ids.setdefault("contract_id", contract_id)
    apply_contract_settings(conn, contract_id, config)

    if should_continue("ready"):
        try:
            missing = lifecycle.mark_contract_ready(conn, contract_id)
        except lifecycle.LifecycleError as exc:
            return _blocked(result, "ready", str(exc), f"synthtask contract ready {contract_id}")
        if missing:
            return _blocked(
                result,
                "ready",
                f"contract is incomplete: {', '.join(missing)}",
                f"fill contract #{contract_id}, then run `synthtask contract ready {contract_id}`",
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
            return _blocked(result, "scaffold", str(exc), f"synthtask scaffold start {contract_id}")
        result.ids["scaffold_run_id"] = scaffold_run_id
        result.ids["workspace_root"] = str(root)
        result.completed.append("scaffold")

    if scaffold_run_id is None:
        return result
    result.ids.setdefault("scaffold_run_id", scaffold_run_id)

    if should_continue("build"):
        scaffold = db.get_scaffold_run(conn, scaffold_run_id)
        built_states = {"built", "verified", "reviewed", "promoted", "submitted", "accepted"}
        build_prompt_file = config.build_prompt_file
        if build_prompt_file is None and DEFAULT_BUILD_PROMPT.exists():
            build_prompt_file = DEFAULT_BUILD_PROMPT
        if scaffold is not None and scaffold["state"] in built_states:
            result.completed.append("build")
        elif not config.allow_build:
            return _blocked(
                result,
                "build",
                "scaffold is not built and this run may not invoke a builder",
                f"synthtask scaffold run {scaffold_run_id} --prompt-file {DEFAULT_BUILD_PROMPT}",
            )
        elif build_prompt_file is None:
            return _blocked(
                result,
                "build",
                "builder prompt file is required for automated scaffold generation",
                f"synthtask scaffold run {scaffold_run_id} --prompt-file /path/to/build_prompt.md",
            )
        else:
            try:
                rc = lifecycle.run_scaffold_worker(
                    conn,
                    scaffold_run_id,
                    build_prompt_file,
                )
            except lifecycle.LifecycleError as exc:
                return _blocked(result, "build", str(exc), f"synthtask scaffold run {scaffold_run_id}")
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
                f"synthtask verify run {scaffold_run_id} --cwd task -- <command>",
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
                f"synthtask audit record {scaffold_run_id} --reviewer <name> --verdict approve",
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
                f"synthtask scaffold promote {scaffold_run_id} /path/to/canonical-task-root",
            )
        else:
            try:
                lifecycle.promote_scaffold(conn, scaffold_run_id, config.canonical_root)
            except lifecycle.LifecycleError as exc:
                return _blocked(result, "promote", str(exc), f"synthtask scaffold promote {scaffold_run_id}")
            result.completed.append("promote")

    if should_continue("publish"):
        publish_record = db.publish_record_for_scaffold(conn, scaffold_run_id)
        if publish_record is not None:
            result.ids["publish_record_id"] = publish_record["id"]
            result.ids["published_task_name"] = publish_record["task_name"]
            result.completed.append("publish")
        else:
            scaffold = db.get_scaffold_run(conn, scaffold_run_id)
            if scaffold is None:
                return _blocked(result, "publish", "scaffold disappeared", "inspect scaffold list")
            if not scaffold["canonical_root"]:
                return _blocked(
                    result,
                    "publish",
                    "scaffold has no canonical root",
                    f"synthtask scaffold promote {scaffold_run_id} /path/to/canonical-task-root",
                )
            task_name = (
                config.publish_task_name
                or config.smoldata_task_name
                or Path(scaffold["canonical_root"]).name
            )
            try:
                publish_record_id = publisher.publish_scaffold(
                    conn,
                    scaffold_run_id,
                    task_name=task_name,
                    remote_url=config.publish_remote or None,
                    branch=config.publish_branch,
                    message=config.publish_message,
                    push=config.publish_push,
                    overwrite=config.publish_overwrite,
                    method=config.publish_method,
                )
            except publisher.PublishError as exc:
                return _blocked(
                    result,
                    "publish",
                    str(exc),
                    f"synthtask publish run {scaffold_run_id} --task-name {task_name}",
                )
            publish_record = db.publish_record_for_scaffold(conn, scaffold_run_id)
            result.ids["publish_record_id"] = publish_record_id
            result.ids["published_task_name"] = task_name
            if publish_record is not None:
                result.ids["published_github_url"] = publish_record["github_url"]
            result.completed.append("publish")

    if should_continue("smoldata"):
        task_name = config.smoldata_task_name
        publish_record = db.publish_record_for_scaffold(conn, scaffold_run_id)
        if not task_name and publish_record is not None:
            task_name = publish_record["task_name"]
        if publish_record is not None and publish_record["status"] == "committed":
            return _blocked(
                result,
                "smoldata",
                "task was committed in a temporary publish clone but not pushed",
                f"synthtask publish run {scaffold_run_id} --task-name {publish_record['task_name']}",
            )
        if not task_name:
            return _blocked(
                result,
                "smoldata",
                "task is not published yet; Codimango needs the task repo path before validation can be watched",
                f"synthtask publish run {scaffold_run_id} --task-name <task-name>",
            )
        try:
            watched = smoldata.watch_task(
                task_name,
                site=config.smoldata_site,
            )
            review = smoldata.agentic_review(
                task_name,
                site=config.smoldata_site,
                source_repo=config.source_repo
                or (publisher.github_repo_name(publish_record["remote_url"]) if publish_record else ""),
                wait=False,
            )
        except smoldata.SmoldataError as exc:
            return _blocked(result, "smoldata", str(exc), f"codimango api tasks show {task_name}")
        record = smoldata.submission_record(
            task_name,
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
