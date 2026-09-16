"""Unattended sweep: refresh external validation state and advance opted-in scaffolds.

Deliberately narrower than `pipeline run`. The sweep never drafts a contract, starts a
scaffold, invokes a builder, records an audit verdict, or decides how to revise a
rejected task — those stay human calls. It does two things: re-polls Codimango for
submissions whose validation has not settled, and advances scaffolds whose contract
opted in via `auto_advance`.

Polling uses `smoldata.show_task` rather than `watch_task`: a watch blocks until the
run finishes, which is wrong for a fixed-interval cron.
"""

from __future__ import annotations

import fcntl
import time
from contextlib import contextmanager
from pathlib import Path

from . import db, lifecycle, orchestrator, smoldata

LOCK_PATH = db.REPO_ROOT / "data" / "sweep.lock"
POLL_TIMEOUT = 300

# Stages the sweep may drive on its own. `contract` and `scaffold` would fan out new
# work, `audit` is the review gate, and `triage` is the call on how to revise a
# rejected task — all four are reported and left alone.
DISPATCHABLE_STAGES = ("verify", "promote", "publish", "smoldata", "learn")
HUMAN_STAGES = ("contract", "scaffold", "audit", "triage")


class SweepError(RuntimeError):
    pass


@contextmanager
def exclusive_lock(path: Path = LOCK_PATH):
    """Refuse to start when a previous tick is still running."""
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a+")
    try:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise SweepError(f"another sweep already holds {path}") from exc
        yield
    finally:
        handle.close()


def _settings(conn, contract_id: int | None):
    return db.get_contract_settings(conn, contract_id) if contract_id else None


def _site_for(conn, contract_id: int | None) -> str:
    row = _settings(conn, contract_id)
    return row["smoldata_site"] if row and row["smoldata_site"] else "default"


def _auto_advance(conn, contract_id: int | None) -> bool:
    row = _settings(conn, contract_id)
    return bool(row and row["auto_advance"])


def poll_action(conn, action: dict) -> dict:
    task_name = action.get("task_name") or ""
    if not task_name:
        raise SweepError("submission has no task name to poll")
    observed = smoldata.show_task(
        task_name,
        site=_site_for(conn, action.get("contract_id")),
        timeout=POLL_TIMEOUT,
    )
    record = smoldata.submission_record(
        task_name,
        status=observed["status"],
        payload={"show": observed.get("payload")},
    )
    submission_id = lifecycle.record_submission(
        conn, action["scaffold_run_id"], **record
    )
    return {"submission_id": submission_id, "status": observed["status"]}


def advance_action(conn, action: dict) -> dict:
    config = orchestrator.PipelineRunConfig(
        scaffold_run_id=action["scaffold_run_id"],
        allow_build=False,
    )
    return orchestrator.run(conn, config).as_dict()


def run(conn, *, dry_run: bool = False, limit: int = 50) -> dict:
    summary: dict = {
        "started_at": time.time(),
        "dry_run": dry_run,
        "polled": [],
        "advanced": [],
        "waiting_on_you": [],
        "skipped": [],
        "errors": [],
    }
    touched: set[int] = set()

    for action in lifecycle.next_actions(conn, limit=limit):
        stage = action["stage"]
        entry = {
            "stage": stage,
            "target": action["target"],
            "action": action["action"],
        }

        if stage in HUMAN_STAGES:
            summary["waiting_on_you"].append({**entry, "reason": action["reason"]})
            continue

        scaffold_run_id = action.get("scaffold_run_id")
        if scaffold_run_id in touched:
            summary["skipped"].append(
                {**entry, "reason": "scaffold already advanced earlier in this sweep"}
            )
            continue

        if stage == "poll":
            entry["task_name"] = action.get("task_name", "")
            if dry_run:
                summary["polled"].append({**entry, "dry_run": True})
                continue
            try:
                summary["polled"].append({**entry, **poll_action(conn, action)})
                touched.add(scaffold_run_id)
            except (SweepError, smoldata.SmoldataError, lifecycle.LifecycleError) as exc:
                summary["errors"].append({**entry, "error": str(exc)})
            continue

        if stage in DISPATCHABLE_STAGES:
            if not _auto_advance(conn, action.get("contract_id")):
                summary["skipped"].append(
                    {**entry, "reason": "contract has auto_advance disabled"}
                )
                continue
            if dry_run:
                summary["advanced"].append({**entry, "dry_run": True})
                continue
            try:
                summary["advanced"].append({**entry, "result": advance_action(conn, action)})
                touched.add(scaffold_run_id)
            except (
                orchestrator.OrchestratorError,
                lifecycle.LifecycleError,
                smoldata.SmoldataError,
            ) as exc:
                summary["errors"].append({**entry, "error": str(exc)})
            continue

        summary["skipped"].append({**entry, "reason": f"stage {stage!r} is not sweepable"})

    summary["finished_at"] = time.time()
    return summary


def format_summary(summary: dict) -> str:
    stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(summary["started_at"]))
    prefix = "[dry-run] " if summary["dry_run"] else ""
    lines = [
        f"{prefix}{stamp}  polled={len(summary['polled'])}"
        f" advanced={len(summary['advanced'])}"
        f" waiting={len(summary['waiting_on_you'])}"
        f" skipped={len(summary['skipped'])}"
        f" errors={len(summary['errors'])}"
    ]
    for item in summary["polled"]:
        lines.append(f"  poll     {item['target']} -> {item.get('status', 'dry-run')}")
    for item in summary["advanced"]:
        result = item.get("result") or {}
        outcome = (
            f"blocked at {result['blocked_at']}: {result['reason']}"
            if result.get("blocked_at")
            else f"completed {', '.join(result.get('completed', [])) or 'nothing'}"
        )
        lines.append(f"  advance  {item['target']} -> {outcome}")
    for item in summary["waiting_on_you"]:
        lines.append(f"  waiting  {item['target']} -> {item['action']}")
    for item in summary["skipped"]:
        lines.append(f"  skipped  {item['target']} -> {item['reason']}")
    for item in summary["errors"]:
        lines.append(f"  ERROR    {item['target']} -> {item['error']}")
    return "\n".join(lines)
